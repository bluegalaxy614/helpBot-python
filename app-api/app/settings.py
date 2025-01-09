from starlette.config import Config
from starlette.datastructures import Secret

config = Config()

DEBUG = config('DEBUG', cast=bool, default=True)
PROJECT_NAME = config('PROJECT_NAME', default='akira')
PROJECT_DOMAIN = config('PROJECT_DOMAIN', default='localhost')
PROJECT_TITLE = config('PROJECT_TITLE', default=PROJECT_NAME)
PROJECT_DESCRIPTION = config('PROJECT_DESCRIPTION', default='')

SECRET_KEY = config(
    'SECRET_KEY', cast=Secret, default='SeCrEt_KeY_PoWeR'
)

API_PREFIX = config(
    'API_PREFIX', default='/api/v1'
)
API_ENDPOINT = config(
    'API_ENDPOINT', default=f'https://{PROJECT_DOMAIN}{API_PREFIX}'
)
OPENAPI_SCHEMA_URL = f'{API_PREFIX}/openapi.json'

ADMIN_AUTH_API_KEY = config(
    'ADMIN_AUTH_API_KEY', default='1111-2222-3333-4444'
)

DATA_DIR = config(
    'DATA_DIR', default='../volumes/data'
)
SCHEMAS_DIR = config(
    'SCHEMAS_DIR', default='../volumes/schemas'
)

OPENAI_API_KEY = config(
    'OPENAI_API_KEY', default='sk-proj-OTVCGTlvFJZ7GwKbeCVzT3BlbkFJ4SwowCGeKYG1DrlebdhJ'
)
