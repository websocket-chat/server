from fastapi import APIRouter

from .v1 import router

router = APIRouter()

router.include_router(router, tags=["v1"])
