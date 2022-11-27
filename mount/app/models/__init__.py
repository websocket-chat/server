import typing
from enum import Enum

from pydantic import BaseModel as _BaseModel


class Status(str, Enum):
    ACTIVE = "active"
    DEACTIVATED = "deactivated"
    DELETED = "deleted"


T = typing.TypeVar("T", bound=type["BaseModel"])


class BaseModel(_BaseModel):
    class Config:
        anystr_strip_whitespace = True

    @classmethod
    def from_mapping(cls: T, mapping: typing.Mapping[str, typing.Any]) -> T:
        return cls(**{k: mapping[k] for k in cls.__fields__})


class ClientMessages(str, Enum):
    SEND_CHAT_MESSAGE = "SEND_CHAT_MESSAGE"
    MARK_AS_READ = "MARK_AS_READ"
    LOG_OUT = "LOG_OUT"


class ServerMessages(str, Enum):
    ACCEPTED = "ACCEPTED"
    SEND_CHAT_MESSAGE = "SEND_CHAT_MESSAGE"


class Packet(BaseModel):
    message_type: ClientMessages

    # to be parsed into a specific model using `message_type`
    data: dict[str, typing.Any]
