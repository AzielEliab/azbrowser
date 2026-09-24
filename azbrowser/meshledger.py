"""AZNet resolver + qnm-node transport adapter.

Looks up ``.aziel`` names and Cap-7 / AZ.* allowlist names on the local
mesh ledger, then asks the local qnm-node to connect (direct, LAN, or
relay). Private keys are refused if a payload contains them. This module
does not embed AZNet and does not open a public qnsd proxy.

Intended HTTP (not on those repos' main branches when this was written):

- ``POST http://127.0.0.1:8771/v1/resolve`` ``{"name": "<name>"}``
- ``POST http://127.0.0.1:8891/local/resolve`` ``{"name": "<name>"}``
- ``POST http://127.0.0.1:8891/local/connect`` ``{"mode","peer","relay"}``
- ``POST http://127.0.0.1:8891/local/pull`` ``{"name","object"}``

Author: Aziel Eliab only.
"""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .hashgate import contains_secret, gate_bytes, verify_record
from .meshguard import evaluate_name, promote_objects
from .names import REFUSE, SPEC, classify_destination
from .lens import clarify
from .policy import policy_page
from .preview import scrub_html

PostFn = Callable[[str, dict[str, Any], float], Any]

AZNET_RESOLVER_URL = "http://127.0.0.1:8771/v1/resolve"
QNM_URL = "http://127.0.0.1:8891"
_UA = "Mozilla/5.0 AZBrowser/0.1.0 (research-shell; +https://github.com/AzielEliab/azbrowser)"


def _default_post(url: str, body: dict[str, Any], timeout: float) -> Any:
    req = Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": _UA, "Accept": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=timeout) as res:  # noqa: S310 — loopback resolver / qnm-node only
        raw = res.read(1_000_000)
    return json.loads(raw.decode("utf-8"))


def _as_bytes(value: Any) -> bytes | None:
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return value.encode("utf-8")
    return None


class MeshDirectory:
    """In-process ledger plus optional loopback HTTP. Keys are not stored."""

    def __init__(
        self,
        records: list[dict[str, Any]] | None = None,
        *,
        http: bool = False,
        timeout: float = 0.8,
        resolver_url: str | None = None,
        qnm_url: str | None = None,
        post: PostFn | None = None,
    ) -> None:
        self.http = http
        self.timeout = timeout
        self.resolver_url = resolver_url or os.environ.get("AZNET_RESOLVER_URL", AZNET_RESOLVER_URL)
        self.qnm_url = (qnm_url or os.environ.get("QNM_URL", QNM_URL)).rstrip("/")
        self._post = post or _default_post
        self.by_name: dict[str, dict[str, Any]] = {}
        self.by_handle: dict[str, dict[str, Any]] = {}
        self.seen_seq: dict[tuple[str, int], str] = {}
        self.digest_at: dict[tuple[str, int], str] = {}
        self.max_seq: dict[str, int] = {}
        self.equivocations: set[str] = set()
        self.load_error = ""
        for record in records or []:
            self.add(record)

    def add(self, record: dict[str, Any]) -> dict[str, Any]:
        if contains_secret(record):
            self.load_error = "keys_must_stay_on_node"
            return {"ok": False, "code": REFUSE, "reason": "keys_must_stay_on_node"}
        name = str(record.get("name") or "").strip().lower()
        handle = str(record.get("handle") or "").strip().lower()
        if not name or not handle:
            return {"ok": False, "reason": "bad_record"}
        self.by_name[name] = record
        # <handle>.aziel is the stable handle name. A longer name does not replace it.
        if name == f"{handle}.aziel" or handle not in self.by_handle:
            self.by_handle[handle] = record
        checked = verify_record(record)
        if checked["ok"]:
            self.note_verified(record)
        return {"ok": True, "name": name, "handle": handle}

    def note_verified(self, record: dict[str, Any]) -> None:
        """Index a signature-checked ref. A second digest at the same seq is equivocation."""
        ref = record.get("ref") if isinstance(record.get("ref"), dict) else None
        if not isinstance(ref, dict):
            return
        handle = str(record.get("handle") or "").strip().lower()
        seq = ref.get("seq")
        if not handle or isinstance(seq, bool) or not isinstance(seq, int):
            return
        digest = str(ref.get("engine_digest") or "") + "|" + str(ref.get("object") or "")
        key = (handle, seq)
        previous = self.seen_seq.get(key)
        if previous is not None and previous != digest:
            self.equivocations.add(handle)
        else:
            self.seen_seq[key] = digest
        self.digest_at[key] = str(ref.get("engine_digest") or "")
        self.max_seq[handle] = max(self.max_seq.get(handle, seq), seq)

    def chain_check(self, record: dict[str, Any]) -> dict[str, Any]:
        ref = record.get("ref") if isinstance(record.get("ref"), dict) else {}
        handle = str(record.get("handle") or "").strip().lower()
        if handle in self.equivocations:
            return {"ok": False, "reason": "equivocating_handle"}
        seq = ref.get("seq")
        if isinstance(seq, bool) or not isinstance(seq, int) or seq < 1:
            return {"ok": False, "reason": "bad_prev"}
        prev = str(ref.get("prev") or "")
        if seq == 1:
            if prev != "0" * 64:
                return {"ok": False, "reason": "bad_prev"}
        else:
            parent = self.digest_at.get((handle, seq - 1))
            if parent is None or prev != parent:
                return {"ok": False, "reason": "bad_prev"}
        known = self.max_seq.get(handle, seq)
        if seq < known:
            return {"ok": False, "reason": "rollback"}
        return {"ok": True, "reason": ""}

    def records(self) -> list[dict[str, Any]]:
        return list(self.by_name.values())

    def isolation_for(self, handle: str) -> dict[str, Any] | None:
        who = str(handle or "").strip().lower()
        if not who:
            return None
        for record in self.by_name.values():
            if str(record.get("handle") or "").strip().lower() != who:
                continue
            isolation = record.get("isolation")
            if isinstance(isolation, dict) and str(isolation.get("state") or "").strip().upper() == "ISOLATED":
                return isolation
        return None

    def lookup(self, *, name: str = "", handle: str = "") -> dict[str, Any] | None:
        name_l = name.strip().lower()
        handle_l = handle.strip().lower()
        if name_l and name_l in self.by_name:
            return self.by_name[name_l]
        if not name_l and handle_l:
            if f"{handle_l}.aziel" in self.by_name:
                return self.by_name[f"{handle_l}.aziel"]
            if handle_l in self.by_handle:
                return self.by_handle[handle_l]
        if not self.http:
            return None
        query = name_l or (f"{handle_l}.aziel" if handle_l else "")
        if not query:
            return None
        return self._http_lookup(query, handle_l)

    def _http_lookup(self, name: str, handle: str) -> dict[str, Any] | None:
        urls = [self.resolver_url, self.qnm_url + "/local/resolve"]
        for url in urls:
            try:
                doc = self._post(url, {"name": name, "handle": handle}, self.timeout)
            except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError):
                continue
            if not isinstance(doc, dict):
                continue
            if contains_secret(doc):
                return {"_refuse": "keys_must_stay_on_node", "name": name, "handle": handle, "ref": {}, "public_key": ""}
            record = doc.get("record") if isinstance(doc.get("record"), dict) else doc
            if not isinstance(record, dict):
                continue
            if contains_secret(record):
                return {"_refuse": "keys_must_stay_on_node", "name": name, "handle": handle, "ref": {}, "public_key": ""}
            if record.get("name") and record.get("public_key") and isinstance(record.get("ref"), dict):
                return record
        return None

    def objects_of(self, record: dict[str, Any]) -> dict[str, bytes]:
        raw = record.get("objects") if isinstance(record.get("objects"), dict) else {}
        out: dict[str, bytes] = {}
        for key, value in raw.items():
            blob = _as_bytes(value)
            if blob is not None:
                out[str(key)] = blob
        return out

    def pull(self, record: dict[str, Any], object_hash: str) -> bytes | None:
        found = self.objects_of(record).get(object_hash)
        if found is not None:
            return found
        if not self.http:
            return None
        url = self.qnm_url + "/local/pull"
        try:
            doc = self._post(
                url,
                {"name": record.get("name"), "handle": record.get("handle"), "object": object_hash},
                self.timeout,
            )
        except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError):
            return None
        if not isinstance(doc, dict) or contains_secret(doc):
            return None
        if isinstance(doc.get("body"), str):
            return doc["body"].encode("utf-8")
        if isinstance(doc.get("body_b64"), str):
            try:
                return base64.b64decode(doc["body_b64"])
            except (ValueError, TypeError):
                return None
        return None

    def connect(self, record: dict[str, Any]) -> dict[str, Any]:
        hint = record.get("connect") if isinstance(record.get("connect"), dict) else {}
        mode = str(hint.get("mode") or "direct").lower()
        if mode not in {"direct", "lan", "relay"}:
            mode = "direct"
        peer = str(hint.get("peer") or record.get("handle") or "")
        relay = hint.get("relay") if mode == "relay" else None
        base = {
            "mode": mode,
            "peer": peer,
            "relay": relay,
            "keys_leave_node": False,
            "qnsd_public_proxy": False,
        }
        if not self.http:
            return {
                **base,
                "ok": True,
                "resolved": True,
                "connected": False,
                "socket": False,
                "via": "mesh-ledger",
                "note": (
                    "Name is on the mesh ledger. Peer transport is local qnm-node "
                    "POST /local/connect (direct, lan, or relay). No socket was opened "
                    "because HTTP transport is off. No private key is held here."
                ),
            }
        url = self.qnm_url + "/local/connect"
        body = {"handle": record.get("handle"), "mode": mode, "peer": peer, "relay": relay}
        try:
            doc = self._post(url, body, self.timeout)
        except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError) as exc:
            return {
                **base,
                "ok": True,
                "resolved": True,
                "connected": False,
                "socket": False,
                "via": "qnm-node",
                "error": "connect_unavailable",
                "detail": str(exc)[:180],
                "endpoint": url,
                "note": "qnm-node did not accept /local/connect. Bytes stay unverified-as-a-socket. Keys were not sent.",
            }
        if not isinstance(doc, dict) or contains_secret(doc):
            return {**base, "ok": False, "connected": False, "socket": False, "code": REFUSE, "reason": "keys_must_stay_on_node"}
        answered = str(doc.get("mode") or mode).lower()
        if answered not in {"direct", "lan", "relay"}:
            answered = mode
        connected = bool(doc.get("connected", doc.get("ok")))
        return {
            "ok": doc.get("ok") is not False,
            "resolved": True,
            "connected": connected,
            "socket": connected,
            "mode": answered,
            "peer": str(doc.get("peer") or peer),
            "relay": doc.get("relay") if answered == "relay" else None,
            "via": "qnm-node",
            "endpoint": url,
            "keys_leave_node": False,
            "qnsd_public_proxy": False,
            "note": "Connected through local qnm-node. The handle key stayed on the node.",
        }


def directory_from_env() -> MeshDirectory:
    path = os.environ.get("AZBROWSER_MESH_LEDGER", "").strip()
    records: list[dict[str, Any]] = []
    if path:
        file = Path(path)
        if file.is_file():
            try:
                loaded = json.loads(file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                loaded = []
            if isinstance(loaded, dict):
                loaded = [loaded]
            if isinstance(loaded, list):
                records = [row for row in loaded if isinstance(row, dict) and not contains_secret(row)]
    http = os.environ.get("AZBROWSER_MESH_HTTP", "1") != "0"
    return MeshDirectory(records, http=http)


def _refuse(reason: str, classified: dict[str, Any], **extra: Any) -> dict[str, Any]:
    handle = classified.get("handle") or ""
    out = {
        "ok": False,
        "code": REFUSE,
        "reason": reason,
        "plane": classified.get("plane") or "mesh",
        "owner_handle": handle,
        "verified_owner": False,
        "url": classified.get("display_url") or classified.get("url") or "",
        "display_url": classified.get("display_url") or classified.get("url") or "",
        "icann": False,
        "ca": False,
        "regular_browsers_resolve_aziel": False,
        "keys_leave_node": False,
        "spec": SPEC,
        "html": "",
        "scripts_executed": False,
        "clarity": clarify(reason),
    }
    out.update(extra)
    return out


def open_mesh(
    directory: MeshDirectory,
    classified: dict[str, Any],
    *,
    island: bool = False,
    blocked: set[str] | None = None,
    operator_override: bool = False,
    now: Any = None,
) -> dict[str, Any]:
    if not classified.get("ok"):
        return _refuse(str(classified.get("reason") or "bad_handle"), classified)
    name = str(classified.get("name") or "")
    handle = str(classified.get("handle") or "")
    if island:
        return _refuse(
            "island_mode",
            classified,
            island_mode=True,
            network_wide=False,
            note="This node dropped its mesh peers and relays. Local apps and normal DNS still run. No other node was cut off.",
        )
    if handle and handle in (blocked or set()):
        return _refuse(
            "peer_blocked",
            classified,
            peer_blocked=True,
            network_wide=False,
            note="This handle is blocked on this node only. Other peers stay reachable.",
        )
    record = directory.lookup(name=name, handle=handle if not name else "")
    if record is None:
        return _refuse("name_not_in_ledger", classified, allowlisted=bool(classified.get("allowlisted")))
    if record.get("_refuse"):
        return _refuse(str(record["_refuse"]), classified)
    if contains_secret(record):
        return _refuse("keys_must_stay_on_node", classified)
    owner = str(record.get("handle") or handle)
    isolation = directory.isolation_for(owner)
    if isolation:
        return _refuse(
            "handle_isolated",
            classified,
            policy_page=True,
            html=policy_page(owner, isolation),
            isolation={
                "state": "ISOLATED",
                "reason": str(isolation.get("reason") or "unspecified"),
                "check": str(isolation.get("check") or "unspecified"),
                "evidence_hash": str(isolation.get("evidence_hash") or ""),
                "content_stored": False,
                "content_forwarded": False,
                "deletes_local_data": False,
                "local_runtime": True,
            },
            scripts_executed=False,
            executed=False,
            network_wide=False,
            note="This handle is isolated from the mesh. The page is this shell's policy refusal. Peer bytes were not loaded.",
        )
    checked = verify_record(record)
    if not checked["ok"]:
        return _refuse(str(checked["reason"]), classified, allowlisted=bool(classified.get("allowlisted")))
    directory.note_verified(record)
    chain = directory.chain_check(record)
    if not chain["ok"]:
        return _refuse(str(chain["reason"]), classified, html="", scripts_executed=False, executed=False)
    status = evaluate_name(record, now() if callable(now) else now)
    if status["state"] == "PENDING":
        return _pending(classified, record, status)
    if status["state"] != "FINAL":
        return _refuse(str(status["reason"] or "name_not_final"), classified, name_status="REFUSED", html="")
    ref = record["ref"]
    page = directory.pull(record, str(ref.get("object") or ""))
    if page is None:
        return _refuse("object_missing", classified)
    objects = directory.objects_of(record)
    objects.setdefault(str(ref.get("object") or ""), page)
    gated = gate_bytes(record, page, objects)
    if not gated["ok"]:
        return _refuse(str(gated["reason"]), classified, content_hash=gated.get("content_hash") or "", html="")
    modules = ref.get("modules") if isinstance(ref.get("modules"), list) else []
    air = promote_objects(page, [item for item in modules if isinstance(item, dict)], objects, operator_override=operator_override is True)
    common = {
        "plane": "mesh",
        "spec": SPEC,
        "name": record.get("name"),
        "url": classified.get("url"),
        "display_url": classified.get("display_url"),
        "host": record.get("name"),
        "owner_handle": record.get("handle"),
        "public_key": record.get("public_key"),
        "identity": "handle-key",
        "ca": False,
        "icann": False,
        "allowlisted": bool(classified.get("allowlisted")),
        "regular_browsers_resolve_aziel": False,
        "keys_leave_node": False,
        "content_hash": gated["content_hash"],
        "engine_digest": gated["engine_digest"],
        "hash_ok": True,
        "signature_ok": True,
        "name_status": "FINAL",
        "sandbox": {
            "network": False,
            "cross_origin": False,
            "storage": "origin",
            "file": False,
            "tracker_detection": False,
        },
        "origin": f"aziel://{record.get('handle')}",
        "title": record.get("name"),
        "scripts_executed": False,
        "executed": False,
        "not_chromium": True,
        "fetched": False,
        "airlock": air,
        "network_wide": False,
    }
    if not air["promoted"]:
        reason = str(air["reason"] or "scanner_absent")
        if reason == "airlock_quarantine":
            return _refuse(reason, classified, **common, ok=False, verified_owner=False, html="", promoted=False, quarantine=True)
        return {
            **common,
            "ok": True,
            "action": "airlock_hold",
            "verified_owner": True,
            "navigable": False,
            "promoted": False,
            "quarantine": True,
            "html": "",
            "excerpt": "",
            "renderer": "mesh-quarantine",
            "bytes_from": "quarantine",
            "reason": reason,
            "clarity": clarify(reason),
            "note": (
                "FINAL name. Handle key and content hash matched. Bytes are in non-executable quarantine. "
                "Malware scanner is absent (no ClamAV, no YARA). They are not shown and not run until an "
                "explicit operator override. The sandbox remains the main defense. This node did not cut off the mesh."
            ),
        }
    link = directory.connect(record)
    if link.get("reason") == "keys_must_stay_on_node" or link.get("code") == REFUSE:
        return _refuse("keys_must_stay_on_node", classified)
    text = page.decode("utf-8", errors="replace")
    scrubbed = scrub_html(text)
    return {
        **common,
        "ok": True,
        "action": "navigate",
        "verified_owner": True,
        "navigable": True,
        "promoted": True,
        "quarantine": False,
        "connect": link,
        "html": scrubbed["html"][:80_000],
        "excerpt": text[:400],
        "stripped_kinds": scrubbed["stripped_kinds"],
        "renderer": "mesh-hash-gate",
        "bytes_from": "qnm-pull" if directory.http and str(ref.get("object")) not in (record.get("objects") or {}) else "mesh-ledger",
        "note": (
            "Mesh site promoted out of quarantine by an explicit operator override. "
            "Scanner is absent. Authenticated with the owner handle key, not a certificate authority. "
            ".aziel is not registered with ICANN. Ordinary browsers do not resolve .aziel names. "
            "This shell does not execute scripts. Outside network, cross-origin, foreign storage, "
            "and local files stay denied until a receipted capability grant."
        ),
    }


def _pending(classified: dict[str, Any], record: dict[str, Any], status: dict[str, Any]) -> dict[str, Any]:
    name = str(record.get("name") or classified.get("name") or "")
    return {
        "ok": True,
        "action": "name_pending",
        "code": "",
        "reason": "name_pending",
        "plane": "mesh",
        "spec": SPEC,
        "name": name,
        "name_status": "PENDING",
        "status_declared": status.get("status_declared") or "",
        "url": classified.get("url"),
        "display_url": classified.get("display_url"),
        "owner_handle": record.get("handle") or classified.get("handle") or "",
        "verified_owner": False,
        "navigable": False,
        "promoted": False,
        "quarantine": False,
        "html": "",
        "scripts_executed": False,
        "executed": False,
        "icann": False,
        "ca": False,
        "allowlisted": bool(classified.get("allowlisted")),
        "regular_browsers_resolve_aziel": False,
        "keys_leave_node": False,
        "witness_count": status.get("witness_count") or 0,
        "chain_age_seconds": status.get("chain_age_seconds"),
        "network_wide": False,
        "note": (
            f"Pending name {name}. Not a verified site. "
            "A name stays pending until it has aged and enough independent witnesses exist, and the record says FINAL. "
            "Ordinary browsers do not resolve .aziel names."
        ),
    }


def resolve_query(directory: MeshDirectory, payload: dict[str, Any], **guard: Any) -> dict[str, Any]:
    handle = str(payload.get("handle") or "").strip().lower()
    raw = str(payload.get("name") or payload.get("url") or payload.get("q") or "").strip()
    if handle and not raw:
        raw = handle + ".aziel"
    classified = classify_destination(raw)
    if classified.get("plane") == "dns":
        return {
            "ok": True,
            "action": "resolve",
            "plane": "dns",
            "url": classified.get("url"),
            "host": classified.get("host"),
            "dns": True,
            "tls": "standard",
            "icann": True,
            "allowlisted": False,
            "spec": SPEC,
            "regular_browsers_resolve_aziel": False,
            "note": classified.get("note") or "Normal DNS and standard TLS.",
        }
    if classified.get("plane") == "local":
        return {
            "ok": True,
            "action": "resolve",
            "plane": "local",
            "spec": SPEC,
            **{k: classified[k] for k in ("origin", "slug", "source", "url") if k in classified},
        }
    if classified.get("plane") != "mesh":
        return {
            "ok": False,
            "action": "resolve",
            "error": classified.get("error") or "not_a_url",
            "suggest_search": classified.get("suggest_search"),
        }
    opened = open_mesh(directory, classified, **guard)
    if opened.get("name_status") != "PENDING" and opened.get("action") != "airlock_hold":
        opened["action"] = "resolve"
    return opened
