from __future__ import annotations

import typing
from uuid import UUID
from uuid import uuid4

from app.common.context import Context
from app.common.errors import ServiceError
from app.common.security import verify_password
from app.repositories.accounts import AccountsRepo
from app.repositories.sessions import SessionsRepo

if typing.TYPE_CHECKING:
    from fastapi import WebSocket


async def authenticate(
    ctx: Context,
    email_address: str,
    password: str,
    user_agent: str,
) -> typing.Mapping[str, typing.Any] | ServiceError:
    s_repo = SessionsRepo(ctx)
    a_repo = AccountsRepo(ctx)

    account = await a_repo.fetch_one(
        email_address=email_address,
    )
    if account is None:
        return ServiceError.CREDENTIALS_INCORRECT

    if not verify_password(password, account["password"]):
        return ServiceError.CREDENTIALS_INCORRECT

    session_id = uuid4()
    session = await s_repo.create(
        session_id=session_id,
        account_id=account["id"],
        user_agent=user_agent,
    )
    return session


async def fetch_one(
    ctx: Context,
    session_id: UUID,
) -> typing.Mapping[str, typing.Any] | None:
    repo = SessionsRepo(ctx)
    session = await repo.fetch_one(session_id)
    return session


async def fetch_many(
    ctx: Context,
    account_id: UUID | None = None,
    user_agent: str | None = None,
) -> typing.List[typing.Mapping[str, typing.Any]]:
    repo = SessionsRepo(ctx)
    sessions = await repo.fetch_many(
        account_id=account_id,
        user_agent=user_agent,
    )
    return sessions


# websockets


async def add_websocket(
    ctx: Context,
    session_id: UUID,
    websocket: WebSocket,
) -> typing.Mapping[str, typing.Any] | ServiceError:
    repo = SessionsRepo(ctx)
    session = await repo.add_websocket(session_id, websocket)
    if session is None:
        return ServiceError.SESSIONS_NOT_FOUND

    return session


async def remove_websocket(
    ctx: Context,
    session_id: UUID,
) -> typing.Mapping[str, typing.Any] | ServiceError:
    repo = SessionsRepo(ctx)
    session = await repo.remove_websocket(session_id)
    if session is None:
        return ServiceError.SESSIONS_NOT_FOUND

    return session
