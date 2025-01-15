import bcrypt
from starlette.requests import Request
from starlette.responses import JSONResponse


def error_json_resp(error, code=400):
    data ={"error" : error}
    return JSONResponse(data, status_code=code)
    

def hash_password(plain_password: str) -> bytes:
    """Hash the plain text password."""
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())


def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    """Verify a password against a given hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)


def get_create_csrf_token(request: Request) -> str:
    """Generate or retrieve the CSRF token for the session."""
    if "csrf_token" not in request.session:
        request.session["csrf_token"] = request.scope["app"].state.csrf_middleware.serializer.dumps("")
    return request.session["csrf_token"]

