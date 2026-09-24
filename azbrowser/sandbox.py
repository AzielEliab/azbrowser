"""Capability sandbox for mesh sites and local apps.

Default deny: no outside network, no cross-origin fetch, no storage
outside the origin, no local files. A grant is a hash-chained receipt.
This is not a tracker detector. The normal web is not covered here.

Author: Aziel Eliab only.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from .names import REFUSE
from .receipts import Ledger

_KINDS = {
    "network": "network",
    "net": "network",
    "fetch": "fetch",
    "cross_origin": "fetch",
    "storage": "storage",
    "file": "file",
}


def _origin_of(target: str) -> str:
    text = str(target or "").strip()
    if "://" not in text:
        return text.rstrip("/")
    parsed = urlparse(text)
    if parsed.scheme in {"aziel", "azbrowser"}:
        return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")
    host = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    return f"{parsed.scheme}://{host}{port}".rstrip("/")


def _same_origin(origin: str, target: str) -> bool:
    return _origin_of(origin) == _origin_of(target)


class CapabilitySandbox:
    """Grants live with the engine. The receipt chain is the record."""

    def __init__(self, ledger: Ledger) -> None:
        self.ledger = ledger
        self.grants: list[dict[str, Any]] = []

    def policy(self) -> dict[str, Any]:
        return {
            "network": False,
            "cross_origin": False,
            "storage": "origin",
            "file": False,
            "tracker_detection": False,
            "note": "Default deny for mesh and local apps. Not a blocklist and not a tracker detector.",
        }

    def grant(self, origin: str, capability: str, resource: str, *, tab_id: str | None = None) -> dict[str, Any]:
        kind = _KINDS.get(str(capability or "").strip().lower())
        origin_n = _origin_of(origin)
        resource_n = str(resource or "").strip()
        if not kind or not origin_n or not resource_n:
            rec = self.ledger.append(
                "capability_grant",
                {"ok": False, "reason": "bad_grant", "origin": origin_n},
                tab_id=tab_id,
            )
            return {
                "ok": False,
                "code": REFUSE,
                "reason": "bad_grant",
                "receipt": rec,
            }
        rec = self.ledger.append(
            "capability_grant",
            {
                "origin": origin_n,
                "capability": kind,
                "resource": resource_n,
                "keys_leave_node": False,
                "node_signature": None,
                "note": "Hash-chained grant. The handle key stays on the local node; this process does not sign with it.",
            },
            tab_id=tab_id,
        )
        row = {"origin": origin_n, "capability": kind, "resource": resource_n, "receipt": rec}
        self.grants.append(row)
        return {"ok": True, "grant": {k: row[k] for k in ("origin", "capability", "resource")}, "receipt": rec, "keys_leave_node": False}

    def _match(self, origin: str, kind: str, target: str) -> dict[str, Any] | None:
        origin_n = _origin_of(origin)
        target_origin = _origin_of(target)
        for row in self.grants:
            if row["origin"] != origin_n or row["capability"] != kind:
                continue
            resource = row["resource"]
            if resource in {target, target_origin, "*"}:
                return row
            if target.startswith(resource.rstrip("/") + "/") or target == resource.rstrip("/"):
                return row
        return None

    def check(self, origin: str, kind: str, target: str, *, tab_id: str | None = None) -> dict[str, Any]:
        norm = _KINDS.get(str(kind or "").strip().lower(), "")
        origin_n = _origin_of(origin)
        target_s = str(target or "").strip()
        if not norm or not origin_n or not target_s:
            rec = self.ledger.append("capability_check", {"ok": False, "reason": "bad_grant"}, tab_id=tab_id)
            return {"ok": False, "code": REFUSE, "reason": "bad_grant", "receipt": rec}

        if norm == "storage" and _same_origin(origin_n, target_s):
            rec = self.ledger.append(
                "capability_check",
                {"ok": True, "origin": origin_n, "kind": "storage", "target": target_s, "default": "own-origin"},
                tab_id=tab_id,
            )
            return {"ok": True, "allowed": True, "origin": origin_n, "kind": "storage", "receipt": rec, "keys_leave_node": False}

        if norm == "storage":
            return self._deny("storage_outside_origin", origin_n, norm, target_s, tab_id)
        if norm == "file":
            grant = self._match(origin_n, "file", target_s)
            if not grant:
                return self._deny("file_not_granted", origin_n, norm, target_s, tab_id)
            return self._allow(grant, origin_n, norm, target_s, tab_id)
        if norm == "fetch" and not _same_origin(origin_n, target_s):
            grant = self._match(origin_n, "fetch", target_s)
            if not grant:
                return self._deny("cross_origin_not_granted", origin_n, norm, target_s, tab_id)
            return self._allow(grant, origin_n, norm, target_s, tab_id)
        if norm == "fetch":
            rec = self.ledger.append(
                "capability_check",
                {"ok": True, "origin": origin_n, "kind": "fetch", "target": target_s, "default": "same-origin"},
                tab_id=tab_id,
            )
            return {"ok": True, "allowed": True, "receipt": rec}
        if norm == "network":
            # Own-origin mesh/local documents are not an outside network.
            if _same_origin(origin_n, target_s):
                rec = self.ledger.append(
                    "capability_check",
                    {"ok": True, "origin": origin_n, "kind": "network", "target": target_s, "default": "same-origin"},
                    tab_id=tab_id,
                )
                return {"ok": True, "allowed": True, "receipt": rec}
            grant = self._match(origin_n, "network", target_s)
            if not grant:
                return self._deny("network_not_granted", origin_n, norm, target_s, tab_id)
            return self._allow(grant, origin_n, norm, target_s, tab_id)
        return self._deny("network_not_granted", origin_n, norm, target_s, tab_id)

    def _deny(self, reason: str, origin: str, kind: str, target: str, tab_id: str | None) -> dict[str, Any]:
        rec = self.ledger.append(
            "capability_check",
            {"ok": False, "code": REFUSE, "reason": reason, "origin": origin, "kind": kind, "target": target},
            tab_id=tab_id,
        )
        return {
            "ok": False,
            "allowed": False,
            "code": REFUSE,
            "reason": reason,
            "origin": origin,
            "kind": kind,
            "target": target,
            "receipt": rec,
            "keys_leave_node": False,
        }

    def _allow(self, grant: dict[str, Any], origin: str, kind: str, target: str, tab_id: str | None) -> dict[str, Any]:
        rec = self.ledger.append(
            "capability_check",
            {"ok": True, "origin": origin, "kind": kind, "target": target, "grant": grant["receipt"]["hash"]},
            tab_id=tab_id,
        )
        return {
            "ok": True,
            "allowed": True,
            "origin": origin,
            "kind": kind,
            "target": target,
            "receipt": grant["receipt"],
            "check_receipt": rec,
            "keys_leave_node": False,
        }
