from app.api.context import RequestContext
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


@router.post("/v1/accounts", response_model=Success[Account])
async def create_account(args: SignupForm, ctx: RequestContext = Depends()):
    data = await accounts.signup(
        ctx,
        email_address=args.email_address,
        password=args.password,
        username=args.username,
    )
    if isinstance(data, ServiceError):
        if data is ServiceError.ACCOUNTS_EMAIL_ADDRESS_EXISTS:
            status_code = status.HTTP_409_CONFLICT
        elif data is ServiceError.ACCOUNTS_SIGNUP_FAILED:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            logger.error("Unhandled service error: ", error=data)
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        return responses.failure(
            error=data,
            message="Failed to create account",
            status_code=status_code,
        )

    resp = Account.from_mapping(data)
    return responses.success(resp)
