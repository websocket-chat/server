import typing
from abc import ABC
from abc import abstractmethod

from aioredis import Redis
from databases import Database

if typing.TYPE_CHECKING:
    from types_aiobotocore_s3.client import S3Client


class Context(ABC):
    @property
    @abstractmethod
    def db(self) -> Database:
        raise NotImplementedError

    @property
    @abstractmethod
    def redis(self) -> Redis:
        raise NotImplementedError

    @property
    @abstractmethod
    def s3_client(self) -> "S3Client":
        raise NotImplementedError
