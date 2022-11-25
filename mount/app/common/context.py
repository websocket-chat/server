from abc import ABC
from abc import abstractmethod

from aioredis import Redis
from databases import Database


class Context(ABC):
    @property
    @abstractmethod
    def db(self) -> Database:
        raise NotImplementedError

    @property
    @abstractmethod
    def redis(self) -> Redis:
        raise NotImplementedError
