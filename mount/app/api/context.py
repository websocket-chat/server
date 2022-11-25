from aioredis import Redis
from app.common.context import Context
from databases import Database
from fastapi import Request


class RequestContext(Context):
    def __init__(self, request: Request) -> None:
        self.request = request

    @property
    def db(self) -> Database:
        return self.request.state.db

    @property
    def redis(self) -> Redis:
        return self.request.state.redis
