from __future__ import annotations

import json
import typing
from datetime import datetime
from datetime import timedelta
from uuid import UUID

from app.common.context import Context


SESSION_EXPIRY = 60 * 60 * 24 * 30  # 30 days


class SessionsRepo:
    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx

    @staticmethod
    def make_key(session_id: UUID | typing.Literal["*"]) -> str:
        return f"server:sessions:{session_id}"

    @staticmethod
    def serialize(session: typing.Mapping[str, typing.Any]) -> str:
        return json.dumps(
            {
                "session_id": str(session["session_id"]),
                "account_id": str(session["account_id"]),
                "user_agent": session["user_agent"],
                "expires_at": session["expires_at"].isoformat(),
                "created_at": session["created_at"].isoformat(),
                "updated_at": session["updated_at"].isoformat(),
            }
        )

    @staticmethod
    def deserialize(raw_session: str) -> dict[str, typing.Any]:
        session = json.loads(raw_session)
        assert isinstance(session, dict)
        session["session_id"] = UUID(session["session_id"])
        session["account_id"] = int(session["account_id"])
        session["expires_at"] = datetime.fromisoformat(session["expires_at"])
        session["created_at"] = datetime.fromisoformat(session["created_at"])
        session["updated_at"] = datetime.fromisoformat(session["updated_at"])
        return session

    async def create(
        self,
        session_id: UUID,
        account_id: int,
        user_agent: str,
    ) -> dict[str, typing.Any]:
        now = datetime.now()
        expires_at = now + timedelta(seconds=SESSION_EXPIRY)
        session = {
            "session_id": session_id,
            "account_id": account_id,
            "user_agent": user_agent,
            "expires_at": expires_at,
            "created_at": now,
            "updated_at": now,
        }
        await self.ctx.redis.set(
            name=self.make_key(session_id),
            value=self.serialize(session),
        )
        # await self.ctx.redis.setex(
        #     name=self.make_key(session_id),
        #     time=SESSION_EXPIRY,
        #     value=self.serialize(session),
        # )
        return session

    async def fetch_one(self, session_id: UUID) -> dict[str, typing.Any] | None:
        session_key = self.make_key(session_id)
        session = await self.ctx.redis.get(session_key)
        return self.deserialize(session) if session is not None else None

    # TODO: fetch_all

    async def fetch_many(
        self,
        account_id: int | None,
        user_agent: str | None,
        page: int,
        page_size: int,
    ) -> list[dict[str, typing.Any]]:
        session_key = self.make_key("*")

        if page > 1:
            cursor, keys = await self.ctx.redis.scan(
                cursor=0,
                match=session_key,
                count=(page - 1) * page_size,
            )
        else:
            cursor = None

        sessions = []
        while cursor != 0:
            cursor, keys = await self.ctx.redis.scan(
                cursor=cursor or 0,
                match=session_key,
                count=page_size,
            )

            raw_sessions = await self.ctx.redis.mget(keys)
            for raw_session in raw_sessions:
                session = self.deserialize(raw_session)

                if account_id is not None and session["account_id"] != account_id:
                    continue

                if user_agent is not None and session["user_agent"] != user_agent:
                    continue

                sessions.append(session)

        return sessions

    async def delete(self, session_id: UUID) -> dict[str, typing.Any] | None:
        session_key = self.make_key(session_id)

        session = await self.ctx.redis.get(session_key)
        if session is None:
            return None

        await self.ctx.redis.delete(session_key)
        return self.deserialize(session)
