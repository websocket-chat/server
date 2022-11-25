from fastapi import APIRouter

from . import accounts

router = APIRouter()


router.include_router(accounts.router, tags=["Accounts"])
