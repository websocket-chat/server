import io
import typing

from app.common import settings
from app.common.context import Context
from app.models import Status
from app.models.avatars import Breakpoint


class AvatarsRepo:
    READ_PARAMS = """\
        id, account_id, content_type, breakpoint, width, height, filesize,
        public_url, status, created_at, updated_at
    """

    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx

    async def create(
        self,
        account_id: int,
        breakpoint: Breakpoint,
        content_type: str,
        width: int,
        height: int,
        filesize: int,
        public_url: str,
        file_name: str,
        file_data: bytes,
    ) -> dict[str, typing.Any] | None:
        with io.BytesIO(file_data) as file_obj:
            await self.ctx.s3_client.put_object(
                Bucket=settings.AWS_S3_BUCKET_NAME,
                Key=f"avatars/{account_id}/{file_name}",
                Body=file_obj,
                ContentType=content_type,
                # TODO: Content-Encoding?
                # TODO: Content-Disposition?
                # TODO: ACL?
            )

        query = """\
            INSERT INTO avatars (account_id, breakpoint, content_type, width,
                                 height, filesize, public_url, status)
                 VALUES (:account_id, :breakpoint, :content_type, :width,
                         :height, :filesize, :public_url, :status)
        """
        params = {
            "account_id": account_id,
            "breakpoint": breakpoint,
            "content_type": content_type,
            "width": width,
            "height": height,
            "filesize": filesize,
            "public_url": public_url,
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

    async def fetch_all(
        self,
        account_id: int,
    ) -> list[dict[str, typing.Any]]:
        query = f"""\
            SELECT {self.READ_PARAMS}
              FROM avatars
             WHERE account_id = :account_id
               AND status = :status
        """
        params = {
            "account_id": account_id,
            "status": Status.ACTIVE,
        }
        recs = await self.ctx.db.fetch_all(query, params)
        return [dict(rec._mapping) for rec in recs]

    async def fetch_one(
        self,
        account_id: int,
        breakpoint: Breakpoint,
    ) -> dict[str, typing.Any] | None:
        query = f"""\
            SELECT {self.READ_PARAMS}
              FROM avatars
             WHERE account_id = :account_id
               AND breakpoint = :breakpoint
               AND status = :status
        """
        params = {
            "account_id": account_id,
            "breakpoint": breakpoint,
            "status": Status.ACTIVE,
        }
        rec = await self.ctx.db.fetch_one(query, params)
        return dict(rec._mapping) if rec is not None else None

    async def delete(
        self,
        account_id: int,
    ) -> list[dict[str, typing.Any]]:
        query = f"""\
            SELECT {self.READ_PARAMS}
              FROM avatars
             WHERE account_id = :account_id
               AND status = :status
        """
        params = {
            "account_id": account_id,
            "status": Status.ACTIVE,
        }
        recs = await self.ctx.db.fetch_all(query, params)

        query = """\
            UPDATE avatars
               SET status = :new_status
             WHERE account_id = :account_id
               AND status = :old_status
        """
        params = {
            "account_id": account_id,
            "new_status": Status.DELETED,
            "old_status": Status.ACTIVE,
        }
        await self.ctx.db.execute(query, params)
        return [dict(rec._mapping) for rec in recs]
