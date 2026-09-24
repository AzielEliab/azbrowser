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

## Human chrome

The address area shows:

- `Verified owner handle · <handle>` when a mesh page verified
- `Blocked · FG-GATE-REFUSE · <reason>` when the gate refuses
- `Local app · azbrowser://local/<slug> · data stays on this machine`
  for a local app

There is no lock icon and no identity-lock treatment of the author.
The author line elsewhere on the page is the product signature, not a
site certificate.

## Lamb Lens

Service, then Clarity, then Peace.

- Service: the existing ethics gate still refuses doxxing, credential
  harvest, and malware-lure queries before resolution.
- Clarity: responses say what happened (DNS, mesh, ledger-only, socket
  or not, scripts not executed).
- Peace: mesh and local apps stay default-deny until a receipted grant.

## Open alignment points

Checked against the public default branches on 24 September 2026.
Other agents may land these after this browser plane. The adapter is
the only place that should change when they do.

1. `docs/designs/FED-MESH-1.0.md` is not on
   [aziel-runtime](https://github.com/AzielEliab/aziel-runtime) `main`
   (tree `bba1d3e`). No branch in that listing was a FED-MESH spec.
   This file is the browser contract until that spec names the fields.
   If the runtime spec uses different JSON names, change
   `azbrowser/meshledger.py` and
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
