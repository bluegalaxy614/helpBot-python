import asyncio
import contextlib
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from app import settings
# from app.app import TemplatesApp
from app.templates import Templates
from app.auth import AuthBackend
from app.api import OpenApiClient


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


for lang in settings.LANGUAGES:
    app.add_route(f'/{lang}/{{path:path}}', templates.handler, methods=['get', 'post'])


if settings.DEBUG:
    app.mount(
        settings.STATIC_URL,
        app=StaticFiles(directory=settings.STATIC_DIR),
        name='static'
    )
