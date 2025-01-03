const qs = require('querystring');
const fs = require('fs');

const data_dir = '/usr/share/data';
const default_lang = 'en';
const default_path = '/en/';

const json_load = (path) => {
    let result;
    try {
        result = JSON.parse(fs.readFileSync(path, 'utf8'));
    } catch (e) {
        console.error(`json_load error; ${path}; ${e}`);
    }
    return result;
};

const langs_dict = {
    'ja': json_load(`${data_dir}/langs/ja.json`),
    'uk': json_load(`${data_dir}/langs/uk.json`),
};

const http_errors = json_load(`${data_dir}/dicts/http_errors.json`);

const gettext = (lang, text) => {
    if (!langs_dict[lang]) return text;

    if (!langs_dict[lang][text]) return text;

    return langs_dict[lang][text];
}

const env_project_name = (r) => process.env.PROJECT_NAME;
const env_project_domain = (r) => process.env.PROJECT_DOMAIN;
const env_project_title = (r) => gettext(r.variables.request_lang, process.env.PROJECT_TITLE);
const env_project_description = (r) => gettext(r.variables.request_lang, process.env.PROJECT_DESCRIPTION);

const _trans_tags_re = /<([a-z][a-z1-6]*)(\s+[^>]*?)translate(?:="yes")?>(.{2,}?)<\/\1>/ig;
const _trans_tags = (lang, data) => {
    return data.replace(_trans_tags_re, (match, tag, extr, text) => {
        const text_t = gettext(lang, text);

        if (text == text_t) {
            return `<${tag}${extr} lang="${default_lang}">${text}</${tag}>`;
        } else {
            return `<${tag}${extr}>${text_t}</${tag}>`;
        }
    });
}

const _trans_vars_re = /(<!--# set var='document_title' value=')([^']+)(' -->)/ig;
const _trans_vars = (lang, data) => {
    return data.replace(_trans_vars_re, (match, prfx, text, suff) => {
        const text_t = gettext(lang, text);
        return `${prfx}${text_t}${suff}`;
    });
}

const trans_tags = (r, data, flags) => {
    const req_lang = r.variables.request_lang;
    const doc_lang = r.variables.document_lang;
    let result = data;

    if (doc_lang == default_lang && req_lang != default_lang) {
        result = _trans_tags(req_lang, data);
    }

    r.sendBuffer(result, flags);
}

const trans_tags_and_vars = (r, data, flags) => {
    const req_lang = r.variables.request_lang;
    const doc_lang = r.variables.document_lang;
    let result = data;

    if (doc_lang == default_lang && req_lang != default_lang) {
        result = _trans_tags(req_lang, data);
        result = _trans_vars(req_lang, result);
    }

    r.sendBuffer(result, flags);
}

function error_page(r) {
    const req_uri = r.variables.request_uri;
    const req_lang = r.variables.request_lang;
    const status = r.variables.status;
    const error = (http_errors[status]) ? http_errors[status] : http_errors["501"];

    if (req_uri.includes('/api/')) {
        r.headersOut['Content-Type'] = 'application/json';
        r.return(error.code, JSON.stringify(error));

    } else if (!req_lang) {
        r.headersOut['Content-Type'] = 'text/plain';
        r.return(error.code, `${status}: ${error.message}`);

    } else {
        const error_message = (req_lang != default_lang) ? gettext(req_lang, error.message) : error.message;

        r.variables['document_title'] = error_message;

        r.internalRedirect('/_ssi/error.html');
    }
}

function set_lang(r) {
    const post_args = qs.parse(r.requestText);

    const req_lang = (post_args.lang) ? post_args.lang : default_lang;
    const prev_path = (post_args.prev) ? post_args.prev : default_path;
    const next_path = `/${req_lang}/` + prev_path.substring(4);

    r.headersOut['Set-Cookie'] = [
        `req_lang=${req_lang}; Path=/; Max-Age=31536000; SameSite=Lax; Secure`
    ]

    r.return(302, next_path);
}

function set_theme(r) {
    const post_args = qs.parse(r.requestText);

    const req_theme = (post_args.theme) ? post_args.theme : 'auto';
    const prev_path = (post_args.prev) ? post_args.prev : default_path;

    r.headersOut['Set-Cookie'] = [
        `req_theme=${req_theme}; Path=/; Max-Age=31536000; SameSite=Lax; Secure`
    ]

    r.return(302, prev_path);
}

export default {
    env_project_name, env_project_domain,
    env_project_title, env_project_description,
    trans_tags, trans_tags_and_vars,
    error_page, set_lang, set_theme
};
