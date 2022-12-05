import typing

from app.common.errors import ServiceError
from app.common.json import ORJSONResponse
from pydantic.generics import GenericModel

T = typing.TypeVar("T")


class Cookie(typing.TypedDict, total=False):
    key: str
    value: str
    max_age: int | None
    expires: int | None
    path: str
    domain: str | None
    secure: bool
    httponly: bool
    samesite: typing.Literal["lax", "strict", "none"]


def create_response(
    content: typing.Mapping[str, typing.Any],
    status_code: int,
    headers: dict[str, str] | None,
    cookies: typing.Iterable[Cookie] | None = None,
) -> ORJSONResponse:
    response = ORJSONResponse(content, status_code, headers)

    if cookies is None:
        cookies = []

    for cookie in cookies:
        response.set_cookie(**cookie)

    return response


class Success(GenericModel, typing.Generic[T]):
    status: typing.Literal["success"]
    data: T


def format_success(data: typing.Any) -> dict[str, typing.Any]:
    return {"status": "success", "data": data}


def success(
    data: typing.Any,
    status_code: int = 200,
    headers: dict | None = None,
    cookies: typing.Iterable[Cookie] | None = None,
) -> ORJSONResponse:
    content = format_success(data)
    return create_response(content, status_code, headers, cookies)


class Error(GenericModel, typing.Generic[T]):
    status: typing.Literal["error"]
    error: T
    message: str


def format_failure(error: ServiceError, message: str) -> dict[str, typing.Any]:
    return {"status": "error", "error": error, "message": message}


def failure(
    error: ServiceError,
    message: str,
    status_code: int = 400,
    headers: dict | None = None,
    cookies: typing.Iterable[Cookie] | None = None,
) -> ORJSONResponse:
    content = format_failure(error, message)
    return create_response(content, status_code, headers, cookies)
