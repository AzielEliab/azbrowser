"""AZBrowser client for the AZNet sidenet. L0 stays put. Cap-7 is not ICANN."""

from __future__ import annotations

import json

from azbrowser.engine import OPS, Engine
from azbrowser.names import classify_destination
from azbrowser.receipts import Ledger
from azbrowser.sidenet import answer, pair_view


def test_l0_navigate_keeps_the_public_url():
    eng = Engine(Ledger())
    web = eng.navigate({"url": "https://example.com/docs"})
    assert web["plane"] == "dns"
    assert web["layer"] == "L0"
    assert web["l0"] is True
    assert web["url"] == "https://example.com/docs"
    assert web.get("code") != "FG-GATE-REFUSE"
    door = eng.navigate({"url": "http://127.0.0.1:8787/"})
    assert door["plane"] == "local"
    assert door["layer"] == "L0"
    assert door["source"] == "fraggate"


def test_l0_public_web_and_fraggate_stay():
    web = classify_destination("https://www.azieleliab.com/library")
    assert web["plane"] == "dns"
    assert web["layer"] == "L0"
    assert web["url"].startswith("https://www.azieleliab.com/")
    other = classify_destination("baku.az/city")
    assert other["plane"] == "dns"
    assert other["icann"] is True
    assert other["url"].startswith("https://baku.az/")
    door = classify_destination("http://127.0.0.1:8787/v1")
    assert door["plane"] == "local"
    assert door["layer"] == "L0"
    assert door["source"] == "fraggate"
    aziel = classify_destination("library.aziel")
    assert aziel["plane"] == "mesh"
    assert aziel["layer"] == "aziel"
    assert aziel["icann"] is False


def test_ops_stay_frozen():
    assert "pair" not in OPS
    assert "softwares" not in OPS
    assert "resolve" in OPS
    assert "navigate" in OPS


def test_cap7_absent_resolver_invents_nothing(monkeypatch):
    monkeypatch.setattr(
        "azbrowser.sidenet.lookup_cap7",
        lambda query, now: {"resolver": "absent", "ledger": "absent", "result": None},
    )
    eng = Engine(Ledger())
    out = eng.navigate({"url": "azgrid.az/shelf"})
    assert out["ok"] is False
    assert out["code"] == "RESOLVER_ABSENT"
    assert out["plane"] == "cap7"
    assert out["icann"] is False
    assert out["public_icann"] is False
    assert out["resolves_to_hub"] is False
    assert out["owner"] is None
    assert out["target"] is None
    assert out["html"] == ""
    assert out["url"] == ""
    assert "https://azgrid.az" not in json.dumps(out)
    assert out["receipt"]["action"] == "cap7"
    assert out["pair_token_echoed"] is False
    assert out["products_merged"] is False
    assert out["softwares_frozen"] is True


def test_cap7_answer_passes_aznet_fields_and_drops_secrets():
    classified = classify_destination("azgrid.az")

    def lookup(query, now):
        assert query == "azgrid.az"
        assert now == "2026-09-29T00:00:00Z"
        return {
            "resolver": "present",
            "ledger": "present",
            "result": {
                "ok": True,
                "code": "OK",
                "name": "azgrid.aziel",
                "owner": "#CPV0CWYPXP4",
                "target_kind": "hash",
                "target": "ab" * 32,
                "false_site": False,
                "resolves_to_hub": True,
                "hosts_payloads": True,
            },
        }

    out = answer(classified, now="2026-09-29T00:00:00Z", lookup=lookup)
    assert out["ok"] is True
    assert out["code"] == "OK"
    assert out["owner"] == "#CPV0CWYPXP4"
    assert out["target"] == "ab" * 32
    assert out["resolves_to_hub"] is False
    assert out["hosts_payloads"] is False
    assert out["html"] == ""
    assert out["icann_registration_by_this_code"] is False

    leaked = answer(
        classified,
        lookup=lambda query, now: {
            "resolver": "present",
            "ledger": "present",
            "result": {"ok": True, "code": "OK", "private_key": "secret-seed", "owner": "hidden"},
        },
    )
    assert leaked["code"] == "LEAK"
    assert "secret-seed" not in json.dumps(leaked)
    assert leaked["owner"] is None


def test_false_site_stays_off_public_dns():
    classified = classify_destination("azbooth.az")
    assert classified["false_site"] is True
    out = answer(
        classified,
        lookup=lambda query, now: {
            "resolver": "present",
            "ledger": "present",
            "result": {"ok": True, "code": "OK", "owner": "#AAAA", "target": "cd" * 32, "false_site": False},
        },
    )
    assert out["false_site"] is True
    assert out["resolves_to_hub"] is False
    assert out["icann"] is False
    assert "false site" in out["address_line"]


def test_pair_view_does_not_echo_a_token():
    view = pair_view()
    assert view["wrote"] is False
    assert view["pair_token_echoed"] is False
    assert "pair_token" not in view
    assert view["products_merged"] is False


def test_health_does_not_claim_a_resolve_route():
    health = Engine(Ledger()).health({})
    assert health["aznet"] is False
    assert health["client_of"] == "aznet"
    assert health["sidenet"]["l0_unbroken"] is True
    assert health["sidenet"]["softwares_frozen"] is True
    assert health["sidenet"]["aznet_http_resolve"] is False
    assert health["sidenet"]["cap7_public_icann"] is False
    assert health["mesh_browser"]["aznet_resolver"] is None
    assert health["mesh_browser"]["loopback_resolve_route"] is False
