---
project: projects/useknockout-python
type: techstack
---

# Tech Stack

## Language

- **Python** — `>=3.9` (tested/classified against 3.9, 3.10, 3.11, 3.12, 3.13).
  Uses `from __future__ import annotations` and `typing` generics for forward-compatible
  type hints. Package uses a `src/` layout (`src/useknockout/`).

## Runtime dependencies

| Dependency | Version | Purpose |
| --- | --- | --- |
| [`httpx`](https://www.python-httpx.org/) | `>=0.27.0` | HTTP transport for both the sync (`httpx.Client`) and async (`httpx.AsyncClient`) clients. Handles multipart file uploads, JSON bodies, query params, timeouts, and connection lifecycle. The **only** runtime dependency — there is no Pillow / numpy; the SDK moves raw bytes and lets the server do all image processing. |

## Dev / tooling dependencies

Installed via the `dev` optional-dependencies group (`pip install -e ".[dev]"`):

| Tool | Version | Purpose |
| --- | --- | --- |
| [`pytest`](https://docs.pytest.org/) | `>=8.0` | Test runner |
| [`pytest-asyncio`](https://pytest-asyncio.readthedocs.io/) | `>=0.23` | Async test support for the `AsyncKnockout` client |
| [`ruff`](https://docs.astral.sh/ruff/) | `>=0.6.0` | Linter / import sorter. Config in `pyproject.toml`: line length 100, target `py39`, rule sets `E`, `F`, `I`, `W`, `UP` |
| [`mypy`](https://mypy-lang.org/) | `>=1.10` | Static type checker (run against `src`) |

## Build & publish

| Tool | Role |
| --- | --- |
| [**Hatchling**](https://hatch.pypa.io/latest/) | Build backend (`[build-system]` → `hatchling.build`). Wheel target packages `src/useknockout`. |
| **PyPI** | Distribution target. Published as [`useknockout`](https://pypi.org/project/useknockout/). Built artifacts (`.whl` + `.tar.gz`) are present under `dist/`. |

Build with any PEP 517 frontend, e.g. `python -m build` or `hatch build`.

## External APIs

| API | Role |
| --- | --- |
| **useknockout background-removal API** | The remote service this SDK wraps. Default base URL `https://useknockout--api.modal.run`, runs on [Modal](https://modal.com), and is BiRefNet-powered. Authenticated via a `Bearer` token (`KNOCKOUT_TOKEN` env var, explicit arg, or a built-in public beta token). Open source and self-hostable (`base_url` is overridable). The API itself orchestrates ML models — BiRefNet (segmentation), Swin2SR / Real-ESRGAN (upscale), GFPGAN v1.4 (face restore), DDColor (colorize), and LaMa (inpaint) — but these run server-side and are **not** dependencies of this SDK. |

## Architecture notes

- Two parallel clients (`client.py` / `async_client.py`) with identical method
  signatures, sharing `_helpers.py` (multipart + form serialization, token resolution,
  base-URL/token constants) and `errors.py` (HTTP-status → typed-exception mapping).
- No code generation, no async/sync drift tooling — the two clients are maintained by hand.
