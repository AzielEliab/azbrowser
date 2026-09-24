"""Unified op dispatcher — same ops for CLI, Worker /v1, OpenAPI, and MCP.

Agents and humans run the same software. Display envelopes for chat.
"""

from __future__ import annotations

from typing import Any

from .airlock import STAGES, airlock
from .ethics import classify_query
from .meshledger import MeshDirectory, directory_from_env, open_mesh, resolve_query
from .names import SPEC as MESH_SPEC
from .names import classify_destination
from .preview import preview_url, sanitize_url, scrub_html
from .receipts import Ledger
from .sandbox import CapabilitySandbox
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
    "resolve",
    "capability_grant",
    "capability_check",
    "local_app",
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
    "resolve_name": "resolve",
    "local": "local_app",
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

    def __init__(self, ledger: Ledger | None = None, mesh: MeshDirectory | None = None) -> None:
        self.tabs = TabSession()
        self.ledger = ledger or Ledger()
        self.mesh = mesh if mesh is not None else directory_from_env()
        self.sandbox = CapabilitySandbox(self.ledger)

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
            "mesh_browser": {
                "spec": MESH_SPEC,
                "aziel_tld_icann": False,
                "regular_browsers_resolve_aziel": False,
                "keys_leave_node": False,
                "paired_with": "aznet",
                "merged_with_aznet": False,
                "qnm": "http://127.0.0.1:8891",
                "aznet_resolver": "http://127.0.0.1:8771/v1/resolve",
                "scripts_executed": False,
                "tracker_detection": False,
            },
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
        classified = classify_destination(url)
        if classified.get("plane") == "mesh":
            return self._finish_mesh(classified)
        if classified.get("plane") == "local":
            return self._finish_local(classified, payload)
        if classified.get("suggest_search"):
            return self.ethical_search({"q": url})
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
        rec = self._receipt("navigate", {"url": preview.get("url") or url, "ok": preview.get("ok"), "hash": preview.get("content_hash") or "", "plane": "dns"})
        preview.update({
            "tab": tab,
            "receipt": rec,
            "limitation": LIMITATION,
            "plane": "dns",
            "dns": True,
            "tls": "standard",
            "icann": True,
        })
        preview["display"] = display_of(
            preview.get("title") or "Preview",
            "Sandbox preview (not Chromium).",
            [("url", preview.get("url")), ("receipt", rec["hash"][:16]), ("ok", preview.get("ok"))],
        )
        return preview

    def _finish_mesh(self, classified: dict[str, Any]) -> dict[str, Any]:
        opened = open_mesh(self.mesh, classified)
        rec = self._receipt(
            "navigate" if opened.get("ok") else "gate_refuse",
            {
                "plane": "mesh",
                "ok": bool(opened.get("ok")),
                "code": opened.get("code") or "",
                "reason": opened.get("reason") or "",
                "name": opened.get("name") or classified.get("name") or "",
                "handle": opened.get("owner_handle") or "",
                "hash": opened.get("content_hash") or "",
                "keys_leave_node": False,
            },
        )
        opened["receipt"] = rec
        opened["limitation"] = LIMITATION
        if opened.get("ok"):
            tab = self.tabs.push(
                str(opened.get("url") or classified.get("url") or ""),
                str(opened.get("owner_handle") or opened.get("name") or "mesh"),
                "mesh",
            )
            tab["owner_handle"] = opened.get("owner_handle")
            opened["tab"] = tab
            opened["display"] = display_of(
                f"Owner {opened.get('owner_handle')}",
                f"Verified owner handle {opened.get('owner_handle')}.",
                [("handle", opened.get("owner_handle")), ("name", opened.get("name")), ("receipt", rec["hash"][:16])],
            )
        else:
            opened["display"] = display_of(
                "Blocked",
                f"FG-GATE-REFUSE — {opened.get('reason')}",
                [("code", "FG-GATE-REFUSE"), ("reason", opened.get("reason")), ("handle", opened.get("owner_handle") or "")],
            )
        return opened

    def _finish_local(self, classified: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        content = payload.get("content")
        html = scrub_html(str(content))["html"] if content is not None else ""
        origin = str(classified.get("origin") or "")
        rec = self._receipt(
            "local_app",
            {
                "origin": origin,
                "slug": classified.get("slug"),
                "source": classified.get("source"),
                "uploaded": False,
                "data_stays_local": True,
            },
        )
        tab = self.tabs.push(str(classified.get("url") or origin), str(classified.get("slug") or "local"), "local-app")
        return {
            "ok": True,
            "action": "navigate",
            "plane": "local",
            "kind": "local-app",
            "origin": origin,
            "url": classified.get("url"),
            "display_url": classified.get("display_url"),
            "slug": classified.get("slug"),
            "source": classified.get("source"),
            "data_stays_local": True,
            "uploaded": False,
            "sandbox": self.sandbox.policy(),
            "scripts_executed": False,
            "html": html,
            "title": classified.get("slug"),
            "host": "127.0.0.1",
            "tab": tab,
            "receipt": rec,
            "keys_leave_node": False,
            "icann": False,
            "note": "Local app tab. Same capability sandbox as mesh apps. Data stays on this machine. This shell does not upload it and does not execute scripts.",
            "display": display_of(
                "Local app",
                f"Local app {classified.get('slug')}. Data stays on this machine.",
                [("origin", origin), ("receipt", rec["hash"][:16])],
            ),
            "limitation": LIMITATION,
        }

    def reload(self, payload: dict[str, Any]) -> dict[str, Any]:
        tab = self.tabs.current()
        url = str(payload.get("url") or tab.get("url") or "")
        if url.startswith("azbrowser://newtab"):
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

    def resolve(self, payload: dict[str, Any]) -> dict[str, Any]:
        out = resolve_query(self.mesh, payload)
        rec = self._receipt(
            "resolve" if out.get("ok") else "gate_refuse",
            {
                "ok": bool(out.get("ok")),
                "plane": out.get("plane") or "",
                "reason": out.get("reason") or "",
                "name": out.get("name") or out.get("url") or "",
                "handle": out.get("owner_handle") or payload.get("handle") or "",
                "keys_leave_node": False,
            },
        )
        out["receipt"] = rec
        out["limitation"] = LIMITATION
        if out.get("ok") and out.get("owner_handle"):
            out["display"] = display_of(
                f"Owner {out.get('owner_handle')}",
                f"Resolved {out.get('name')}. Verified owner handle {out.get('owner_handle')}.",
                [("handle", out.get("owner_handle")), ("receipt", rec["hash"][:16])],
            )
        elif out.get("code") == "FG-GATE-REFUSE":
            out["display"] = display_of(
                "Blocked",
                f"FG-GATE-REFUSE — {out.get('reason')}",
                [("code", "FG-GATE-REFUSE"), ("reason", out.get("reason"))],
            )
        else:
            out["display"] = display_of(
                "Resolve",
                out.get("note") or ("Normal DNS." if out.get("plane") == "dns" else "Resolved."),
                [("plane", out.get("plane")), ("url", out.get("url")), ("receipt", rec["hash"][:16])],
            )
        return out

    def capability_grant(self, payload: dict[str, Any]) -> dict[str, Any]:
        out = self.sandbox.grant(
            str(payload.get("origin") or ""),
            str(payload.get("capability") or payload.get("kind") or ""),
            str(payload.get("resource") or payload.get("target") or ""),
            tab_id=self.tabs.active,
        )
        out["limitation"] = LIMITATION
        out["keys_leave_node"] = False
        if out.get("ok"):
            out["display"] = display_of(
                "Capability grant",
                "Grant recorded as a hash-chained receipt. The handle key stays on the local node.",
                [("capability", (out.get("grant") or {}).get("capability")), ("receipt", out["receipt"]["hash"][:16])],
            )
        else:
            out["display"] = display_of("Blocked", f"FG-GATE-REFUSE — {out.get('reason')}", [("reason", out.get("reason"))])
        return out

    def capability_check(self, payload: dict[str, Any]) -> dict[str, Any]:
        out = self.sandbox.check(
            str(payload.get("origin") or ""),
            str(payload.get("kind") or payload.get("capability") or ""),
            str(payload.get("target") or payload.get("resource") or ""),
            tab_id=self.tabs.active,
        )
        out["limitation"] = LIMITATION
        if out.get("ok"):
            out["display"] = display_of(
                "Capability allowed",
                "Request allowed under a receipted grant or the origin's own storage.",
                [("kind", out.get("kind")), ("receipt", (out.get("receipt") or {}).get("hash", "")[:16])],
            )
        else:
            out["display"] = display_of(
                "Blocked",
                f"FG-GATE-REFUSE — {out.get('reason')}",
                [("code", "FG-GATE-REFUSE"), ("reason", out.get("reason"))],
            )
        return out

    def local_app(self, payload: dict[str, Any]) -> dict[str, Any]:
        slug = str(payload.get("slug") or payload.get("app") or "app")
        source = str(payload.get("source") or "qnm")
        classified = classify_destination(f"azbrowser://local/{slug}")
        if source in {"qnm", "fraggate", "azbrowser"}:
            classified["source"] = source
        return self._finish_local(classified, payload)

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
