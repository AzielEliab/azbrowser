# AZBrowser Phase 1 — Secure Research Browser / AZNet

**Author:** Aziel Eliab only
**Software:** AZBrowser 0.1.0
**License:** Apache-2.0
**Date:** September 2026

## Abstract

AZBrowser is a **secure research browser** and hardened investigation
platform. Phase 1 ships a **browser-chrome UX** (not a Chromium binary)
with a receipted security kernel, an ingestion airlock, and **AZNet** —
the ethical-search / network mode.

The kernel rule is simple: **No receipt = no action.**

AZInterface, AZ-OS, and Lumen are **out of scope** and are not built
here. AZMail is a **sibling product** already live
([github.com/AzielEliab/azmail](https://github.com/AzielEliab/azmail))
— optional deep-link only; this repo does not rebuild mail.

## Honesty (read this)

v0.1 **cannot** ship a full Chromium / WebKit / Gecko binary. The Worker
delivers a research shell: address bar, tabs, Home sigil, controlled
fetch/proxy preview in a sandbox iframe, receipted airlock, and AZNet
ethical search. It does **not** replace the operator's OS browser.

## Architecture (Phase 1)

```
┌─────────────────────────────────────────────┐
│  Browser runtime (chrome UX, tab isolation) │
├─────────────────────────────────────────────┤
│  Network layer — AZNet ethical search mode  │
├─────────────────────────────────────────────┤
│  Security kernel — integrity + receipts     │
│  "No receipt = no action"                   │
├─────────────────────────────────────────────┤
│  Data ingestion airlock                     │
│  download → scan → scrub → verify → vault   │
└─────────────────────────────────────────────┘
```

### Browser runtime

Human chrome matches a real browser: tab strip, Back / Forward / Reload,
Home = everblooming sigil
(`https://www.azielcorpuslibrary.net/sigil.png`), address/search bar,
black background / gold trim / white text. Tabs are isolated in UX even
when rendering is an iframe / proxy sandbox.

### Network layer (AZNet)

AZNet is the product's ethical-search / network **mode label**. Lamb
Lens style: cite sources; refuse doxxing, credential harvest, and
malware lure; label every result **advisory**.

### Security kernel

Every navigate, search, airlock, and tab mutation appends a hash-chained
receipt (`prev` = SHA-256 of the prior receipt). Verify walks the chain.
If an action cannot mint a receipt, it does not proceed.

### Data ingestion airlock

Inbound bytes walk five stages. Each stage records a hash in the UI and
in the receipt payload. Hosted v0.1 **vaults metadata**, not binary
blobs.

## Dual surface (product law)

1. **Human software** — Worker homepage (complete browser chrome),
   Flutter `mobile/`, local `azbrowser ui`, counted `/download`.
2. **Agent / MCP** — FragGate only on aziel-runtime:
   `POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call`
   with `{ slug: "azbrowser", op, payload }`. Catalog MCP:
   `POST https://aziel-runtime.vibelock.workers.dev/mcp`.
   This Worker `/mcp` is a pointer, not a second agent brand. Human
   chrome uses same-origin `/v1` (same op names). Agents display
   `display.title` / `summary` / `fields` in chat and feed the next
   input. No technical MCP chrome is required for the human.

Every major UI action has a matching op: `navigate`, `preview`,
`ethical_search` / `lamb_lens`, `back`, `forward`, `reload`, `home`,
`tab_new` / `tab_close` / `tab_switch` / `tab_list`, `airlock`,
`airlock_status`, `receipts`, `receipt_verify`, `ethics_gate`, `scrub`.

## What this is not

Not Chromium. Not a VPN. Not AZ-OS / Lumen / AZInterface. Not AZMail.
Not a guaranteed ethics oracle. Hosted `/v1` does not persist vault
bytes. Catalog listing of slug `azbrowser` lands in a sibling
aziel-runtime PR; ops already run on this Worker.

## Software tabs (parent listing)

Once the Worker URL is live, the parent surfaces list AZBrowser on:

- https://www.azielcorpuslibrary.net/software
- https://godlock.uk/software
- https://www.azieleliab.com (Software section)

Expected Worker: `https://azbrowser-download-tracker.vibelock.workers.dev/`

## Cite

Eliab, Aziel. (2026). AZBrowser 0.1.0 [Software]. Apache-2.0.
https://github.com/AzielEliab/azbrowser

Do not invent a DOI.
