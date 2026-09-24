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
| Home | `home` |
| New / close / switch tab | `tab_new` `tab_close` `tab_switch` `tab_list` |
| Airlock panel | `airlock` `airlock_status` |
| Receipts list | `receipts` `receipt` `receipt_verify` |
| Ethics gate | `ethics_gate` |
| HTML scrub | `scrub` |
| Liveness / skill | `health` `skill` |
| Mesh resolve | `resolve` |
| Capability grant / check | `capability_grant` `capability_check` |
| Local app tab | `local_app` |
| Peer block / unblock | `peer_block` `peer_unblock` |
| Island mode | `island_mode` |
| Local trust | `trust` |
| Domain slots | `slots` |
| Design mode | `design_mode` |

No receipt = no action. Every mutating op appends a hash-chained receipt.

## Local-first edge mesh

AZBrowser is the browser for the local-first edge mesh. AZNet stays a
separate Software. Pairing is resolve-and-connect only.

- `<handle>.aziel` resolves through the AZNet resolver adapter
  (`POST http://127.0.0.1:8771/v1/resolve`) against the local mesh ledger,
  then the local shell asks qnm-node (`POST http://127.0.0.1:8891/local/connect`)
  for direct, LAN, or relay. `.aziel` is not an ICANN TLD. Ordinary browsers
  do not resolve it.
- `.az` is Azerbaijan's country domain and stays on normal DNS and standard
  TLS, except the operator Cap-7 / AZ.* allowlist (`azgrid.az`, `azcloak.az`,
  `azvault.az`, `azshift.az`, `AZ.AzielEliab.AZ`, `AZ.Godlock.AZ`,
  `AZ.AzielCorpusLibrary.AZ`, `AZ.HeDidntJump.AZ`). Cloak names
  `azbooth.az`, `azflag.az`, and `azstandby.az` are not on that list.
- Mesh pages, scripts, and modules must match the handle key's signed
  content hash. Mismatch, an unsigned module, or tampered bytes return
  `FG-GATE-REFUSE` plus the reason. The address bar shows the verified
  owner handle, or that refusal. There is no identity-lock chrome.
- Mesh and local apps (qnm-node `127.0.0.1:8891`, local FragGate
  `127.0.0.1:8787`) get no outside network, no cross-origin fetch, no
  storage outside their origin, and no local files unless a capability
  grant receipt allows that exact resource. This is default deny, not
  tracker detection. The normal web keeps Lamb Lens plus the existing
  HTML scrub. This shell does not execute scripts.
- Handle keys never leave the local node. A payload that contains a
  private key is refused.
- Only a FINAL name (aged, and witnessed by at least two other handles)
  can verify. A PENDING name is shown as pending and is not a verified
  site. An equivocating handle, a stale seq, or a broken prev-hash is
  `FG-GATE-REFUSE`.
- Mesh downloads and modules enter the airlock before they are shown.
  This process has no ClamAV and no YARA (`scanner: absent`). Bytes stay
  in quarantine unless the operator passes `operator_override: true`.
  This shell still does not execute scripts.
- `peer_block` cuts off one handle on this node. `island_mode` drops
  this node's mesh peers and leaves local apps and normal DNS running.
  Rejoin appends a receipt and does not rewrite earlier ones. There is
  no network-wide cutoff. `trust` is a local view (chain age, witnessed
  heartbeats, hash matches, vouches, equivocation). It is not a public ranking.
- The first visit is night: black background, white text. A later choice
  of day or Aziel mode is remembered on this machine. Aziel mode is black,
  royal purple, and gold. The new-tab page is the sigil, one search box,
  and quick links. Honest limits sit in Settings under About.
- `slots` lists the four reserved hub mirrors and three user names.
  MirageGrid Cap-7 names are a separate layer and stay unchanged.
- `design_mode` opens a local tab on the loopback shell. The hosted
  Worker refuses it (`design_mode_local_only`). Publishing and the
  designer stay on qnm-node. Keys stay on the node.
- An isolated handle returns `FG-GATE-REFUSE` and a policy page. Peer
  bytes are not loaded. Isolation does not delete local data.

Lamb Lens order is Service, then Clarity, then Peace. A feature that
sacrifices one of the three fails review. Service is one request for a
local app, a mesh name, or an ordinary web address. Clarity puts a
plain reason and a next step on every refusal, and keeps verified,
pending, and isolated handles distinct. Peace means no ads, no
tracking, no telemetry, and no notification spam. Capability grants
stay rare. MirageGrid Cap-7 decoys stay separate from the four reserved
hub mirrors and three user slots.

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
