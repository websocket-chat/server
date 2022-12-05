import io
import typing

from app.common import settings
from app.common.context import Context
from app.models import Status
from app.models.avatars import Breakpoint


class AvatarsRepo:
    READ_PARAMS = """\
        id, account_id, breakpoint, width, height, filesize, status, created_at,
        updated_at
    """

    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx

    async def create(
        self,
        account_id: int,
        width: int,
        height: int,
        filesize: int,
        breakpoint: Breakpoint,
        file_data: bytes,
    ) -> dict[str, typing.Any] | None:
        with io.BytesIO(file_data) as file_obj:
            xd = await self.ctx.s3_client.put_object(
                Bucket=settings.AWS_S3_BUCKET_NAME,
                Key=f"avatars/{account_id}/{breakpoint}",
                Body=file_obj,
                # TODO: Content-Type?
                # TODO: Content-Encoding?
                # TODO: Content-Disposition?
                # TODO: ACL?
            )

        query = """\
            INSERT INTO avatars (account_id, breakpoint, width, height, filesize, status)
                 VALUES (:account_id, :breakpoint, :width, :height, :filesize, :status)
        """
        params = {
            "account_id": account_id,
            "breakpoint": breakpoint,
            "width": width,
            "height": height,
            "filesize": filesize,
            "status": Status.ACTIVE,
        }
        insert_id = await self.ctx.db.execute(query, params)
        assert insert_id is not None

        query = f"""\
            SELECT {self.READ_PARAMS}
                FROM avatars
                WHERE id = :id
        """
        params = {
            "id": insert_id,
        }
        rec = await self.ctx.db.fetch_one(query, params)
        assert rec is not None
        return dict(rec._mapping)
