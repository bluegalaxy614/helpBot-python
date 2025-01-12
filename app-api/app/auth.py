from starlette.authentication import (
    BaseUser, AuthCredentials, AuthenticationBackend, AuthenticationError
)
from app import settings

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
        api_key = conn.headers.get('X-API-Key')

        if api_key == settings.ADMIN_AUTH_API_KEY:
            return AuthCredentials([SCOPE_ADMIN]), AuthUser('admin@email.com')

        # auth = conn.headers["Authorization"]
        # try:
        #     scheme, credentials = auth.split()
        #     if scheme.lower() != 'basic':
        #         return
        #     decoded = base64.b64decode(credentials).decode("ascii")
        # except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
        #     raise AuthenticationError('Invalid basic auth credentials')

        # user_email, _, password = decoded.partition(":")
        # # TODO: You'd want to verify the username and password here.
        # return AuthCredentials([SCOPE_MEMBER]), AuthUser('user@email')


