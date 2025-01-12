import httpx
import contextlib

from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware

from app import settings
from app.auth import AuthBackend, SCOPE_ADMIN
from app.handlers import JsonSchemaHandlers
from app.schemas import JsonSchemaDescriber, openapi_schema_handler
from app.backends.base import BaseBackend
from app.backends.openai import AssistantsBackend
from app.responses import http_exception_handler
from app.helpbot import helpbot_ws_handler


items = JsonSchemaHandlers(
    schema=JsonSchemaDescriber.load(f'{settings.SCHEMAS_DIR}/item.json'),
    backend=BaseBackend(f'{settings.DATA_DIR}/items.json'),
    scopes={
        'list': [],
        'read': [],
        'create': [],
        'update': [],
        'delete': [],
    }
)

assistants = JsonSchemaHandlers(
    schema=JsonSchemaDescriber.load(f'{settings.SCHEMAS_DIR}/assistant.json'),
    backend=AssistantsBackend(
        f'{settings.DATA_DIR}/assistants.json',
        api_key=settings.OPENAI_API_KEY
    ),
    scopes={
        'list': [SCOPE_ADMIN],
        'read': [SCOPE_ADMIN],
        'create': [SCOPE_ADMIN],
        'update': [SCOPE_ADMIN],
        'delete': [SCOPE_ADMIN]
    }
)


@contextlib.asynccontextmanager
async def lifespan(app):
    async with httpx.AsyncClient(verify=False) as http_client:
        app.state.http_client = http_client
        yield

app = Starlette(
    debug=settings.DEBUG,
    routes=[
        Route(
            settings.OPENAPI_SCHEMA_URL,
            openapi_schema_handler,
            name='openapi_schema_url',
            include_in_schema=False
        ),
        Mount(settings.API_PREFIX, routes=[
            *items.get_routes(),
            *assistants.get_routes(),
        ])
    ],
    exception_handlers={
        HTTPException: http_exception_handler
    },
    lifespan=lifespan,
    middleware=[
        Middleware(AuthenticationMiddleware, backend=AuthBackend())
    ]
)


# extra routes
app.add_websocket_route('/ws/helpbot', helpbot_ws_handler)

