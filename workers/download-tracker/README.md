# AZBrowser download tracker

Cloudflare Worker `azbrowser-download-tracker`.

URL pattern after deploy (workers.dev + account subdomain, same as sibling products):

`https://azbrowser-download-tracker.vibelock.workers.dev`

- `GET /` — complete browser-chrome UI (tabs, omnibox, Home sigil, AZNet, airlock, receipts) + counted views
- `GET /download` — counted tarball (HTTP 200 gzip, no 302)
- `GET /count` — `{views, downloads, total}`
- `GET /openapi.json` — first-class backend OpenAPI
- `GET|POST /mcp` — MCP docs + JSON-RPC tools/list and tools/call
- `GET /v1/*` — health/skill (does **not** increment downloads)
- `POST /v1/{op}` — same ops as UI chrome and FragGate slug `azbrowser`

KV binding `DOWNLOADS` (create `AZBROWSER_DOWNLOADS` on first deploy). Account `ac575a9b822bea2bed97d0ab73aed238`.

Human UI is this Worker. Agent / MCP path is FragGate:

`POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call` with
`{"slug":"azbrowser","op":"…","payload":{}}`

Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`.
This host also implements `/mcp` so the backend is first-class (not UI-only).
Catalog listing of `azbrowser` lands in a sibling aziel-runtime PR.

Author: Aziel Eliab. Apache-2.0.
