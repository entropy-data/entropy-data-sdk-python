"""Exceptions raised by the SDK."""

from __future__ import annotations

import json
import re

import httpx


class EntropyDataError(Exception):
    """Base class for every error the SDK raises on purpose."""


class ApiError(EntropyDataError):
    """A non-2xx response from the Entropy Data API."""

    def __init__(self, status_code: int, message: str, url: str, body: str = ""):
        self.status_code = status_code
        self.message = message
        self.url = url
        self.body = body
        super().__init__(f"HTTP {status_code} from {url}: {message}")


class BadRequestError(ApiError):
    """400."""


class UnauthorizedError(ApiError):
    """401: the API key is missing or invalid."""


class ForbiddenError(ApiError):
    """403."""


class NotFoundError(ApiError):
    """404."""


class ConflictError(ApiError):
    """409."""


class UnprocessableContentError(ApiError):
    """422."""


_ERRORS_BY_STATUS: dict[int, type[ApiError]] = {
    400: BadRequestError,
    401: UnauthorizedError,
    403: ForbiddenError,
    404: NotFoundError,
    409: ConflictError,
    422: UnprocessableContentError,
}


def _extract_message(response: httpx.Response) -> str:
    text = response.text
    try:
        body = response.json()
    except (json.JSONDecodeError, ValueError):
        body = None
    if isinstance(body, dict):
        for key in ("detail", "message", "title"):
            if body.get(key):
                return str(body[key])
        return text
    if "<html" in text.lower():
        match = re.search(r"<title>([^<]+)</title>", text, re.IGNORECASE)
        return match.group(1).strip() if match else (response.reason_phrase or "Server error")
    return text or response.reason_phrase or f"HTTP {response.status_code}"


def raise_for_status(response: httpx.Response) -> None:
    if response.is_success:
        return
    error_type = _ERRORS_BY_STATUS.get(response.status_code, ApiError)
    raise error_type(response.status_code, _extract_message(response), str(response.url), response.text)
