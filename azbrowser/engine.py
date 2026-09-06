"""Unified op dispatcher — same ops for CLI, Worker /v1, OpenAPI, and MCP.

Agents and humans run the same software. Display envelopes for chat.
"""

from __future__ import annotations

from typing import Any

from .airlock import STAGES, airlock
from .ethics import classify_query
from .preview import preview_url, sanitize_url, scrub_html
from .receipts import Ledger
from .mesh import mesh_pointer
from .meta import (
    AZMAIL,
    FRAGGATE,
    FRAGGATE_CALL,
    HOST,
    IDENTITY,
    LIMITATION,
    RUNTIME,
    SIGIL,
    SPEC,
    __version__,
)
from .search import ethical_search
from .tabs import TabSession

OPS = (
    "health",
    "skill",
    "navigate",
    "preview",
    "reload",
    "back",
    "forward",
    "home",
    "tab_new",
    "tab_close",
    "tab_switch",
    "tab_list",
    "ethical_search",
    "lamb_lens",
    "search",
    "airlock",
    "airlock_status",
    "receipt",
    "receipts",
    "receipt_verify",
    "scrub",
    "ethics_gate",
)

ALIASES = {
    "preview": "navigate",
    "lamb_lens": "ethical_search",
    "lamb_lens_search": "ethical_search",
    "search": "ethical_search",
    "airlock_ingest": "airlock",
    "tab_open": "tab_new",
    "receipt_list": "receipts",
    "verify": "receipt_verify",
}


def display_of(title: str, summary: str, fields: list[tuple[str, Any]] | None = None) -> dict[str, Any]:
    rows = [{"label": k, "value": str(v)} for k, v in (fields or [])]
    return {
        "title": title,
        "summary": summary,
        "fields": rows,
        "next": "Show this output to the user, then take the next input.",
    }


class Engine:
    """In-process AZBrowser engine. Ephemeral tabs; optional JSONL receipts."""

    def __init__(self, ledger: Ledger | None = None) -> None:
        self.tabs = TabSession()
        self.ledger = ledger or Ledger()

    def _receipt(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self.ledger.append(action, payload, tab_id=self.tabs.active)

    def _gate(self, text: str) -> dict[str, Any] | None:
        ethics = classify_query(text)
        if ethics["refuse"]:
            rec = self._receipt("ethics_refuse", {"reasons": ethics["reasons"], "text_len": len(text)})
            return {
                "ok": False,
                "code": "ETHICS_REFUSE",
                "ethics": ethics,
                "receipt": rec,
                "display": display_of(
                    "AZNet refused",
                    "Advisory ethical gate refused this input.",
                    [("reasons", ",".join(ethics["reasons"])), ("receipt", rec["hash"][:16])],
                ),
                "limitation": LIMITATION,
            }
        return None

    def health(self, _payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "ok": True,
            "product": "azbrowser",
            "name": "AZBrowser",
            "aznet": True,
            "version": __version__,
            "spec": SPEC,
            "identity": IDENTITY,
            "author": IDENTITY,
            "ops": list(OPS),
            "door": "fraggate",
            "slug": "azbrowser",
            "agent_path": FRAGGATE_CALL,
            "runtime": RUNTIME,
            "kernel": FRAGGATE,
            "host": HOST,
            "sigil": SIGIL,
            "azmail": AZMAIL,
            "mesh": mesh_pointer(),
            "kv_increment": False,
            "stored": False,
            "chromium": False,
            "limitation": LIMITATION,
            "display": display_of("AZBrowser health", "Phase 1 research shell. Dual surface.", [("version", __version__), ("ops", len(OPS))]),
        }

    def skill(self, _payload: dict[str, Any]) -> dict[str, Any]:
        from pathlib import Path

        skill = Path(__file__).resolve().parent.parent / "SKILL.md"
        text = skill.read_text(encoding="utf-8") if skill.exists() else LIMITATION
        return {"ok": True, "markdown": text, "limitation": LIMITATION}

    def navigate(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = str(payload.get("url") or payload.get("q") or "").strip()
        if not url:
            return {"ok": False, "error": "url required", "limitation": LIMITATION}
        refused = self._gate(url)
        if refused:
            return refused
        safe = sanitize_url(url)
        if safe.get("suggest_search"):
            return self.ethical_search({"q": url})
        preview = preview_url(url, fetch=bool(payload.get("fetch")))
        if not preview.get("ok") and preview.get("code") == "ETHICS_REFUSE":
            rec = self._receipt("ethics_refuse", {"url": url})
            preview["receipt"] = rec
            preview["display"] = display_of("Navigate refused", "Ethics gate.", [("url", url)])
            return preview
        tab = self.tabs.push(preview.get("url") or url, preview.get("title") or url, "preview")
        rec = self._receipt("navigate", {"url": preview.get("url") or url, "ok": preview.get("ok"), "hash": preview.get("content_hash") or ""})
        preview.update({"tab": tab, "receipt": rec, "limitation": LIMITATION})
        preview["display"] = display_of(
            preview.get("title") or "Preview",
            "Sandbox preview (not Chromium).",
            [("url", preview.get("url")), ("receipt", rec["hash"][:16]), ("ok", preview.get("ok"))],
        )
        return preview

    def reload(self, payload: dict[str, Any]) -> dict[str, Any]:
        tab = self.tabs.current()
        url = str(payload.get("url") or tab.get("url") or "")
        if url.startswith("azbrowser://"):
            rec = self._receipt("reload", {"url": url})
            return {"ok": True, "action": "reload", "tab": tab, "receipt": rec, "display": display_of("Reload", "Home shell reloaded.", [("receipt", rec["hash"][:16])])}
        return self.navigate({"url": url, "fetch": payload.get("fetch")})

    def back(self, _payload: dict[str, Any]) -> dict[str, Any]:
        moved = self.tabs.back()
        rec = self._receipt("back", {"ok": moved.get("ok"), "url": (moved.get("tab") or {}).get("url")})
        moved["receipt"] = rec
        moved["display"] = display_of("Back", "Tab history back.", [("ok", moved.get("ok")), ("receipt", rec["hash"][:16])])
        return moved

    def forward(self, _payload: dict[str, Any]) -> dict[str, Any]:
        moved = self.tabs.forward()
        rec = self._receipt("forward", {"ok": moved.get("ok"), "url": (moved.get("tab") or {}).get("url")})
        moved["receipt"] = rec
        moved["display"] = display_of("Forward", "Tab history forward.", [("ok", moved.get("ok")), ("receipt", rec["hash"][:16])])
        return moved

    def home(self, _payload: dict[str, Any]) -> dict[str, Any]:
        tab = self.tabs.home()
        rec = self._receipt("home", {"url": "azbrowser://newtab"})
        return {
            "ok": True,
            "action": "home",
            "sigil": SIGIL,
            "tab": tab if isinstance(tab, dict) and "id" in tab else self.tabs.current(),
            "receipt": rec,
            "display": display_of("Home", "Everblooming sigil home.", [("sigil", SIGIL), ("receipt", rec["hash"][:16])]),
            "limitation": LIMITATION,
        }

    def tab_new(self, payload: dict[str, Any]) -> dict[str, Any]:
        out = self.tabs.new(str(payload.get("title") or "New Tab"))
        rec = self._receipt("tab_new", {"tab_id": out["tab"]["id"]})
        out["receipt"] = rec
        out["display"] = display_of("New tab", "Isolated tab UX.", [("id", out["tab"]["id"]), ("receipt", rec["hash"][:16])])
        return out

    def tab_close(self, payload: dict[str, Any]) -> dict[str, Any]:
        out = self.tabs.close(str(payload.get("tab_id") or self.tabs.active))
        rec = self._receipt("tab_close", {"ok": out.get("ok")})
        out["receipt"] = rec
        out["display"] = display_of("Close tab", "Tab closed or refused.", [("ok", out.get("ok")), ("receipt", rec["hash"][:16])])
        return out

    def tab_switch(self, payload: dict[str, Any]) -> dict[str, Any]:
        out = self.tabs.switch(str(payload.get("tab_id") or ""))
        rec = self._receipt("tab_switch", {"ok": out.get("ok"), "tab_id": payload.get("tab_id")})
        out["receipt"] = rec
        out["display"] = display_of("Switch tab", "Active tab changed.", [("ok", out.get("ok")), ("receipt", rec["hash"][:16])])
        return out

    def tab_list(self, _payload: dict[str, Any]) -> dict[str, Any]:
        out = self.tabs.list()
        rec = self._receipt("tab_list", {"count": len(out["tabs"])})
        out["receipt"] = rec
        out["display"] = display_of("Tabs", f"{len(out['tabs'])} open.", [("active", out["active"]), ("receipt", rec["hash"][:16])])
        return out

    def ethical_search(self, payload: dict[str, Any]) -> dict[str, Any]:
        q = str(payload.get("q") or payload.get("query") or payload.get("url") or "").strip()
        if not q:
            return {"ok": False, "error": "q required", "limitation": LIMITATION}
        refused = self._gate(q)
        if refused:
            return refused
        out = ethical_search(q, limit=int(payload.get("limit") or 8))
        rec = self._receipt("ethical_search", {"q": q, "ok": out.get("ok"), "n": len(out.get("results") or [])})
        out["receipt"] = rec
        out["limitation"] = LIMITATION
        out["display"] = display_of(
            "AZNet / Lamb Lens",
            out.get("label") or "Ethical search.",
            [("query", q), ("results", len(out.get("results") or [])), ("receipt", rec["hash"][:16])],
        )
        return out

    def airlock(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = str(payload.get("url") or "")
        content = payload.get("content")
        filename = str(payload.get("filename") or "")
        refused = self._gate(" ".join([url, filename, str(content or "")[:200]]))
        if refused:
            return refused
        out = airlock(url=url, content=content, filename=filename, fetch=bool(payload.get("fetch")))
        rec = self._receipt(
            "airlock",
            {"url": url, "ok": out.get("ok"), "hash": out.get("content_hash") or "", "verdict": (out.get("scan") or {}).get("verdict")},
        )
        out["receipt"] = rec
        out["limitation"] = LIMITATION
        hashes = [s.get("hash", "")[:12] for s in out.get("stages") or []]
        out["display"] = display_of(
            "Airlock",
            "download → scan → scrub → verify → vault",
            [("ok", out.get("ok")), ("stages", " ".join(hashes)), ("receipt", rec["hash"][:16])],
        )
        return out

    def airlock_status(self, _payload: dict[str, Any]) -> dict[str, Any]:
        rec = self._receipt("airlock_status", {"pipeline": list(STAGES)})
        return {
            "ok": True,
            "pipeline": list(STAGES),
            "receipt": rec,
            "display": display_of("Airlock status", "Five stages.", [("pipeline", " → ".join(STAGES))]),
            "limitation": LIMITATION,
        }

    def receipt(self, payload: dict[str, Any]) -> dict[str, Any]:
        action = str(payload.get("action") or "note")
        rec = self._receipt(action, dict(payload.get("payload") or {"note": payload.get("note") or "manual"}))
        return {"ok": True, "receipt": rec, "display": display_of("Receipt", "Appended.", [("hash", rec["hash"])]), "limitation": LIMITATION}

    def receipts(self, payload: dict[str, Any]) -> dict[str, Any]:
        rows = self.ledger.list(int(payload.get("limit") or 64))
        return {
            "ok": True,
            "count": len(self.ledger.entries),
            "tip": self.ledger.tip,
            "receipts": rows,
            "display": display_of("Receipts", f"{len(self.ledger.entries)} append-only.", [("tip", self.ledger.tip[:16])]),
            "limitation": LIMITATION,
        }

    def receipt_verify(self, _payload: dict[str, Any]) -> dict[str, Any]:
        out = self.ledger.verify()
        out["display"] = display_of("Verify receipts", "Chain walk.", [("ok", out.get("ok")), ("count", out.get("count"))])
        out["limitation"] = LIMITATION
        return out

    def scrub(self, payload: dict[str, Any]) -> dict[str, Any]:
        out = scrub_html(str(payload.get("html") or payload.get("text") or ""))
        rec = self._receipt("scrub", {"kinds": out.get("stripped_kinds")})
        out.update({"ok": True, "receipt": rec, "limitation": LIMITATION})
        out["display"] = display_of("Scrub", "Scripts/embeds stripped.", [("kinds", ",".join(out.get("stripped_kinds") or []))])
        return out

    def ethics_gate(self, payload: dict[str, Any]) -> dict[str, Any]:
        q = str(payload.get("q") or payload.get("text") or payload.get("url") or "")
        ethics = classify_query(q)
        rec = self._receipt("ethics_gate", {"refuse": ethics["refuse"], "reasons": ethics["reasons"]})
        return {
            "ok": True,
            "ethics": ethics,
            "receipt": rec,
            "display": display_of("Ethics gate", "Advisory Lamb Lens.", [("refuse", ethics["refuse"]), ("reasons", ",".join(ethics["reasons"]))]),
            "limitation": LIMITATION,
        }

    def call(self, op: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        name = ALIASES.get(op, op)
        if name not in OPS and op not in OPS:
            return {
                "ok": False,
                "code": "FG-HALLUC-TOOL",
                "error": "unknown op",
                "op": op,
                "ops": list(OPS),
                "door": "fraggate",
                "slug": "azbrowser",
                "display": display_of("Unknown op", "Refused. Discover first.", [("op", op)]),
            }
        fn = getattr(self, name)
        return fn(dict(payload or {}))


_ENGINE: Engine | None = None


def default_engine() -> Engine:
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = Engine()
    return _ENGINE


def dispatch(op: str, payload: dict[str, Any] | None = None, engine: Engine | None = None) -> dict[str, Any]:
    return (engine or default_engine()).call(op, payload)
