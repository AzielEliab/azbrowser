"""Per-node domain slots this browser can display.

Four reserved slots mirror the primary hub names. Three user slots are
claimable under .aziel, plus the automatic <handle>.aziel name.
MirageGrid's global Cap-7 factory names are a separate layer and are
not changed here.

Author: Aziel Eliab only.
"""

from __future__ import annotations

from typing import Any

from .names import CAP7_ALLOWLIST, CAP7_FALSE_SITES

RESERVED_SLOTS = (
    {
        "id": "ae",
        "label": "AZ.AzielEliab.AZ",
        "host": "az.azieleliab.az",
        "user_nameable": False,
        "role": "hub-mirror",
    },
    {
        "id": "corpus",
        "label": "AZ.AzielCorpusLibrary.AZ",
        "host": "az.azielcorpuslibrary.az",
        "user_nameable": False,
        "role": "hub-mirror",
    },
    {
        "id": "godlock",
        "label": "AZ.Godlock.AZ",
        "host": "az.godlock.az",
        "user_nameable": False,
        "role": "hub-mirror",
    },
    {
        "id": "hdj",
        "label": "AZ.HeDidntJump.AZ",
        "host": "az.hedidntjump.az",
        "user_nameable": False,
        "role": "hub-mirror",
    },
)

USER_SLOT_COUNT = 3


def _user_index(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and 1 <= value <= USER_SLOT_COUNT:
        return value - 1
    text = str(value or "").strip().lower()
    if text in {"1", "2", "3", "user-1", "user-2", "user-3"}:
        return int(text[-1]) - 1
    return None


def slots_for(records: list[dict[str, Any]], handle: str = "") -> dict[str, Any]:
    """Display slots. Reserved hosts are fixed. User claims come only from the ledger."""
    who = str(handle or "").strip().lower()
    user: list[dict[str, Any]] = [
        {"id": f"user-{i + 1}", "name": None, "status": "empty", "user_nameable": True, "conflict": False}
        for i in range(USER_SLOT_COUNT)
    ]
    for record in records:
        if not isinstance(record, dict):
            continue
        if who and str(record.get("handle") or "").strip().lower() != who:
            continue
        index = _user_index(record.get("slot"))
        if index is None:
            continue
        name = str(record.get("name") or "") or None
        status = str(record.get("status") or "PENDING").upper() or "PENDING"
        current = user[index]
        if current["name"] and current["name"] != name:
            current["conflict"] = True
            continue
        current["name"] = name
        current["status"] = status
    return {
        "ok": True,
        "handle": who,
        "automatic_name": f"{who}.aziel" if who else "",
        "reserved": [dict(row) for row in RESERVED_SLOTS],
        "user": user,
        "reserved_count": len(RESERVED_SLOTS),
        "user_count": USER_SLOT_COUNT,
        "user_nameable_reserved": False,
        "miragegrid": {
            "separate_layer": True,
            "changed": False,
            "real": sorted(CAP7_ALLOWLIST),
            "decoy": sorted(CAP7_FALSE_SITES),
            "note": "MirageGrid global Cap-7 factory names are a separate layer and are unchanged.",
        },
        "note": (
            "Four reserved slots mirror the hub names and are not user-nameable. "
            "Three user slots are claimed with the existing name rules. "
            "The automatic handle name is separate from those three."
        ),
    }
