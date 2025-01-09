from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings

config = Config()

DEBUG = config('DEBUG', cast=bool, default=True)
PROJECT_NAME = config('PROJECT_NAME', default='akira')
PROJECT_DOMAIN = config('PROJECT_DOMAIN', default='localhost')
PROJECT_TITLE = config('PROJECT_TITLE', default=PROJECT_NAME)
PROJECT_DESCRIPTION = config('PROJECT_DESCRIPTION', default='')

LANGUAGES = config(
    'LANGUAGES', cast=CommaSeparatedStrings, default='en,ja,uk'
)

INTERNAL_API_HOST = config(
    'INTERNAL_API_HOST', default='http://localhost:8000'
)
INTERNAL_API_SCHEMA = config(
    'INTERNAL_API_SCHEMA', default=f'{INTERNAL_API_HOST}/api/v1/openapi.json'
)
INTERNAL_API_ACCESS_KEY = config(
    'INTERNAL_API_ACCESS_KEY', default='1111-2222-3333-4444'
)
# API_ENDPOINT = config(
#     'API_ENDPOINT', default=API_INTERNAL
# )
# OPENAPI_SCHEMA_URL = f'{API_ENDPOINT}/openapi.json'

STATIC_DIR = config(
    'STATIC_DIR', default='../volumes/html/_'
)
STATIC_URL = config(
    'STATIC_URL', default='/_'
)
TEMPLATES_DIR = config(
    'TEMPLATES_DIR', default='../volumes/templates'
)
