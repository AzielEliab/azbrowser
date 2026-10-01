"""Unified op dispatcher — same ops for CLI, Worker /v1, OpenAPI, and MCP.

Agents and humans run the same software. Display envelopes for chat.
"""

from __future__ import annotations

from typing import Any

from .airlock import STAGES, airlock
from .ethics import classify_query
from .lens import clarify, ethics_clarity, lens_status
from .meshguard import NAME_MIN_AGE_SECONDS, NAME_MIN_WITNESSES, local_trust
from .meshledger import MESH_SECURITY_MODEL, MeshDirectory, directory_from_env, open_mesh, resolve_query, security_stamp
from .policy import design_page, design_remote_page
from .slots import slots_for
from .names import SPEC as MESH_SPEC
from .names import _handle_ok
from .names import classify_destination
from .sidenet import answer as sidenet_answer
from .sidenet import prepair
from .sidenet import sidenet_status
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
from .search import ethical_search, fetch_corpus
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
    "peer_block",
    "peer_unblock",
    "island_mode",
    "trust",
    "slots",
    "design_mode",
)

ALIASES = {
    "preview": "navigate",
    "lamb_lens": "ethical_search",
    "lamb_lens_search": "ethical_search",
    "search": "ethical_search",
    "az_search": "ethical_search",
    "airlock_ingest": "airlock",
    "tab_open": "tab_new",
    "receipt_list": "receipts",
    "verify": "receipt_verify",
    "resolve_name": "resolve",
    "local": "local_app",
    "trust_view": "trust",
    "peer_quarantine": "peer_block",
    "design": "design_mode",
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
        self.island = False
        self.blocked: set[str] = set()
        self.hash_matches: dict[str, int] = {}
        self.node_paths: dict[str, str] = {}
        self.airlock_history: list[dict[str, Any]] = []

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
                "results": [],
                "citations": [],
                "invented": False,
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
            "aznet": False,
            "client_of": "aznet",
            "sidenet": sidenet_status(),
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
                "aznet_resolver": None,
                "aznet_http_resolve": False,
                "loopback_resolve_route": False,
                "scripts_executed": False,
                "tracker_detection": False,
                "scanner": "absent",
                "network_wide_cutoff": False,
                "security_model": MESH_SECURITY_MODEL,
                "loopback_isolation": False,
                "phoenix": "local-wait-reseal",
                "public_hostname_resurrection": False,
                "island_mode": self.island,
                "name_min_age_seconds": NAME_MIN_AGE_SECONDS,
                "name_min_witnesses": NAME_MIN_WITNESSES,
                "reserved_slots": 4,
                "user_slots": 3,
                "design_mode": "local-tab",
                "themes": ["night", "day", "aziel"],
            },
            "lamb_lens": lens_status(),
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
        if url.startswith("azbrowser://search"):
            from urllib.parse import parse_qs, urlparse

            asked = (parse_qs(urlparse(url).query).get("q") or [""])[0]
            return self.ethical_search({"q": asked, "fetch_corpus": payload.get("fetch_corpus") is True})
        classified = classify_destination(url)
        if classified.get("plane") in {"cap7", "cite"}:
            return self._finish_sidenet(classified, payload)
        if classified.get("plane") == "mesh":
            pair = prepair(payload)
            if pair.get("blocked"):
                return self._finish_pair(pair, classified)
            return self._finish_mesh(classified, payload)
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
            "layer": "L0",
            "l0": True,
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

    def _expect_hash(self, payload: dict[str, Any]) -> str:
        raw = payload.get("expect_hash", payload.get("statement_hash", payload.get("object", "")))
        text = "" if raw is None else str(raw).strip().lower()
        return text if len(text) == 64 and all(ch in "0123456789abcdef" for ch in text) else ""

    def _guard(self, payload: dict[str, Any]) -> dict[str, Any]:
        posted = "relay" in payload
        reader = None if posted or payload.get("read_relay") is False else getattr(self.mesh, "relay_read", None)
        return {
            "island": self.island,
            "blocked": set(self.blocked),
            "operator_override": payload.get("operator_override") is True,
            "relay": payload.get("relay"),
            "expect_hash": self._expect_hash(payload),
            "read_relay": reader,
        }

    def _note_node_path(self, opened: dict[str, Any], classified: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        key = str(opened.get("name") or classified.get("name") or "").lower()
        if opened.get("reason") == "hash_mismatch":
            self.node_paths[key] = "local-wait"
        elif opened.get("hash_ok") and self.node_paths.get(key) == "local-wait":
            self.node_paths.pop(key, None)
            phoenix = dict(opened.get("phoenix") or security_stamp("").get("phoenix") or {})
            phoenix["state"] = "resealed"
            opened["phoenix"] = phoenix
            opened["node_path"] = "resealed"
            opened["node_path_isolated"] = False
        pair = prepair(payload)
        opened["pair_required"] = pair.get("required")
        opened["pair_ui"] = pair.get("pair_ui")
        opened["pair_token_echoed"] = False
        return opened

    def _finish_pair(self, pair: dict[str, Any], classified: dict[str, Any]) -> dict[str, Any]:
        rec = self._receipt(
            "pair_refuse",
            {
                "ok": False,
                "code": "AZN-PAIR-REQUIRED",
                "pair_status": "UNPAIRED",
                "pair_token_present": bool(pair.get("pair_token_present")),
                "pair_flag_ok": bool(pair.get("pair_flag_ok")),
                "pair_token_echoed": False,
                "name": classified.get("name") or "",
            },
        )
        return {
            "ok": False,
            "code": "AZN-PAIR-REQUIRED",
            "reason": "pair_required",
            "pair_ui": "broken",
            "pair_status": "UNPAIRED",
            "pair_required": True,
            "pair_token_present": bool(pair.get("pair_token_present")),
            "pair_flag_ok": bool(pair.get("pair_flag_ok")),
            "pair_flag_required": "azbrowser",
            "pair_token_echoed": False,
            "products_merged": False,
            "tunnel": False,
            "vpn": False,
            "pairing": "order and token only",
            "plane": "mesh",
            "html": "",
            "dns": False,
            "icann": False,
            "scripts_executed": False,
            **security_stamp(""),
            "receipt": rec,
            "limitation": LIMITATION,
            "clarity": {
                "code": "AZN-PAIR-REQUIRED",
                "reason": "pair_required",
                "plain": "AZNet garden verify needs a pair token and the azbrowser flag. The token was not shown.",
                "next": "Pair from AZNet, then try this name again. Ordinary web addresses stay open.",
            },
            "display": display_of(
                "Pair broken",
                "AZNet garden verify needs a pair token and the azbrowser flag. The token was not shown.",
                [("pair", "broken"), ("tunnel", "no")],
            ),
            "note": "Pair UI is for a broken pair. Relay name read does not require the pair. This is not a tunnel.",
        }

    def _finish_sidenet(self, classified: dict[str, Any], payload: dict[str, Any] | None = None) -> dict[str, Any]:
        now = payload.get("now") if isinstance(payload, dict) and isinstance(payload.get("now"), str) else None
        opened = sidenet_answer(classified, now=now)
        rec = self._receipt(
            str(opened.get("action") or "sidenet"),
            {
                "plane": opened.get("plane") or "",
                "ok": bool(opened.get("ok")),
                "code": opened.get("code") or "",
                "reason": opened.get("reason") or "",
                "name": opened.get("name") or "",
                "false_site": bool(opened.get("false_site")),
                "icann": False,
                "icann_registration_by_this_code": False,
                "resolves_to_hub": bool(opened.get("resolves_to_hub")),
                "hosts_payloads": False,
                "keys_leave_node": False,
                "pair_token_echoed": False,
            },
        )
        opened["receipt"] = rec
        opened["limitation"] = LIMITATION
        opened["display"] = display_of(
            str(opened.get("title") or "AZNet"),
            str(opened.get("summary") or ""),
            list(opened.get("fields") or []) + [("receipt", rec["hash"][:16])],
        )
        return opened

    def _finish_mesh(self, classified: dict[str, Any], payload: dict[str, Any] | None = None) -> dict[str, Any]:
        opened = self._note_node_path(open_mesh(self.mesh, classified, **self._guard(payload or {})), classified, payload or {})
        if opened.get("hash_ok") and opened.get("owner_handle"):
            who = str(opened["owner_handle"])
            self.hash_matches[who] = self.hash_matches.get(who, 0) + 1
        if opened.get("name_status") == "PENDING":
            action = "name_pending"
        elif opened.get("promoted"):
            action = "navigate"
        elif opened.get("quarantine") and opened.get("ok"):
            action = "airlock_hold"
        else:
            action = "gate_refuse"
        rec = self._receipt(
            action,
            {
                "plane": "mesh",
                "ok": bool(opened.get("ok")),
                "code": opened.get("code") or "",
                "reason": opened.get("reason") or "",
                "name": opened.get("name") or classified.get("name") or "",
                "handle": opened.get("owner_handle") or "",
                "hash": opened.get("content_hash") or "",
                "name_status": opened.get("name_status") or "",
                "promoted": bool(opened.get("promoted")),
                "keys_leave_node": False,
                "network_wide": False,
            },
        )
        opened["receipt"] = rec
        opened["limitation"] = LIMITATION
        if opened.get("name_status") == "PENDING":
            opened["display"] = display_of(
                "Pending",
                f"Pending name {opened.get('name')}. Not a verified site.",
                [("name", opened.get("name")), ("status", "PENDING"), ("receipt", rec["hash"][:16])],
            )
        elif opened.get("promoted"):
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
        elif opened.get("quarantine") and opened.get("ok"):
            tab = self.tabs.push(
                str(opened.get("url") or classified.get("url") or ""),
                str(opened.get("owner_handle") or opened.get("name") or "quarantine"),
                "mesh-quarantine",
            )
            tab["owner_handle"] = opened.get("owner_handle")
            opened["tab"] = tab
            opened["display"] = display_of(
                "Quarantine",
                f"Verified owner handle {opened.get('owner_handle')}. Scanner absent. Bytes not promoted and not run.",
                [("handle", opened.get("owner_handle")), ("scanner", "absent"), ("receipt", rec["hash"][:16])],
            )
        else:
            opened["display"] = display_of(
                "Blocked",
                f"FG-GATE-REFUSE — {opened.get('reason')}",
                [("code", "FG-GATE-REFUSE"), ("reason", opened.get("reason")), ("handle", opened.get("owner_handle") or "")],
            )
        return opened

    def _finish_local(self, classified: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        if str(classified.get("slug") or "") == "design" or payload.get("design") is True:
            return self.design_mode({"handle": payload.get("handle") or "", "remote": payload.get("remote") is True})
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
            "layer": "L0",
            "l0": True,
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
        return self.navigate({"url": url, "fetch": payload.get("fetch"), "operator_override": payload.get("operator_override") is True})

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

    def home(self, payload: dict[str, Any]) -> dict[str, Any]:
        asked = str(payload.get("url") or payload.get("name") or payload.get("q") or "").strip()
        if asked and (".aziel" in asked.lower() or asked.lower().startswith("aziel:")):
            body = dict(payload)
            body["url"] = asked
            return self.navigate(body)
        tab = self.tabs.home()
        rec = self._receipt("home", {"url": "azbrowser://newtab"})
        return {
            "ok": True,
            "action": "home",
            "sigil": SIGIL,
            "tab": tab if isinstance(tab, dict) and "id" in tab else self.tabs.current(),
            "receipt": rec,
            **security_stamp(""),
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
        corpus_rows = payload.get("corpus") if isinstance(payload.get("corpus"), list) else None
        corpus_status: dict[str, Any] | None = None
        if corpus_rows is None and payload.get("fetch_corpus") is True:
            fetched = fetch_corpus(q)
            corpus_rows = fetched.get("records") if isinstance(fetched.get("records"), list) else []
            corpus_status = {"asked": True, "ok": bool(fetched.get("ok")), "error": fetched.get("error") or ""}
        out = ethical_search(
            q,
            limit=int(payload.get("limit") or 8),
            records=self.mesh.records(),
            receipts=self.ledger.list(64),
            airlocks=list(self.airlock_history),
            corpus=corpus_rows,
            corpus_status=corpus_status,
            handle=str(payload.get("handle") or ""),
        )
        rec = self._receipt("ethical_search", {"q": q, "ok": out.get("ok"), "n": len(out.get("results") or [])})
        out["receipt"] = rec
        out["limitation"] = LIMITATION
        if out.get("ok"):
            from urllib.parse import quote

            tab = self.tabs.push("azbrowser://search?q=" + quote(q, safe=""), (q[:48] or "AZ Search"), "search")
            out["tab"] = tab
        out["display"] = display_of(
            "AZ Search",
            out.get("label") or "AZ Search.",
            [
                ("query", q),
                ("results", len(out.get("results") or [])),
                ("receipt", rec["hash"][:16]),
                ("sidenet", "AZNet"),
            ],
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
        self.airlock_history.append(
            {
                "url": url,
                "filename": filename,
                "verdict": str((out.get("scan") or {}).get("verdict") or ""),
                "hash": str(out.get("content_hash") or ""),
                "ok": out.get("ok"),
            }
        )
        self.airlock_history = self.airlock_history[-32:]
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
        handle = str(payload.get("handle") or "").strip().lower()
        raw = str(payload.get("name") or payload.get("url") or payload.get("q") or "").strip()
        if handle and not raw:
            raw = handle + ".aziel"
        classified = classify_destination(raw) if raw else {}
        if classified.get("plane") == "mesh":
            pair = prepair(payload)
            if pair.get("blocked"):
                return self._finish_pair(pair, classified)
        out = resolve_query(self.mesh, payload, **self._guard(payload))
        if classified.get("plane") == "mesh":
            out = self._note_node_path(out, classified, payload)
        if out.get("hash_ok") and out.get("owner_handle"):
            who = str(out["owner_handle"])
            self.hash_matches[who] = self.hash_matches.get(who, 0) + 1
        if out.get("name_status") == "PENDING":
            resolve_action = "name_pending"
        elif out.get("quarantine") and out.get("ok"):
            resolve_action = "airlock_hold"
        elif out.get("ok"):
            resolve_action = "resolve"
        else:
            resolve_action = "gate_refuse"
        rec = self._receipt(
            resolve_action,
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
        if out.get("name_status") == "PENDING":
            out["display"] = display_of(
                "Pending",
                f"Pending name {out.get('name')}. Not a verified site.",
                [("name", out.get("name")), ("status", "PENDING")],
            )
        elif out.get("ok") and out.get("quarantine"):
            out["display"] = display_of(
                "Quarantine",
                f"Verified owner handle {out.get('owner_handle')}. Scanner absent. Bytes not promoted and not run.",
                [("handle", out.get("owner_handle")), ("scanner", "absent")],
            )
        elif out.get("ok") and out.get("owner_handle"):
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
        elif out.get("plane") in {"cap7", "cite"}:
            out["display"] = display_of(
                str(out.get("title") or "AZNet"),
                str(out.get("summary") or out.get("note") or ""),
                list(out.get("fields") or []) + [("receipt", rec["hash"][:16])],
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

    def peer_block(self, payload: dict[str, Any]) -> dict[str, Any]:
        handle = str(payload.get("handle") or "").strip().lower()
        if not _handle_ok(handle):
            rec = self._receipt("peer_block", {"ok": False, "reason": "bad_handle", "network_wide": False})
            return {
                "ok": False,
                "code": "FG-GATE-REFUSE",
                "reason": "bad_handle",
                "network_wide": False,
                "receipt": rec,
                "limitation": LIMITATION,
                "display": display_of("Blocked", "FG-GATE-REFUSE — bad_handle", [("reason", "bad_handle")]),
            }
        self.blocked.add(handle)
        rec = self._receipt("peer_block", {"handle": handle, "scope": "this-node", "network_wide": False})
        return {
            "ok": True,
            "handle": handle,
            "peer_blocked": True,
            "scope": "this-node",
            "network_wide": False,
            "island_mode": self.island,
            "receipt": rec,
            "limitation": LIMITATION,
            "note": "This handle is blocked on this node only. There is no network-wide cutoff.",
            "display": display_of(
                "Peer blocked",
                f"{handle} is blocked on this node only.",
                [("handle", handle), ("scope", "this-node"), ("receipt", rec["hash"][:16])],
            ),
        }

    def peer_unblock(self, payload: dict[str, Any]) -> dict[str, Any]:
        handle = str(payload.get("handle") or "").strip().lower()
        if not _handle_ok(handle):
            rec = self._receipt("peer_unblock", {"ok": False, "reason": "bad_handle", "network_wide": False})
            return {
                "ok": False,
                "code": "FG-GATE-REFUSE",
                "reason": "bad_handle",
                "network_wide": False,
                "receipt": rec,
                "limitation": LIMITATION,
                "display": display_of("Blocked", "FG-GATE-REFUSE — bad_handle", [("reason", "bad_handle")]),
            }
        self.blocked.discard(handle)
        rec = self._receipt("peer_unblock", {"handle": handle, "scope": "this-node", "network_wide": False})
        return {
            "ok": True,
            "handle": handle,
            "peer_blocked": False,
            "scope": "this-node",
            "network_wide": False,
            "receipt": rec,
            "limitation": LIMITATION,
            "display": display_of(
                "Peer unblocked",
                f"{handle} can be opened on this node again.",
                [("handle", handle), ("receipt", rec["hash"][:16])],
            ),
        }

    def island_mode(self, payload: dict[str, Any]) -> dict[str, Any]:
        enabled = payload.get("enabled")
        if not isinstance(enabled, bool):
            rec = self._receipt("island_mode", {"ok": False, "reason": "bad_island", "network_wide": False})
            return {
                "ok": False,
                "code": "FG-GATE-REFUSE",
                "reason": "bad_island",
                "network_wide": False,
                "receipt": rec,
                "limitation": LIMITATION,
                "display": display_of("Blocked", "FG-GATE-REFUSE — bad_island", [("reason", "bad_island")]),
            }
        self.island = enabled
        rec = self._receipt("island_mode", {"enabled": enabled, "scope": "this-node", "network_wide": False})
        summary = (
            "This node left the mesh. Local apps and normal DNS still run."
            if enabled
            else "This node rejoined. Earlier receipts were not rewritten."
        )
        return {
            "ok": True,
            "island_mode": enabled,
            "local_runtime": True,
            "scope": "this-node",
            "network_wide": False,
            "receipt": rec,
            "limitation": LIMITATION,
            "note": summary + " No other node was cut off.",
            "display": display_of("Island mode", summary, [("enabled", enabled), ("receipt", rec["hash"][:16])]),
        }

    def trust(self, payload: dict[str, Any]) -> dict[str, Any]:
        handle = str(payload.get("handle") or "").strip().lower()
        if not _handle_ok(handle):
            rec = self._receipt("trust", {"ok": False, "reason": "bad_handle"})
            return {
                "ok": False,
                "code": "FG-GATE-REFUSE",
                "reason": "bad_handle",
                "receipt": rec,
                "limitation": LIMITATION,
                "display": display_of("Blocked", "FG-GATE-REFUSE — bad_handle", [("reason", "bad_handle")]),
            }
        record = self.mesh.lookup(name=f"{handle}.aziel", handle="")
        if record is None:
            record = self.mesh.lookup(name="", handle=handle)
        out = local_trust(
            handle=handle,
            record=record,
            equivocating=handle in self.mesh.equivocations,
            hash_matches=self.hash_matches.get(handle, 0),
            peer_blocked=handle in self.blocked,
            island_mode=self.island,
        )
        rec = self._receipt(
            "trust",
            {
                "handle": handle,
                "local_only": True,
                "public_ranking": False,
                "equivocating": out["equivocating"],
                "hash_matches": out["hash_matches"],
            },
        )
        out["receipt"] = rec
        out["limitation"] = LIMITATION
        out["display"] = display_of(
            "Local trust",
            f"Local trust for {handle}. Chain age, witnessed heartbeats, hash matches, vouches, equivocation.",
            [
                ("handle", handle),
                ("name_status", out.get("name_status")),
                ("heartbeats_witnessed", out.get("heartbeats_witnessed")),
                ("hash_matches", out.get("hash_matches")),
                ("equivocating", out.get("equivocating")),
            ],
        )
        return out

    def slots(self, payload: dict[str, Any]) -> dict[str, Any]:
        handle = str(payload.get("handle") or "").strip().lower()
        if handle and not _handle_ok(handle):
            rec = self._receipt("slots", {"ok": False, "reason": "bad_handle"})
            return {
                "ok": False,
                "code": "FG-GATE-REFUSE",
                "reason": "bad_handle",
                "receipt": rec,
                "limitation": LIMITATION,
                "display": display_of("Blocked", "FG-GATE-REFUSE — bad_handle", [("reason", "bad_handle")]),
            }
        out = slots_for(self.mesh.records(), handle)
        rec = self._receipt("slots", {"handle": handle, "reserved": 4, "user": 3, "miragegrid_changed": False})
        out["receipt"] = rec
        out["limitation"] = LIMITATION
        out["display"] = display_of(
            "Domain slots",
            "Four reserved hub mirrors and three user slots. MirageGrid factory names are unchanged.",
            [("handle", handle or "unset"), ("automatic", out.get("automatic_name") or "unset")],
        )
        return out

    def design_mode(self, payload: dict[str, Any]) -> dict[str, Any]:
        if payload.get("remote") is True:
            rec = self._receipt("design_mode", {"ok": False, "reason": "design_mode_local_only", "remote": True})
            return {
                "ok": False,
                "code": "FG-GATE-REFUSE",
                "reason": "design_mode_local_only",
                "policy_page": True,
                "html": design_remote_page(),
                "scripts_executed": False,
                "executed": False,
                "plane": "local",
                "keys_leave_node": False,
                "receipt": rec,
                "limitation": LIMITATION,
                "note": "Design mode is refused off the hosting node. Nothing was published.",
                "display": display_of(
                    "Blocked",
                    "FG-GATE-REFUSE — design_mode_local_only",
                    [("reason", "design_mode_local_only")],
                ),
            }
        handle = str(payload.get("handle") or "").strip().lower()
        slot_view = slots_for(self.mesh.records(), handle if _handle_ok(handle) else "")
        html = design_page(slot_view)
        origin = "azbrowser://local/design"
        rec = self._receipt(
            "design_mode",
            {"origin": origin, "local": True, "publish": False, "keys_leave_node": False},
        )
        tab = self.tabs.push(origin, "Design", "local-app")
        return {
            "ok": True,
            "action": "design_mode",
            "plane": "local",
            "kind": "local-app",
            "origin": origin,
            "url": origin,
            "display_url": origin,
            "slug": "design",
            "source": "local",
            "data_stays_local": True,
            "uploaded": False,
            "publish": False,
            "keys_leave_node": False,
            "scripts_executed": False,
            "executed": False,
            "html": html,
            "shell_page": True,
            "slots": slot_view,
            "title": "Design",
            "host": "127.0.0.1",
            "tab": tab,
            "receipt": rec,
            "icann": False,
            "note": "Local design tab. qnm-node hosts the designer. This shell does not publish and does not hold the handle key.",
            "display": display_of(
                "Design mode",
                "Local tab only. Publish stays on qnm-node. The handle key stays on the node.",
                [("origin", origin), ("receipt", rec["hash"][:16])],
            ),
            "limitation": LIMITATION,
        }

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


def _stamp(out: Any) -> Any:
    """Plain reason and next step on every refusal. Success payloads stay as they are."""
    if not isinstance(out, dict):
        return out
    code = str(out.get("code") or "")
    if code == "ETHICS_REFUSE":
        ethics = out.get("ethics") if isinstance(out.get("ethics"), dict) else {}
        clarity = ethics_clarity(list(ethics.get("reasons") or []))
        out["clarity"] = clarity
        out["display"] = display_of(
            "Refused",
            str(clarity["plain"]),
            [("code", "ETHICS_REFUSE"), ("next", clarity["next"])],
        )
        return out
    if code == "FG-GATE-REFUSE":
        reason = str(out.get("reason") or "")
        clarity = clarify(reason)
        out["clarity"] = clarity
        display = out.get("display") if isinstance(out.get("display"), dict) else None
        summary = str((display or {}).get("summary") or "")
        title = str((display or {}).get("title") or "")
        if display is None or title == "Blocked" or "FG-GATE-REFUSE" in summary:
            out["display"] = display_of(
                "Blocked",
                str(clarity["plain"]),
                [("code", "FG-GATE-REFUSE"), ("reason", reason), ("next", clarity["next"])],
            )
        return out
    return out


def _bind_lens(fn):
    def inner(self, payload=None, *args, **kwargs):
        body = {} if payload is None else payload
        out = fn(self, body, *args, **kwargs)
        return _stamp(out)

    inner.__name__ = getattr(fn, "__name__", "op")
    inner.__doc__ = getattr(fn, "__doc__", None)
    return inner


for _op in OPS:
    _current = getattr(Engine, _op, None)
    if callable(_current):
        setattr(Engine, _op, _bind_lens(_current))
