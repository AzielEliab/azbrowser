"""Mesh Security checks this browser can do locally.

Name state, equivocation, rollback, airlock promotion, and the local
trust view. Relay gossip, proof-of-work, end-to-end transport, and
ClamAV/YARA live in aziel-runtime, qnm-node, and aznet. This module
does not cut the mesh off for anyone else.

Author: Aziel Eliab only.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from .airlock import airlock
from .ed25519 import verify
from .hashgate import canonical, sha256_text
from .names import REFUSE

# Brief example until aziel-runtime publishes the Mesh Security section.
NAME_MIN_AGE_SECONDS = 72 * 3600
NAME_MIN_WITNESSES = 2

NowFn = Callable[[], datetime]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def witness_message(record: dict[str, Any], witness_handle: str) -> dict[str, Any]:
    ref = record.get("ref") if isinstance(record.get("ref"), dict) else {}
    return {
        "claimed_at": str(record.get("claimed_at") or ""),
        "engine_digest": str(ref.get("engine_digest") or ""),
        "handle": str(ref.get("handle") or ""),
        "name": str(ref.get("name") or ""),
        "object": str(ref.get("object") or ""),
        "seq": int(ref.get("seq") or 0) if isinstance(ref.get("seq"), int) and not isinstance(ref.get("seq"), bool) else 0,
        "witness": str(witness_handle),
    }


def vouch_message(owner_handle: str, vouch_handle: str) -> dict[str, str]:
    return {"handle": str(owner_handle), "vouch": str(vouch_handle)}


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _verified_witnesses(record: dict[str, Any]) -> list[str]:
    raw = record.get("witnesses")
    if not isinstance(raw, list):
        return []
    owner = str(record.get("handle") or "").lower()
    found: list[str] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        handle = str(item.get("handle") or "").strip().lower()
        if not handle or handle == owner or handle in found:
            continue
        try:
            public = bytes.fromhex(str(item.get("public_key") or ""))
            signature = bytes.fromhex(str(item.get("signature") or ""))
        except ValueError:
            continue
        if len(public) != 32 or len(signature) != 64:
            continue
        message = witness_message(record, handle)
        digest = sha256_text(canonical(message))
        if str(item.get("receipt") or "") != digest:
            continue
        if not verify(public, canonical(message).encode("utf-8"), signature):
            continue
        found.append(handle)
    return found


def evaluate_name(record: dict[str, Any], now: datetime | None = None) -> dict[str, Any]:
    """FINAL only when the record says so, the claim has aged, and K witnesses verify."""
    moment = now or utc_now()
    status = str(record.get("status") or "").strip().upper()
    claimed = _parse_time(record.get("claimed_at"))
    age = int((moment - claimed).total_seconds()) if claimed is not None else None
    witnesses = _verified_witnesses(record)
    aged = age is not None and age >= NAME_MIN_AGE_SECONDS
    witnessed = len(witnesses) >= NAME_MIN_WITNESSES
    base = {
        "witnesses": witnesses,
        "witness_count": len(witnesses),
        "chain_age_seconds": age,
        "min_age_seconds": NAME_MIN_AGE_SECONDS,
        "min_witnesses": NAME_MIN_WITNESSES,
        "status_declared": status,
    }
    if status == "FINAL" and aged and witnessed:
        return {**base, "state": "FINAL", "reason": ""}
    if status == "FINAL":
        return {**base, "state": "REFUSED", "reason": "name_not_final"}
    return {**base, "state": "PENDING", "reason": "name_pending"}


def verified_vouches(record: dict[str, Any]) -> list[str]:
    raw = record.get("vouches")
    if not isinstance(raw, list):
        return []
    owner = str(record.get("handle") or "").lower()
    found: list[str] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        handle = str(item.get("handle") or "").strip().lower()
        if not handle or handle == owner or handle in found:
            continue
        try:
            public = bytes.fromhex(str(item.get("public_key") or ""))
            signature = bytes.fromhex(str(item.get("signature") or ""))
        except ValueError:
            continue
        if len(public) != 32 or len(signature) != 64:
            continue
        message = vouch_message(owner, handle)
        if not verify(public, canonical(message).encode("utf-8"), signature):
            continue
        found.append(handle)
    return found


def mesh_verdict(flags: list[str]) -> str:
    """Advisory flags. A signed .js path is not a malware verdict.

    This process has no ClamAV or YARA. Magic bytes and other executable
    extensions stay in quarantine. `.js` is recorded and held, because the
    hash gate already required a signature and this shell does not run it.
    """
    hard = [
        flag
        for flag in flags
        if flag == "suspicious_magic" or (flag.startswith("suspicious_extension:") and flag != "suspicious_extension:.js")
    ]
    if hard:
        return "quarantine"
    if flags:
        return "hold"
    return "clean"


def promote_objects(
    page: bytes,
    modules: list[dict[str, Any]],
    objects: dict[str, bytes],
    *,
    operator_override: bool,
) -> dict[str, Any]:
    """Quarantine first. Promote only with an explicit operator override.

    scanner is absent: this process does not run ClamAV or YARA. The
    advisory extension/magic scan is not that scanner. Override does not
    promote a quarantine verdict.
    """
    page_scan = airlock(content=page, filename="page.html")
    flags = list((page_scan.get("scan") or {}).get("flags") or [])
    verdict = mesh_verdict(flags)
    module_rows: list[dict[str, Any]] = []
    for item in modules:
        digest = str(item.get("hash") or "")
        blob = objects.get(digest)
        if blob is None:
            continue
        path = str(item.get("path") or "module")
        scanned = airlock(content=blob, filename=path.rsplit("/", 1)[-1] or "module")
        module_flags = list((scanned.get("scan") or {}).get("flags") or [])
        module_verdict = mesh_verdict(module_flags)
        if module_verdict == "quarantine":
            verdict = "quarantine"
        elif module_verdict == "hold" and verdict == "clean":
            verdict = "hold"
        flags.extend(module_flags)
        module_rows.append(
            {
                "path": path,
                "hash": digest,
                "quarantined": True,
                "verdict": module_verdict,
                "body_included": False,
            }
        )
    promoted = False
    reason = ""
    if verdict == "quarantine":
        reason = "airlock_quarantine"
    elif operator_override is True:
        promoted = True
    else:
        reason = "scanner_absent"
    return {
        "scanner": "absent",
        "scanner_version": None,
        "clamav": False,
        "yara": False,
        "advisory": True,
        "verdict": verdict,
        "flags": flags,
        "content_hash": page_scan.get("content_hash") or "",
        "operator_override": operator_override is True,
        "promoted": promoted,
        "scripts_executed": False,
        "executed": False,
        "modules": module_rows,
        "reason": reason,
        "pipeline": ["download", "scan", "scrub", "verify", "vault"],
    }


def local_trust(
    *,
    handle: str,
    record: dict[str, Any] | None,
    equivocating: bool,
    hash_matches: int,
    peer_blocked: bool,
    island_mode: bool,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Local signals only. No public ranking and no use-based number."""
    status = evaluate_name(record, now) if record else None
    beats = 0
    vouches: list[str] = []
    if record:
        raw_beats = record.get("heartbeats")
        if isinstance(raw_beats, list):
            seen: list[str] = []
            for item in raw_beats:
                if not isinstance(item, dict):
                    continue
                who = str(item.get("handle") or "").strip().lower()
                if who and who not in seen:
                    seen.append(who)
            beats = len(seen)
        elif status:
            beats = int(status["witness_count"])
        vouches = verified_vouches(record)
    return {
        "ok": True,
        "local_only": True,
        "public_ranking": False,
        "handle": handle,
        "name_status": None if status is None else status["state"],
        "chain_age_seconds": None if status is None else status["chain_age_seconds"],
        "heartbeats_witnessed": beats,
        "hash_matches": int(hash_matches),
        "vouches": vouches,
        "equivocating": bool(equivocating),
        "peer_blocked": bool(peer_blocked),
        "island_mode": bool(island_mode),
        "network_wide": False,
        "spec_note": (
            "Local trust view. Relays, proof-of-work, and witness gossip are not decided here. "
            "This node does not publish a ranking."
        ),
    }


def refusal(reason: str) -> dict[str, Any]:
    return {"ok": False, "code": REFUSE, "reason": reason}
