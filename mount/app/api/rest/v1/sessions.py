from datetime import datetime
from uuid import UUID

from app.api.authentication import HTTPAuthorizationCredentials
from app.api.authentication import HTTPBearer
from app.api.context import HTTPRequestContext
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


def get_status_code(error: ServiceError) -> int:
    if error is ServiceError.SESSIONS_NOT_FOUND:
        return status.HTTP_400_BAD_REQUEST
    elif error is ServiceError.CREDENTIALS_INCORRECT:
        return status.HTTP_401_UNAUTHORIZED

    logger.error("Unhandled service error: ", error=error)
    return status.HTTP_500_INTERNAL_SERVER_ERROR


@router.post("/v1/sessions", response_model=Success[Session])
async def login(
    args: LoginForm,
    user_agent: str = Header(...),
    ctx: HTTPRequestContext = Depends(),
):
    data = await sessions.login(
        ctx,
        username=args.username,
        password=args.password,
        user_agent=user_agent,
    )
    if isinstance(data, ServiceError):
        return responses.failure(
            error=data,
            message="Failed to create session",
            status_code=get_status_code(data),
        )

    resp = Session.from_mapping(data)
    return responses.success(
        resp,
        status_code=status.HTTP_201_CREATED,
        cookies=[
            {
                "key": "session_id",
                "value": data["session_id"],
                "httponly": True,
                "secure": True,
                "samesite": "strict",
                "expires": int((data["expires_at"] - datetime.now()).total_seconds()),
            }
        ],
    )


@router.get("/v1/sessions", response_model=Success[list[Session]])
async def fetch_many(
    account_id: int | None = None,
    user_agent: str | None = None,
    page: int = 1,
    page_size: int = 10,
    ctx: HTTPRequestContext = Depends(),
):
    data = await sessions.fetch_many(
        ctx,
        account_id=account_id,
        user_agent=user_agent,
        page=page,
        page_size=page_size,
    )
    if isinstance(data, ServiceError):
        return responses.failure(
            error=data,
            message="Failed to fetch sessions",
            status_code=get_status_code(data),
        )

    resp = [Session.from_mapping(rec) for rec in data]
    return responses.success(resp)


@router.get("/v1/sessions/{session_id}", response_model=Success[Session])
async def fetch_one(
    session_id: UUID,
    ctx: HTTPRequestContext = Depends(),
):
    data = await sessions.fetch_one(ctx, session_id=session_id)
    if isinstance(data, ServiceError):
        return responses.failure(
            error=data,
            message="Failed to fetch session",
            status_code=get_status_code(data),
        )

    resp = Session.from_mapping(data)
    return responses.success(resp)


@router.delete("/v1/sessions", response_model=Success[Session])
async def logout(
    http_credentials: HTTPAuthorizationCredentials = Depends(http_scheme),
    ctx: HTTPRequestContext = Depends(),
):
    data = await sessions.logout(ctx, session_id=http_credentials.credentials)
    if isinstance(data, ServiceError):
        return responses.failure(
            error=data,
            message="Failed to log out of session",
            status_code=get_status_code(data),
        )

    resp = Session.from_mapping(data)
    return responses.success(resp, status_code=status.HTTP_201_CREATED)
