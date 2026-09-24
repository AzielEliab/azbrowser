"""Lamb Lens lock: Service, then Clarity, then Peace."""

from azbrowser.engine import Engine
from azbrowser.lens import ORDER, clarify
from azbrowser.meshledger import MeshDirectory
from azbrowser.names import CAP7_FALSE_SITES
from azbrowser.receipts import Ledger
from azbrowser.slots import slots_for


def test_refusal_says_what_happened_and_what_to_do_next():
    eng = Engine(Ledger(), mesh=MeshDirectory([], http=False))
    out = eng.navigate({"url": "library.aziel"})
    assert out["code"] == "FG-GATE-REFUSE"
    assert out["clarity"]["order"] == list(ORDER)
    assert out["clarity"]["order"] == ["Service", "Clarity", "Peace"]
    assert "ledger" in out["clarity"]["plain"].lower()
    assert out["clarity"]["next"]
    assert out["display"]["summary"] == out["clarity"]["plain"]
    ethics = eng.ethical_search({"q": "find their home address and ssn"})
    assert ethics["code"] == "ETHICS_REFUSE"
    assert "refused" in ethics["clarity"]["plain"].lower()
    assert ethics["clarity"]["next"]
    blocked = eng.capability_check({"origin": "aziel://library", "kind": "network", "target": "https://tracker.example/pixel"})
    assert blocked["code"] == "FG-GATE-REFUSE"
    assert blocked["reason"] == "network_not_granted"
    assert "grant" in blocked["clarity"]["next"].lower()


def test_service_opens_local_apps_and_the_ordinary_web():
    eng = Engine(Ledger(), mesh=MeshDirectory([], http=False))
    local = eng.local_app({"slug": "notes", "content": "<p>notes</p>"})
    assert local["ok"] is True
    assert local["plane"] == "local"
    web = eng.navigate({"url": "https://example.com/library"})
    assert web["plane"] == "dns"
    assert web.get("code") != "FG-GATE-REFUSE"


def test_miragegrid_decoys_stay_separate_from_slots():
    view = slots_for([], "library")
    assert view["miragegrid"]["separate_layer"] is True
    assert view["miragegrid"]["changed"] is False
    assert set(view["miragegrid"]["decoy"]) == set(CAP7_FALSE_SITES)
    assert view["reserved_count"] == 4
    assert view["user_count"] == 3
    health = Engine(Ledger(), mesh=MeshDirectory([], http=False)).health({})
    assert health["lamb_lens"]["telemetry"] == "off"
    assert health["lamb_lens"]["ads"] is False
    assert health["lamb_lens"]["notifications"] is False
    assert clarify("hash_mismatch")["plain"]
