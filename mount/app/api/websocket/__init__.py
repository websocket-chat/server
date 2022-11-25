from app.api.websocket import v1
from fastapi import APIRouter

router = APIRouter()

router.include_router(v1.router)
