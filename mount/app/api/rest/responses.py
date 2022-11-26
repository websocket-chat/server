import typing

from app.common.json import JSONResponse
from app.common.errors import ServiceError
from pydantic.generics import GenericModel

T = typing.TypeVar("T")


class Success(GenericModel, typing.Generic[T]):
    status: typing.Literal["success"]
    data: T


def success(
    content: typing.Any,
    status_code: int = 200,
    headers: dict | None = None,
) -> JSONResponse:
    data = {"status": "success", "data": content}
    return JSONResponse(data, status_code, headers)


class ErrorResponse(GenericModel, typing.Generic[T]):
    status: typing.Literal["error"]
    error: T
    message: str


def failure(
    error: ServiceError,
    message: str,
    status_code: int = 400,
    headers: dict | None = None,
) -> JSONResponse:
    data = {"status": "error", "error": error, "message": message}
    return JSONResponse(data, status_code, headers)
