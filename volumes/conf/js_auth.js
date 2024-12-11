const qs = require('querystring');
const fs = require('fs');

const users_data_dir = '/usr/share/data/users';

const auth_issuers = ['google', 'github', 'oidc', 'azure', 'facebook', 'keycloak', 'linkedin'];
const admin_emails = process.env.ADMIN_EMAILS.split(' ');

async function _fetch_userinfo(r) {
    const has_info = auth_issuers.filter(
        (iss) => r.variables[`auth_${iss}_upstream`] && r.variables[`cookie_auth_${iss}`]
    );

    const responses = await Promise.all(
        has_info.map((iss) => r.subrequest(`/auth/${iss}/userinfo`))
    );

    let user_info = {};

    responses.forEach((resp) => {
        let iss = resp.uri.split('/')[2];
        if (resp.status == 200) {
            let data = JSON.parse(resp.responseText);

            if (!user_info.hasOwnProperty('user_email')) {
                user_info['auth_iss'] = iss;
                user_info['auth_uid'] = data['user'];
                user_info['user_email'] = data['email'];
                // user_info['user_name'] = data['email'].split('@')[0];
                // user_info['user_avatar'] = '';
            }

            user_info[`auth_${iss}_uid`] = data['user'];
            user_info[`auth_${iss}_email`] = data['email'];
        }
    });

    return user_info;
}

async function _load_userinfo(user_email) {
    let user_info = {};

    try {
        let user_json = await fs.promises.readFile(`${users_data_dir}/${user_email}.json`);
        user_info = JSON.parse(user_json.toString('utf8'));
    } catch (e) {
        console.error(e);
    }

    return user_info;
}

async function _dump_userinfo(user_email, user_info) {
    const user_json = JSON.stringify(user_info, null, 4);

    try {
        await fs.promises.writeFile(`${users_data_dir}/${user_email}.json`, user_json);
    } catch (e) {
        console.error(e);
    }

    return user_info;
}

async function _refresh_userinfo(r, user_info_extra) {
    const user_info_auth = await _fetch_userinfo(r);
    const user_email = user_info_auth['user_email'];
    if (!user_email) return {};

    const user_info_stor = await _load_userinfo(user_email);
    const user_info = Object.assign({}, user_info_stor, user_info_auth, user_info_extra || {});

    if (!user_info['user_name']) {
        user_info['user_name'] = user_email.split('@')[0];
    }

    if (!user_info['user_avatar']) {
        let ehash = await crypto.subtle.digest('SHA-256', user_email);
        let ehash_hex = Buffer.from(ehash).toString('hex');
        user_info['user_avatar'] = `https://gravatar.com/avatar/${ehash_hex}?d=identicon&s=40`;
    }

    return user_info;
}

// async function _get_userinfo(r) {

//     const request_sid = r.variables.request_sid;

//     let user_info = {};
//     let user_email = ngx.shared['auth_sessions'].get(request_sid);
//     if (user_email) user_info = await _load_userinfo(user_email);

//     if (!user_email || !user_info['user_email']) {
//         user_info = await _refresh_userinfo(r, {'user_groups': ['member']});
//         user_email = user_info['user_email'];

//         if (user_email) {
//             ngx.shared['auth_sessions'].set(request_sid, user_email);
//             user_info = await _dump_userinfo(user_email, user_info);
//         }
//     }

//     return user_info;
// }

// async function auth_request(r) {
//     let ret_iss = null;
//     let ret_uid = null;
//     let ret_email = null;

//     for (let i = 0; i < auth_issuers.length; i++) {
//         let iss_name = auth_issuers[i];

//         if (r.variables[`auth_${iss_name}_upstream`] && r.variables[`cookie_auth_${iss_name}`]) {
//             let resp = await r.subrequest(`/auth/${iss_name}/auth`);
//             if (resp.status == 202) {
//                 ret_iss = iss_name;
//                 ret_uid = resp.headersOut['X-Auth-Request-User'];
//                 ret_email = resp.headersOut['X-Auth-Request-Email'];
//             }
//         }
//         if (ret_iss) break;
//     }

//     r.headersOut['Content-Type'] = 'text/plain';

//     if (ret_iss) {
//         r.headersOut['X-Auth-Iss'] = ret_iss;
//         r.headersOut['X-Auth-Uid'] = ret_uid;
//         r.headersOut['X-User-Email'] = ret_email;
//         r.return(202);
//     } else {
//         r.return(401);
//     }
// }

async function user_sign_in(r) {
    const request_sid = r.variables.request_sid;
    const redirect_url = r.variables.arg_rd || '/';

    if (ngx.shared['auth_sessions'].get(request_sid)) {
        ngx.shared['auth_sessions'].delete(request_sid);
    }

    const user_info = await _refresh_userinfo(r, {'user_groups': ['member']});
    const user_email = user_info['user_email'];

    if (user_email) {
        ngx.shared['auth_sessions'].set(request_sid, user_email);
        await _dump_userinfo(user_email, user_info);
    }

    r.headersOut['Content-Type'] = 'text/plain';
    r.return(301, redirect_url);
}

async function user_sign_out(r) {
    const request_sid = r.variables.request_sid;
    const redirect_url = r.variables.arg_rd || '/';

    let set_cookie_header = [];

    for (let i = 0; i < auth_issuers.length; i++) {
        let iss_name = auth_issuers[i];

        if (r.variables[`cookie_auth_${iss_name}`]) {
            set_cookie_header.push(
                `auth_${iss_name}=; Path=/; Max-Age=-1; SameSite=Lax; Secure`
            );
        }
    }

    if (ngx.shared['auth_sessions'].get(request_sid)) {
        ngx.shared['auth_sessions'].delete(request_sid);
    }

    r.headersOut['Content-Type'] = 'text/plain';
    r.headersOut['Set-Cookie'] = set_cookie_header;
    r.return(301, redirect_url);
}

// async function user_variables(r) {
//     const userinfo = await _fetch_userinfo(r);
//     let response_text = '';

//     for (let key in userinfo) {
//         let val = userinfo[key];
//         response_text += `<!--# set var='${key}' value='${val}' -->`;
//     }

//     r.headersOut['Content-Type'] = 'text/html';
//     r.return(200, response_text);
// }

async function user_information(r) {
    const user_email = ngx.shared['auth_sessions'].get(r.variables.request_sid);

    if (user_email && r.method == 'POST') {
        const post_args = qs.parse(r.requestText);
        const prev_path = (post_args.prev) ? post_args.prev : r.variables.request_uri;

        const user_info = await _refresh_userinfo(r, {'user_name': post_args.user_name});
        await _dump_userinfo(user_email, user_info);

        r.return(302, prev_path);

    } else {
        const user_info = (user_email) ? await _load_userinfo(user_email) : {};
        const user_json = JSON.stringify(user_info);

        r.headersOut['Content-Type'] = 'application/json';
        r.return(200, user_json);
    }
}

// async function set_user_information(r) {
//     const post_args = qs.parse(r.requestText);
//     const prev_path = (post_args.prev) ? post_args.prev : '/';

//     const user_email = ngx.shared['auth_sessions'].get(r.variables.request_sid);
//     if (user_email && post_args.user_name) {
//         const user_info = await _refresh_userinfo(r, {'user_name': post_args.user_name});
//         await _dump_userinfo(user_email, user_info);
//     }

//     r.return(302, prev_path);
// }

// function get_user_property(r, property) {
//     const user_email = ngx.shared['auth_sessions'].get(r.variables.request_sid);

//     let result;

//     if (!user_email) {
//         result = '';

//     } else if (property == 'user_email') {
//         result = user_email;

//     } else {
//         try {
//             let user_json = fs.readFileSync(`${users_data_dir}/${user_email}.json`);
//             let user_info = JSON.parse(user_json.toString('utf8'));
//             result = user_info[property] || '';
//         } catch (e) {
//             console.error(e);
//         }
//     }

//     return result;
// }

// const get_user_name = (r) => get_user_property(r, 'user_name');
// const get_user_email = (r) => get_user_property(r, 'user_email');
// const get_user_avatar = (r) => get_user_property(r, 'user_avatar');


function user_set_variables(r) {
    const user_email = ngx.shared['auth_sessions'].get(r.variables.request_sid);

    if (user_email) {
        // const is_admin = admin_emails.includes(user_email);
        let user_json;

        try {
            user_json = fs.readFileSync(`${users_data_dir}/${user_email}.json`);
        } catch (e) {
            console.error(e);
        }

        if (user_json) {
            const user_info = JSON.parse(user_json.toString('utf8'));

            r.variables['user_name'] = user_info['user_name'];
            r.variables['user_avatar'] = user_info['user_avatar'];
            r.variables['user_groups'] = user_info['user_groups'].join(', ');
        }
    }

    return user_email || '';
}

function user_is_superadmin(r) {
    const user_email = ngx.shared['auth_sessions'].get(r.variables.request_sid);
    return (user_email && admin_emails.includes(user_email)) ? 'yes' : '';
}

export default {
    user_set_variables, user_is_superadmin,
    user_sign_in, user_sign_out, user_information
};
