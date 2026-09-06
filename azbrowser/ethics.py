"""Lamb Lens / AZNet ethics gate.

Refuse doxxing, credential harvest, and malware-lure queries.
Advisory only — not a law-enforcement tool and not a content oracle.
"""

from __future__ import annotations

import re
from typing import Any

LIMITATION = (
    "AZNet ethical search is advisory. Cite sources. Refuse doxxing, "
    "credential harvest, and malware lure. Not a guaranteed block."
)

_DOXX = [
    re.compile(p, re.I)
    for p in (
        r"\bdoxx(?:ing|ed)?\b",
        r"\bhome address\b",
        r"\blives at\b",
        r"\bwhere does\b.+\blive\b",
        r"\bfind(?:ing)?\b.+\b(?:home )?address\b",
        r"\bssn\b",
        r"\bsocial security(?: number)?\b",
        r"\bphone number of\b",
        r"\bpersonal phone of\b",
        r"\breal name of\b",
        r"\bhome of\b.+\b(?:find|locate)\b",
        r"\bprivate address of\b",
        r"\bwhere does .+ work\b.+\bhome\b",
    )
]
_CREDS = [
    re.compile(p, re.I)
    for p in (
        r"\bcredential harvest",
        r"\bharvest (?:login|password|credential|cookie|token)s?\b",
        r"\bsteal (?:passwords?|cookies?|tokens?|sessions?|logins?)\b",
        r"\bpassword dump\b",
        r"\bapi[_ -]?key\s*[:=]",
        r"\bpassword\s*[:=]\s*\S",
        r"\bdump (?:passwords?|hashes|credentials)\b",
        r"\bphishing kit\b",
        r"\bcapture (?:login|password|credential)s?\b",
    )
]
_MALWARE = [
    re.compile(p, re.I)
    for p in (
        r"\bmalware (?:lure|kit|dropper|payload)\b",
        r"\bransomware\b",
        r"\bexploit kit\b",
        r"\bc2 (?:payload|server|beacon)\b",
        r"\bhow to hack\b",
        r"\b0-?day exploit\b",
        r"\bwrite (?:a |an )?(?:virus|trojan|worm)\b",
        r"\bdrive-?by download\b",
        r"\bmalicious (?:apk|exe|payload)\b",
    )
]


def classify_query(text: str) -> dict[str, Any]:
    """Return an advisory ethics verdict for a search or navigate query."""
    blob = str(text or "")
    reasons: list[str] = []
    if any(p.search(blob) for p in _DOXX):
        reasons.append("doxxing")
    if any(p.search(blob) for p in _CREDS):
        reasons.append("credential_harvest")
    if any(p.search(blob) for p in _MALWARE):
        reasons.append("malware_lure")
    refuse = bool(reasons)
    return {
        "ok": not refuse,
        "refuse": refuse,
        "reasons": reasons,
        "advisory": True,
        "label": "AZNet / Lamb Lens — advisory ethical gate",
        "limitation": LIMITATION,
        "query_len": len(blob),
    }
