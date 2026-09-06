# AZBrowser

Open-source **secure research browser / AZNet ethical search** — Phase 1.
Browser-chrome UX, receipted kernel, ingestion airlock. Not Chromium.

**Author:** Aziel Eliab only
**Date:** September 2026 · v0.1.0
**License:** [Apache-2.0](LICENSE)

> No receipt = no action.

See the spec: [docs/whitepaper.md](docs/whitepaper.md).
How to contribute: [CONTRIBUTING.md](CONTRIBUTING.md).

**Forks are welcome and always allowed.**

AZMail is a **sibling** product already live — optional deep-link only.
Do not rebuild it here: https://github.com/AzielEliab/azmail

AZ-OS / Lumen / AZInterface are **not** this product.

## Honest scope (read this)

v0.1 is a **research shell**. It cannot ship a Chromium binary. The
Worker looks like a real browser (tabs, omnibox, Back/Forward/Reload,
Home = everblooming sigil) and sandboxes navigation via controlled
fetch/proxy preview + receipted airlock + AZNet ethical search. It does
**not** replace the operator's OS browser.

## Dual surface (mandatory)

1. **Human UI** — Worker homepage is complete software: browser chrome,
   AZNet / Lamb Lens panel, airlock stages + hashes, append-only
   receipts, counted download. Black / gold / white. Humans stay here.
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

Worker `/v1/{op}` is the **human UI backend** (same ops as chrome).
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

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
azbrowser doctor
azbrowser ui
```

Open http://127.0.0.1:8878 (loopback only).

## One-click install

```bash
curl -fsSL https://azbrowser-download-tracker.vibelock.workers.dev/install.sh | bash
```

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
| `/v1/{op}` | Human UI backend — same ops FragGate will call |

- Homepage: [https://azbrowser-download-tracker.vibelock.workers.dev/](https://azbrowser-download-tracker.vibelock.workers.dev/)
- Direct tarball: [azbrowser-0.1.0.tar.gz](https://azbrowser-download-tracker.vibelock.workers.dev/download?asset=azbrowser-0.1.0.tar.gz)
- Sigil: [https://www.azielcorpuslibrary.net/sigil.png](https://www.azielcorpuslibrary.net/sigil.png)
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
| AZNet search panel | `POST /v1/ethical_search` (`lamb_lens` alias) | `ethical_search` |
| Airlock | `POST /v1/airlock` | `airlock` |
| New tab `+` | `POST /v1/tab_new` | `tab_new` |
| Tab click / × | `POST /v1/tab_switch` / `tab_close` | tabs |
| FragGate list | `GET /v1/runtime/list` | list/call pattern |

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

```bash
azbrowser version
azbrowser ui                 # 127.0.0.1:8878
azbrowser doctor
azbrowser search 'library'
azbrowser navigate https://www.azieleliab.com/
azbrowser airlock --content '<script>x</script>'
azbrowser receipts
azbrowser verify
```

## Tests

```bash
pip install -e ".[dev]"
python -m pytest -q
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
- FragGate: https://github.com/AzielEliab/fraggate
- Digital Library: https://www.azielcorpuslibrary.net/
- AZMail (sibling): https://github.com/AzielEliab/azmail
- godlock.uk
- https://www.azieleliab.com

## License

Apache-2.0. See [LICENSE](LICENSE).

Forks are welcome and always allowed.
