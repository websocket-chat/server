import uuid
import typing

import orjson
from fastapi.responses import JSONResponse
from pydantic import BaseModel


def _default_processor(data: typing.Any) -> typing.Any:
    if isinstance(data, BaseModel):
        return _default_processor(data.dict())
    elif isinstance(data, dict):
        return {k: _default_processor(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_default_processor(v) for v in data]
    elif isinstance(data, uuid.UUID):
        return str(data)
    else:
        return data


def dumps(data: typing.Any) -> bytes:
    return orjson.dumps(data, default=_default_processor)


def loads(data: str) -> typing.Any:
    return orjson.loads(data)


class ORJSONResponse(JSONResponse):
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        return dumps(content)
