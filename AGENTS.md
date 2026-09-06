# AZBrowser

Public identity: **Aziel Eliab** only.

This is a Phase 1 research-browser shell + Lamb Lens ethical search.
It is not Chromium, not AZ-OS, not Lumen, not AZInterface, and not AZMail.

AZMail is a sibling: https://github.com/AzielEliab/azmail
AZNet is a sibling functional pair (separate app): https://github.com/AzielEliab/aznet

**Dual surface is mandatory.** Human Worker chrome stays complete.
Backend MCP / OpenAPI / FragGate ops stay first-class. Do not ship UI-only.

Agent path is FragGate only:
`POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call`
with `slug=azbrowser`. Catalog MCP:
`POST https://aziel-runtime.vibelock.workers.dev/mcp`.
This Worker's `/mcp` is a pointer, not a second MCP. Human chrome uses
`/v1/{op}` (single-segment local ops). `/v1/fraggate/*` and
`/v1/runtime/*` PROXY to aziel-runtime — they are not local op names.

No receipt = no action.

Forks are welcome and always allowed. Apache-2.0.
