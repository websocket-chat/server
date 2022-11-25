import typing

from app.common.context import Context
from app.common.errors import ServiceError
from app.repositories.accounts import AccountsRepo


async def signup(
    ctx: Context,
    email_address: str,
    password: str,
    name: str,
) -> typing.Mapping[str, typing.Any] | ServiceError:
    repo = AccountsRepo(ctx)

    account = await repo.fetch_one(
        email_address=email_address,
    )
    if account is not None:
        return ServiceError.ACCOUNTS_EMAIL_ADDRESS_EXISTS

    account = await repo.sign_up(
        email_address=email_address,
        password=password,
        name=name,
    )
    if account is None:
        return ServiceError.ACCOUNTS_SIGNUP_FAILED

    return account
