"""Top-level package for Radegast."""

__author__ = """Damian Świstowski"""
__email__ = "damian@swistowski.org"
__version__ = "0.1.0"

import dataclasses
from dataclasses import dataclass
from enum import Enum
from string import Formatter
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Mapping
from typing import Optional
from typing import Protocol
from typing import TYPE_CHECKING
from typing import Type
from typing import TypeVar

import requests
from svarog import forge

_REQUESTS = "__radegast_requests__"

T = TypeVar("T")


class Method(Enum):
    GET = "GET"


@dataclass
class Request:
    method: Method
    response_type: Type
    params: Type
    path: Optional[str] = None

    def annotation(self):
        class RequestProtocol(Protocol):
            def __call__(self) -> self.response_type:
                ...

            params = Callable[..., "MyProtocol"]

        return RequestProtocol

    def for_path(self, path: str) -> "Request":
        if self.path:
            raise RuntimeError("Path already exists")
        return dataclasses.replace(self, path=path)


class Radegast:
    _default_base_url: ClassVar[str]

    def __init_subclass__(cls, base_url: str):
        cls._default_base_url = base_url
        requests = {
            name: request
            for name, request in cls.__annotations__.items()
            if isinstance(request, Request)
        }
        for name, request in requests.items():
            cls.__annotations__[name] = request.annotation()

        setattr(cls, _REQUESTS, requests)
        for name in requests:

            def _binder(name: str):
                @property  # type: ignore
                def _property(self) -> BoundRequest:
                    return BoundRequest(self, name, requests[name])

                return _property

            setattr(cls, name, _binder(name))

    def __init__(self, base_url: Optional[str] = None, session=None):
        self._base_url = base_url or self._default_base_url
        self._session = session or requests.session()

    def url(self, path: str) -> str:
        return self._base_url + path

    def session(
        self, method: Method, url: str, params: Optional[Mapping[str, Any]] = None
    ):
        response = self._session.request(method.value, self.url(url), params=params)
        response.raise_for_status()
        return response.json()


@dataclass
class BoundRequest:
    _radegast: Radegast
    _name: str
    _request: Request
    _params: Optional[Any] = None

    @property
    def method(self) -> Method:
        return self._request.method

    def url(self, params: Mapping[str, Any]) -> str:
        url = self._request.path or self._name
        return url.format_map(params)

    def url_params(self, kwargs: Mapping[str, Any]) -> Mapping[str, Any]:
        field_names = {
            field_name for _, field_name, *__ in Formatter().parse(self._name)
        }
        return {k: v for k, v in kwargs.items() if k in field_names}

    def __call__(self, *args, **kwargs) -> T:
        json = self._radegast.session(
            self.method, self.url(self.url_params(kwargs)), params=self.get_params()
        )
        return forge(self._request.response_type, json)

    def get_params(self) -> Optional[Mapping[str, Any]]:
        if self._params:
            return dataclasses.asdict(self._params)
        return None

    def params(self, **kwargs):
        return dataclasses.replace(self, _params=forge(self._request.params, kwargs))


def request(
    method: Method = Method.GET, response_type: Type = Any, params: Type = None,
) -> Request:
    request = Request(method=method, response_type=response_type, params=params)

    if TYPE_CHECKING:
        return request.annotation()

    return request


def get(response_type: Type = Any, params: Type = None) -> Request:
    return request(method=Method.GET, response_type=response_type, params=params)
