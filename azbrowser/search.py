"""AZ Search — AZ Browser's primary search.

Lamb Lens order is Service, then Clarity, then Peace. A hit is a record
this shell already holds, or a corpus row whose returned fields contain
the query. An empty page is an honest miss. Nothing is invented.

AZ Search is not a Softwares card. Agents use the FragGate door,
slug ``azbrowser``, op ``ethical_search``. The sidenet is AZNet.
Cap-7 names are mesh pairing and are not ICANN names.

Author: Aziel Eliab only.
"""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .ethics import classify_query
from .lens import ORDER, LOCK
from .meta import FRAGGATE_CALL
from .sidenet import AZ_DOMAIN_REACH, CAP7_FACTORY_LABELS, CAP7_FALSE_SITE_LABELS
from .slots import RESERVED_SLOTS

ENGINE = "AZ Search"
PRODUCT = "AZ Browser"
SIDENET = "AZNet"
CATALOG: list[dict[str, str]] = [
    {
        "title": "Aziel Digital Library",
        "url": "https://www.azielcorpuslibrary.net/",
        "source": "cite",
        "blurb": "Public library site. A live corpus row is listed only when FragGate returns one whose fields contain the query.",
        "tags": "library corpus aziel research",
    },
    {
        "title": "FragGate kernel",
        "url": "https://github.com/AzielEliab/fraggate",
        "source": "cite",
        "blurb": "One door — discover, route, refuse. FG-0.1.",
        "tags": "fraggate mcp door kernel",
    },
    {
        "title": "aziel-runtime",
        "url": "https://github.com/AzielEliab/aziel-runtime",
        "source": "cite",
        "blurb": "Catalog and FragGate door. Host: https://aziel-runtime.vibelock.workers.dev/",
        "tags": "runtime mcp openapi catalog",
    },
    {
        "title": "AZMail (sibling, not this product)",
        "url": "https://github.com/AzielEliab/azmail",
        "source": "cite",
        "blurb": "Mail airlock. Separate program. Not rebuilt in AZ Browser.",
        "tags": "azmail mail airlock sibling",
    },
    {
        "title": "GodLock",
        "url": "https://godlock.uk/",
        "source": "cite",
        "blurb": "Offline hardening score. Not a VPN.",
        "tags": "godlock abad hardening",
    },
    {
        "title": "Aziel Eliab",
        "url": "https://www.azieleliab.com/",
        "source": "cite",
        "blurb": "Public identity: Aziel Eliab only.",
        "tags": "author identity aziel eliab",
    },
    {
        "title": "Wikipedia",
        "url": "https://en.wikipedia.org/wiki/Main_Page",
        "source": "cite",
        "blurb": "Encyclopedia main page. Cite the article you open.",
        "tags": "encyclopedia wiki wikipedia",
    },
    {
        "title": "MDN Web Docs",
        "url": "https://developer.mozilla.org/",
        "source": "cite",
        "blurb": "Public web-platform documentation.",
        "tags": "html css javascript http browser mdn",
    },
]

_TOKEN = re.compile(r"[a-z0-9][a-z0-9._-]*")
_STOP = frozenset({"a", "an", "the", "of", "or", "and", "to", "for", "in", "on"})
_SKIP_RECEIPT = frozenset({"ethics_refuse"})
_SOURCE_RANK = {
    "mesh": 0,
    "slot": 1,
    "airlock": 2,
    "receipt": 3,
    "cap7": 4,
    "hub-cite": 5,
    "aziel-corpus": 6,
    "cite": 7,
}
_SECRET = frozenset({"private_key", "secret", "seed", "sk", "pair_token"})


def _tokens(query: str) -> list[str]:
    words = _TOKEN.findall(str(query or "").lower())
    return [word for word in words if word not in _STOP and len(word) >= 2]


def _contains(token: str, blob: str) -> bool:
    if len(token) >= 4:
        return token in blob
    return re.search(rf"(?<![a-z0-9]){re.escape(token)}(?![a-z0-9])", blob) is not None


def _score(tokens: list[str], blob: str) -> int:
    low = blob.lower()
    return sum(1 for token in tokens if _contains(token, low))


def _http_url(value: Any) -> str:
    text = str(value or "").strip()
    if text.startswith("https://") or text.startswith("http://"):
        return text
    return ""


def _clip(text: str, limit: int = 240) -> str:
    flat = re.sub(r"\s+", " ", str(text or "")).strip()
    return flat[:limit]


def _candidate(
    *,
    title: str,
    url: str,
    source: str,
    blurb: str,
    tags: str = "",
    plane: str = "",
    icann: bool | None = None,
    false_site: bool | None = None,
    receipt: str = "",
    record_id: str = "",
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "title": title,
        "url": url,
        "source": source,
        "blurb": _clip(blurb),
        "tags": tags,
        "plane": plane or source,
    }
    if icann is not None:
        row["icann"] = icann
        row["public_icann"] = False if source in {"cap7", "hub-cite", "mesh", "slot"} else icann
    if false_site is not None:
        row["false_site"] = false_site
    if receipt:
        row["receipt"] = receipt
    if record_id:
        row["record_id"] = record_id
    return row


def _mesh_candidates(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        if any(key in record for key in _SECRET):
            continue
        name = str(record.get("name") or "").strip()
        handle = str(record.get("handle") or "").strip()
        if not name and not handle:
            continue
        bits = [name, handle, str(record.get("status") or "")]
        objects = record.get("objects")
        if isinstance(objects, dict):
            for key, value in list(objects.items())[:4]:
                bits.append(str(key)[:80])
                if isinstance(value, str):
                    bits.append(value[:240])
        title = name or f"{handle}.aziel"
        found.append(
            _candidate(
                title=title,
                url=title,
                source="mesh",
                plane="mesh",
                icann=False,
                blurb=f"Local mesh name {title}. Handle {handle or 'unset'}. Not an ICANN name.",
                tags=" ".join(bits),
            )
        )
    return found


def _slot_candidates(records: list[dict[str, Any]], handle: str) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for row in RESERVED_SLOTS:
        found.append(
            _candidate(
                title=str(row["label"]),
                url=str(row["host"]),
                source="slot",
                plane="cite",
                icann=False,
                blurb=(
                    f"Reserved hub mirror {row['label']}. Not user-nameable. "
                    "AZ Browser did not register .az."
                ),
                tags=f"{row['label']} {row['host']} {row['id']} reserved hub mirror slot",
            )
        )
    who = str(handle or "").strip().lower()
    seen_handles: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            continue
        owner = str(record.get("handle") or "").strip().lower()
        if not owner:
            continue
        if who and owner != who:
            continue
        seen_handles.add(owner)
        slot = record.get("slot")
        if isinstance(slot, bool):
            slot_text = ""
        elif isinstance(slot, int):
            slot_text = str(slot)
        else:
            slot_text = str(slot or "").strip()
        name = str(record.get("name") or "").strip()
        if name and slot_text in {"1", "2", "3"}:
            found.append(
                _candidate(
                    title=name,
                    url=name,
                    source="slot",
                    plane="mesh",
                    icann=False,
                    blurb=f"User slot {slot} for {owner}. Status {record.get('status') or 'PENDING'}.",
                    tags=f"{name} {owner} user slot {slot}",
                )
            )
    for owner in sorted(seen_handles):
        automatic = f"{owner}.aziel"
        found.append(
            _candidate(
                title=automatic,
                url=automatic,
                source="slot",
                plane="mesh",
                icann=False,
                blurb=f"Automatic mesh name for handle {owner}.",
                tags=f"{automatic} {owner} automatic",
            )
        )
    return found


def _cap7_candidates() -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for label in CAP7_FACTORY_LABELS:
        host = f"{label}.az"
        false_site = label in CAP7_FALSE_SITE_LABELS
        if false_site:
            blurb = f"Cap-7 false site {host}. Not public DNS. Not an ICANN name. Not a hub."
        else:
            blurb = f"Cap-7 name {host} on the AZNet sidenet. Mesh pairing only. Not an ICANN name. Not a hub."
        found.append(
            _candidate(
                title=host,
                url=host,
                source="cap7",
                plane="cap7",
                icann=False,
                false_site=false_site,
                blurb=blurb,
                tags=f"cap7 {label} {host} sidenet aznet mesh",
            )
        )
    return found


def _hub_candidates() -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for row in AZ_DOMAIN_REACH:
        hub = str(row["hub"])
        found.append(
            _candidate(
                title=str(row["display_name"]),
                url=hub,
                source="hub-cite",
                plane="cite",
                icann=False,
                blurb=(
                    f"Hub cite {hub}. Mirror {row['mirrors']}. "
                    f"Cap-7 label {row['cap7_label']} is a separate mesh name. "
                    "AZ Browser did not register .az."
                ),
                tags=f"{row['display_name']} {row['mesh_key']} {hub} {row['mirrors']} hub mirror",
            )
        )
    return found


def _history_candidates(receipts: list[dict[str, Any]], airlocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    air_hashes = {str(row.get("hash") or "") for row in airlocks if isinstance(row, dict)}
    for row in airlocks:
        if not isinstance(row, dict):
            continue
        url = str(row.get("url") or "")
        filename = str(row.get("filename") or "")
        verdict = str(row.get("verdict") or "")
        digest = str(row.get("hash") or row.get("content_hash") or "")
        title = filename or url or "Airlock"
        found.append(
            _candidate(
                title=f"Airlock · {title}",
                url=url if url else "",
                source="airlock",
                plane="airlock",
                blurb=f"Airlock history. Verdict {verdict or 'unset'}.",
                tags=f"airlock {url} {filename} {verdict} {digest}",
                receipt=digest,
            )
        )
    for row in receipts:
        if not isinstance(row, dict):
            continue
        action = str(row.get("action") or "")
        if action in _SKIP_RECEIPT:
            continue
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
        if action == "airlock" and str(payload.get("hash") or "") in air_hashes:
            continue
        bits = [action, str(row.get("hash") or "")]
        for key in ("url", "q", "query", "filename", "verdict", "note", "name", "handle"):
            value = payload.get(key)
            if isinstance(value, str) and value:
                bits.append(value[:180])
        url = str(payload.get("url") or "") if isinstance(payload.get("url"), str) else ""
        if not any(bits[2:]):
            continue
        digest = str(row.get("hash") or "")
        source = "airlock" if action == "airlock" else "receipt"
        found.append(
            _candidate(
                title=f"Receipt · {action}",
                url=url,
                source=source,
                plane=source,
                blurb=f"Receipt {digest[:16]} for {action}.",
                tags=" ".join(bits),
                receipt=digest,
            )
        )
    return found


def _cite_candidates() -> list[dict[str, Any]]:
    return [
        _candidate(
            title=item["title"],
            url=item["url"],
            source=item["source"],
            plane="cite",
            blurb=item["blurb"],
            tags=item.get("tags", ""),
        )
        for item in CATALOG
    ]


def _corpus_candidates(rows: list[dict[str, Any]], tokens: list[str]) -> tuple[list[dict[str, Any]], int]:
    """Keep a corpus row only when returned fields contain the query."""
    matched: list[dict[str, Any]] = []
    returned = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        if any(key in row for key in _SECRET):
            continue
        returned += 1
        title = str(row.get("title") or row.get("name") or "").strip()
        record_id = str(row.get("record_id") or row.get("id") or "").strip()
        if not title and not record_id:
            continue
        keywords = row.get("keywords") or row.get("subjects") or ""
        if isinstance(keywords, list):
            keywords = " ".join(str(part) for part in keywords)
        identity = " ".join([title, record_id, str(keywords), str(row.get("subjects") or "")])
        if _score(tokens, identity) <= 0:
            continue
        url = _http_url(row.get("url") or row.get("href") or row.get("link"))
        snippet = row.get("snippet") or row.get("blurb") or ""
        matched.append(
            _candidate(
                title=title or record_id,
                url=url,
                source="aziel-corpus",
                plane="corpus",
                blurb=str(snippet or f"Corpus record {record_id}."),
                tags=identity,
                record_id=record_id,
            )
        )
    return matched, returned


def _dedupe(scored: list[tuple[int, int, dict[str, Any]]], limit: int) -> list[dict[str, Any]]:
    scored.sort(key=lambda item: (-item[0], item[1]))
    seen: set[str] = set()
    hits: list[dict[str, Any]] = []
    for _score_n, _rank, row in scored:
        key = row.get("url") or "|".join([row.get("source", ""), row.get("title", ""), row.get("record_id", ""), row.get("receipt", "")])
        if not key or key in seen:
            continue
        seen.add(key)
        clean = {k: v for k, v in row.items() if k != "tags"}
        hits.append(clean)
        if len(hits) >= limit:
            break
    return hits


def collect_hits(
    query: str,
    *,
    limit: int = 8,
    records: list[dict[str, Any]] | None = None,
    receipts: list[dict[str, Any]] | None = None,
    airlocks: list[dict[str, Any]] | None = None,
    corpus: list[dict[str, Any]] | None = None,
    handle: str = "",
) -> dict[str, Any]:
    tokens = _tokens(query)
    cap = max(1, min(int(limit), 16))
    ledger = [row for row in (records or []) if isinstance(row, dict)]
    corpus_rows = [row for row in (corpus or []) if isinstance(row, dict)]
    corpus_hits, corpus_returned = _corpus_candidates(corpus_rows, tokens)
    pool = (
        _mesh_candidates(ledger)
        + _slot_candidates(ledger, handle)
        + _cap7_candidates()
        + _hub_candidates()
        + _history_candidates(list(receipts or []), list(airlocks or []))
        + _cite_candidates()
        + corpus_hits
    )
    scored: list[tuple[int, int, dict[str, Any]]] = []
    for row in pool:
        blob = " ".join([str(row.get("title") or ""), str(row.get("blurb") or ""), str(row.get("tags") or ""), str(row.get("url") or "")])
        rank = _score(tokens, blob)
        if rank <= 0:
            continue
        scored.append((rank, _SOURCE_RANK.get(str(row.get("source")), 9), row))
    hits = _dedupe(scored, cap) if tokens else []
    return {
        "results": hits,
        "corpus_returned": corpus_returned,
        "corpus_matched": len(corpus_hits),
    }


def extract_corpus_records(body: Any) -> list[dict[str, Any]]:
    """Read record objects a FragGate corpus response actually carried."""
    found: list[dict[str, Any]] = []

    def walk(node: Any, depth: int) -> None:
        if depth > 6 or not isinstance(node, dict):
            return
        for key in ("records", "results", "hits"):
            rows = node.get(key)
            if isinstance(rows, list):
                found.extend(row for row in rows if isinstance(row, dict))
        for key in ("result", "data", "payload"):
            child = node.get(key)
            if isinstance(child, dict):
                walk(child, depth + 1)

    if isinstance(body, dict):
        walk(body, 0)
    return found


def fetch_corpus(query: str, *, timeout: float = 8.0) -> dict[str, Any]:
    """Ask the FragGate door for aziel-corpus search. Failure returns no rows."""
    payload = json.dumps({"slug": "aziel-corpus", "op": "search", "payload": {"q": query}}).encode("utf-8")
    req = Request(
        FRAGGATE_CALL,
        data=payload,
        headers={"content-type": "application/json", "user-agent": "Mozilla/5.0"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read(1_000_000).decode("utf-8", "replace")
        body = json.loads(raw)
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError):
        return {"asked": True, "ok": False, "records": [], "error": "corpus_unreachable"}
    if not isinstance(body, dict):
        return {"asked": True, "ok": False, "records": [], "error": "corpus_unreadable"}
    return {"asked": True, "ok": True, "records": extract_corpus_records(body), "error": ""}


def ethical_search(
    query: str,
    *,
    limit: int = 8,
    records: list[dict[str, Any]] | None = None,
    receipts: list[dict[str, Any]] | None = None,
    airlocks: list[dict[str, Any]] | None = None,
    corpus: list[dict[str, Any]] | None = None,
    corpus_status: dict[str, Any] | None = None,
    handle: str = "",
) -> dict[str, Any]:
    ethics = classify_query(query)
    if ethics["refuse"]:
        return {
            "ok": False,
            "code": "ETHICS_REFUSE",
            "action": "ethical_search",
            "engine": ENGINE,
            "product": PRODUCT,
            "sidenet": SIDENET,
            "alias": "lamb_lens",
            "query": query,
            "ethics": ethics,
            "results": [],
            "citations": [],
            "invented": False,
            "advisory": True,
            "softwares_card": False,
            "label": "AZ Search refused. Lamb Lens advisory gate.",
            "note": "Cite sources. Refuse doxxing, credential harvest, and malware lure.",
        }

    gathered = collect_hits(
        query,
        limit=limit,
        records=records,
        receipts=receipts,
        airlocks=airlocks,
        corpus=corpus,
        handle=handle,
    )
    hits = gathered["results"]
    status = dict(corpus_status or {})
    if corpus is not None and "asked" not in status:
        status["asked"] = True
        status["ok"] = True
    status.setdefault("asked", False)
    status["returned"] = gathered["corpus_returned"]
    status["matched"] = gathered["corpus_matched"]
    count = len(hits)
    if count:
        plain = f"AZ Search listed {count} record{'s' if count != 1 else ''} this shell holds or that a corpus response contained."
        nxt = "Open a result, or search again. A .aziel name or a web address goes straight to navigation."
    else:
        plain = "AZ Search found no matching name, slot, receipt, airlock row, or cite."
        nxt = "Try another word, or open a .aziel name or a web address. Nothing was invented."
    if status.get("asked"):
        if status.get("ok") is False:
            plain += " The corpus door was not reached, so no corpus row was added."
        else:
            plain += (
                f" The corpus returned {gathered['corpus_returned']} rows;"
                f" {gathered['corpus_matched']} contained the query in the fields AZ Search read."
            )
    citations = []
    for hit in hits:
        citations.append(
            {
                "title": hit.get("title") or "",
                "url": hit.get("url") or "",
                "source": hit.get("source") or "",
                "record_id": hit.get("record_id") or "",
                "receipt": hit.get("receipt") or "",
            }
        )
    return {
        "ok": True,
        "action": "ethical_search",
        "engine": ENGINE,
        "product": PRODUCT,
        "sidenet": SIDENET,
        "alias": "lamb_lens",
        "mode": "az_search",
        "query": query,
        "ethics": ethics,
        "lens": {
            "order": list(ORDER),
            "lock": LOCK,
            "service": "The query was searched once, across names, slots, Cap-7, hub cites, receipts, and corpus rows already in hand.",
            "clarity": plain,
            "peace": "No ads, no tracking, and no invented hits.",
        },
        "clarity": {"order": list(ORDER), "lock": LOCK, "plain": plain, "next": nxt},
        "results": hits,
        "citations": citations,
        "corpus": status,
        "invented": False,
        "advisory": True,
        "softwares_card": False,
        "cap7_public_icann": False,
        "label": "AZ Search. Lamb Lens — Service, then Clarity, then Peace. Cite sources.",
        "note": plain,
    }


def az_search(query: str, **kwargs: Any) -> dict[str, Any]:
    return ethical_search(query, **kwargs)
