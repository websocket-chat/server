import typing

from app.common.context import Context
from app.common.errors import ServiceError
from app.common.validation import validate_email
from app.common.validation import validate_password
from app.common.validation import validate_username
from app.repositories.accounts import AccountsRepo


async def signup(
    ctx: Context,
    email_address: str,
    password: str,
    username: str,
) -> dict[str, typing.Any] | ServiceError:
    repo = AccountsRepo(ctx)

    # perform data validation

    if not validate_username(username):
        return ServiceError.ACCOUNTS_USERNAME_INVALID

    if not validate_email(email_address):
        return ServiceError.ACCOUNTS_EMAIL_ADDRESS_INVALID

    if not validate_password(password):
        return ServiceError.ACCOUNTS_PASSWORD_INVALID

    if await repo.fetch_one(email_address=email_address) is not None:
        return ServiceError.ACCOUNTS_EMAIL_ADDRESS_EXISTS

    if await repo.fetch_one(username=username) is not None:
        return ServiceError.ACCOUNTS_USERNAME_EXISTS

    # perform sign up

    account = await repo.sign_up(
        email_address=email_address,
        password=password,
        username=username,
    )
    if account is None:
        return ServiceError.ACCOUNTS_SIGNUP_FAILED

    return account


async def fetch_one(
    ctx: Context,
    account_id: int | None = None,
    email_address: str | None = None,
    username: str | None = None,
) -> dict[str, typing.Any] | ServiceError:
    repo = AccountsRepo(ctx)

    account = await repo.fetch_one(
        account_id=account_id,
        email_address=email_address,
        username=username,
    )
    if account is None:
        return ServiceError.ACCOUNTS_NOT_FOUND

    return account


async def fetch_many(
    ctx: Context,
    page: int,
    page_size: int,
) -> list[dict[str, typing.Any]] | ServiceError:
    repo = AccountsRepo(ctx)

    accounts = await repo.fetch_many(page=page, page_size=page_size)
    if accounts is None:
        return ServiceError.ACCOUNTS_NOT_FOUND

    return accounts
