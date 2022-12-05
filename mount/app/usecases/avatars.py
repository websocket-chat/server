import io
import os
import typing

from app.common.context import Context
from app.common.errors import ServiceError
from app.models.avatars import Breakpoint
from app.repositories.avatars import AvatarsRepo
from fastapi import UploadFile
from PIL import Image

MAX_AVATAR_SIZE = 1024 * 1024 * 20  # 20 MB
ALLOWED_AVATAR_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

BREAKPOINTS = {
    Breakpoint.ORIGINAL: (0, 0),
    Breakpoint.THUMBNAIL: (256, 256),
    Breakpoint.SM: (640, 640),
    Breakpoint.MD: (768, 768),
    Breakpoint.LG: (1024, 1024),
    Breakpoint.XL: (1280, 1280),
    Breakpoint.XXL: (1536, 1536),
}


async def create(
    ctx: Context,
    account_id: int,
    upload_file: UploadFile,
) -> list[dict[str, typing.Any]] | ServiceError:
    repo = AvatarsRepo(ctx)

    if upload_file.content_type not in ALLOWED_AVATAR_CONTENT_TYPES:
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

            resized_file_data = resized_image.tobytes()
            avatar = await repo.create(
                account_id=account_id,
                width=width,
                height=height,
                filesize=len(resized_file_data),
                breakpoint=breakpoint,
                file_data=resized_file_data,
            )
            if avatar is None:
                return ServiceError.AVATARS_CREATE_FAILED

            avatars.append(avatar)

    return avatars
