---
name: AZBrowser
description: >-
  Use when researching through AZBrowser — navigate preview,
  Lamb Lens ethical search, receipted airlock, tabs. Phase 1 research
  shell, not a Chromium replacement. Author Aziel Eliab.
---

# AZBrowser

Secure research browser / hardened investigation platform (Phase 1).
Lamb Lens is AZBrowser ethical search. AZNet is a separate product/engine;
pairing is order/token only — not a shared Phase-1 UI
(https://github.com/AzielEliab/aznet).

Author: **Aziel Eliab** only.

**THIS IS:** browser-chrome UX + controlled fetch/proxy preview +
receipted airlock (`download → scan → scrub → verify → vault`) +
Lamb Lens ethical search + append-only integrity receipts.

**THIS IS NOT:** Chromium, Firefox, Safari, or Edge. Not AZ-OS, Lumen,
AZInterface, or AZNet. Not an AZNet protocol implementation. AZMail is a
**sibling** (https://github.com/AzielEliab/azmail). AZNet is a
**sibling** (https://github.com/AzielEliab/aznet) — pairing order/token only.

Always send `User-Agent: Mozilla/5.0`. Cloudflare Workers may 403 an empty agent.

**Agent path is FragGate only.** MCP / agents call aziel-runtime.
Prefer:

```
POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call
{"slug":"azbrowser","op":"<op>","payload":{}}
```

Same door as the `fraggate_call` MCP tool (`slug=azbrowser`). Kernel:
https://github.com/AzielEliab/fraggate. Catalog listing lands in a
sibling aziel-runtime PR. Human chrome uses this Worker's `/v1/{op}`
(single-segment local ops). `/v1/fraggate/*`, `/v1/runtime/*`, and
`/v1/mesh/*` PROXY to aziel-runtime. `GET|POST /mcp` on this host is a
**pointer**, not a second MCP. AI / MCP path is FragGate only. Catalog
MCP `mesh_*` + FragGate `slug=mesh` is the agent mesh door. Suite mesh
default **OFF**. QNM-BUILD-1.0 rollup live|locked|isolated. QNS-CD-1.0
(photon QNS1 packet transfer) is a hub cite / Worker mesh cross-map
only — local qnsd is [qnm-node](https://github.com/AzielEliab/qnm-node);
runtime cites live in [aziel-runtime](https://github.com/AzielEliab/aziel-runtime).
AZInterface holds pair custody. Not a Softwares-tab product. No public
qnsd proxy. No Node Gate. No auto-heal. Not anonymity. Author: Aziel Eliab only.

**Human UI stays on this Worker.** Agents display `display.title`,
`display.summary`, and `display.fields` in the AI client, then take the
next input. No technical MCP UI is required for the human.

## Ops (UI action = MCP / FragGate op)

| UI chrome | op |
|-----------|-----|
| Address Go / preview | `navigate` / `preview` |
| Lamb Lens search | `ethical_search` / `lamb_lens` / `lamb_lens_search` / `search` |
| Back / Forward / Reload | `back` `forward` `reload` |
| Home (everblooming sigil) | `home` |
| New / close / switch tab | `tab_new` `tab_close` `tab_switch` `tab_list` |
| Airlock panel | `airlock` `airlock_status` |
| Receipts list | `receipts` `receipt` `receipt_verify` |
| Ethics gate | `ethics_gate` |
| HTML scrub | `scrub` |
| Liveness / skill | `health` `skill` |

No receipt = no action. Every mutating op appends a hash-chained receipt.

## Human Worker (not a second agent brand)

Host: `https://azbrowser-download-tracker.vibelock.workers.dev`

| Method | Path | What |
|--------|------|------|
| GET | `/` | Complete browser chrome. Increments views. |
| GET | `/v1/health` | Liveness. Does not increment downloads. |
| GET | `/v1/skill` | This markdown. |
| GET | `/openapi.json` | OpenAPI 3.1 — documents ops; agents use FragGate. |
| GET/POST | `/mcp` | Pointer to FragGate (`slug=azbrowser`). Not a second MCP. |
| POST | `/v1/{op}` | Human UI backend. Single-segment local ops only. |
| GET | `/v1/fraggate/list` | PROXY to aziel-runtime FragGate list. |
| POST | `/v1/fraggate/call` | PROXY to aziel-runtime FragGate call. |
| GET/POST | `/v1/runtime/*` | PROXY aliases (`list`/`call` → FragGate). |
| GET | `/v1/mesh` | PROXY suite mesh status. Default OFF. QNS-CD-1.0 cross-map in payload. |
| GET | `/v1/mesh/nodes` | PROXY Live Nodes (5-minute presence). |
| POST | `/v1/mesh/{enable,disable,join,heartbeat,leave,broadcast}` | PROXY. No auto-heal. Not AnonBroadcast. |
| GET | `/download` | Counted tarball. |
| GET | `/count` | `{views, downloads, total}` |

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude
(Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot /
Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence
surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other
MCP/OpenAPI-capable assistants — **through FragGate only**.

## How to call (Mozilla/5.0)

```bash
curl -s -A 'Mozilla/5.0' -X POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call \
  -H 'content-type: application/json' \
  -d '{"slug":"azbrowser","op":"ethical_search","payload":{"q":"FragGate kernel"}}'
curl -s -A 'Mozilla/5.0' -X POST https://azbrowser-download-tracker.vibelock.workers.dev/v1/navigate \
  -H 'content-type: application/json' \
  -d '{"url":"https://www.azieleliab.com/"}'
curl -s -A 'Mozilla/5.0' https://aziel-runtime.vibelock.workers.dev/v1/fraggate/list
curl -s -A 'Mozilla/5.0' -X POST https://azbrowser-download-tracker.vibelock.workers.dev/v1/fraggate/call \
  -H 'content-type: application/json' \
  -d '{"slug":"azbrowser","op":"health","payload":{}}'
```

## Local

```bash
curl -fsSL https://azbrowser-download-tracker.vibelock.workers.dev/install.sh | bash
azbrowser ui
azbrowser doctor
```

Then open http://127.0.0.1:8878 (this computer only).

## Honest banner

THIS IS: a Phase 1 research-browser shell with Lamb Lens ethical search.
THIS IS NOT: a Chromium replacement, a VPN, AZ-OS, Lumen, AZInterface,
or AZNet. AZNet is a separate product/engine; pairing is order/token
only — not a shared Phase-1 UI. AZMail is a separate repo. Suite mesh
is presence + QNM live|locked|isolated (default OFF) plus QNS-CD-1.0
photon QNS1 cross-map (local qnm-node; no public qnsd proxy) — not an
anonymity network, not a Node Gate, not auto-heal, not a Softwares-tab
product. Author: Aziel Eliab only.

Apache-2.0. Forks are welcome and always allowed.

## Catalog + links

- Product homepage: https://azbrowser-download-tracker.vibelock.workers.dev/
- Agent door: `POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call` `{slug:azbrowser,op,payload}`
- FragGate: https://github.com/AzielEliab/fraggate
- Runtime: https://github.com/AzielEliab/aziel-runtime
- QNM local node + qnsd: https://github.com/AzielEliab/qnm-node
- AZInterface (pair custody): https://github.com/AzielEliab/azinterface
- Library: https://www.azielcorpuslibrary.net/
- AZMail (sibling): https://github.com/AzielEliab/azmail
- AZNet (sibling functional pair): https://github.com/AzielEliab/aznet
- godlock.uk · https://www.azieleliab.com
- GitHub: https://github.com/AzielEliab/azbrowser
