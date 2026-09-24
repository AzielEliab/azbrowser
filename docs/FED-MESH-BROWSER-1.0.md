# FED-MESH-BROWSER-1.0

**Browser plane for the local-first edge mesh**

Author: Aziel Eliab only
Software: AZBrowser
License: Apache-2.0
Date: September 2026

AZBrowser and AZNet are separate Softwares. This document is the
browser side of the pair. It does not merge AZNet, qnm-node, or
aziel-runtime into this repository.

## What this repository is

AZBrowser is a Phase 1 research-browser shell:

- Python library (`azbrowser/`) and loopback chrome (`azbrowser ui`,
  `127.0.0.1:8878`)
- Cloudflare Worker chrome with the same `/v1/{op}` ops
- Receipted airlock and Lamb Lens ethical search
- In-process tabs

It is not Chromium, Electron, Tauri, Firefox, Safari, or Edge. It does
not ship a browser engine that executes page scripts. Building a full
engine would not make `.aziel` names, handle keys, or local qnm-node
transport exist. Those belong in this shell's navigation plane, which
is what this spec adds.

The Worker does not dial `127.0.0.1` and does not proxy qnsd. Live
peer sockets are the local shell only. The Worker implements the same
name, hash, and capability decisions when a public ledger snapshot is
posted with the op, so the human chrome and the agent ops stay the
same shape.

## Planes

| Input | Plane | Transport |
| --- | --- | --- |
| `<handle>.aziel`, `https://<name>.aziel/…`, `aziel://<handle>/…` | mesh | AZNet resolver, then qnm-node |
| Cap-7 / AZ.* allowlist below | mesh | same |
| Any other `.az` host | DNS | normal DNS, standard TLS |
| Other `http`/`https` hosts | DNS | normal DNS, standard TLS (`http` is upgraded to `https`, as before) |
| `azbrowser://local/<slug>`, `127.0.0.1:8891`, `127.0.0.1:8787` | local app | loopback only |

`<handle>.aziel` is always a mesh name. A missing ledger row is
`FG-GATE-REFUSE` / `name_not_in_ledger`. It is not sent to DNS.

`.aziel` is not registered with ICANN. Ordinary browsers do not
resolve `.aziel` names. Nothing in this repository registers a TLD.

`.az` is Azerbaijan's country-code domain. It stays on normal DNS
except this explicit operator allowlist:

| Host | Why it is mesh |
| --- | --- |
| `azgrid.az` | Cap-7 real duplication (factory label) |
| `azcloak.az` | Cap-7 real duplication |
| `azvault.az` | Cap-7 real duplication |
| `azshift.az` | Cap-7 real duplication |
| `az.azieleliab.az` | `AZ.AzielEliab.AZ` |
| `az.godlock.az` | `AZ.Godlock.AZ` |
| `az.azielcorpuslibrary.az` | `AZ.AzielCorpusLibrary.AZ` |
| `az.hedidntjump.az` | `AZ.HeDidntJump.AZ` |

`azbooth.az`, `azflag.az`, and `azstandby.az` are Cap-7 cloak names.
They are not on the allowlist, so they use normal DNS.
`AZBROWSER_AZ_ALLOWLIST` may add hosts. It does not turn every `.az`
name into a mesh name.

## Resolver adapter

AZBrowser does not embed the AZNet protocol. `MeshDirectory` in
`azbrowser/meshledger.py` is the adapter.

Lookup order:

1. Records already in the local directory (tests, or
   `AZBROWSER_MESH_LEDGER`, a JSON file of public records).
2. If HTTP transport is on: `POST {AZNET_RESOLVER_URL}` default
   `http://127.0.0.1:8771/v1/resolve` with `{"name","handle"}`.
3. Then `POST http://127.0.0.1:8891/local/resolve` with the same body.

A hit must be a public record:

```json
{
  "name": "library.aziel",
  "handle": "library",
  "public_key": "<64 hex chars, Ed25519>",
  "signature": "<128 hex chars>",
  "ref": {
    "name": "library.aziel",
    "handle": "library",
    "public_key": "<same 64 hex chars>",
    "object": "<sha256 hex of the page bytes>",
    "engine_digest": "<sha256 hex>",
    "seq": 1,
    "prev": "<64 hex chars>",
    "modules": [{"path": "/app.js", "hash": "<sha256 hex>", "signed": true, "kind": "script"}]
  },
  "connect": {"mode": "direct", "peer": "library", "relay": null},
  "objects": {"<sha256 hex>": "<utf-8 body>"}
}
```

`engine_digest` is SHA-256 of the canonical JSON of `ref` with the
`engine_digest` field removed. Canonical JSON is UTF-8, keys sorted,
separators `,` and `:`. The Ed25519 signature covers the canonical
JSON of the full `ref`, including `engine_digest`. The public key
inside the ref must equal the record's `public_key`.

Handle resolution (`resolve` with `{"handle":"library"}`) looks up
`library.aziel`.

## Connect

After the hash gate passes, the local shell posts:

```json
POST http://127.0.0.1:8891/local/connect
{"handle":"library","mode":"direct","peer":"library","relay":null}
```

`mode` is `direct`, `lan`, or `relay`. When HTTP transport is off, or
the node does not answer, the name can still be shown from the ledger
and `connect.socket` is `false`. That is not a live peer session.
When the node answers `connected: true`, `connect.socket` is `true`
and `connect.via` is `qnm-node`.

Object bytes come from the record's `objects` map. If the hash is
missing and HTTP is on, the shell posts `POST /local/pull` with
`{"name","handle","object"}` and accepts `body` or `body_b64` only.

No private key is sent. If a record or a response contains
`private_key`, `secret`, `seed`, `sk`, or the other secret field names
in `azbrowser/hashgate.py`, the shell refuses `keys_must_stay_on_node`
and does not echo the secret.

## Hash gate

Shown mesh bytes must match the signed ref.

| Condition | `reason` |
| --- | --- |
| Page SHA-256 ≠ `ref.object` | `hash_mismatch` |
| Script `src` or inline script has no `signed: true` module | `unsigned_module` |
| Module bytes ≠ declared hash | `hash_mismatch` |
| `engine_digest` ≠ recomputed digest | `engine_digest_mismatch` |
| Ed25519 verify fails | `bad_handle_signature` |
| Name not in the ledger | `name_not_in_ledger` |
| Object bytes absent | `object_missing` |
| Secret field present | `keys_must_stay_on_node` |

Every one of those returns `code: "FG-GATE-REFUSE"`. The tampered body
is not returned. The address line shows `FG-GATE-REFUSE` and the
reason. Mesh identity is the owner handle, not a certificate authority.

This shell then scrubs the HTML for the preview iframe and does not
execute scripts (`scripts_executed: false`). A later renderer that
does execute modules has to keep this gate in front of execution.

## Capability sandbox

Mesh origins (`aziel://<handle>`) and local apps
(`azbrowser://local/<slug>`) start from default deny:

- outside network
- cross-origin fetch
- storage outside that origin
- local files

Own-origin storage and same-origin fetch are allowed and receipted.
Anything else needs `capability_grant`. The grant is an append-only
`azbrowser.receipt` (`capability_grant`). A later `capability_check`
that matches returns that grant receipt. The handle key is not used
to sign the grant in this process: `node_signature` is null and
`keys_leave_node` is false. When qnm-node grows a sign-on-node op,
the adapter can attach the returned signature without ever receiving
the key.

This sandbox is what stops mesh apps from calling trackers or loading
injected third-party ads. It is not a detector and it does not claim
to classify the normal web. This repository does not ship a URL
blocklist. The normal web still uses Lamb Lens (Service, then Clarity,
then Peace) and the existing HTML scrub.

## Local apps

`local_app`, `azbrowser://local/<slug>`, `http://127.0.0.1:8891/…`
(qnm-node), and `http://127.0.0.1:8787/…` (local FragGate) open a tab
with `kind: local-app`. The same capability sandbox applies.
`uploaded` is false. `data_stays_local` is true. The shell does not
upload the body.

## Mesh Security

This section is the browser side of the operator brief dated 2026-09-24.
aziel-runtime `main` (`bba1d3e`) still has no `docs/designs/FED-MESH-1.0.md`
Mesh Security section. The constants below are the brief's example
(`72h`, `K = 2`) so Python and the Worker agree. If the runtime spec
lands with different names or numbers, change `azbrowser/meshguard.py`
and `workers/download-tracker/src/mesh-browser.js` together.

| Constant | Value |
| --- | --- |
| `NAME_MIN_AGE_SECONDS` | `259200` (72 hours) |
| `NAME_MIN_WITNESSES` | `2` |

A name record may add:

```json
{
  "status": "PENDING",
  "claimed_at": "2020-01-01T00:00:00Z",
  "witnesses": [
    {"handle": "relay-a", "public_key": "<64 hex>", "signature": "<128 hex>", "receipt": "<sha256 of the witness message>"}
  ],
  "vouches": [
    {"handle": "elder", "public_key": "<64 hex>", "signature": "<128 hex>"}
  ],
  "heartbeats": [{"handle": "relay-a"}]
}
```

The witness message is the canonical JSON of `claimed_at`,
`engine_digest`, `handle`, `name`, `object`, `seq`, and `witness`.
A vouch message is the canonical JSON of `handle` (the owner) and
`vouch` (the vouching handle). Witnesses must be handles other than
the owner. The browser does not invent witnesses.

| State | What the address line does |
| --- | --- |
| `status` missing or `PENDING` | `Pending · <name> · not a verified site`. No page bytes. |
| `FINAL` but the claim is younger than 72h or has fewer than 2 verified witnesses | `FG-GATE-REFUSE` / `name_not_final` |
| `FINAL` and both rules pass | Verified owner handle. Bytes still sit in quarantine until promotion. |

Two verified refs for the same handle at the same `seq` with different
object bytes or `engine_digest` values are an equivocating handle:
`FG-GATE-REFUSE` / `equivocating_handle`. No page bytes. Gossip of that
proof is a relay's job. This browser only refuses what the local ledger
already holds.

`seq` 1 must use `prev` of 64 zero hex chars. A later `seq` must name
the previous ref's `engine_digest`. A lower `seq` than the highest
verified seq for that handle is `rollback`. A broken link is `bad_prev`.

### Airlock before run

Hash-checked mesh page and module bytes go through the existing airlock
(download, scan, scrub, verify, vault) before they are shown. This
process has no ClamAV and no YARA. The response says `scanner: "absent"`.
The extension and magic flags are advisory only. Scanners, when a node
has them, catch known malware. The capability sandbox is the main defense.

Promotion requires `operator_override: true` on the op. That flag does
not promote a quarantine verdict (`airlock_quarantine`), and it does not
execute scripts. `scripts_executed` and `executed` stay false. Module
bodies are not returned. A signed `.js` path is held, not treated as a
malware hit, because the hash gate already required a signature and this
shell does not run it.

### This node only

`peer_block` / `peer_unblock` record a local receipt and refuse that one
handle on this engine. `island_mode` with `{"enabled": true}` drops mesh
names on this engine (`island_mode`) while local apps and normal DNS keep
working. `{"enabled": false}` rejoins by appending a receipt. Earlier
receipt hashes are not rewritten. `receipt_verify` still walks the chain.

There is no local op that cuts the mesh off for every node.
`network_wide` is false on these results. `health.mesh_browser.network_wide_cutoff`
is false. The suite strip's `/v1/mesh/*` proxy is a different plane and
is not an edge-mesh cutoff.

`trust` (alias `trust_view`) returns local signals only: chain age,
heartbeats witnessed by other handles, hash-match count, vouches, and
whether the handle is equivocating. `local_only` is true. `public_ranking`
is false. The payload has no ranking field.

### What this repository does not do

Proof-of-work on claims, relay witness co-signing, equivocation gossip,
end-to-end Noise or WireGuard, two-hop relay, a Tor bearer, per-peer
relay rate limits, ClamAV, YARA, and airgap bundle import/export belong
to aziel-runtime, qnm-node, and aznet. This shell consumes their fields
when a ledger row carries them.

This is not zero-knowledge. It is not a claim of protection against a
state-level adversary. Keys do not leave the local node. The Worker
still does not open a peer socket.

## Wave 3 chrome, slots, and isolation

The loopback chrome and the Worker chrome share three looks:

| Look | Surface |
| --- | --- |
| Night | Black background, white text. This is the default when the OS preference is dark or missing. |
| Day | White background, black text. |
| Aziel mode | Black base, royal purple bars and panels, gold on the active tab, the Go button, and the focus ring. |

One control flips day and night immediately. Aziel mode is a separate control. The choice is stored on this machine as `azbrowser-appearance`. The first visit with nothing stored follows `prefers-color-scheme`. There is no lock icon and no identity-lock banner.

`slots` returns four reserved hub mirrors (`AZ.AzielEliab.AZ`, `AZ.AzielCorpusLibrary.AZ`, `AZ.Godlock.AZ`, `AZ.HeDidntJump.AZ`). Those are not user-nameable. Three user slots show ledger claims whose `slot` is `1`, `2`, or `3` for that handle, plus the automatic `<handle>.aziel` name. A second digest for the same handle at the same sequence is still `equivocating_handle`. Slot display does not create a second chain. MirageGrid's global Cap-7 factory names (`azgrid.az`, `azcloak.az`, `azvault.az`, `azshift.az`, and the three cloak names) are a separate layer and are not edited by this display.

`design_mode` on the loopback shell opens `azbrowser://local/design`. The page lists the slots and says the designer itself is qnm-node on `127.0.0.1`. This process does not publish and does not unlock the handle key. The hosted Worker returns `FG-GATE-REFUSE` / `design_mode_local_only`.

A ledger record with `isolation.state` of `ISOLATED` makes every name for that handle `FG-GATE-REFUSE` / `handle_isolated`. The response HTML is this shell's policy page. It names the reason code, the check, and the evidence hash. It does not include peer bytes. Isolation does not delete local data. A signed appeal can ask for a re-check; this shell does not decide it. Classifiers can miss and can false-positive. This browser does not run them. Operators follow the law in their jurisdiction, including US reporting to NCMEC where that duty applies. This browser does not keep that material.

aziel-runtime `main` still has no FED-MESH Mesh Security or wave-3 section. These field names are the browser contract until that spec says otherwise.

## Human chrome

The address area shows:

- `Pending · <name> · not a verified site` for a pending or unstamped name
- `Verified owner handle · <handle> · quarantined · scanner absent` when a FINAL name matched and bytes are not promoted
- `Verified owner handle · <handle>` after an explicit operator override promotes scrubbed HTML
- `Blocked · FG-GATE-REFUSE · <reason>` when the gate refuses
- `Local app · azbrowser://local/<slug> · data stays on this machine`
  for a local app
- `Island mode · this node only · local runtime stays up` when this node leaves the mesh
- `Local trust · <handle> · …` for the local trust view

Promote, Island, Block peer, and Trust call `navigate` (with
`operator_override`), `island_mode`, `peer_block`, and `trust`. There
is no control that disconnects every node.

There is no lock icon and no identity-lock treatment of the author.
The author line elsewhere on the page is the product signature, not a
site certificate.

## Lamb Lens

Operator lock. AZBrowser follows Lamb Lens under all conditions, in this
order: Service, then Clarity, then Peace. A feature that sacrifices one
of the three fails review.

- Service: do what the person asked, in one request. `navigate` opens an
  ordinary web address. `local_app` and `azbrowser://local/<slug>` open
  a local app. A mesh name resolves in that same request. Quarantine is
  a status on that result, not a second product. The ordinary web keeps
  working when the mesh is islanded or a handle is blocked.
- Clarity: verified handles, pending names, and isolated handles are
  different states. A verified handle is named in the address line. A
  pending name says it is not a verified site and returns no page bytes.
  An isolated handle shows the policy page and the address chip
  `Isolated`. Every `FG-GATE-REFUSE`, ethics refusal, and blocked
  capability carries `clarity.plain` (what happened) and `clarity.next`
  (what to do next). Settings lists Day/Night, Aziel mode, bookmarks,
  and the side-panel mesh tools. There is no hidden switch and no dark
  pattern.
- Peace: no ads, no tracking, no telemetry, and no notification spam.
  There is no telemetry channel to opt into. Capability grants stay
  receipted and rare: own-origin storage does not ask, and a denial
  names the resource instead of raising a prompt. The chrome stays on
  the three themes above. Mesh and local apps stay default-deny until
  a grant.

Health reports this lock as `lamb_lens`. `miragegrid_decoys` is
`separate`: the live MirageGrid global Cap-7 decoys (`azbooth.az`,
`azflag.az`, `azstandby.az`) are not the per-node slots. Those slots
remain four reserved hub mirrors plus three user domains, plus the
automatic `<handle>.aziel` name.

## Open alignment points

Checked against the public default branches on 24 September 2026.
Other agents may land these after this browser plane. The adapter is
the only place that should change when they do.

1. `docs/designs/FED-MESH-1.0.md` is not on
   [aziel-runtime](https://github.com/AzielEliab/aziel-runtime) `main`
   (tree `bba1d3e`), and that tree has no Mesh Security section.
   This file is the browser contract until that spec names the fields.
   Name age and witness count use the brief's example (72 hours, K=2).
   If the runtime spec uses different JSON names or constants, change
   `azbrowser/meshguard.py`, `azbrowser/meshledger.py`, and
   `workers/download-tracker/src/mesh-browser.js` together.

2. [aznet](https://github.com/AzielEliab/aznet) `main` (`0cb9993`) has
   no `.aziel` resolver library and no `/v1/resolve`. AZNet today is
   the silent verification side-net (hashes only, pairing required).
   Intended call: `POST http://127.0.0.1:8771/v1/resolve`. The record
   shape above is what this browser will accept. AZNet must not start
   storing payloads or private keys to satisfy it; the ledger row is
   public key, signature, and content hashes. Page bytes can come from
   the local object store or `qnm-node` pull.

3. [qnm-node](https://github.com/AzielEliab/qnm-node) `main` already
   binds `127.0.0.1:8891` and already has `POST /local/pull` for the
   payload plane. It does not list `/local/resolve` or
   `/local/connect`. This browser posts those paths. `/local/pull` is
   called with `{"name","handle","object"}` and only `body` or
   `body_b64` is read. The live QNM pull body is the cite/lockset
   contract; if that stays the only pull, name resolution still needs
   a distinct route so a cite pull is not overloaded into a browser
   fetch. Connect modes are `direct`, `lan`, and `relay`.

4. Signature suite assumed here is Ed25519 (RFC 8032) over the
   canonical ref. Python `azbrowser/ed25519.py` verifies. The Worker
   verifies with WebCrypto `Ed25519`. `node_sign` is not on the
   navigate path. If FED-MESH picks another suite, replace `verify`
   only.

5. Cap-7 names follow
   `cursor/cap7-az-domain-reach-cb90` `src/cap7-shuffle.js`
   (CAP7-SHUFFLE-1.0), which is not necessarily merged to runtime
   `main`. Four real factory names and four `AZ.*` display names are
   allowlisted. Three false sites are not. `resolves_to_hub` stays
   false on Cap-7; this browser does not pretend an allowlisted name
   is an ICANN `AZ` domain.

6. The Worker hash gate matches the local shell, but
   `connect.socket` stays false there. A posted `ledger` on the op is
   a public snapshot for the hosted chrome, not a peer session and not
   a qnsd proxy.

7. Capability receipts are hash-chained `azbrowser.receipt` rows.
   They are not yet ChainLock / TemporalLock rows from aziel-runtime.
   When those products expose a local append that does not take a
   private key, the grant can also be appended there. This shell will
   not grow a second key store to do that.

8. There is no normal-web blocklist in this repository. Adding one
   later must stay a list, not a claim that the mesh sandbox detects
   trackers on the public web.
