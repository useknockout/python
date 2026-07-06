"""Asynchronous client for the useknockout API."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import httpx

from useknockout._helpers import (
    DEFAULT_BASE_URL,
    PUBLIC_BETA_TOKEN,
    FileInput,
    _form,
    _multipart_batch,
    _multipart_files,
    _resolve_token,
    _to_bytes_and_name,
)
from useknockout._version import __version__
from useknockout.errors import KnockoutError, raise_for_status


class AsyncKnockout:
    """
    Asynchronous client for the useknockout background-removal API.

    Use as an async context manager to ensure the underlying httpx client closes:

        async with AsyncKnockout() as client:
            png = await client.remove("photo.jpg")
    """

    def __init__(
        self,
        token: Optional[str] = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 60.0,
    ) -> None:
        self.token = _resolve_token(token) or PUBLIC_BETA_TOKEN
        self.base_url = base_url.rstrip("/")
        self._http = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {self.token}",
                "User-Agent": f"useknockout-python/{__version__}",
            },
        )

    async def __aenter__(self) -> "AsyncKnockout":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._http.aclose()

    async def _request_bytes(
        self,
        method: str,
        path: str,
        *,
        files=None,
        data=None,
        json=None,
        params=None,
        timeout=None,
    ) -> bytes:
        try:
            kwargs = {"files": files, "data": data, "json": json, "params": params}
            if timeout is not None:
                kwargs["timeout"] = timeout
            r = await self._http.request(method, path, **kwargs)
        except httpx.RequestError as e:
            raise KnockoutError(f"network error: {e}", code="unknown") from e
        if r.status_code >= 400:
            raise_for_status(r.status_code, r.content)
        return r.content

    async def _request_json(
        self,
        method: str,
        path: str,
        *,
        files=None,
        data=None,
        json=None,
        params=None,
    ) -> Any:
        try:
            r = await self._http.request(
                method, path, files=files, data=data, json=json, params=params
            )
        except httpx.RequestError as e:
            raise KnockoutError(f"network error: {e}", code="unknown") from e
        if r.status_code >= 400:
            raise_for_status(r.status_code, r.content)
        try:
            return r.json()
        except ValueError as e:
            raise KnockoutError(f"invalid JSON response: {e}", code="server") from e

    async def health(self) -> Dict[str, Any]:
        return await self._request_json("GET", "/health")

    async def stats(self) -> Dict[str, Any]:
        return await self._request_json("GET", "/stats")

    async def remove(self, file: FileInput, *, format: str = "png") -> bytes:
        # /remove reads `format` as a QUERY param (bare default in the API).
        return await self._request_bytes(
            "POST",
            "/remove",
            files=_multipart_files(file),
            params={"format": format},
        )

    async def remove_url(self, url: str, *, format: str = "png") -> bytes:
        return await self._request_bytes(
            "POST",
            "/remove-url",
            json={"url": url, "format": format},
        )

    async def replace_background(
        self,
        file: FileInput,
        *,
        bg_color: str = "#FFFFFF",
        bg_url: Optional[str] = None,
        format: str = "png",
    ) -> bytes:
        return await self._request_bytes(
            "POST",
            "/replace-bg",
            files=_multipart_files(file),
            data=_form({"bg_color": bg_color, "bg_url": bg_url, "format": format}),
        )

    async def remove_batch(
        self,
        files: List[FileInput],
        *,
        format: str = "png",
    ) -> Dict[str, Any]:
        if len(files) > 10:
            raise ValueError("max 10 files per batch")
        # /remove-batch reads `format` as a QUERY param (bare default in the API).
        return await self._request_json(
            "POST",
            "/remove-batch",
            files=_multipart_batch(files),
            params={"format": format},
        )

    async def remove_batch_url(self, urls: List[str], *, format: str = "png") -> Dict[str, Any]:
        if len(urls) > 10:
            raise ValueError("max 10 urls per batch")
        return await self._request_json(
            "POST",
            "/remove-batch-url",
            json={"urls": urls, "format": format},
        )

    async def mask(self, file: FileInput, *, format: str = "png") -> bytes:
        return await self._request_bytes(
            "POST",
            "/mask",
            files=_multipart_files(file),
            data=_form({"format": format}),
        )

    async def smart_crop(
        self,
        file: FileInput,
        *,
        padding: int = 24,
        transparent: bool = True,
        format: str = "png",
    ) -> bytes:
        return await self._request_bytes(
            "POST",
            "/smart-crop",
            files=_multipart_files(file),
            data=_form({"padding": padding, "transparent": transparent, "format": format}),
        )

    async def shadow(
        self,
        file: FileInput,
        *,
        bg_color: str = "#FFFFFF",
        bg_url: Optional[str] = None,
        shadow_color: str = "#000000",
        shadow_offset_x: int = 8,
        shadow_offset_y: int = 12,
        shadow_blur: int = 14,
        shadow_opacity: float = 0.45,
        format: str = "png",
    ) -> bytes:
        return await self._request_bytes(
            "POST",
            "/shadow",
            files=_multipart_files(file),
            data=_form(
                {
                    "bg_color": bg_color,
                    "bg_url": bg_url,
                    "shadow_color": shadow_color,
                    "shadow_offset_x": shadow_offset_x,
                    "shadow_offset_y": shadow_offset_y,
                    "shadow_blur": shadow_blur,
                    "shadow_opacity": shadow_opacity,
                    "format": format,
                }
            ),
        )

    async def sticker(
        self,
        file: FileInput,
        *,
        stroke_color: str = "#FFFFFF",
        stroke_width: int = 20,
        format: str = "png",
    ) -> bytes:
        return await self._request_bytes(
            "POST",
            "/sticker",
            files=_multipart_files(file),
            data=_form(
                {"stroke_color": stroke_color, "stroke_width": stroke_width, "format": format}
            ),
        )

    async def outline(
        self,
        file: FileInput,
        *,
        outline_color: str = "#000000",
        outline_width: int = 4,
        format: str = "png",
    ) -> bytes:
        return await self._request_bytes(
            "POST",
            "/outline",
            files=_multipart_files(file),
            data=_form(
                {"outline_color": outline_color, "outline_width": outline_width, "format": format}
            ),
        )

    async def studio_shot(
        self,
        file: FileInput,
        *,
        bg_color: str = "#FFFFFF",
        aspect: str = "1:1",
        padding: int = 48,
        shadow: bool = True,
        transparent: bool = False,
        enhance: bool = False,
        enhance_strength: float = 0.15,
        format: str = "jpg",
    ) -> bytes:
        return await self._request_bytes(
            "POST",
            "/studio-shot",
            files=_multipart_files(file),
            data=_form(
                {
                    "bg_color": bg_color,
                    "aspect": aspect,
                    "padding": padding,
                    "shadow": shadow,
                    "transparent": transparent,
                    "enhance": enhance,
                    "enhance_strength": enhance_strength,
                    "format": format,
                }
            ),
        )

    async def collage(
        self,
        files: List[FileInput],
        *,
        main_index: int = 0,
        main_position: str = "BR",
        bg_color: str = "#FFFFFF",
        aspect: str = "1:1",
        padding: int = 24,
        format: str = "jpg",
    ) -> bytes:
        """POST /collage — 2-9 photos laid out around a main image. Paid tiers only;
        billed at N base-image units (9 photos = 9x per-image price)."""
        if not 2 <= len(files) <= 9:
            raise ValueError("collage requires 2-9 files")
        return await self._request_bytes(
            "POST",
            "/collage",
            files=_multipart_batch(files),
            data=_form(
                {
                    "main_index": main_index,
                    "main_position": main_position,
                    "bg_color": bg_color,
                    "aspect": aspect,
                    "padding": padding,
                    "format": format,
                }
            ),
            timeout=45.0 + len(files) * 20.0,
        )

    async def compare(self, file: FileInput, *, format: str = "png") -> bytes:
        return await self._request_bytes(
            "POST",
            "/compare",
            files=_multipart_files(file),
            data=_form({"format": format}),
        )

    async def headshot(
        self,
        file: FileInput,
        *,
        bg_color: str = "#FFFFFF",
        bg_blur: bool = False,
        blur_radius: int = 20,
        aspect: str = "4:5",
        padding: int = 64,
        head_top_ratio: float = 0.18,
        format: str = "jpg",
    ) -> bytes:
        return await self._request_bytes(
            "POST",
            "/headshot",
            files=_multipart_files(file),
            data=_form(
                {
                    "bg_color": bg_color,
                    "bg_blur": bg_blur,
                    "blur_radius": blur_radius,
                    "aspect": aspect,
                    "padding": padding,
                    "head_top_ratio": head_top_ratio,
                    "format": format,
                }
            ),
        )

    async def preview(
        self,
        file: FileInput,
        *,
        max_dim: int = 512,
        format: str = "png",
    ) -> bytes:
        return await self._request_bytes(
            "POST",
            "/preview",
            files=_multipart_files(file),
            data=_form({"max_dim": max_dim, "format": format}),
        )

    async def estimate(self, endpoint: str, width: int, height: int) -> Dict[str, Any]:
        return await self._request_json(
            "POST",
            "/estimate",
            json={"endpoint": endpoint, "width": width, "height": height},
        )

    async def upscale(
        self,
        file: FileInput,
        *,
        scale: int = 4,
        model: str = "swin2sr",
        face_enhance: bool = False,
        format: str = "png",
    ) -> bytes:
        if scale not in (2, 4):
            raise ValueError("scale must be 2 or 4")
        if model not in ("swin2sr", "realesrgan"):
            raise ValueError("model must be 'swin2sr' or 'realesrgan'")
        return await self._request_bytes(
            "POST",
            "/upscale",
            files=_multipart_files(file),
            data=_form({
                "scale": scale,
                "model": model,
                "face_enhance": face_enhance,
                "format": format,
            }),
        )

    async def face_restore(
        self,
        file: FileInput,
        *,
        only_center_face: bool = False,
        bg_enhance: bool = False,
        format: str = "png",
    ) -> bytes:
        return await self._request_bytes(
            "POST",
            "/face-restore",
            files=_multipart_files(file),
            data=_form(
                {
                    "only_center_face": only_center_face,
                    "bg_enhance": bg_enhance,
                    "format": format,
                }
            ),
        )

    async def colorize(
        self,
        file: FileInput,
        *,
        format: str = "png",
    ) -> bytes:
        """POST /colorize — DDColor (Apache-2.0) image colorization. Async."""
        return await self._request_bytes(
            "POST",
            "/colorize",
            files=_multipart_files(file),
            data=_form({"format": format}),
        )

    async def silhouette(
        self,
        file: FileInput,
        *,
        subject_color: str = "#7C3AED",
        bg_color: str = "#FFFFFF",
        format: str = "png",
    ) -> bytes:
        """POST /silhouette — two-tone silhouette portrait. Async."""
        return await self._request_bytes(
            "POST",
            "/silhouette",
            files=_multipart_files(file),
            data=_form({
                "subject_color": subject_color,
                "bg_color": bg_color,
                "format": format,
            }),
        )

    async def inpaint(
        self,
        file: FileInput,
        *,
        mask: Optional[FileInput] = None,
        bbox: Optional[Tuple[int, int, int, int]] = None,
        dilation: int = 8,
        format: str = "png",
    ) -> bytes:
        """POST /inpaint — LaMa-based image inpainting. Async."""
        files = _multipart_files(file)
        if mask is not None:
            mdata, mname = _to_bytes_and_name(mask, default_name="mask.png")
            files.append(("mask", (mname, mdata, "application/octet-stream")))
        data = {"dilation": str(int(dilation)), "format": format}
        if bbox is not None:
            x, y, w, h = bbox
            data.update({"x": str(int(x)), "y": str(int(y)), "w": str(int(w)), "h": str(int(h))})
        return await self._request_bytes(
            "POST",
            "/inpaint",
            files=files,
            data=_form(data),
        )
