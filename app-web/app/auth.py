from starlette.authentication import (
    BaseUser, AuthCredentials, AuthenticationBackend
)

SCOPE_ADMIN = 'admin'
SCOPE_OWNER = 'owner'
SCOPE_MEMBER = 'member'


class AuthUser(BaseUser):

    def __init__(self, email: str) -> None:
        self.email = email

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.email


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
