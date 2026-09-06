---
name: AZBrowser
description: >-
  Use when researching through AZBrowser — navigate preview, Lamb Lens
  ethical search, receipted airlock, tabs, AZNet side-net viewer.
  Pairing with sibling AZNet is required. Phase 1 research shell, not
  Chromium. Author Aziel Eliab.
---

# AZBrowser

Secure research browser / hardened investigation platform (Phase 1).
AZNet is a **sibling side-net** (https://github.com/AzielEliab/aznet).
AZBrowser **views** it and **requires pairing** to run. FragGate unlocks;
StaticClock times. AZNet branding here is the sidenet viewer — not a
second whitepaper fork.

Author: **Aziel Eliab** only.

**THIS IS:** browser-chrome UX + controlled fetch/proxy preview +
receipted airlock (`download → scan → scrub → verify → vault`) +
Lamb Lens ethical search + AZNet side-net viewer + append-only
integrity receipts.

**THIS IS NOT:** Chromium, Firefox, Safari, or Edge. Not AZ-OS, Lumen,
or AZInterface. Not an AZNet protocol implementation. AZMail is a
**sibling** (https://github.com/AzielEliab/azmail). AZNet is a
**sibling** (https://github.com/AzielEliab/aznet).

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
(same op names). `GET|POST /mcp` on this host is a **pointer**, not a
second MCP. AI / MCP path is FragGate only.

**Human UI stays on this Worker.** Agents display `display.title`,
`display.summary`, and `display.fields` in the AI client, then take the
next input. No technical MCP UI is required for the human.

Research ops (`navigate`, `ethical_search`, `airlock`, `scrub`) return
`PAIR_REQUIRED` until AZNet pair-status is true **and** FragGate unlocks
via StaticClock. `pair_status` and `sidenet_view` stay open so the gate
and viewer work.

## Ops (UI action = MCP / FragGate op)

| UI chrome | op |
|-----------|-----|
| Address Go / preview | `navigate` / `preview` |
| Lamb Lens search | `ethical_search` / `lamb_lens` / `search` |
| Side-net viewer | `sidenet_view` |
| Pair status | `pair_status` |
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
| POST | `/v1/{op}` | Human UI backend. Same ops as the table above. |
| POST | `/v1/runtime/call` | FragGate-shaped `{slug,op,payload}`. `azbrowser` is local; allowlisted siblings (incl. `staticclock`) proxy. |
| GET | `/v1/runtime/list` | Local ops + FragGate list pointer. |
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
  -d '{"slug":"azbrowser","op":"pair_status","payload":{}}'
curl -s -A 'Mozilla/5.0' -X POST https://azbrowser-download-tracker.vibelock.workers.dev/v1/sidenet_view \
  -H 'content-type: application/json' \
  -d '{}'
curl -s -A 'Mozilla/5.0' https://aziel-runtime.vibelock.workers.dev/v1/fraggate/list
```

## Local

```bash
curl -fsSL https://azbrowser-download-tracker.vibelock.workers.dev/install.sh | bash
azbrowser ui
azbrowser doctor
azbrowser pair-status
azbrowser sidenet
```

Then open http://127.0.0.1:8878 (this computer only).

## Honest banner

THIS IS: a Phase 1 research-browser shell that views sibling AZNet.
THIS IS NOT: a Chromium replacement, a VPN, AZ-OS, Lumen, AZInterface,
or an AZNet protocol fork. Pairing required. Author: Aziel Eliab only.

Apache-2.0. Forks are welcome and always allowed.

## Catalog + links

- Product homepage: https://azbrowser-download-tracker.vibelock.workers.dev/
- Agent door: `POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call` `{slug:azbrowser,op,payload}`
- FragGate: https://github.com/AzielEliab/fraggate
- Runtime: https://github.com/AzielEliab/aziel-runtime
- Library: https://www.azielcorpuslibrary.net/
- AZMail (sibling): https://github.com/AzielEliab/azmail
- AZNet (sibling side-net): https://github.com/AzielEliab/aznet
- AZNet Worker (expected): https://aznet-download-tracker.vibelock.workers.dev
- AZNet garden (expected): https://aznet-download-tracker.vibelock.workers.dev/garden
- StaticClock: https://github.com/AzielEliab/staticclock
- Pairing: docs/pair.md
- godlock.uk · https://www.azieleliab.com
- GitHub: https://github.com/AzielEliab/azbrowser
