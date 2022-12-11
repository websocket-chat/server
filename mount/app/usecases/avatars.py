import io
import os
import typing

from app.common import settings
from app.common.context import Context
from app.common.errors import ServiceError
from app.models.avatars import Breakpoint
from app.repositories.avatars import AvatarsRepo
from fastapi import UploadFile
from PIL import Image

MAX_AVATAR_SIZE = 1024 * 1024 * 20  # 20 MB

BREAKPOINTS = {
    Breakpoint.ORIGINAL: (0, 0),
    Breakpoint.THUMBNAIL: (256, 256),
    Breakpoint.SM: (640, 640),
    Breakpoint.MD: (768, 768),
    Breakpoint.LG: (1024, 1024),
    Breakpoint.XL: (1280, 1280),
    Breakpoint.XXL: (1536, 1536),
}


def _get_s3_public_url(bucket_name: str, file_path: str) -> str:
    return f"https://{bucket_name}.s3.amazonaws.com/{file_path}"


async def create(
    ctx: Context,
    account_id: int,
    upload_file: UploadFile,
) -> list[dict[str, typing.Any]] | ServiceError:
    repo = AvatarsRepo(ctx)

    if upload_file.content_type == "image/jpeg":
        extension = "jpeg"
    elif upload_file.content_type == "image/png":
        extension = "png"
    elif upload_file.content_type == "image/webp":
        extension = "webp"
    else:
        return ServiceError.AVATARS_CONTENT_TYPE_INVALID

    await upload_file.seek(os.SEEK_SET)
    file_data = await upload_file.read(size=MAX_AVATAR_SIZE + 1)

    if len(file_data) > MAX_AVATAR_SIZE:
        return ServiceError.AVATARS_SIZE_TOO_LARGE

    with io.BytesIO(file_data) as file_obj:
        original_image = Image.open(file_obj)

        avatars = []
        for breakpoint, (width, height) in BREAKPOINTS.items():
            if breakpoint == Breakpoint.ORIGINAL:
                resized_image = original_image
                width = original_image.width
                height = original_image.height
            else:
                resized_image = original_image.resize((width, height))

            file_name = f"{breakpoint}.{extension}"
            public_url = _get_s3_public_url(
                bucket_name=settings.AWS_S3_BUCKET_NAME,
                file_path=file_name,
            )

            resized_file_data = resized_image.tobytes()
            avatar = await repo.create(
                account_id=account_id,
                breakpoint=breakpoint,
                content_type=upload_file.content_type,
                width=width,
                height=height,
                filesize=len(resized_file_data),
                public_url=public_url,
                file_name=file_name,
                file_data=resized_file_data,
            )
            if avatar is None:
                return ServiceError.AVATARS_CREATION_FAILED

            avatars.append(avatar)

    return avatars


async def fetch_all(
    ctx: Context,
    account_id: int,
) -> list[dict[str, typing.Any]] | ServiceError:
    repo = AvatarsRepo(ctx)
    avatars = await repo.fetch_all(account_id=account_id)
    if avatars is None:
        return ServiceError.AVATARS_NOT_FOUND

    return avatars


async def fetch_one(
    ctx: Context,
    account_id: int,
    breakpoint: Breakpoint,
) -> dict[str, typing.Any] | ServiceError:
    repo = AvatarsRepo(ctx)
    avatar = await repo.fetch_one(account_id=account_id, breakpoint=breakpoint)
    if avatar is None:
        return ServiceError.AVATARS_NOT_FOUND

    return avatar


async def delete(
    ctx: Context,
    account_id: int,
) -> list[dict[str, typing.Any]] | ServiceError:
    repo = AvatarsRepo(ctx)
    deleted = await repo.delete(account_id=account_id)
    if not deleted:
        return ServiceError.AVATARS_DELETION_FAILED

    return deleted
