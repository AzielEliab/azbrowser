"""AZNet / Lamb Lens ethical internet search. Advisory. Cite sources."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus

from .ethics import classify_query

CATALOG: list[dict[str, str]] = [
    {
        "title": "Aziel Digital Library",
        "url": "https://www.azielcorpuslibrary.net/",
        "source": "aziel-corpus",
        "blurb": "Public MASTER library. Search via FragGate slug=aziel-corpus op=search.",
        "tags": "library corpus aziel research",
    },
    {
        "title": "FragGate kernel",
        "url": "https://github.com/AzielEliab/fraggate",
        "source": "github",
        "blurb": "One door — discover, route, refuse. FG-0.1.",
        "tags": "fraggate mcp door kernel",
    },
    {
        "title": "aziel-runtime",
        "url": "https://github.com/AzielEliab/aziel-runtime",
        "source": "github",
        "blurb": "Catalog + FragGate + MCP. Host: https://aziel-runtime.vibelock.workers.dev/",
        "tags": "runtime mcp openapi catalog",
    },
    {
        "title": "AZMail (sibling, not this product)",
        "url": "https://github.com/AzielEliab/azmail",
        "source": "github",
        "blurb": "APP 1.0 Mail Airlock. Optional deep-link only. Not rebuilt here.",
        "tags": "azmail mail airlock sibling",
    },
    {
        "title": "GodLock",
        "url": "https://godlock.uk/",
        "source": "godlock.uk",
        "blurb": "Offline ABAD / hardening score. Not a VPN.",
        "tags": "godlock abad hardening",
    },
    {
        "title": "Aziel Eliab",
        "url": "https://www.azieleliab.com/",
        "source": "author",
        "blurb": "Public identity: Aziel Eliab only.",
        "tags": "author identity aziel eliab",
    },
    {
        "title": "Wikipedia",
        "url": "https://en.wikipedia.org/wiki/Main_Page",
        "source": "wikipedia",
        "blurb": "Cite the article. Encyclopedia, not a doxxing source.",
        "tags": "encyclopedia wiki research",
    },
    {
        "title": "MDN Web Docs",
        "url": "https://developer.mozilla.org/",
        "source": "mdn",
        "blurb": "Public web-platform documentation.",
        "tags": "html css javascript http browser",
    },
]


def _rank(query: str, item: dict[str, str]) -> int:
    q = query.lower().split()
    blob = " ".join([item.get("title", ""), item.get("blurb", ""), item.get("tags", "")]).lower()
    return sum(1 for w in q if w and w in blob)


def ethical_search(query: str, *, limit: int = 8) -> dict[str, Any]:
    ethics = classify_query(query)
    cited = [
        {"title": "Operator query (not executed as doxx/malware)", "url": "", "source": "ethics"}
    ]
    if ethics["refuse"]:
        return {
            "ok": False,
            "code": "ETHICS_REFUSE",
            "action": "ethical_search",
            "alias": "lamb_lens",
            "query": query,
            "ethics": ethics,
            "results": [],
            "citations": [],
            "advisory": True,
            "label": "AZNet / Lamb Lens — refused. Advisory ethical gate.",
            "note": "Cite sources. Refuse doxxing, credential harvest, malware lure.",
        }

    scored = sorted(CATALOG, key=lambda it: _rank(query, it), reverse=True)
    hits = [it for it in scored if _rank(query, it) > 0][: max(1, min(int(limit), 16))]
    if not hits:
        hits = [
            {
                "title": f"Wikipedia search: {query}",
                "url": "https://en.wikipedia.org/w/index.php?search=" + quote_plus(query),
                "source": "wikipedia",
                "blurb": "Open via AZBrowser preview (sandbox). Cite the article. Advisory.",
                "tags": "wikipedia",
            },
            {
                "title": f"Library lookup: {query}",
                "url": "https://www.azielcorpuslibrary.net/",
                "source": "aziel-corpus",
                "blurb": "FragGate: slug=aziel-corpus op=search. Read-only corpus.",
                "tags": "library",
            },
        ]
    citations = [{"title": h["title"], "url": h["url"], "source": h["source"]} for h in hits]
    return {
        "ok": True,
        "action": "ethical_search",
        "alias": "lamb_lens",
        "mode": "AZNet",
        "query": query,
        "ethics": ethics,
        "results": hits,
        "citations": citations,
        "advisory": True,
        "label": "AZNet / Lamb Lens — ethical internet search. Advisory. Cite sources.",
        "note": "Not a guaranteed index. Not doxxing. Not a malware lure.",
        "placeholder": cited,
    }
