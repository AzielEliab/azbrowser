"""Wave 3: slots, isolation policy, and local design mode."""

from __future__ import annotations

from azbrowser.engine import Engine
from azbrowser.meshledger import MeshDirectory
from azbrowser.names import CAP7_ALLOWLIST, CAP7_FALSE_SITES
from azbrowser.receipts import Ledger
from azbrowser.slots import RESERVED_SLOTS
from tests.test_mesh_browser import engine_with, signed_record


def test_slots_keep_reserved_mirrors_and_three_user_names():
    hosts = {row["host"] for row in RESERVED_SLOTS}
    assert hosts == {
        "az.azieleliab.az",
        "az.azielcorpuslibrary.az",
        "az.godlock.az",
        "az.hedidntjump.az",
    }
    assert CAP7_ALLOWLIST == frozenset({"azgrid.az", "azcloak.az", "azvault.az", "azshift.az"})
    assert CAP7_FALSE_SITES == frozenset({"azbooth.az", "azflag.az", "azstandby.az"})
    library = signed_record()
    notes = signed_record(name="notes.library.aziel", handle="library", page="<p>notes</p>", seed=bytes(range(32)))
    notes["slot"] = 1
    eng = Engine(Ledger(), mesh=MeshDirectory([library, notes], http=False))
    out = eng.slots({"handle": "library"})
    assert out["ok"] is True
    assert out["reserved_count"] == 4
    assert out["user_count"] == 3
    assert all(row["user_nameable"] is False for row in out["reserved"])
    assert out["user"][0]["name"] == "notes.library.aziel"
    assert out["user"][1]["status"] == "empty"
    assert out["user"][2]["status"] == "empty"
    assert out["automatic_name"] == "library.aziel"
    assert out["miragegrid"]["separate_layer"] is True
    assert out["miragegrid"]["changed"] is False
    assert set(out["miragegrid"]["real"]) == set(CAP7_ALLOWLIST)
    assert set(out["miragegrid"]["decoy"]) == set(CAP7_FALSE_SITES)


def test_isolated_handle_gets_a_policy_page_and_no_peer_bytes():
    record = signed_record()
    record["isolation"] = {
        "state": "ISOLATED",
        "reason": "policy_hate",
        "check": "text_classifier",
        "evidence_hash": "ab" * 32,
    }
    eng = engine_with(record)
    out = eng.navigate({"url": "library.aziel", "operator_override": True})
    assert out["ok"] is False
    assert out["code"] == "FG-GATE-REFUSE"
    assert out["reason"] == "handle_isolated"
    assert out["policy_page"] is True
    html = out["html"]
    assert "This handle is isolated" in html
    assert "What you can do next: go back, or open a different site. If this is your handle, you can file a signed appeal to ask for a re-check." in html
    assert "use another handle" not in html.lower()
    assert html.index("What you can do next") < html.index("<details>")
    assert "<summary>Details</summary>" in html
    assert html.index("<details>") < html.index("NCMEC")
    assert html.index("<details>") < html.index("false-positive")
    assert "Library" not in html
    assert "another handle" not in out["clarity"]["next"].lower()
    assert "different site" in out["clarity"]["next"]
    assert out["isolation"]["content_stored"] is False
    assert out["isolation"]["deletes_local_data"] is False
    assert out["scripts_executed"] is False
    other = signed_record(name="shelf.aziel", handle="shelf", seed=bytes(range(96, 128)))
    both = Engine(Ledger(), mesh=MeshDirectory([record, other], http=False))
    shelf = both.navigate({"url": "shelf.aziel"})
    assert shelf.get("reason") != "handle_isolated"
    assert shelf["ok"] is True


def test_design_mode_is_a_local_tab_and_remote_is_refused():
    eng = Engine(Ledger(), mesh=MeshDirectory([], http=False))
    out = eng.design_mode({"handle": "library"})
    assert out["ok"] is True
    assert out["plane"] == "local"
    assert out["origin"] == "azbrowser://local/design"
    assert out["data_stays_local"] is True
    assert out["publish"] is False
    assert out["keys_leave_node"] is False
    assert out["scripts_executed"] is False
    assert "Design mode" in out["html"]
    assert "qnm-node" in out["html"]
    assert out["slots"]["reserved_count"] == 4
    assert out["slots"]["user_count"] == 3
    remote = eng.design_mode({"remote": True})
    assert remote["code"] == "FG-GATE-REFUSE"
    assert remote["reason"] == "design_mode_local_only"
    assert "hosting node" in remote["html"]
    via_nav = eng.navigate({"url": "azbrowser://local/design"})
    assert via_nav["origin"] == "azbrowser://local/design"
    assert via_nav["publish"] is False
