---
project: projects/useknockout-python
type: services
---

# Services

External hosted services this project depends on.

## useknockout background-removal API

- **What:** The remote HTTP API this SDK is a client for. Provides background
  removal and subject-aware image operations (replace background, mask, smart crop,
  shadow, sticker, outline, silhouette, studio shot, headshot, upscale, face restore,
  colorize, inpaint, compare, preview, estimate, health, stats).
- **Default endpoint:** `https://useknockout--api.modal.run` (hosted on
  [Modal](https://modal.com)). Overridable via the `base_url` constructor argument
  for self-hosted deployments.
- **Auth:** `Bearer` token, resolved from the `token=` argument, the
  `KNOCKOUT_TOKEN` environment variable, or a built-in public beta token (free,
  rate-limited).
- **Open source / self-hostable:** API code at `https://github.com/useknockout/api`
  (deployable with `modal deploy`).

## PyPI

- **What:** Python Package Index — the distribution channel for this SDK.
- **Package:** [`useknockout`](https://pypi.org/project/useknockout/)
- **Role:** Where the built wheel / sdist are published and from where users
  `pip install useknockout`.

---

Notes:
- **Modal** is the underlying compute platform that hosts the API, but it is consumed
  transitively through the useknockout API endpoint — the SDK does not talk to Modal
  directly.
- No analytics, logging, database, or other third-party hosted services are used by
  the SDK itself.
