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
from app.api import OpenApiClient
from app.utils import hash_password, verify_password


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
# Basic authentication Routes
################################################


async def register_user(request: Request):
    
    data = await request.form()
    email = data.get("email")
    password = data.get("password")
    username = data.get("username")
    error_resp = RedirectResponse(url=f'/{lang}/user/sign-up.html', status_code=302)

    if not email or not password or not username:
        request.session['errors'] = ['Missing form data!']
        return error_resp
    
    if len(password) < 8:
        request.session['errors'] = ['Password is too short (min 8)']
        return error_resp

    existing_user = await app.state.db[settings.USER_COLLECTION_NAME].find_one({"email": email})
    if existing_user:
        request.session['errors'] = ['Username or email is not available, try another!']
        return error_resp

    existing_user = await app.state.db[settings.USER_COLLECTION_NAME].find_one({"username": username})
    if existing_user:
        request.session['errors'] = ['Username or email not available, try another one']
        return error_resp

    hashed_password = hash_password(password)

    try:
        await app.state.db[settings.USER_COLLECTION_NAME].insert_one(
            {
                "username": username,
                "email" : email,
                "password": hashed_password.decode("utf-8")
            }
        )
    except Exception as e:
        if settings.DEBUG:
            request.session['errors'] = [str(e)]
        else:
            request.session['errors'] = ['Unable to create user -- contact admin with code 002']
        return error_resp

    request.session["messages"] = ["User created! Log In!"]
    resp = RedirectResponse(url=f'/{lang}/user/sign-in.html', status_code=302)
    return resp


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


async def reset_password_request(request: Request):
    data = await request.json()
    email = data.get("email")
    user = await request.app.state.db[settings.USER_COLLECTION_NAME].find_one({"email": email})
    if not user:
        return JSONResponse({"error": "Incorrect email"}, status_code=400)

    token = settings.RESET_PASSWORD_SECRET.dumps(email, salt="reset-password")
    reset_link = f"https://{settings.PROJECT_DOMAIN}/en/reset-password/{token}"

    msg = EmailMessage()
    msg["Subject"] = "Password Reset Request"
    msg["From"] = settings.APP_EMAIL_ADDRESS
    msg["To"] = email
    msg.set_content(f"Click the link to reset your password: {reset_link}")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(settings.APP_EMAIL_ADDRESS, settings.APP_EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        return JSONResponse({"error": "Failed to send email"}, status_code=400)

    return JSONResponse({"message": "If the email is registered, a reset link will be sent."})


async def reset_password_page(request: Request):
    token = request.path_params["token"]

    try:
        email = RESET_PASSWORD_SECRET.loads(token, salt="reset-password", max_age=3600)
    except (SignatureExpired, BadSignature):
        return RedirectResponse("/en/user/sign-in.html", status_code=302)

    errors = request.session.pop("errors", [])
    return templates.TemplateResponse("reset.html", {"request": request, "token": token, "errors": errors})



async def reset_password(request: Request):
    token = request.path_params["token"]
    form = await request.form()

    try:
        email = RESET_PASSWORD_SECRET.loads(token, salt="reset-password", max_age=3600)
    except (SignatureExpired, BadSignature):
        return RedirectResponse(f"/reset-password/{token}", status_code=302)

    new_password = form.get("password")
    confirm_password = form.get("confirm_password")

    if not new_password or not confirm_password or new_password != confirm_password:
        request.session["errors"] = ["Passwords do not match."]
        return RedirectResponse(f"/reset-password/{token}", status_code=302)

    hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    await app.state.db[settings.USER_COLLECTION_NAME].update_one({"email": email}, {"$set": {"password": hashed_password}})

    request.session["messages"] = ["Password reset successful. Please log in."]
    return RedirectResponse("/login", status_code=302)

routes = []
for lang in settings.LANGUAGES:
    routes.append(Route(f"/{lang}/sign-in", endpoint=sign_in, methods=['post']))
    routes.append(Route(f'/{lang}/register', endpoint=register_user, methods=['post']))	
    routes.append(Route(f'/{lang}/sign-out', endpoint=sign_out, methods=["post"]))
    routes.append(Route(f'/{lang}/google-oauth', endpoint=handle_google_oauth, methods=["get"]))
    #routes.append(Route(f'/{lang}/google-callback', endpoint=google_callback, methods=['get']))
    routes.append(Route("/{lang}/reset-password-request/", reset_password_request, methods=["POST"]))
    routes.append(Route("/{lang}/reset-password/{token}", reset_password_page, methods=["GET"]))
    routes.append(Route("/{lang}/reset-password/{token}", reset_password, methods=["POST"]))


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
