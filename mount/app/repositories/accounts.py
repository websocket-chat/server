import typing
from uuid import UUID

from app.common import security
from app.common.context import Context
from app.models import Status


class AccountsRepo:
    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx

    async def sign_up(
        self,
        email_address: str,
        password: str,
        username: str,
    ) -> typing.Mapping[str, typing.Any] | None:
        query = """\
            INSERT INTO accounts (email_address, password, username, status)
                 VALUES (:email_address, :password, :username, :status)
        """
        params = {
            "email_address": email_address,
            "password": security.hash_password(password),
            "username": username,
            "status": Status.ACTIVE,
        }
        insert_id = await self.ctx.db.execute(query, params)
        assert insert_id is not None

        query = """\
            SELECT id, email_address, username
              FROM accounts
             WHERE id = :id
        """
        params = {"id": insert_id}
        rec = await self.ctx.db.fetch_one(query, params)
        return rec._mapping if rec is not None else None

    async def fetch_one(
        self,
        account_id: UUID | None = None,
        email_address: str | None = None,
        username: str | None = None,
    ) -> typing.Mapping[str, typing.Any] | None:
        query = """\
            SELECT id, email_address, username
              FROM accounts
             WHERE id = COALESCE(:id, id)
               AND email_address = COALESCE(:email_address, email_address)
               AND username = COALESCE(:username, username)
        """
        params = {
            "id": account_id,
            "email_address": email_address,
            "username": username,
        }
        rec = await self.ctx.db.fetch_one(query, params)
        return rec._mapping if rec is not None else None
