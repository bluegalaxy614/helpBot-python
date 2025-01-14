import os

from itsdangerous import URLSafeTimedSerializer
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings

config = Config()

############################################
# APP CONFIGS
############################################

SECRET_KEY = "fskljdsdjfhsdkjfhs9805423"

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

#API_ENDPOINT = config(
#     'API_ENDPOINT', default=API_INTERNAL
#)

#OPENAPI_SCHEMA_URL = f'{API_ENDPOINT}/openapi.json'

STATIC_DIR = config(
    'STATIC_DIR', default='../volumes/html/_'
)

STATIC_URL = config(
    'STATIC_URL', default='/_'
)

TEMPLATES_DIR = config(
    'TEMPLATES_DIR', default='../volumes/templates'
)

###################################################
# OAUTH
###################################################

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

GOOGLE_AUTH_SCOPE = os.getenv("GOOGLE_AUTH_SCOPE", "external")

GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "")

###################################################
# Database
###################################################

MONGO_URI = "mongodb://akira-db-user:fkujsdhfkjsdfhdksjfsd9405@mongo:27017"

MONGO_DATABASE_NAME = "akira_db"

USER_COLLECTION_NAME = "users"

##################################################
# Email
##################################################

RESET_PASSWORD_SECRET = URLSafeTimedSerializer(SECRET_KEY)

APP_EMAIL_ADDRESS = os.getenv("APP_EMAIL_ADDRESS")

APP_EMAIL_PASSWORD = os.getenv("APP_EMAIL_PASSWORD")


