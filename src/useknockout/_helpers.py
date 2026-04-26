"""Internal helpers shared by sync + async clients."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

FileInput = Union[str, Path, bytes, bytearray]
"""Anything the SDK accepts as image input.

- ``str`` / ``Path``: filesystem path to read.
- ``bytes`` / ``bytearray``: raw image bytes.
"""


def _to_bytes_and_name(file: FileInput, default_name: str = "image") -> Tuple[bytes, str]:
    """Normalize a FileInput to (bytes, filename) for httpx multipart."""
    if isinstance(file, (bytes, bytearray)):
        return bytes(file), default_name
    if isinstance(file, (str, Path)):
        path = Path(file)
        return path.read_bytes(), path.name
    raise TypeError(f"file must be path | bytes, got {type(file).__name__}")


def _multipart_files(
    file: FileInput,
    extra_files: Optional[List[FileInput]] = None,
) -> List[Tuple[str, Tuple[str, bytes, str]]]:
    """Build httpx-style files= argument for one or many uploads."""
    files: List[Tuple[str, Tuple[str, bytes, str]]] = []
    data, name = _to_bytes_and_name(file)
    files.append(("file", (name, data, "application/octet-stream")))
    if extra_files:
        for f in extra_files:
            d, n = _to_bytes_and_name(f)
            files.append(("files", (n, d, "application/octet-stream")))
    return files


def _multipart_batch(files_in: List[FileInput]) -> List[Tuple[str, Tuple[str, bytes, str]]]:
    """Build files= for /remove-batch (field name ``files``, repeated)."""
    out: List[Tuple[str, Tuple[str, bytes, str]]] = []
    for i, f in enumerate(files_in):
        data, name = _to_bytes_and_name(f, default_name=f"image-{i}")
        out.append(("files", (name, data, "application/octet-stream")))
    return out


def _form(data: Dict[str, Any]) -> Dict[str, str]:
    """Drop None values, stringify the rest, for httpx data= multipart fields."""
    out: Dict[str, str] = {}
    for k, v in data.items():
        if v is None:
            continue
        if isinstance(v, bool):
            out[k] = "true" if v else "false"
        else:
            out[k] = str(v)
    return out


def _resolve_token(token: Optional[str]) -> Optional[str]:
    """Resolve token from arg or KNOCKOUT_TOKEN env var."""
    if token:
        return token
    env = os.environ.get("KNOCKOUT_TOKEN", "").strip()
    return env or None


DEFAULT_BASE_URL = "https://useknockout--api.modal.run"
PUBLIC_BETA_TOKEN = "kno_public_beta_4d7e9f1a3c5b2e8d6a9f7c1b3e5d8a2f"
