from aiobotocore.client import AioBaseClient
from aioredis import Redis
from app.common.context import Context
from databases import Database
from fastapi import Request
from fastapi import WebSocket


class HTTPRequestContext(Context):
    def __init__(self, request: Request) -> None:
        self.request = request

    @property
    def db(self) -> Database:
        return self.request.state.db

    @property
    def redis(self) -> Redis:
        return self.request.state.redis

    @property
    def s3_client(self) -> AioBaseClient:
        return self.request.state.s3_client


class WebSocketRequestContext(Context):
    def __init__(self, websocket: WebSocket) -> None:
        self.websocket = websocket

    @property
    def db(self) -> Database:
        return self.websocket.app.state.db

    @property
    def redis(self) -> Redis:
        return self.websocket.app.state.redis

    @property
    def s3_client(self) -> AioBaseClient:
        return self.websocket.app.state.s3_client
