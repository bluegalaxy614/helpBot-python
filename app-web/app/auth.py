from starlette.authentication import (
    BaseUser, AuthCredentials, AuthenticationBackend
)
from app import settings


SCOPE_ADMIN = 'admin'
SCOPE_OWNER = 'owner'
SCOPE_MEMBER = 'member'


class AnonUser(BaseUser):

    @property
    def is_authenticated(self) -> bool:
        return False

    @property
    def display_name(self) -> str:
        return ""


class AuthBackend(AuthenticationBackend):

    async def authenticate(self, conn):
        user_email = conn.headers.get('X-User-Email')

        if user_email:
            return AuthCredentials([SCOPE_MEMBER]), AuthUser(user_email)


class AuthUser(BaseUser):

    def __init__(self, email: str, username: str) -> None:
        self.email = email
        self.username = username

    @property
    def is_authenticated(self) -> bool:
        return True


    @property
    def display_name(self) -> str:
        return self.email


    @classmethod
    async def cook_user(cls, request, **user):
        try:
            result = await request.app.state.db[settings.USER_COLLECTION_NAME].insert_one(new_user)
        except Exception as error:
            errors = ["Unable to register user using google oauth!"]
            return False, errors
        return True, result


class MongoAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        email = request.session.get("user_email")
        if not email:
            return None

        user_data = await request.app.state.db[settings.USER_COLLECTION_NAME].find_one({"email": email})
        if not user_data:
            return None

        user = AuthUser(username=user_data["username"], email=user_data["email"])
        return AuthCredentials(["authenticated"]), user

