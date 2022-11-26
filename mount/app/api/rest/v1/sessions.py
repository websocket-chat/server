from uuid import UUID

from app.api.authentication import HTTPAuthorizationCredentials
from app.api.authentication import HTTPBearer
from app.api.context import RequestContext
from app.api.rest import responses
from app.api.rest.responses import Success
from app.common import logger
from app.common.errors import ServiceError
from app.models.sessions import LoginForm
from app.models.sessions import Session
from app.usecases import sessions
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Header
from fastapi import status

http_scheme = HTTPBearer()
router = APIRouter()


@router.post("/v1/sessions", response_model=Success[Session])
async def login(
    args: LoginForm,
    user_agent: str = Header(...),
    ctx: RequestContext = Depends(),
):
    data = await sessions.login(
        ctx,
        username=args.username,
        password=args.password,
        user_agent=user_agent,
    )
    if isinstance(data, ServiceError):
        if data is ServiceError.CREDENTIALS_INCORRECT:
            status_code = status.HTTP_401_UNAUTHORIZED
        else:
            logger.error("Unhandled service error: ", error=data)
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        return responses.failure(
            error=data,
            message="Failed to create session",
            status_code=status_code,
        )

    resp = Session.from_mapping(data)
    return responses.success(resp, status_code=status.HTTP_201_CREATED)


@router.delete("/v1/sessions", response_model=Success[Session])
async def logout(
    http_credentials: HTTPAuthorizationCredentials = Depends(http_scheme),
    ctx: RequestContext = Depends(),
):
    data = await sessions.logout(ctx, session_id=http_credentials.credentials)
    if isinstance(data, ServiceError):
        if data is ServiceError.SESSIONS_NOT_FOUND:
            status_code = status.HTTP_404_NOT_FOUND
        else:
            logger.error("Unhandled service error: ", error=data)
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        return responses.failure(data, "Failed to log out of session", status_code)

    resp = Session.from_mapping(data)
    return responses.success(resp, status_code=status.HTTP_201_CREATED)
