import logging
import asyncio
import contextlib
import smtplib
from email.message import EmailMessage

import bcrypt
from itsdangerous import BadSignature, SignatureExpired
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.routing import Route
from starlette.responses import RedirectResponse, JSONResponse
from starlette_csrf import CSRFMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from app import settings
from app.templates import Templates
from app.auth import AuthBackend, MongoAuthBackend
from app.oauths.google_oauth import handle_google_oauth
from app.email_funcs import send_reset_password_email, send_verify_email_email
from app.api import OpenApiClient
from app.redis_funcs import (
    delete_redis_key,
	set_key as set_redis_key, 
	get_key as get_redis_key,
    store_dict_in_redis,
    get_dict_from_redis,
)
from app.utils import hash_password, verify_password, error_json_resp
from app.validators import validate_password, validate_user_email


logger = logging.getLogger(__name__)


templates = Templates(
    templates_dir=settings.TEMPLATES_DIR,
    fallback_lang=settings.LANGUAGES[0],
    debug=settings.DEBUG,
)



@contextlib.asynccontextmanager
async def lifespan(app):
    await asyncio.sleep(5)
    app.state.templates = templates
    app.state.internal_api = await OpenApiClient(
        schema_url=settings.INTERNAL_API_SCHEMA,
        host=settings.INTERNAL_API_HOST,
        headers={
            'X-API-Key': settings.INTERNAL_API_ACCESS_KEY
        }
    )

    #app.state.csrf_middleware = csrf_middleware
    
    ################################################################
    # Create the default user (admin)
    ################################################################

    app.state.db_client = AsyncIOMotorClient(settings.MONGO_URI)
    app.state.db = app.state.db_client[settings.MONGO_DATABASE_NAME]

    await app.state.db[settings.USER_COLLECTION_NAME].create_index("email", unique=True)
    await app.state.db[settings.USER_COLLECTION_NAME].create_index("username", unique=True)
	
    admin_email = "akira@admin.com"
    admin_username = "admin"
    admin_password = "AkiraAdmin135" 

    hashed_password = hash_password(admin_password).decode("utf-8")

    admin_user = await app.state.db[settings.USER_COLLECTION_NAME].find_one({"email": admin_email})
    if not admin_user:
        await app.state.db[settings.USER_COLLECTION_NAME].insert_one({
            "email": admin_email,
            "username": admin_username,
            "password": hashed_password,
            "role": "admin"
        })
        logger.info("Admin user created with email:", admin_email)
    else:
        logger.info("Admin user already exists.")

    yield

    app.state.db_client.close()
    app.state.internal_api.aclose()



################################################
# Reegistration routes
################################################


async def register_user_step_1_send_verification_email(request: Request):
    
    data = await request.json()
    email = data.get("email")
    password = data.get("password")
    username = data.get("username")

    if not email or not password or not username:
        return error_json_resp("Missing form data", 400)
    
    password_valid, message = validate_password(password)
    if not password_valid:
        return error_json_resp(message, 400)
    
    email_valid, message = validate_user_email(email)
    if not email_valid:
        return error_json_resp(message, 400)

    existing_user = await app.state.db[settings.USER_COLLECTION_NAME].find_one({"email": email})
    if existing_user:
        return error_json_resp("Username or email not available, try another!", 400)

    existing_user = await app.state.db[settings.USER_COLLECTION_NAME].find_one({"username": username})
    if existing_user:
        return error_json_resp("Username or email not available, try another one!", 400)
	
    ##########################################################
    # Generate the token and store the user in temp storage
    # Until verification step finishes.
    ##########################################################

    token = settings.TOKEN_SECRET_SERIALIZER.dumps(email, salt="email-verification")
    temp_user = {
        "username" : username,
        "email" : email,
        "password" : password
    }
    
    stored_key, message = store_dict_in_redis(token, temp_user)
    if not stored_key:
        return error_json_resp(message, 400)
    
    ##########################################################
    # Generate the link with the token
    ##########################################################

    link = f"https://{settings.PROJECT_DOMAIN}/{lang}/register-step-2-page?token={token}"
    send_email_status, message = send_verify_email_email(settings.APP_EMAIL_ADDRESS, email, link)
    if not send_email_status:
        return error_json_resp(message, 400)

    ##########################################################
    # Final step
    ##########################################################
    
    data = {"message" : "We sent an email with your verification link to the email you registered with!"}
    return JSONResponse(data, status_code=200)


async def register_user_step_2_verify_email_page(request):
    """Verify email token and register the user."""
    token = request.query_params.get("token")
    lang = "en"
    resp = RedirectResponse(url=f"/{lang}/user/registration-verify-email.html", status_code=302)

    try:
        email = settings.TOKEN_SECRET_SERIALIZER.loads(token, salt="email-verification", max_age=3600)
    except SignatureExpired:
        request.session['errors'] = ['Link expired.']
        return resp
    except BadSignature:
        request.session['errors'] = ['Invalid link.']
        return resp

    user = get_dict_from_redis(token)
    if not user:
        request.session['errors'] = ['Token invalid or expired!']
        return resp

    try:
        username = user.get("username")
        email = user.get("email")
        password = hash_password(user.get("password"))
        await app.state.db[settings.USER_COLLECTION_NAME].insert_one(
            {
                "username": username,
                "email" : email,
                "password": password.decode("utf-8")
            }
        )
    except Exception as e:
        #request.session['errors'] = [str(e)]
        request.session['errors'] = ['Unable to create user -- contact admin with code 002']
        return resp

    delete_redis_key(token)
    request.session["messages"] = ["Email verified! Log In!"]
    resp = RedirectResponse(url=f'/{lang}/user/registration-verify-email.html', status_code=302)
    return resp



async def reset_password_step_1_send_reset_password_email(request: Request):
    status_code = 200
    data = await request.json()
    email = data.get("email")
    lang = data.get("lang")

    user = await request.app.state.db[settings.USER_COLLECTION_NAME].find_one({"email": email})
    if not user:
        data = {"error" : "Invalid email."}
        return JSONResponse(data, status_code=400)

    token = settings.TOKEN_SECRET_SERIALIZER.dumps(email, salt="reset-password")
    reset_link = f"https://{settings.PROJECT_DOMAIN}/{lang}/user/reset-password-step-2.html?token={token}"
    
    status, message = send_reset_password_email(settings.APP_EMAIL_ADDRESS, email, reset_link)
    if not status:
        status_code = 400
        data = {"error" : message}
    else:
        data = {"message" : "Success! Check your email for a reset link!"}

    return JSONResponse(data, status_code=status_code)


async def reset_password_step_2_set_new_password(request: Request):
    form = await request.form()
    token = form.get("token")
    new_password = form.get("password")
    confirm_password = form.get("password2")
    lang = form.get("lang")
    this_route_url = f"/{lang}/user/reset-password-step-2.html?token={token}"
    reset_page = f"{lang}/user/reset-password.html"

    try:
        email = settings.TOKEN_SECRET_SERIALIZER.loads(token, salt="reset-password", max_age=3600)
    except (SignatureExpired, BadSignature):
        request.session['errors'] = ["Link expired or invalid"] 
        return RedirectResponse(url=reset_page, status_code=302)

    if not new_password or not confirm_password or new_password != confirm_password:
        request.session["errors"] = ["Passwords do not match."]
        # redirect to same page but with error message.
        return RedirectResponse(this_route_url, status_code=302)
    
    hashed_password = hash_password(new_password).decode("utf-8")
    await request.app.state.db[settings.USER_COLLECTION_NAME].update_one({"email": email}, {"$set": {"password": hashed_password}})

    request.session["messages"] = ["Password reset successful. Please log in."]
    return RedirectResponse(url=f"/{lang}/user/sign-in.html", status_code=302)


##############################################################
# Sign In and Sign Out Routes
##############################################################


async def sign_in(request: Request):
    errors = request.session.pop("errors", [])  # Retrieve and clear session errors
    data = await request.form()
    email = data.get("email")
    password = data.get("password")
    lang = data.get("lang")

    if not email or not password:
        request.session['errors'] = ['Missing form data!']
        return RedirectResponse(f'/{lang}/user/sign-in.html', status_code=302)

    user = await app.state.db[settings.USER_COLLECTION_NAME].find_one({"email": email})
    if not user or not verify_password(password, user["password"].encode("utf-8")):
        request.session['errors'] = ['Invalid credentials']
        return RedirectResponse(
            url=f'/{lang}/user/sign-in.html',
            status_code=302,
        )

    request.session['user_email'] = email
    return RedirectResponse(url=f"/{lang}/user/profile.html", status_code=302) 


async def sign_out(request: Request):
    request.session.pop('user_email')
    form = await request.form()
    lang = form.get("lang")
    return RedirectResponse(url=f'/{lang}/user/sign-in.html', status_code=302)



##################################################
# Starlette Routes
##################################################


routes = []
for lang in settings.LANGUAGES:
    ##############################################
    # Sing in routes
    ##############################################
    
    routes.append(Route(f"/{lang}/sign-in", endpoint=sign_in, methods=['post']))
    routes.append(Route(f'/{lang}/sign-out', endpoint=sign_out, methods=["post"]))
    
    ##############################################
    # Register Routes
    ##############################################

    routes.append(Route(f'/{lang}/register-step-1', register_user_step_1_send_verification_email, methods=['post']))
    routes.append(Route(f'/{lang}/register-step-2-page', endpoint=register_user_step_2_verify_email_page, methods=['get']))	
    
    ##############################################
    # Reset Password Routes
    ##############################################
    
    routes.append(Route("/{lang}/reset-password-step-1", reset_password_step_1_send_reset_password_email, methods=["POST"]))
    routes.append(Route("/{lang}/reset-password/", reset_password_step_2_set_new_password, methods=["POST"]))


    ##############################################
    # Oauth
    ##############################################

    routes.append(Route(f'/{lang}/google-oauth', endpoint=handle_google_oauth, methods=["get"]))
    #routes.append(Route(f'/{lang}/google-callback', endpoint=google_callback, methods=['get']))
   
app = Starlette(
    debug=settings.DEBUG,
    lifespan=lifespan,
    routes=routes,
)

app.add_middleware(AuthenticationMiddleware, backend=MongoAuthBackend())
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
#app.add_middleware(
#    CSRFMiddleware, 
#    secret=settings.SECRET_KEY, 
#    cookie_secure=True,
#    cookie_name="csrf_token"
#)


for lang in settings.LANGUAGES:
    app.add_route(f'/{lang}/{{path:path}}', templates.handler, methods=['get', 'post'])


if settings.DEBUG:
    app.mount(
        settings.STATIC_URL,
        app=StaticFiles(directory=settings.STATIC_DIR),
        name='static'
    )
