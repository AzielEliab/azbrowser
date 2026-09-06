from azbrowser.engine import Engine, OPS
from azbrowser.pair import pair_status, sidenet_view
from azbrowser.receipts import Ledger


def test_ops_include_pair_and_sidenet():
    assert "pair_status" in OPS
    assert "sidenet_view" in OPS


def test_unpaired_refuses_research():
    eng = Engine(Ledger(), paired=False)
    nav = eng.navigate({"url": "https://www.azieleliab.com/"})
    assert nav["ok"] is False
    assert nav["code"] == "PAIR_REQUIRED"
    assert nav["pair"]["links"]["aznet_github"] == "https://github.com/AzielEliab/aznet"
    assert nav["pair"]["links"]["aznet_garden"].endswith("/garden")
    search = eng.ethical_search({"q": "FragGate kernel"})
    assert search["code"] == "PAIR_REQUIRED"
    air = eng.airlock({"content": "hello", "filename": "a.txt"})
    assert air["code"] == "PAIR_REQUIRED"
    scrub = eng.scrub({"html": "<p>ok</p>"})
    assert scrub["code"] == "PAIR_REQUIRED"


def test_paired_allows_search():
    eng = Engine(Ledger(), paired=True)
    out = eng.ethical_search({"q": "FragGate kernel"})
    assert out.get("ok") is True
    assert out.get("receipt")
    assert out.get("results")


def test_sidenet_view_is_viewer_only():
    out = sidenet_view()
    assert out["ok"] is True
    assert out["viewer"] is True
    assert out["protocol_embedded"] is False
    assert out["github"] == "https://github.com/AzielEliab/aznet"
    assert "garden" in out
    eng = Engine(Ledger(), paired=False)
    viewed = eng.sidenet_view({})
    assert viewed["protocol_embedded"] is False
    assert viewed.get("receipt")


def test_pair_status_has_deep_links():
    stub = pair_status(fetch=False, stub_paired=False)
    assert stub["paired"] is False
    assert stub["protocol_embedded"] is False
    assert stub["links"]["aznet_worker"].startswith("https://aznet-download-tracker")
    assert stub["links"]["staticclock"]
    ready = pair_status(fetch=False, stub_paired=True)
    assert ready["paired"] is True
    assert ready["fraggate_unlock"] is True


def test_home_and_pair_status_stay_open_unpaired():
    eng = Engine(Ledger(), paired=False)
    home = eng.home({})
    assert home.get("ok") is True
    status = eng.pair_status({})
    assert status.get("ok") is True
    assert status.get("paired") is False
