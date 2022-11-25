import time

import aioredis
import databases
from app.adapters.database import dsn
from app.api.rest import router as rest_router
from app.api.websocket import router as websocket_router
from app.common import logger
from app.common import settings
from fastapi import FastAPI
from fastapi import Request


def init_db(api: FastAPI) -> None:
    @api.on_event("startup")
    async def startup_db() -> None:
        database = databases.Database(
            dsn(
                db_driver=settings.DB_DRIVER,
                db_host=settings.DB_HOST,
                db_port=settings.DB_PORT,
                db_user=settings.DB_USER,
                db_pass=settings.DB_PASS,
                db_name=settings.DB_NAME,
            )
        )
        await database.connect()
        api.state.db = database
        logger.info("Database pool started up")

    @api.on_event("shutdown")
    async def shutdown_db() -> None:
        await api.state.db.disconnect()
        del api.state.db
        logger.info("Database pool shut down")


def init_redis(api: FastAPI) -> None:
    @api.on_event("startup")
    async def startup_redis() -> None:
        redis = aioredis.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
        )
        api.state.redis = redis
        await api.state.redis.initialize()
        logger.info("Redis pool started up")

    @api.on_event("shutdown")
    async def shutdown_redis() -> None:
        await api.state.redis.close()
        del api.state.redis
        logger.info("Redis pool shut down")


def init_middlewares(api: FastAPI) -> None:
    # NOTE: these run bottom to top

    @api.middleware("http")
    async def add_db_to_request(request: Request, call_next):
        async with request.app.state.db.connection() as conn:
            request.state.db = conn
            response = await call_next(request)
        return response

    @api.middleware("http")
    async def add_redis_to_request(request: Request, call_next):
        request.state.redis = request.app.state.redis
        response = await call_next(request)
        return response

    @api.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.perf_counter_ns()
        response = await call_next(request)
        process_time = (time.perf_counter_ns() - start_time) / 1e6
        response.headers["X-Process-Time"] = str(process_time)  # ms
        return response


def init_routes(api: FastAPI) -> None:
    api.include_router(rest_router)
    api.include_router(websocket_router)


def init_api():
    api = FastAPI()

    init_db(api)
    init_redis(api)
    init_middlewares(api)
    init_routes(api)

    return api
