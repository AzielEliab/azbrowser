# AZBrowser ↔ AZNet pairing (sibling contract)

AZNet is a **separate product**: https://github.com/AzielEliab/aznet

Silent verification network. Hash continuity without hosting. Pairs
with AZBrowser. FragGate unlocks access; StaticClock stamps time;
TemporalLock receipts live on AZNet.

This repo does **not** embed the AZNet protocol or fork its whitepaper.
AZBrowser is the **side-net viewer**. Both products are required to run
research ops.

## Deep links (expected Worker pattern)

| Surface | URL |
|---------|-----|
| GitHub | https://github.com/AzielEliab/aznet |
| Worker | https://aznet-download-tracker.vibelock.workers.dev |
| Garden | https://aznet-download-tracker.vibelock.workers.dev/garden |

AZNet Worker may not be live yet. Pair-status is honest: unreachable
Worker = unpaired.

## Pair contract (documented, not implemented here)

```
GET {AZNET_WORKER}/v1/pair?peer=azbrowser
```

Expected JSON:

```json
{ "ok": true, "paired": true, "peer": "azbrowser" }
```

Live pair on AZBrowser is **AZNet paired AND FragGate unlock**.
Unlock is `POST` FragGate call `{ slug: "staticclock", op: "advise", payload: { geo: "UTC" } }`.
StaticClock times; it does not host the side-net.

## Ops on this product

| Op | Always allowed? | Role |
|----|-----------------|------|
| `pair_status` | yes | Sibling probe + FragGate/StaticClock unlock |
| `sidenet_view` | yes | Viewer envelope (garden / worker / github) |
| `navigate` | no | Requires pair |
| `ethical_search` | no | Requires pair (Lamb Lens, not AZNet) |
| `airlock` | no | Requires refuse `PAIR_REQUIRED` until paired |
| `scrub` | no | Requires pair |
| `health` `home` tabs receipts | yes | Gate/viewer stay usable |

Unpaired research returns `code: PAIR_REQUIRED` plus the deep links.
`protocol_embedded` is always `false`.

## Branding

AZNet in the browser chrome is the **Side-net** viewer button.
Lamb Lens is AZBrowser ethical search. Do not treat AZNet as a second
search-mode label or a whitepaper copy.
