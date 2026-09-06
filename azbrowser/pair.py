"""AZNet sibling pair-status client.

Does not embed the AZNet protocol. Talks to the documented Worker/garden
and records FragGate unlock + StaticClock time. Both products required.
"""

from __future__ import annotations

import json
from typing import Any
from urllib.request import Request, urlopen

from .meta import (
    AZNET,
    AZNET_GARDEN,
    AZNET_WORKER,
    FRAGGATE,
    FRAGGATE_CALL,
    RUNTIME,
    STATICCLOCK,
)

UA = "Mozilla/5.0 AZBrowser/0.1.0 (pair-status; sibling-client)"


def _get_json(url: str, timeout: float = 4.0) -> tuple[bool, Any]:
    try:
        req = Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        with urlopen(req, timeout=timeout) as resp:  # noqa: S310 — documented sibling/public URL
            raw = resp.read(64_000)
            try:
                return True, json.loads(raw.decode("utf-8", errors="replace"))
            except json.JSONDecodeError:
                return True, {"ok": resp.status == 200, "text": raw[:200].decode("utf-8", errors="replace")}
    except Exception as exc:
        return False, {"error": str(exc)[:240]}


def _post_json(url: str, body: dict[str, Any], timeout: float = 6.0) -> tuple[bool, Any]:
    try:
        req = Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with urlopen(req, timeout=timeout) as resp:  # noqa: S310
            return True, json.loads(resp.read(64_000).decode("utf-8", errors="replace"))
    except Exception as exc:
        return False, {"error": str(exc)[:240]}


def links() -> dict[str, str]:
    return {
        "aznet_github": AZNET,
        "aznet_worker": AZNET_WORKER,
        "aznet_garden": AZNET_GARDEN,
        "fraggate": FRAGGATE,
        "fraggate_call": FRAGGATE_CALL,
        "runtime": RUNTIME,
        "staticclock": STATICCLOCK,
    }


def pair_status(*, fetch: bool = True, stub_paired: bool | None = None) -> dict[str, Any]:
    """Return pair-status. stub_paired bypasses the network (tests / doctor)."""
    base = {
        "action": "pair_status",
        "peer": "azbrowser",
        "sibling": "aznet",
        "required": True,
        "viewer": True,
        "protocol_embedded": False,
        "links": links(),
        "note": "AZBrowser views the AZNet side-net. Pairing is required to run. Protocol lives in AZNet. FragGate unlocks; StaticClock times.",
    }
    if stub_paired is True:
        return {
            **base,
            "ok": True,
            "paired": True,
            "code": "PAIRED",
            "aznet": {"reachable": True, "paired": True, "source": "stub"},
            "fraggate_unlock": True,
            "staticclock": {"source": "stub", "note": "Tests do not call StaticClock."},
        }
    if stub_paired is False:
        return {
            **base,
            "ok": True,
            "paired": False,
            "code": "PAIR_REQUIRED",
            "aznet": {"reachable": False, "paired": False, "source": "stub"},
            "fraggate_unlock": False,
            "staticclock": {},
        }

    aznet_reachable = False
    aznet_paired = False
    aznet_detail: Any = None
    if fetch:
        ok_h, health = _get_json(AZNET_WORKER.rstrip("/") + "/v1/health")
        ok_p, pair = _get_json(AZNET_WORKER.rstrip("/") + "/v1/pair?peer=azbrowser")
        aznet_reachable = bool(ok_h or ok_p)
        blob = pair if ok_p else health
        aznet_detail = blob
        if isinstance(blob, dict) and (blob.get("paired") is True or (blob.get("ok") is True and blob.get("peer") == "azbrowser")):
            aznet_paired = True

    fg_ok, fg = _post_json(FRAGGATE_CALL, {"slug": "staticclock", "op": "advise", "payload": {"geo": "UTC"}}) if fetch else (False, {})
    sc = {}
    if fg_ok and isinstance(fg, dict):
        inner = (fg.get("result") or {}).get("result") or fg.get("result") or {}
        if isinstance(inner, dict):
            sc = {
                "optimal_time": inner.get("optimal_time"),
                "optimal_date": inner.get("optimal_date"),
                "motto": inner.get("motto"),
                "source": "fraggate/staticclock",
            }
    fraggate_unlock = bool(fg_ok and isinstance(fg, dict) and (fg.get("ok") is True or (fg.get("result") or {}).get("ok") is True or sc))

    paired = bool(aznet_paired and fraggate_unlock)
    return {
        **base,
        "ok": True,
        "paired": paired,
        "code": "PAIRED" if paired else "PAIR_REQUIRED",
        "aznet": {"reachable": aznet_reachable, "paired": aznet_paired, "detail": aznet_detail, "source": "worker"},
        "fraggate_unlock": fraggate_unlock,
        "staticclock": sc,
    }


def sidenet_view() -> dict[str, Any]:
    """Deep-link viewer envelope. Not an AZNet protocol implementation."""
    return {
        "ok": True,
        "action": "sidenet_view",
        "viewer": True,
        "protocol_embedded": False,
        "garden": AZNET_GARDEN,
        "worker": AZNET_WORKER,
        "github": AZNET,
        "links": links(),
        "note": "AZNet branding here is the side-net viewer. The protocol and whitepaper live in https://github.com/AzielEliab/aznet.",
    }
