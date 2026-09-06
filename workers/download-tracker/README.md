# AZBrowser download tracker

Cloudflare Worker `azbrowser-download-tracker`.

URL pattern after deploy (workers.dev + account subdomain, same as sibling products):

`https://azbrowser-download-tracker.vibelock.workers.dev`

- `GET /` — complete browser-chrome UI (tabs, omnibox, Home sigil, AZNet, airlock, receipts) + counted views
- `GET /download` — counted tarball (HTTP 200 gzip, no 302)
- `GET /count` — `{views, downloads, total}`
- `GET /openapi.json` — documents ops; agents use FragGate
- `GET|POST /mcp` — pointer to FragGate (`slug=azbrowser`)
- `GET /v1/*` — health/skill (does **not** increment downloads)
- `POST /v1/{op}` — human UI backend; same ops FragGate will call

KV binding `DOWNLOADS` (create `AZBROWSER_DOWNLOADS` on first deploy). Account `ac575a9b822bea2bed97d0ab73aed238`.

Human UI is this Worker. Agent / MCP path is FragGate:

`POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call` with
`{"slug":"azbrowser","op":"…","payload":{}}`

Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`.
This host `/mcp` is a pointer, not a second MCP. Catalog listing of
`azbrowser` lands in a sibling aziel-runtime PR.

Author: Aziel Eliab. Apache-2.0.
