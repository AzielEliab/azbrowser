"""Signed content hash gate for mesh pages, scripts, and modules.

A mesh response is shown only when the handle key's Ed25519 signature
matches the ref and every loaded byte matches its signed SHA-256.
Mismatch, an unsigned module, or tampered bytes yield FG-GATE-REFUSE.

Author: Aziel Eliab only.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from .ed25519 import verify
from .names import REFUSE

SECRET_FIELDS = frozenset(
    {
        "private_key",
        "privatekey",
        "secret_key",
        "secretkey",
        "signing_key",
        "signingkey",
        "seed",
        "priv",
        "privkey",
        "ed25519_secret",
        "sk",
        "secret",
    }
)

_SCRIPT_SRC = re.compile(r"<script\b[^>]*\bsrc\s*=\s*['\"]([^'\"]+)['\"][^>]*>", re.I)
_SCRIPT_INLINE = re.compile(r"<script\b(?![^>]*\bsrc\s*=)[^>]*>([\s\S]*?)</script\s*>", re.I)


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def contains_secret(obj: Any) -> bool:
    if isinstance(obj, dict):
        for key, value in obj.items():
            norm = str(key).lower().replace("-", "_")
            if norm in SECRET_FIELDS:
                return True
            if contains_secret(value):
                return True
        return False
    if isinstance(obj, list):
        return any(contains_secret(item) for item in obj)
    return False


def engine_digest_for(ref: dict[str, Any]) -> str:
    body = {k: v for k, v in ref.items() if k != "engine_digest"}
    return sha256_text(canonical(body))


def verify_record(record: dict[str, Any]) -> dict[str, Any]:
    """Check the handle key against the signed ref. No secret is read."""
    if contains_secret(record):
        return _no("keys_must_stay_on_node")
    ref = record.get("ref")
    if not isinstance(ref, dict):
        return _no("bad_handle_signature")
    if contains_secret(ref):
        return _no("keys_must_stay_on_node")
    if str(record.get("handle") or "") != str(ref.get("handle") or ""):
        return _no("bad_handle_signature")
    if str(record.get("name") or "") != str(ref.get("name") or ""):
        return _no("bad_handle_signature")
    if str(record.get("public_key") or "") != str(ref.get("public_key") or ""):
        return _no("bad_handle_signature")
    expect = engine_digest_for(ref)
    if str(ref.get("engine_digest") or "") != expect:
        return _no("engine_digest_mismatch")
    try:
        public = bytes.fromhex(str(record.get("public_key") or ""))
        signature = bytes.fromhex(str(record.get("signature") or ""))
    except ValueError:
        return _no("bad_handle_signature")
    message = canonical(ref).encode("utf-8")
    if not verify(public, message, signature):
        return _no("bad_handle_signature")
    return {"ok": True, "engine_digest": expect, "code": "", "reason": ""}


def _modules(ref: dict[str, Any]) -> list[dict[str, Any]]:
    raw = ref.get("modules")
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict)]


def gate_bytes(record: dict[str, Any], page: bytes, objects: dict[str, bytes]) -> dict[str, Any]:
    """Page, script, and module bytes must match the signed ref."""
    checked = verify_record(record)
    if not checked["ok"]:
        return checked
    ref = record["ref"]
    page_hash = sha256_bytes(page)
    if page_hash != str(ref.get("object") or ""):
        return _no("hash_mismatch")
    modules = _modules(ref)
    by_path = {str(item.get("path") or ""): item for item in modules}
    by_hash = {str(item.get("hash") or ""): item for item in modules}
    text = page.decode("utf-8", errors="replace")
    for src in _SCRIPT_SRC.findall(text):
        item = by_path.get(src)
        if item is None or item.get("signed") is not True:
            return _no("unsigned_module")
        blob = objects.get(str(item.get("hash") or ""))
        if blob is None or sha256_bytes(blob) != str(item.get("hash") or ""):
            return _no("hash_mismatch")
    for inline in _SCRIPT_INLINE.findall(text):
        body = inline.strip()
        if not body:
            continue
        digest = sha256_bytes(body.encode("utf-8"))
        item = by_hash.get(digest)
        if item is None or item.get("signed") is not True:
            return _no("unsigned_module")
        blob = objects.get(digest)
        if blob is None or sha256_bytes(blob) != digest:
            return _no("hash_mismatch")
    for item in modules:
        if item.get("signed") is not True:
            return _no("unsigned_module")
        digest = str(item.get("hash") or "")
        blob = objects.get(digest)
        if blob is None:
            continue
        if sha256_bytes(blob) != digest:
            return _no("hash_mismatch")
    return {"ok": True, "content_hash": page_hash, "engine_digest": checked["engine_digest"], "code": "", "reason": ""}


def _no(reason: str) -> dict[str, Any]:
    return {"ok": False, "code": REFUSE, "reason": reason}
