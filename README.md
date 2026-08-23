

<div align="center">

# 🥊 useknockout

**State-of-the-art background removal API — Python SDK.**

[![PyPI](https://img.shields.io/pypi/v/useknockout.svg)](https://pypi.org/project/useknockout/)
[![Python](https://img.shields.io/pypi/pyversions/useknockout.svg)](https://pypi.org/project/useknockout/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/useknockout?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/useknockout)

[Website](https://useknockout.com) ·
[API repo](https://github.com/useknockout/api) ·
[Node SDK](https://github.com/useknockout/node) ·
[React SDK](https://github.com/useknockout/react) ·
[CLI](https://github.com/useknockout/cli)

<img src="https://raw.githubusercontent.com/useknockout/api/main/docs/banner.png" width="800" alt="useknockout — background removal API for developers" />

*Background removal, 40× cheaper than remove.bg. MIT licensed. Self-hostable.*

</div>

---

## What it is

`useknockout` is the official Python SDK for the [useknockout](https://useknockout.com)
background-removal API — a BiRefNet-powered image service that runs on
[Modal](https://modal.com). Beyond plain cutouts, the API exposes a full suite of
subject-aware image operations: background replacement, drop shadows, stickers and
outlines, e-commerce / LinkedIn presets, super-resolution upscaling, face
restoration, colorization, silhouettes, and inpainting.

The SDK is a thin, fully-typed wrapper over [`httpx`](https://www.python-httpx.org/).
It ships both a synchronous client (`Knockout`) and an asynchronous one
(`AsyncKnockout`) with identical method signatures. Every image-returning method
hands you **raw bytes**, so you can pipe results straight to a file, `BytesIO`,
`PIL`, `numpy`, S3, or anywhere else bytes go. There are no heavy dependencies —
no Pillow, no numpy — just `httpx`.

## Install

```bash
pip install useknockout
```

Requires Python 3.9+. The only runtime dependency is `httpx>=0.27.0`.

## Quickstart

```python
from useknockout import Knockout

client = Knockout()  # uses public beta token by default
png = client.remove("photo.jpg")

with open("out.png", "wb") as f:
    f.write(png)
```

That's it. Free during the public beta.

## Async

`AsyncKnockout` mirrors the sync API one-for-one. Use it as an async context
manager so the underlying `httpx.AsyncClient` is closed cleanly:

```python
import asyncio
from useknockout import AsyncKnockout

async def main():
    async with AsyncKnockout() as client:
        png = await client.remove("photo.jpg")
        open("out.png", "wb").write(png)

asyncio.run(main())
```

The sync client is also a context manager (`with Knockout() as c: ...`) and exposes
`close()` / `aclose()` if you prefer to manage the lifecycle manually.

## Authentication

The client resolves its token by falling through three sources, in order:

1. The `token=` constructor argument
2. The `KNOCKOUT_TOKEN` environment variable
3. The public beta token (free, rate-limited — baked into the SDK)

```python
client = Knockout(token="kno_...")          # explicit
client = Knockout()                          # env var or public beta token
```

The token is sent as a `Bearer` header on every request. Get your own token by
emailing `troy@useknockout.com` (paid tier launches at $0.005/image — 40× cheaper
than remove.bg).

## Input types

Every method that takes an image accepts a `FileInput`, which is any of:

- `str` / `pathlib.Path` — a filesystem path the SDK reads for you
- `bytes` / `bytearray` — raw image bytes you already have in memory

```python
client.remove("photo.jpg")                   # path
client.remove(Path("photo.jpg"))             # Path
client.remove(open("photo.jpg", "rb").read())# bytes
```

## All endpoints

```python
from useknockout import Knockout

c = Knockout()

# --- Core background removal ---
c.remove("photo.jpg")                                  # returns PNG/WebP bytes
c.remove_url("https://example.com/photo.jpg")          # fetch + remove remote image
c.remove_batch(["a.jpg", "b.jpg", "c.jpg"])            # up to 10 files -> JSON
c.remove_batch_url(["https://...", "https://..."])     # up to 10 URLs -> JSON

# --- Replace background ---
c.replace_background("photo.jpg", bg_color="#000000")
c.replace_background("photo.jpg", bg_url="https://example.com/bg.jpg")

# --- Mask / crop ---
c.mask("photo.jpg")                                    # alpha mask only (grayscale PNG)
c.smart_crop("photo.jpg", padding=24)                  # crop to subject bbox + padding

# --- Effects ---
c.shadow("photo.jpg", shadow_blur=14, shadow_opacity=0.45)   # drop shadow
c.sticker("photo.jpg", stroke_width=20)                # WhatsApp-style thick outline
c.outline("photo.jpg", outline_color="#000000", outline_width=4)  # thin outline
c.silhouette("photo.jpg", subject_color="#7C3AED")     # two-tone silhouette portrait

# --- Presets ---
c.studio_shot("photo.jpg", aspect="1:1", shadow=True)  # e-commerce
c.studio_shot("photo.jpg", transparent=True)           # transparent bg (PNG)
c.studio_shot("photo.jpg", enhance=True)               # brightness + saturation lift
c.headshot("photo.jpg", bg_color="#FFFFFF")            # LinkedIn 4:5 portrait
c.headshot("photo.jpg", bg_blur=True, blur_radius=24)  # blurred original bg

# --- Enhancement ---
c.upscale("photo.jpg", scale=4, model="swin2sr")       # 2x/4x super-resolution
c.upscale("photo.jpg", model="realesrgan", face_enhance=True)  # legacy + GFPGAN
c.face_restore("portrait.jpg")                         # GFPGAN v1.4 face restoration
c.colorize("bw.jpg")                                   # DDColor colorization
c.inpaint("photo.jpg", bbox=(40, 40, 200, 150))        # LaMa inpainting

# --- Marketing ---
c.compare("photo.jpg")                                 # before/after side-by-side

# --- UX helpers ---
c.preview("photo.jpg", max_dim=512)                    # fast low-res preview (~80ms warm)
c.estimate("remove", width=1024, height=1024)          # predict latency + cost (no processing)

# --- Telemetry ---
c.health()                                             # service status + model info
c.stats()                                              # public usage counter
```

Most methods return raw image **bytes**. The batch endpoints (`remove_batch`,
`remove_batch_url`) and the telemetry / estimate endpoints (`health`, `stats`,
`estimate`) return parsed JSON (`dict`). Pipe image bytes to
`open(path, "wb").write(...)`, `BytesIO`, `PIL.Image.open(BytesIO(...))`, `numpy`,
S3 — anywhere bytes go.

### Endpoint reference

| Method | HTTP | Returns | Notes |
| --- | --- | --- | --- |
| `remove` | `POST /remove` | bytes | `format` is a query param |
| `remove_url` | `POST /remove-url` | bytes | JSON body `{url, format}` |
| `remove_batch` | `POST /remove-batch` | dict | up to 10 files; `format` is a query param |
| `remove_batch_url` | `POST /remove-batch-url` | dict | up to 10 URLs |
| `replace_background` | `POST /replace-bg` | bytes | `bg_color` or `bg_url` |
| `mask` | `POST /mask` | bytes | grayscale alpha mask |
| `smart_crop` | `POST /smart-crop` | bytes | `padding`, `transparent` |
| `shadow` | `POST /shadow` | bytes | configurable drop shadow |
| `sticker` | `POST /sticker` | bytes | thick stroke, transparent bg |
| `outline` | `POST /outline` | bytes | thin stroke, transparent bg |
| `silhouette` | `POST /silhouette` | bytes | two-tone; API ≥ v0.7.1 |
| `studio_shot` | `POST /studio-shot` | bytes | e-commerce preset |
| `headshot` | `POST /headshot` | bytes | LinkedIn 4:5 portrait |
| `upscale` | `POST /upscale` | bytes | 2x/4x; `swin2sr` or `realesrgan` |
| `face_restore` | `POST /face-restore` | bytes | GFPGAN v1.4 |
| `colorize` | `POST /colorize` | bytes | DDColor; API ≥ v0.7.0 |
| `inpaint` | `POST /inpaint` | bytes | LaMa; API ≥ v0.8.0 |
| `compare` | `POST /compare` | bytes | before/after side-by-side |
| `preview` | `POST /preview` | bytes | fast low-res preview |
| `estimate` | `POST /estimate` | dict | predict latency + cost |
| `health` | `GET /health` | dict | status + model info |
| `stats` | `GET /stats` | dict | public usage counter |

### Enhancement endpoints in detail

**`upscale`** — 2x or 4x super-resolution. `model="swin2sr"` (default) is sharper on
real photos; `model="realesrgan"` is the legacy backend, better on anime /
illustrations. `face_enhance=True` routes through GFPGAN (Real-ESRGAN backend only).
`scale` must be `2` or `4`; `model` must be `"swin2sr"` or `"realesrgan"` — both are
validated client-side and raise `ValueError` otherwise.

**`face_restore`** — GFPGAN v1.4 portrait restoration for blurry / damaged / low-res
faces. By default the background is preserved as-is; `bg_enhance=True` also upscales
the background 2x via Real-ESRGAN. `only_center_face=True` restores just the most
prominent face (faster).

**`colorize`** — DDColor (Apache-2.0) colorization via a ConvNeXt-Large backbone
(single feed-forward, ~500ms warm). Works on B&W or color input — color images are
converted to grayscale internally first, making round-trip recoloring easy.

**`inpaint`** — LaMa-based inpainting with three auto-detected modes:

```python
c.inpaint("photo.jpg", mask="mask.png")             # user-supplied mask
c.inpaint("photo.jpg", bbox=(x, y, w, h))           # rectangular region
c.inpaint("photo.jpg")                              # auto-subject (BiRefNet, inverted)
```

`dilation` (0–32, default 8) expands the mask before LaMa runs to reduce ghost
outlines.

## Errors

All errors inherit from `KnockoutError`. The SDK maps HTTP status codes to typed
subclasses, and wraps transport-level failures (`httpx.RequestError`) as a base
`KnockoutError` with `code="unknown"`.

```python
from useknockout import Knockout
from useknockout.errors import (
    AuthError,           # 401 / 403
    BadRequestError,     # 400
    PayloadTooLargeError,# 413 (image too large)
    RateLimitError,      # 429
    ServerError,         # 5xx
    KnockoutError,       # base class / network errors
)

try:
    png = client.remove("photo.jpg")
except AuthError:
    ...  # bad token
except RateLimitError:
    ...  # back off
except KnockoutError as e:
    print(f"{e.code} ({e.status}): {e.message}")
```

Each `KnockoutError` carries three attributes: `status` (HTTP code, or `None` for
transport errors), `code` (a short machine-readable category like `"auth"` or
`"rate_limit"`), and `message` (human-readable detail, taken from the response body
when available).

## Configuration

| Constructor arg | Default | Purpose |
| --- | --- | --- |
| `token` | env var → public beta token | API token, sent as `Bearer` header |
| `base_url` | `https://useknockout--api.modal.run` | API base URL (override for self-hosted) |
| `timeout` | `60.0` | per-request timeout in seconds |

| Environment variable | Purpose |
| --- | --- |
| `KNOCKOUT_TOKEN` | API token, used when `token=` is not passed |

## Self-host

The API is open source and runs on Modal. Deploy your own copy:

```bash
git clone https://github.com/useknockout/api
cd api
modal deploy main.py
```

Then point the SDK at your deployment:

```python
client = Knockout(token="your-token", base_url="https://your-deploy.modal.run")
```

## Project structure

```
useknockout-python/
├── pyproject.toml              # hatchling build, deps, ruff config
├── README.md
├── LICENSE                     # MIT
├── dist/                       # built wheel + sdist artifacts
└── src/
    └── useknockout/
        ├── __init__.py         # public exports (Knockout, AsyncKnockout, errors)
        ├── _version.py         # __version__
        ├── client.py           # synchronous Knockout client
        ├── async_client.py     # asynchronous AsyncKnockout client
        ├── errors.py           # KnockoutError hierarchy + raise_for_status
        └── _helpers.py         # multipart/form helpers, token resolution, constants
```

The package uses a `src/` layout and is built with [Hatchling](https://hatch.pypa.io/).
Both clients share `_helpers.py` (multipart construction, form serialization, token
resolution) and `errors.py` (status-to-exception mapping), keeping the sync and async
surfaces in lockstep.

## Development

```bash
pip install -e ".[dev]"     # installs pytest, pytest-asyncio, ruff, mypy
ruff check .                # lint (line length 100; E, F, I, W, UP rules)
mypy src                    # type-check
pytest                      # run tests
```

## Notes

- **No heavy deps.** `httpx` is the only runtime dependency. Image manipulation
  happens server-side; the SDK just moves bytes.
- **Bytes in, bytes out.** Image-returning methods give you raw bytes — no implicit
  Pillow / numpy conversion, so you stay in control of the output pipeline.
- **Sync + async parity.** `Knockout` and `AsyncKnockout` have identical method
  signatures; switch by adding/removing `await`.
- **API version gating.** Some methods require a minimum API version: `colorize`
  needs API ≥ v0.7.0, `silhouette` ≥ v0.7.1, `inpaint` ≥ v0.8.0. The default
  hosted endpoint is kept current.
- **`format` quirk.** `remove` and `remove_batch` pass `format` as a **query**
  parameter (the API reads it there), while form-based endpoints send it in the
  multipart body. The SDK handles this for you.

## License

MIT. Use it however you want.
