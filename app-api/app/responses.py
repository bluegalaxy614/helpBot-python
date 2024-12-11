import typing
import orjson
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException


class ORJSONResponse(JSONResponse):
    def render(self, content: typing.Any) -> bytes:
        return orjson.dumps(
            content, option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY
        )



class HTTPValidationException(HTTPException):
    def __init__(self,
        status_code: int = 400,
        detail: str = 'Validation Errors',
        errors: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code, detail=detail, headers=headers)
        self.errors = errors

    def __str__(self) -> str:
        str_ = f"{self.status_code}: {self.detail}"
        if self.errors:
            str_ += '; '.join([f'{k}: {v}' for k, v in self.errors.items()])
        return str_

    
def http_exception_handler(request: Request, exc: HTTPException) -> ORJSONResponse:
    payload = {
        'code': exc.status_code,
        'message': exc.detail,
    }

    if hasattr(exc, 'errors') and isinstance(exc.errors, dict):
        payload['errors'] = exc.errors

    return ORJSONResponse(
        payload,
        status_code=exc.status_code,
        headers=exc.headers
    )
