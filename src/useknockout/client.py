"""Synchronous client for the useknockout API."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from useknockout._helpers import (
    DEFAULT_BASE_URL,
    PUBLIC_BETA_TOKEN,
    FileInput,
    _form,
    _multipart_batch,
    _multipart_files,
    _resolve_token,
)
from useknockout._version import __version__
from useknockout.errors import KnockoutError, raise_for_status


class Knockout:
    """
    Synchronous client for the useknockout background-removal API.

    Args:
        token: API token. Falls back to ``KNOCKOUT_TOKEN`` env var, then to the
            public beta token.
        base_url: API base URL (override for self-hosted deployments).
        timeout: Per-request timeout in seconds.

    Example:
        >>> client = Knockout()  # uses public beta token by default
        >>> png = client.remove("photo.jpg")
        >>> open("out.png", "wb").write(png)
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
        self._http = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {self.token}",
                "User-Agent": f"useknockout-python/{__version__}",
            },
        )

    # ---- lifecycle ----

    def __enter__(self) -> "Knockout":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        self._http.close()

    # ---- low-level transport ----

    def _request_bytes(
        self,
        method: str,
        path: str,
        *,
        files=None,
        data=None,
        json=None,
    ) -> bytes:
        try:
            r = self._http.request(method, path, files=files, data=data, json=json)
        except httpx.RequestError as e:
            raise KnockoutError(f"network error: {e}", code="unknown") from e
        if r.status_code >= 400:
            raise_for_status(r.status_code, r.content)
        return r.content

    def _request_json(
        self,
        method: str,
        path: str,
        *,
        files=None,
        data=None,
        json=None,
    ) -> Any:
        try:
            r = self._http.request(method, path, files=files, data=data, json=json)
        except httpx.RequestError as e:
            raise KnockoutError(f"network error: {e}", code="unknown") from e
        if r.status_code >= 400:
            raise_for_status(r.status_code, r.content)
        try:
            return r.json()
        except ValueError as e:
            raise KnockoutError(f"invalid JSON response: {e}", code="server") from e

    # ---- public API ----

    def health(self) -> Dict[str, Any]:
        """GET /health — service status + model info."""
        return self._request_json("GET", "/health")

    def stats(self) -> Dict[str, Any]:
        """GET /stats — public usage counter (total + today + last 7 days)."""
        return self._request_json("GET", "/stats")

    def remove(self, file: FileInput, *, format: str = "png") -> bytes:
        """POST /remove — remove background, return transparent PNG/WebP bytes."""
        return self._request_bytes(
            "POST",
            "/remove",
            files=_multipart_files(file),
            data=_form({"format": format}),
        )

    def remove_url(self, url: str, *, format: str = "png") -> bytes:
        """POST /remove-url — fetch remote image, return transparent PNG/WebP."""
        return self._request_bytes(
            "POST",
            "/remove-url",
            json={"url": url, "format": format},
        )

    def replace_background(
        self,
        file: FileInput,
        *,
        bg_color: str = "#FFFFFF",
        bg_url: Optional[str] = None,
        format: str = "png",
    ) -> bytes:
        """POST /replace-bg — composite subject onto solid color or remote bg image."""
        return self._request_bytes(
            "POST",
            "/replace-bg",
            files=_multipart_files(file),
            data=_form({"bg_color": bg_color, "bg_url": bg_url, "format": format}),
        )

    def remove_batch(
        self,
        files: List[FileInput],
        *,
        format: str = "png",
    ) -> Dict[str, Any]:
        """POST /remove-batch — up to 10 multipart uploads in one call."""
        if len(files) > 10:
            raise ValueError("max 10 files per batch")
        return self._request_json(
            "POST",
            "/remove-batch",
            files=_multipart_batch(files),
            data=_form({"format": format}),
        )

    def remove_batch_url(self, urls: List[str], *, format: str = "png") -> Dict[str, Any]:
        """POST /remove-batch-url — up to 10 remote URLs in one call."""
        if len(urls) > 10:
            raise ValueError("max 10 urls per batch")
        return self._request_json(
            "POST",
            "/remove-batch-url",
            json={"urls": urls, "format": format},
        )

    def mask(self, file: FileInput, *, format: str = "png") -> bytes:
        """POST /mask — return alpha mask only (grayscale)."""
        return self._request_bytes(
            "POST",
            "/mask",
            files=_multipart_files(file),
            data=_form({"format": format}),
        )

    def smart_crop(
        self,
        file: FileInput,
        *,
        padding: int = 24,
        transparent: bool = True,
        format: str = "png",
    ) -> bytes:
        """POST /smart-crop — crop to subject bbox + padding."""
        return self._request_bytes(
            "POST",
            "/smart-crop",
            files=_multipart_files(file),
            data=_form({"padding": padding, "transparent": transparent, "format": format}),
        )

    def shadow(
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
        """POST /shadow — subject on bg with configurable drop shadow."""
        return self._request_bytes(
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

    def sticker(
        self,
        file: FileInput,
        *,
        stroke_color: str = "#FFFFFF",
        stroke_width: int = 20,
        format: str = "png",
    ) -> bytes:
        """POST /sticker — subject + thick outline on transparent bg."""
        return self._request_bytes(
            "POST",
            "/sticker",
            files=_multipart_files(file),
            data=_form(
                {"stroke_color": stroke_color, "stroke_width": stroke_width, "format": format}
            ),
        )

    def outline(
        self,
        file: FileInput,
        *,
        outline_color: str = "#000000",
        outline_width: int = 4,
        format: str = "png",
    ) -> bytes:
        """POST /outline — subject + thin outline on transparent bg."""
        return self._request_bytes(
            "POST",
            "/outline",
            files=_multipart_files(file),
            data=_form(
                {"outline_color": outline_color, "outline_width": outline_width, "format": format}
            ),
        )

    def studio_shot(
        self,
        file: FileInput,
        *,
        bg_color: str = "#FFFFFF",
        aspect: str = "1:1",
        padding: int = 48,
        shadow: bool = True,
        format: str = "jpg",
    ) -> bytes:
        """POST /studio-shot — e-commerce preset (cutout + crop + center + shadow)."""
        return self._request_bytes(
            "POST",
            "/studio-shot",
            files=_multipart_files(file),
            data=_form(
                {
                    "bg_color": bg_color,
                    "aspect": aspect,
                    "padding": padding,
                    "shadow": shadow,
                    "format": format,
                }
            ),
        )

    def compare(self, file: FileInput, *, format: str = "png") -> bytes:
        """POST /compare — side-by-side before/after image."""
        return self._request_bytes(
            "POST",
            "/compare",
            files=_multipart_files(file),
            data=_form({"format": format}),
        )

    def headshot(
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
        """POST /headshot — LinkedIn-ready portrait preset."""
        return self._request_bytes(
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

    def preview(
        self,
        file: FileInput,
        *,
        max_dim: int = 512,
        format: str = "png",
    ) -> bytes:
        """POST /preview — fast low-res preview (~80ms warm)."""
        return self._request_bytes(
            "POST",
            "/preview",
            files=_multipart_files(file),
            data=_form({"max_dim": max_dim, "format": format}),
        )

    def estimate(self, endpoint: str, width: int, height: int) -> Dict[str, Any]:
        """POST /estimate — predict latency + cost without processing."""
        return self._request_json(
            "POST",
            "/estimate",
            json={"endpoint": endpoint, "width": width, "height": height},
        )

    def upscale(
        self,
        file: FileInput,
        *,
        scale: int = 4,
        model: str = "swin2sr",
        face_enhance: bool = False,
        format: str = "png",
    ) -> bytes:
        """POST /upscale — 2x/4x super-resolution.

        ``model="swin2sr"`` (default, v0.6.0+) is sharper on real photos.
        ``model="realesrgan"`` is the legacy backend — better on anime / illustrations.
        ``face_enhance=True`` routes through GFPGAN (Real-ESRGAN backend).
        """
        if scale not in (2, 4):
            raise ValueError("scale must be 2 or 4")
        if model not in ("swin2sr", "realesrgan"):
            raise ValueError("model must be 'swin2sr' or 'realesrgan'")
        return self._request_bytes(
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

    def face_restore(
        self,
        file: FileInput,
        *,
        only_center_face: bool = False,
        format: str = "png",
    ) -> bytes:
        """POST /face-restore — GFPGAN v1.4 portrait restoration.

        Fixes blurry / damaged / low-res faces; background is 2x upscaled by
        Real-ESRGAN. ``only_center_face=True`` restores just the most prominent
        face (faster).
        """
        return self._request_bytes(
            "POST",
            "/face-restore",
            files=_multipart_files(file),
            data=_form({"only_center_face": only_center_face, "format": format}),
        )

    def colorize(
        self,
        file: FileInput,
        *,
        format: str = "png",
    ) -> bytes:
        """POST /colorize — DDColor (Apache-2.0) image colorization.

        Predicts plausible color from grayscale luminance via a ConvNeXt-Large
        backbone (single feed-forward, ~500ms warm). Works on B&W or color
        input — color images are converted to grayscale internally before
        prediction, which makes round-trip recoloring straightforward.

        Added in v0.1.0; requires API ≥ v0.7.0.
        """
        return self._request_bytes(
            "POST",
            "/colorize",
            files=_multipart_files(file),
            data=_form({"format": format}),
        )
