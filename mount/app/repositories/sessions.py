from __future__ import annotations

import json
import typing
from datetime import datetime
from datetime import timedelta
from uuid import UUID

from app.common.context import Context

if typing.TYPE_CHECKING:
    from fastapi import WebSocket

SESSION_EXPIRY = 3600  # 1h


class SessionsRepo:
    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx

    @staticmethod
    def make_key(session_id: UUID | typing.Literal["*"]) -> str:
        return f"server:sessions:{session_id}"

    async def create(
        self,
        session_id: UUID,
        account_id: UUID,
        user_agent: str,
    ) -> typing.Mapping[str, typing.Any]:
        now = datetime.now()
        # expires_at = now + timedelta(seconds=SESSION_EXPIRY)
        session = {
            "session_id": session_id,
            "account_id": account_id,
            "user_agent": user_agent,
            # "expires_at": expires_at,
            "created_at": now,
            "updated_at": now,
            "websocket": None,
        }
        await self.ctx.redis.set(
            name=self.make_key(session_id),
            value=json.dumps(session),
        )
        # await self.ctx.redis.setex(
        #     name=self.make_key(session_id),
        #     time=SESSION_EXPIRY,
        #     value=json.dumps(session),
        # )
        return session

    async def fetch_one(
        self, session_id: UUID
    ) -> typing.Mapping[str, typing.Any] | None:
        session_key = self.make_key(session_id)
        session = await self.ctx.redis.get(session_key)
        return json.loads(session) if session is not None else None

    # TODO: fetch_all

    async def fetch_many(
        self,
        account_id: UUID | None = None,
        user_agent: str | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> list[typing.Mapping[str, typing.Any]]:
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
                session = json.loads(raw_session)

                if account_id is not None and session["account_id"] != account_id:
                    continue

                if user_agent is not None and session["user_agent"] != user_agent:
                    continue

                sessions.append(session)

        return sessions

    async def delete(self, session_id: UUID) -> typing.Mapping[str, typing.Any] | None:
        session_key = self.make_key(session_id)

        session = await self.ctx.redis.get(session_key)
        if session is None:
            return None

        await self.ctx.redis.delete(session_key)
        return session
