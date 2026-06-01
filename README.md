<div align="center">

# 🥊 useknockout

**State-of-the-art background removal API — Python SDK.**

[![PyPI](https://img.shields.io/pypi/v/useknockout.svg)](https://pypi.org/project/useknockout/)
[![Python](https://img.shields.io/pypi/pyversions/useknockout.svg)](https://pypi.org/project/useknockout/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[Website](https://useknockout.com) ·
[API repo](https://github.com/useknockout/api) ·
[Node SDK](https://github.com/useknockout/node) ·
[React SDK](https://github.com/useknockout/react) ·
[CLI](https://github.com/useknockout/cli)

<img src="https://raw.githubusercontent.com/useknockout/api/main/docs/banner.png" width="800" alt="useknockout — background removal API for developers" />

*Background removal, 40× cheaper than remove.bg. MIT licensed. Self-hostable.*

</div>

---

## Install

```bash
pip install useknockout
```

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

```python
import asyncio
from useknockout import AsyncKnockout

async def main():
    async with AsyncKnockout() as client:
        png = await client.remove("photo.jpg")
        open("out.png", "wb").write(png)

asyncio.run(main())
```

## Authentication

The client falls back through three sources in order:

1. The `token=` argument
2. The `KNOCKOUT_TOKEN` environment variable
3. The public beta token (free, rate-limited, in the README of the API repo)

Get your own token by emailing `troy@useknockout.com` (paid tier launches at $0.005/image — 40× cheaper than remove.bg).

## All endpoints

```python
from useknockout import Knockout

c = Knockout()

# Remove background
c.remove("photo.jpg")                                  # returns PNG bytes
c.remove_url("https://example.com/photo.jpg")
c.remove_batch(["a.jpg", "b.jpg", "c.jpg"])            # up to 10
c.remove_batch_url(["https://...", "https://..."])

# Replace background
c.replace_background("photo.jpg", bg_color="#000000")
c.replace_background("photo.jpg", bg_url="https://example.com/bg.jpg")

# Mask only
c.mask("photo.jpg")                                    # returns grayscale PNG

# Crop to subject
c.smart_crop("photo.jpg", padding=24)

# Effects
c.shadow("photo.jpg", shadow_blur=14, shadow_opacity=0.45)
c.sticker("photo.jpg", stroke_width=20)                # WhatsApp-style
c.outline("photo.jpg", outline_color="#000000", outline_width=4)

# Presets
c.studio_shot("photo.jpg", aspect="1:1", shadow=True)  # e-commerce
c.studio_shot("photo.jpg", transparent=True)           # transparent bg (PNG)
c.headshot("photo.jpg", bg_color="#FFFFFF")            # LinkedIn 4:5 portrait
c.headshot("photo.jpg", bg_blur=True, blur_radius=24)  # blurred original bg

# Marketing
c.compare("photo.jpg")                                 # before/after side-by-side

# UX helpers
c.preview("photo.jpg", max_dim=512)                    # ~80ms warm
c.estimate("remove", width=1024, height=1024)          # predict latency + cost

# Telemetry
c.health()
c.stats()                                              # public usage counter
```

Every method that returns an image returns raw bytes. Pipe to `open(path, "wb").write(...)`, `BytesIO`, `PIL.Image.open(BytesIO(...))`, `numpy`, S3 — anywhere bytes go.

## Errors

All errors inherit from `KnockoutError`:

```python
from useknockout import Knockout
from useknockout.errors import (
    AuthError,           # 401 / 403
    BadRequestError,     # 400
    PayloadTooLargeError,# 413 (>25 MB)
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

## License

MIT. Use it however you want.
