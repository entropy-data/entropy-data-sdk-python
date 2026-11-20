"""Thin HTTP layer shared by every API group. Also usable directly for endpoints without a typed method."""

from __future__ import annotations

import ipaddress
import re
from collections.abc import Iterator
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from typing import Any, Generic, TypeVar
from urllib.parse import quote
from urllib.request import getproxies

import httpx
from pydantic import BaseModel

from entropy_data_sdk.errors import raise_for_status

T = TypeVar("T", bound=BaseModel)

DEFAULT_TIMEOUT = 30.0
DEFAULT_RETRIES = 3
JSON = "application/json"
YAML = "application/yaml"
LOCATION_HTML = "location-html"
MAX_SEGMENT_LENGTH = 256

try:
    _SDK_VERSION = version("entropy-data-sdk")
except PackageNotFoundError:
    _SDK_VERSION = "dev"


def seg(value: str, *, safe: str = "") -> str:
    """Validate and percent-encode one path segment, typically a resource id.

    Rejects empty, overlong and ``..`` segments. Everything else is encoded, so an id containing ``?``, ``#`` or a
    space reaches the server intact instead of changing the request. ``safe="/"`` keeps the slashes of an id that
    spans several segments, such as a hierarchical tag id: the server reads those from the raw path and rejects an
    encoded slash.
    """
    if not isinstance(value, str) or not value:
        raise ValueError("Resource id must be a non-empty string.")
    if len(value) > MAX_SEGMENT_LENGTH:
        raise ValueError(f"Resource id must not exceed {MAX_SEGMENT_LENGTH} characters.")
    if ".." in value.split("/"):
        raise ValueError(f"Resource id must not contain path traversal: {value!r}")
    return quote(value, safe=safe)


def to_payload(body: BaseModel | dict[str, Any]) -> dict[str, Any]:
    """Serialize a request body the way the API expects it: JSON types, no unset fields."""
    if isinstance(body, BaseModel):
        return body.model_dump(mode="json", by_alias=True, exclude_none=True)
    return body


def has_next_page(response: httpx.Response) -> bool:
    return bool(re.search(r'rel="next"', response.headers.get("Link", "")))


def _json_or_none(response: httpx.Response) -> Any:
    if response.content and JSON in response.headers.get("Content-Type", ""):
        return response.json()
    return None


def _is_ip_address(host: str) -> bool:
    try:
        ipaddress.ip_address(host.split("/")[0])
    except ValueError:
        return False
    return True


def environment_proxy_mounts(*, retries: int, verify: bool | str) -> dict[str, httpx.BaseTransport | None]:
    """Transports for the proxies named by ``HTTP_PROXY``, ``HTTPS_PROXY``, ``ALL_PROXY`` and ``NO_PROXY``.

    httpx reads these variables only when it builds the transport itself, so a client with its own transport has to
    mount the proxies explicitly. The URL patterns follow the ones httpx derives from the same variables.
    """
    proxies = getproxies()
    no_proxy_hosts = [host.strip() for host in proxies.get("no", "").split(",")]
    if "*" in no_proxy_hosts:
        return {}

    mounts: dict[str, httpx.BaseTransport | None] = {}
    for scheme in ("http", "https", "all"):
        url = proxies.get(scheme)
        if url:
            proxy = url if "://" in url else f"http://{url}"
            mounts[f"{scheme}://"] = httpx.HTTPTransport(retries=retries, verify=verify, proxy=proxy)

    if not mounts:
        return {}

    for host in filter(None, no_proxy_hosts):
        if "://" in host:
            mounts[host] = None
        elif _is_ip_address(host):
            mounts[f"all://[{host}]" if ":" in host else f"all://{host}"] = None
        elif host.lower() == "localhost":
            mounts[f"all://{host}"] = None
        else:
            mounts[f"all://*{host}"] = None
    return mounts


class Page(list, Generic[T]):
    """One page of a list endpoint. ``has_next`` tells whether the next page number returns more."""

    def __init__(self, items, *, has_next: bool = False):
        super().__init__(items)
        self.has_next = has_next


@dataclass
class ApiResponse:
    """What a write call returned: the parsed body, if any, and the headers the API uses to carry extra information."""

    status_code: int
    data: Any
    headers: httpx.Headers

    @property
    def location_html(self) -> str | None:
        """Link to the resource in the web application, when the API provides one."""
        return self.headers.get(LOCATION_HTML)


class HttpClient:
    def __init__(
        self,
        host: str,
        api_key: str,
        *,
        timeout: float | httpx.Timeout = DEFAULT_TIMEOUT,
        verify: bool | str = True,
        retries: int = DEFAULT_RETRIES,
        trust_env: bool = True,
        transport: httpx.BaseTransport | None = None,
    ):
        self.base_url = host.rstrip("/")
        # Retries cover connection failures only, never a request the server may have seen.
        mounts = None
        if transport is None:
            transport = httpx.HTTPTransport(retries=retries, verify=verify, trust_env=trust_env)
            if trust_env:
                mounts = environment_proxy_mounts(retries=retries, verify=verify)
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "x-api-key": api_key,
                "Accept": JSON,
                "User-Agent": f"entropy-data-sdk-python/{_SDK_VERSION}",
            },
            timeout=timeout,
            transport=transport,
            mounts=mounts,
            trust_env=trust_env,
        )

    def close(self) -> None:
        self._client.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: BaseModel | dict[str, Any] | list[Any] | None = None,
        content: str | bytes | None = None,
        content_type: str | None = None,
        accept: str | None = None,
        timeout: float | httpx.Timeout | None = None,
    ) -> httpx.Response:
        """Send one request and raise an :class:`~entropy_data_sdk.errors.ApiError` on a non-2xx status."""
        headers: dict[str, str] = {}
        if content_type:
            headers["Content-Type"] = content_type
        if accept:
            headers["Accept"] = accept
        payload: Any = json
        if isinstance(json, BaseModel):
            payload = to_payload(json)
        elif isinstance(json, list):
            payload = [to_payload(item) if isinstance(item, BaseModel) else item for item in json]
        clean_params = {key: value for key, value in (params or {}).items() if value is not None}
        response = self._client.request(
            method,
            path,
            params=clean_params or None,
            json=payload,
            content=content,
            headers=headers or None,
            timeout=timeout if timeout is not None else httpx.USE_CLIENT_DEFAULT,
        )
        raise_for_status(response)
        return response

    def get_json(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        return self.request("GET", path, params=params).json()

    def get_model(self, path: str, model: type[T], *, params: dict[str, Any] | None = None) -> T:
        return model.model_validate(self.get_json(path, params=params))

    def get_page(self, path: str, model: type[T] | None = None, *, params: dict[str, Any] | None = None) -> Page:
        """GET a list endpoint. Items are parsed into ``model`` when given, otherwise kept as dictionaries."""
        response = self.request("GET", path, params=params)
        items = response.json()
        if model is not None:
            items = [model.model_validate(item) for item in items]
        return Page(items, has_next=has_next_page(response))

    def get_list(self, path: str, model: type[T], *, params: dict[str, Any] | None = None) -> Page[T]:
        return self.get_page(path, model, params=params)

    def get_text(self, path: str, *, accept: str = YAML, params: dict[str, Any] | None = None) -> str:
        return self.request("GET", path, params=params, accept=accept).text

    def put_json(
        self, path: str, body: BaseModel | dict[str, Any], *, params: dict[str, Any] | None = None
    ) -> ApiResponse:
        response = self.request("PUT", path, json=body, params=params)
        return ApiResponse(response.status_code, _json_or_none(response), response.headers)

    def put_model(self, path: str, body: BaseModel | dict[str, Any], model: type[T]) -> T:
        return model.model_validate(self.request("PUT", path, json=body).json())

    def put_text(self, path: str, text: str, *, content_type: str = YAML, timeout: float | None = None) -> ApiResponse:
        response = self.request("PUT", path, content=text, content_type=content_type, timeout=timeout)
        return ApiResponse(response.status_code, _json_or_none(response), response.headers)

    def post_json(
        self,
        path: str,
        body: BaseModel | dict[str, Any] | list[Any] | None = None,
        *,
        params: dict[str, Any] | None = None,
        timeout: float | httpx.Timeout | None = None,
    ) -> ApiResponse:
        response = self.request("POST", path, json=body, params=params, timeout=timeout)
        return ApiResponse(response.status_code, _json_or_none(response), response.headers)

    def post_model(
        self,
        path: str,
        model: type[T],
        body: BaseModel | dict[str, Any] | None = None,
        *,
        params: dict[str, Any] | None = None,
        timeout: float | httpx.Timeout | None = None,
    ) -> T:
        return model.model_validate(self.request("POST", path, json=body, params=params, timeout=timeout).json())

    def patch_model(self, path: str, body: BaseModel | dict[str, Any], model: type[T]) -> T:
        return model.model_validate(self.request("PATCH", path, json=body).json())

    def delete(self, path: str, *, params: dict[str, Any] | None = None) -> ApiResponse:
        response = self.request("DELETE", path, params=params)
        return ApiResponse(response.status_code, _json_or_none(response), response.headers)

    def iterate_pages(self, path: str, *, params: dict[str, Any] | None = None, page_param: str = "p") -> Iterator[Any]:
        """Yield the items of every page of a paginated list endpoint."""
        page = 0
        while True:
            response = self.request("GET", path, params={**(params or {}), page_param: page})
            yield from response.json()
            if not has_next_page(response):
                return
            page += 1
