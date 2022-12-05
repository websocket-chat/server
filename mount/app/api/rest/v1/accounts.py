from app.api.context import HTTPRequestContext
from app.api.rest import responses
from app.api.rest.responses import Success
from app.common import logger
from app.common.errors import ServiceError
from app.models.accounts import Account
from app.models.accounts import SignupForm
from app.usecases import accounts
from fastapi import APIRouter
from fastapi import Depends
from fastapi import status

router = APIRouter()


def get_status_code(error: ServiceError) -> int:
    if error is ServiceError.ACCOUNTS_SIGNUP_FAILED:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    elif error is ServiceError.ACCOUNTS_USERNAME_EXISTS:
        return status.HTTP_409_CONFLICT
    elif error is ServiceError.ACCOUNTS_EMAIL_ADDRESS_EXISTS:
        return status.HTTP_409_CONFLICT
    elif error is ServiceError.ACCOUNTS_USERNAME_INVALID:
        return status.HTTP_400_BAD_REQUEST
    elif error is ServiceError.ACCOUNTS_EMAIL_ADDRESS_INVALID:
        return status.HTTP_400_BAD_REQUEST
    elif error is ServiceError.ACCOUNTS_PASSWORD_INVALID:
        return status.HTTP_400_BAD_REQUEST
    elif error is ServiceError.ACCOUNTS_NOT_FOUND:
        return status.HTTP_404_NOT_FOUND
    else:
        logger.error("Unhandled service error: ", error=error)
        return status.HTTP_500_INTERNAL_SERVER_ERROR


@router.post("/v1/accounts", response_model=Success[Account])
async def signup(args: SignupForm, ctx: HTTPRequestContext = Depends()):
    data = await accounts.signup(
        ctx,
        email_address=args.email_address,
        password=args.password,
        username=args.username,
    )
    if isinstance(data, ServiceError):
        return responses.failure(
            error=data,
            message="Failed to create account",
            status_code=get_status_code(data),
        )

    resp = Account.from_mapping(data)
    return responses.success(resp, status_code=status.HTTP_201_CREATED)


@router.get("/v1/accounts", response_model=Success[list[Account]])
async def fetch_many(
    page: int = 1,
    page_size: int = 10,
    ctx: HTTPRequestContext = Depends(),
):
    data = await accounts.fetch_many(ctx, page=page, page_size=page_size)
    if isinstance(data, ServiceError):
        return responses.failure(
            error=data,
            message="Failed to fetch accounts",
            status_code=get_status_code(data),
        )

    resp = [Account.from_mapping(rec) for rec in data]
    return responses.success(resp, status_code=status.HTTP_200_OK)


@router.get("/v1/accounts/{account_id}", response_model=Success[Account])
async def fetch_one(
    account_id: int,
    ctx: HTTPRequestContext = Depends(),
):
    data = await accounts.fetch_one(ctx, account_id=account_id)
    if isinstance(data, ServiceError):
        return responses.failure(
            error=data,
            message="Failed to fetch account",
            status_code=get_status_code(data),
        )

    resp = Account.from_mapping(data)
    return responses.success(resp, status_code=status.HTTP_200_OK)
