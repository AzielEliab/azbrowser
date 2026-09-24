# AZBrowser

A local research browser for search, tabs, and `.aziel` names.

**Author:** Aziel Eliab only
**Version:** 0.1.0
**License:** [Apache-2.0](LICENSE)

Forks are welcome and always allowed.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate && pip install -e .
azbrowser ui
```

Open http://127.0.0.1:8878/

Type a search, a `.aziel` name, or a web address, then press Go.
Airlock, mesh, slots, and design mode are under Advanced.

## One-click install

```bash
curl -fsSL https://azbrowser-download-tracker.vibelock.workers.dev/install.sh | bash
```

Then run `azbrowser ui` and open http://127.0.0.1:8878/

## Notes

Version 0.1.0 is a research shell: tabs, an address bar, a sandboxed preview, a receipted airlock, and Lamb Lens search. The local app listens on 127.0.0.1. It does not ship a Chromium binary.

`.aziel` names resolve in this shell. `.aziel` is not an ICANN registration. Handle keys stay on this machine. AZMail and AZNet are separate programs: https://github.com/AzielEliab/azmail and https://github.com/AzielEliab/aznet

See [docs/FED-MESH-BROWSER-1.0.md](docs/FED-MESH-BROWSER-1.0.md) and [docs/whitepaper.md](docs/whitepaper.md).
How to contribute: [CONTRIBUTING.md](CONTRIBUTING.md).

No receipt = no action.

## Lamb Lens

AZBrowser follows Lamb Lens under all conditions, in this order:
**Service, then Clarity, then Peace.** A feature that sacrifices one of
the three fails review.

- **Service.** Do what the person asked, in one request. Local apps and
  mesh names open from that request, and ordinary web addresses keep
  working.
- **Clarity.** Verified handles, pending names, and isolated handles
  look different. Every refusal (`FG-GATE-REFUSE`, an ethics refusal, a
  blocked capability) says what happened and what to do next. Settings
  are on the page. There is no hidden switch.
- **Peace.** No ads, no tracking, no telemetry, and no notification
  spam. Capability grants are rare, receipted, and specific.

The live MirageGrid global Cap-7 decoys (`azbooth.az`, `azflag.az`,
`azstandby.az`) stay a separate layer from the per-node slots: four
reserved hub mirrors plus three user domains.

## Dual surface (mandatory)

1. **Human UI** — Worker homepage is complete software: browser chrome,
   AZNet / Lamb Lens panel, airlock stages + hashes, append-only
   receipts, counted download. Night (black / white), day, and Aziel
   mode (gold, black, royal purple). Humans stay here.
2. **Agent / MCP — FragGate only.** There is no separate AZBrowser MCP
   outside the door. Catalog door:

```bash
curl -s -A 'Mozilla/5.0' -X POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call \
  -H 'content-type: application/json' \
  -d '{"slug":"azbrowser","op":"ethical_search","payload":{"q":"FragGate kernel"}}'
```

MCP clients already on aziel-runtime call `fraggate_call` with
`slug=azbrowser`. Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`.
Catalog listing lands in a sibling runtime PR.

Worker `/v1/{op}` is the **human UI backend** (single-segment local ops).
`/v1/fraggate/*`, `/v1/runtime/*`, and `/v1/mesh/*` **PROXY** to
aziel-runtime (`/v1/fraggate/list`, `/v1/fraggate/call`, `/v1/mesh`, …).
They are not local ops. Suite mesh default **OFF**. QNM rollup
live|locked|isolated. QNS-CD-1.0 (photon QNS1 packet transfer) is a
hub cite / Worker mesh cross-map only — local qnsd lives in
[qnm-node](https://github.com/AzielEliab/qnm-node); runtime cites live
in [aziel-runtime](https://github.com/AzielEliab/aziel-runtime). Not a
Softwares-tab product. No public qnsd proxy. No Node Gate. No auto-heal.
Not anonymity.
`GET|POST /mcp` and `/openapi.json` document those ops and **point at
FragGate** — they are not a second agent brand.

Agents display `display.title`, `display.summary`, and `display.fields`
in chat, then take the next input. No technical MCP UI is required for
the human.

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude
(Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot /
Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence
surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other
MCP/OpenAPI-capable assistants.

## Counted download (Cloudflare Worker)

**This is the counted download.** GitHub releases exist as a mirror.
The Worker serves the gzip itself (HTTP 200, no 302 to GitHub).

Worker name: `azbrowser-download-tracker`

URL pattern (same as sibling Aziel Eliab products):

`https://azbrowser-download-tracker.vibelock.workers.dev`

| Path | What |
|------|------|
| `/` | Complete browser chrome + views |
| `/download` | Counted tarball |
| `/count` | `{views, downloads, total}` |
| `/openapi.json` | OpenAPI 3.1 (docs; agents use FragGate) |
| `/mcp` | Pointer to FragGate (`slug=azbrowser`) |
| `/v1/{op}` | Human UI backend — single-segment local ops only |
| `/v1/fraggate/*` | PROXY to aziel-runtime FragGate door |
| `/v1/runtime/*` | PROXY aliases (`list`/`call` → `/v1/fraggate/list`/`call`) |
| `/v1/mesh/*` | PROXY to aziel-runtime suite mesh (default OFF; QNM live / locked / isolated; QNS-CD-1.0 cross-map cite; no public qnsd proxy) |

- Homepage: [https://azbrowser-download-tracker.vibelock.workers.dev/](https://azbrowser-download-tracker.vibelock.workers.dev/)
- Direct tarball: [azbrowser-0.1.0.tar.gz](https://azbrowser-download-tracker.vibelock.workers.dev/download?asset=azbrowser-0.1.0.tar.gz)
- Sigil: [/sigil.png](https://azbrowser-download-tracker.vibelock.workers.dev/sigil.png)
- Cite: [cite.json](https://azbrowser-download-tracker.vibelock.workers.dev/cite.json) — Eliab, Aziel. (2026). AZBrowser 0.1.0 [Software]. Apache-2.0. Do not invent a DOI.

Isolated counter: Worker `azbrowser-download-tracker`, KV `AZBROWSER_DOWNLOADS`. `/v1` and `/mcp` do not increment downloads.

## Software tabs (parent listing)

Once this Worker is live, AZBrowser is listed on:

- https://www.azielcorpuslibrary.net/software
- https://godlock.uk/software
- https://www.azieleliab.com (Software section)

Parent lists after deploy. Expected URL:
`https://azbrowser-download-tracker.vibelock.workers.dev/`

## Chrome button checklist

Every control calls a real `/v1` handler (same op agents call). No dead buttons.

| Button | Handler | Op |
|--------|---------|-----|
| Back | `POST /v1/back` | `back` |
| Forward | `POST /v1/forward` | `forward` |
| Reload | `POST /v1/reload` | `reload` |
| Home (sigil) | `POST /v1/home` | `home` |
| Go / Enter | `POST /v1/navigate` or `/v1/ethical_search` | `navigate` / `ethical_search` |
| Lamb Lens search | `POST /v1/ethical_search` (`lamb_lens` alias) | `ethical_search` |
| Airlock | `POST /v1/airlock` | `airlock` |
| New tab `+` | `POST /v1/tab_new` | `tab_new` |
| Tab click / × | `POST /v1/tab_switch` / `tab_close` | tabs |
| FragGate list | `GET /v1/fraggate/list` | PROXY to aziel-runtime |
| FragGate call | `POST /v1/fraggate/call` | PROXY to aziel-runtime |
| Live Nodes strip | `GET /v1/mesh` · `GET /v1/mesh/nodes` | PROXY to aziel-runtime (default OFF; QNS-CD-1.0 cross-map in payload) |
| Resolve | `POST /v1/resolve` | `resolve` |
| Capability grant / check | `POST /v1/capability_grant` · `/v1/capability_check` | receipted sandbox |
| Local app | `POST /v1/local_app` | `local_app` |
| Promote quarantined mesh bytes | `POST /v1/navigate` with `operator_override: true` | explicit operator override; scanner stays absent |
| Island / block peer / trust | `POST /v1/island_mode` · `/v1/peer_block` · `/v1/trust` | this node only; no network-wide cutoff |
| Domain slots | `POST /v1/slots` | 4 reserved hub mirrors + 3 user names |
| Design mode | `POST /v1/design_mode` | local tab on the loopback shell; hosted Worker refuses |
| Day / Night / Aziel | chrome only | night on first run; later choice is remembered |
| Mesh enable / disable / join / leave | `POST /v1/mesh/{op}` | PROXY to suite mesh; not an edge-mesh cutoff |

Prove locally (after `pip install -e ".[dev]"`):

```bash
azbrowser doctor
azbrowser call home
azbrowser call ethical_search --payload '{"q":"FragGate"}'
azbrowser call navigate --payload '{"url":"https://www.azieleliab.com/"}'
azbrowser call airlock --payload '{"content":"<p>hi</p>","filename":"n.html"}'
azbrowser call tab_new
azbrowser call back
azbrowser verify
```

## CLI

People get short text. Add `--json` for the same machine payload.

```bash
azbrowser                     # welcome and the next step
azbrowser --help
azbrowser ui                  # prints: Open http://127.0.0.1:8878/
azbrowser doctor
azbrowser search library
azbrowser navigate https://www.azieleliab.com/
azbrowser --json health
```

Advanced commands stay available: `back`, `forward`, `reload`, `lamb-lens`, `airlock`, `receipts`, `verify`, `ethics`, `ops`, `version`, and `call`.

## Tests

```bash
pip install -e ".[dev]"
python -m pytest -q
node tests/test_worker_engine.mjs
node tests/test_worker_door.mjs
node tests/test_worker_mesh.mjs
azbrowser doctor
```

## iPhone & Android

Flutter sources: [`mobile/`](mobile/). Application id `com.azieeliab.azbrowser`.
Offline. No analytics. Dark matte / gold.

```bash
cd mobile
flutter create --org com.azieeliab --project-name azbrowser .
flutter pub get
flutter run
```

## Layout

```
azbrowser/          library (ethics, search, airlock, receipts, tabs, engine, cli)
tests/              pytest
docs/               Phase 1 whitepaper
workers/download-tracker/   Cloudflare Worker azbrowser-download-tracker
mobile/             Flutter scaffold
SKILL.md            agent skill (also GET /v1/skill)
```

## Cross-links (optional, not required)

- Runtime: https://github.com/AzielEliab/aziel-runtime · https://aziel-runtime.vibelock.workers.dev/
- QNM local node + qnsd: https://github.com/AzielEliab/qnm-node (QNS-CD-1.0 photon QNS1; not hosted here)
- AZInterface (pair custody): https://github.com/AzielEliab/azinterface
- FragGate: https://github.com/AzielEliab/fraggate
- Digital Library: https://www.azielcorpuslibrary.net/
- AZMail (sibling): https://github.com/AzielEliab/azmail
- AZNet (sibling functional pair): https://github.com/AzielEliab/aznet
- godlock.uk
- https://www.azieleliab.com

## License

Apache-2.0. See [LICENSE](LICENSE).

Forks are welcome and always allowed.
