from app.api.context import HTTPRequestContext
from app.api.rest import responses
from app.api.rest.authentication import HTTPAuthorizationCredentials
from app.api.rest.authentication import HTTPBearer
from app.api.rest.responses import Success
from app.common import logger
from app.common.errors import ServiceError
from app.models.avatars import Avatar
from app.models.avatars import Breakpoint
from app.usecases import avatars
from app.usecases import sessions
from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from fastapi import UploadFile

http_scheme = HTTPBearer(auto_error=False)
router = APIRouter()


def get_status_code(error: ServiceError) -> int:
    if error is ServiceError.ACCOUNTS_NOT_FOUND:
        return status.HTTP_404_NOT_FOUND
    else:
        logger.error("Unhandled service error: ", error=error)
        return status.HTTP_500_INTERNAL_SERVER_ERROR


@router.post("/v1/accounts/{account_id}/avatar", response_model=Success[list[Avatar]])
async def set_avatar(
    account_id: int,
    upload_file: UploadFile,
    http_credentials: HTTPAuthorizationCredentials | None = Depends(
        http_scheme),
    ctx: HTTPRequestContext = Depends(),
):
    if http_credentials is None:
        return responses.failure(
            error=ServiceError.SESSIONS_NOT_FOUND,
            message="Failed to authenticate user",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    session = await sessions.fetch_one(ctx, session_id=http_credentials.credentials)
    if session is None:
        data = ServiceError.SESSIONS_NOT_FOUND
        return responses.failure(
            error=data,
            message="Failed to set avatar",
            status_code=get_status_code(data),
        )

    data = await avatars.create(
        ctx,
        account_id=account_id,
        upload_file=upload_file,
    )
    if isinstance(data, ServiceError):
        return responses.failure(
            error=data,
            message="Failed to set avatar",
            status_code=get_status_code(data),
        )

    resp = [Avatar.from_mapping(rec) for rec in data]
    return responses.success(resp, status_code=status.HTTP_201_CREATED)


@router.get("/v1/accounts/{account_id}/avatar", response_model=Success[list[Avatar]])
async def fetch_avatar_sizes(
    account_id: int,
    ctx: HTTPRequestContext = Depends(),
):
    data = await avatars.fetch_all(ctx, account_id=account_id)
    if isinstance(data, ServiceError):
        return responses.failure(
            error=data,
            message="Failed to fetch avatar",
            status_code=get_status_code(data),
        )

    resp = [Avatar.from_mapping(rec) for rec in data]
    return responses.success(resp, status_code=status.HTTP_200_OK)


@router.get(
    "/v1/accounts/{account_id}/avatar/{breakpoint}",
    response_model=Success[Avatar],
)
async def fetch_avatar(
    account_id: int,
    breakpoint: Breakpoint,
    ctx: HTTPRequestContext = Depends(),
):
    data = await avatars.fetch_one(
        ctx,
        account_id=account_id,
        breakpoint=breakpoint,
    )
    if isinstance(data, ServiceError):
        return responses.failure(
            error=data,
            message="Failed to fetch avatar",
            status_code=get_status_code(data),
        )

    resp = Avatar.from_mapping(data)
    return responses.success(resp, status_code=status.HTTP_200_OK)


@router.delete("/v1/accounts/{account_id}/avatar", response_model=Success[list[Avatar]])
async def delete_avatar(
    account_id: int,
    http_credentials: HTTPAuthorizationCredentials | None = Depends(
        http_scheme),
    ctx: HTTPRequestContext = Depends(),
):
    if http_credentials is None:
        return responses.failure(
            error=ServiceError.SESSIONS_NOT_FOUND,
            message="Failed to authenticate user",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    session = await sessions.fetch_one(ctx, session_id=http_credentials.credentials)
    if session is None:
        data = ServiceError.SESSIONS_NOT_FOUND
        return responses.failure(
            error=data,
            message="Failed to delete avatar",
            status_code=get_status_code(data),
        )

    data = await avatars.delete(ctx, account_id=account_id)
    if isinstance(data, ServiceError):
        return responses.failure(
            error=data,
            message="Failed to delete avatar",
            status_code=get_status_code(data),
        )

    resp = [Avatar.from_mapping(rec) for rec in data]
    return responses.success(resp, status_code=status.HTTP_200_OK)
