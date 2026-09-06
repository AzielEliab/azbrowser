# Contributing to AZBrowser

**Forks are first-class.** This project is Apache-2.0; you do not need
permission to fork, patch, or redistribute.

**Forks are welcome and always allowed.**

## How to run tests

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest -q
azbrowser doctor
```

Python 3.10+. Engine is stdlib only. pytest is the dev extra.

## Ground rules

1. **Not Chromium.** Do not claim a full browser engine. Preview is
   controlled fetch + sandbox iframe.
2. **Dual surface.** Every chrome action needs a matching FragGate / MCP
   / `/v1` op. Do not gut the human UI. Do not ship UI-only.
3. **No receipt = no action.** Mutating ops append a hash-chained receipt.
4. **AZNet refuses** doxxing, credential harvest, and malware lure.
5. **UI binds loopback only** for `azbrowser ui` (`127.0.0.1:8878`).
   No telemetry. No CDN.
6. **Do not mix the download tracker** with any other product's Worker
   or KV. Namespace `AZBROWSER_DOWNLOADS` only.
7. **Public identity is Aziel Eliab only.**
8. **Independence.** Do not import AZ-OS, Lumen, rebuild AZMail, or
   embed the AZNet protocol. AZNet is a sibling functional pair
   (https://github.com/AzielEliab/aznet). Optional documentation links
   are fine.
9. **Door vs local op.** `/v1/fraggate/*` and `/v1/runtime/*` PROXY to
   aziel-runtime. Local ops are `/v1/{op}` only. Never treat
   `fraggate/call` as a local op name.
10. New behavior needs a test that fails without the change.

## Where to change things

- Ethics / search / airlock / receipts / tabs / dispatch: `azbrowser/`
- Door path classifier: `azbrowser/door.py` + `workers/download-tracker/src/door.js`
- Worker engine (same ops): `workers/download-tracker/src/engine.js`
- OpenAPI / door proxy: `workers/download-tracker/src/runtime.js`
- Browser chrome: `workers/download-tracker/src/ui.js`
- Spec: `docs/whitepaper.md`
- Skill: `SKILL.md` (same text at Worker `GET /v1/skill`)
- Flutter: `mobile/`
- Isolated counter: `workers/download-tracker/`

## License of contributions

By submitting a change you agree it is licensed under Apache-2.0, the
same license as the rest of the tree. Keep the copyright lines honest.
Ship as Aziel Eliab.
