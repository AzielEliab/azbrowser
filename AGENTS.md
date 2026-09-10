# AZBrowser

Public identity: **Aziel Eliab** only.

This is a Phase 1 research-browser shell + Lamb Lens ethical search.
It is not Chromium, not AZ-OS, not Lumen, not AZInterface, not AZMail,
and not AZNet. AZNet is a separate product/engine; pairing is
order/token only — not a shared Phase-1 UI.

AZMail is a sibling: https://github.com/AzielEliab/azmail
AZNet is a sibling functional pair (separate app): https://github.com/AzielEliab/aznet

**Dual surface is mandatory.** Human Worker chrome stays complete.
Backend MCP / OpenAPI / FragGate ops stay first-class. Do not ship UI-only.

Agent path is FragGate only:
`POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call`
with `slug=azbrowser`. Catalog MCP:
`POST https://aziel-runtime.vibelock.workers.dev/mcp`.
This Worker's `/mcp` is a pointer, not a second MCP. Human chrome uses
`/v1/{op}` (single-segment local ops). `/v1/fraggate/*`,
`/v1/runtime/*`, and `/v1/mesh/*` PROXY to aziel-runtime — they are not
local op names. Suite mesh default OFF. QNM rollup live|locked|isolated.
QNS-CD-1.0 (photon QNS1 packet transfer) is a hub cite / Worker mesh
cross-map only — local qnsd is https://github.com/AzielEliab/qnm-node;
runtime cites live in https://github.com/AzielEliab/aziel-runtime.
Not a Softwares-tab product. No public qnsd proxy.
No Node Gate. No auto-heal. Not anonymity.

No receipt = no action.

Forks are welcome and always allowed. Apache-2.0.
