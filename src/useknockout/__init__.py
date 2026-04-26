"""
useknockout — state-of-the-art background removal API.

Quickstart:

    from useknockout import Knockout

    client = Knockout(token="kno_public_beta_4d7e9f1a3c5b2e8d6a9f7c1b3e5d8a2f")
    png_bytes = client.remove("photo.jpg")
    open("out.png", "wb").write(png_bytes)

Async:

    import asyncio
    from useknockout import AsyncKnockout

    async def main():
        async with AsyncKnockout(token="...") as client:
            png = await client.remove("photo.jpg")
            open("out.png", "wb").write(png)

    asyncio.run(main())
"""

from useknockout._version import __version__
from useknockout.client import Knockout
from useknockout.async_client import AsyncKnockout
from useknockout.errors import (
    KnockoutError,
    AuthError,
    BadRequestError,
    PayloadTooLargeError,
    RateLimitError,
    ServerError,
)

__all__ = [
    "__version__",
    "Knockout",
    "AsyncKnockout",
    "KnockoutError",
    "AuthError",
    "BadRequestError",
    "PayloadTooLargeError",
    "RateLimitError",
    "ServerError",
]
