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


class Success(GenericModel, typing.Generic[T]):
    status: typing.Literal["success"]
    data: T


def create_response(
    data: typing.Mapping[str, typing.Any],
    status_code: int,
    headers: dict[str, str] | None,
    cookies: typing.Iterable[Cookie] | None = None,
) -> ORJSONResponse:
    response = ORJSONResponse(data, status_code, headers)

    if cookies is None:
        cookies = []

    for cookie in cookies:
        response.set_cookie(**cookie)

    return response


def success(
    content: typing.Any,
    status_code: int = 200,
    headers: dict | None = None,
    cookies: typing.Iterable[Cookie] | None = None,
) -> ORJSONResponse:
    data = {"status": "success", "data": content}
    return create_response(data, status_code, headers, cookies)


class ErrorResponse(GenericModel, typing.Generic[T]):
    status: typing.Literal["error"]
    error: T
    message: str


def failure(
    error: ServiceError,
    message: str,
    status_code: int = 400,
    headers: dict | None = None,
    cookies: typing.Iterable[Cookie] | None = None,
) -> ORJSONResponse:
    data = {"status": "error", "error": error, "message": message}
    return create_response(data, status_code, headers, cookies)
