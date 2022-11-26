from fastapi import APIRouter

from . import accounts
from . import sessions

router = APIRouter()


router.include_router(accounts.router, tags=["Accounts"])
router.include_router(sessions.router, tags=["Sessions"])
