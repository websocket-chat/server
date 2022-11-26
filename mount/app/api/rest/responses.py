import typing

from app.common.errors import ServiceError
from app.common.json import ORJSONResponse
from pydantic.generics import GenericModel

T = typing.TypeVar("T")


class Success(GenericModel, typing.Generic[T]):
    status: typing.Literal["success"]
    data: T


def success(
    content: typing.Any,
    status_code: int = 200,
    headers: dict | None = None,
) -> ORJSONResponse:
    data = {"status": "success", "data": content}
    return ORJSONResponse(data, status_code, headers)


class ErrorResponse(GenericModel, typing.Generic[T]):
    status: typing.Literal["error"]
    error: T
    message: str


def failure(
    error: ServiceError,
    message: str,
    status_code: int = 400,
    headers: dict | None = None,
) -> ORJSONResponse:
    data = {"status": "error", "error": error, "message": message}
    return ORJSONResponse(data, status_code, headers)
