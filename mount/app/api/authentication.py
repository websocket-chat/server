from uuid import UUID

from fastapi import HTTPException
from fastapi import Request
from fastapi.openapi.models import HTTPBearer as HTTPBearerModel
from fastapi.security.http import HTTPBase
from fastapi.security.utils import get_authorization_scheme_param
from pydantic import BaseModel
from starlette.status import HTTP_403_FORBIDDEN


# direct copy of fastapi.security.http.HTTPBearer & HTTPAuthorizationCredentials,
# just edited to use UUID instead of str for credentials (session_id) so that it
# nicely handles 422 for me lol

class HTTPAuthorizationCredentials(BaseModel):
    scheme: str
    credentials: UUID


class HTTPBearer(HTTPBase):
    def __init__(
        self,
        *,
        bearerFormat: str | None = None,
        scheme_name: str | None = None,
        description: str | None = None,
        auto_error: bool = True,
    ):
        self.model = HTTPBearerModel(
            bearerFormat=bearerFormat,
            description=description,
        )  # type: ignore
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        authorization = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None
        if scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Invalid authentication credentials",
                )
            else:
                return None
        try:
            uuid_credentials = UUID(credentials)
        except ValueError:
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Invalid authentication credentials",
                )
            else:
                return None
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=uuid_credentials)
