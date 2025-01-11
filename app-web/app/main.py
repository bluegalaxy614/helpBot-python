import asyncio
import contextlib

import bcrypt
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient

from app import settings
# from app.app import TemplatesApp
from app.templates import Templates
from app.auth import AuthBackend
from app.api import OpenApiClient
from app.oauth import handle_google_oauth, handle_google_callback


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

    yield

    await app.state.internal_api.aclose()


app = Starlette(
    debug=settings.DEBUG,
    lifespan=lifespan,
    middleware=[
        Middleware(AuthenticationMiddleware, backend=AuthBackend())
    ])


@app.on_event("startup")
async def startup_event():
    app.state.db_client = AsyncIOMotorClient(settings.MONGO_URI)
    app.state.db = app.state.db_client
    await app.state.db[COLLECTION_NAME].create_index("username", unique=True)


@app.on_event("shutdown")
async def shutdown_event():
    app.state.db_client.close()


@app.route("/register-user", methods=["POST"])
async def register_user(request: Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return JSONResponse({"error": "Missing username or password"}, status_code=400)

    existing_user = await db[COLLECTION_NAME].find_one({"username": username})
    if existing_user:
        return JSONResponse({"error": "User already exists"}, status_code=409)

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    try:
        await db[COLLECTION_NAME].insert_one({"username": username, "password": hashed_password.decode("utf-8")})
        return JSONResponse({"message": "User registered successfully"}, status_code=201)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


for lang in settings.LANGUAGES:
    app.add_route(f'/{lang}/{{path:path}}', templates.handler, methods=['get', 'post'])



if settings.DEBUG:
    app.mount(
        settings.STATIC_URL,
        app=StaticFiles(directory=settings.STATIC_DIR),
        name='static'
    )
