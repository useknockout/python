"""Typed errors raised by the useknockout SDK."""

from __future__ import annotations

from typing import Optional


class KnockoutError(Exception):
    """
    Base error raised by the useknockout SDK.

    Attributes:
        status: HTTP status code (or None for transport errors).
        code: Short machine-readable error category.
        message: Human-readable message.
    """

    def __init__(
        self,
        message: str,
        *,
        status: Optional[int] = None,
        code: str = "unknown",
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


class AuthError(KnockoutError):
    """401 / 403 — token missing or invalid."""

    def __init__(self, message: str, *, status: int) -> None:
        super().__init__(message, status=status, code="auth")


class BadRequestError(KnockoutError):
    """400 — bad input (invalid format, missing fields, etc.)."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status=400, code="bad_request")


class PayloadTooLargeError(KnockoutError):
    """413 — image exceeds size limit."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status=413, code="payload_too_large")


class RateLimitError(KnockoutError):
    """429 — rate limit exceeded."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status=429, code="rate_limit")


class ServerError(KnockoutError):
    """5xx — server-side failure."""

    def __init__(self, message: str, status: int) -> None:
        super().__init__(message, status=status, code="server")


def raise_for_status(status: int, body: bytes) -> None:
    """Map an HTTP error status to the appropriate KnockoutError subclass."""
    text = body.decode("utf-8", errors="replace") if body else ""
    detail = text or f"HTTP {status}"

    if status == 401 or status == 403:
        raise AuthError(detail, status=status)
    if status == 400:
        raise BadRequestError(detail)
    if status == 413:
        raise PayloadTooLargeError(detail)
    if status == 429:
        raise RateLimitError(detail)
    if 500 <= status < 600:
        raise ServerError(detail, status=status)
    raise KnockoutError(detail, status=status, code="unknown")
