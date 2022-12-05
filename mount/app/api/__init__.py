import time

import aioredis
import databases
from aiobotocore.session import get_session
from app.adapters.database import dsn
from app.api.rest import router as rest_router
from app.api.websocket import router as websocket_router
from app.common import logger
from app.common import settings
from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware


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


# TODO: can this be cleaned up?
def init_s3_client(api: FastAPI) -> None:
    @api.on_event("startup")
    async def startup_s3_client() -> None:
        session = get_session()
        client = await session._create_client(  # type: ignore
            service_name="s3",
            region_name=settings.AWS_S3_BUCKET_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        api.state.s3_client = client
        await api.state.s3_client.__aenter__()

    @api.on_event("shutdown")
    async def shutdown_s3_client() -> None:
        await api.state.s3_client.__aexit__(None, None, None)
        del api.state.s3_client


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
    async def add_s3_client_to_request(request: Request, call_next):
        request.state.s3_client = request.app.state.s3_client
        response = await call_next(request)
        return response

    @api.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.perf_counter_ns()
        response = await call_next(request)
        process_time = (time.perf_counter_ns() - start_time) / 1e6
        response.headers["X-Process-Time"] = str(process_time)  # ms
        return response

    # TODO: staging/production origins
    CORS_ORIGINS = [
        "http://localhost",
        "http://localhost:8080",
    ]

    api.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def init_routes(api: FastAPI) -> None:
    api.include_router(rest_router)
    api.include_router(websocket_router)


def init_api() -> FastAPI:
    api = FastAPI()

    init_db(api)
    init_redis(api)
    init_s3_client(api)
    init_middlewares(api)
    init_routes(api)

    return api
