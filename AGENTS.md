# AZBrowser

Public identity: **Aziel Eliab** only.

This is a Phase 1 research-browser shell + AZNet ethical search.
It is not Chromium, not AZ-OS, not Lumen, not AZInterface, and not AZMail.

AZMail is a sibling: https://github.com/AzielEliab/azmail

**Dual surface is mandatory.** Human Worker chrome stays complete.
Backend MCP / OpenAPI / FragGate ops stay first-class. Do not ship UI-only.

Agent path is FragGate only:
`POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call`
with `slug=azbrowser`. Catalog MCP:
`POST https://aziel-runtime.vibelock.workers.dev/mcp`.
This Worker's `/mcp` is a pointer, not a second MCP. Human chrome uses `/v1`.

No receipt = no action.

Forks are welcome and always allowed. Apache-2.0.
