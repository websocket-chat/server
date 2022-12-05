from app.api.context import HTTPRequestContext
from app.api.rest import responses
from app.api.rest.responses import Success
from app.common import logger
from app.common.errors import ServiceError
from app.models.avatars import Avatar
from app.usecases import avatars
from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from fastapi import UploadFile

router = APIRouter()


def get_status_code(error: ServiceError) -> int:
    if error is ServiceError.ACCOUNTS_NOT_FOUND:
        return status.HTTP_404_NOT_FOUND
    else:
        logger.error("Unhandled service error: ", error=error)
        return status.HTTP_500_INTERNAL_SERVER_ERROR


@router.post("/v1/accounts/{account_id}/avatar", response_model=Success[Avatar])
async def set_avatar(
    account_id: int,
    upload_file: UploadFile,
    ctx: HTTPRequestContext = Depends(),
):
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
