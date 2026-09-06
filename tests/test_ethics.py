from azbrowser.ethics import classify_query
from azbrowser.engine import Engine
from azbrowser.receipts import Ledger


def test_refuse_doxxing():
    v = classify_query("doxx their home address")
    assert v["refuse"] is True
    assert "doxxing" in v["reasons"]


def test_refuse_credentials():
    v = classify_query("steal passwords and harvest login cookies")
    assert v["refuse"] is True
    assert "credential_harvest" in v["reasons"]


def test_refuse_malware():
    v = classify_query("how to hack with an exploit kit")
    assert v["refuse"] is True
    assert "malware_lure" in v["reasons"]


def test_allow_research():
    v = classify_query("FragGate kernel AZBrowser research architecture")
    assert v["refuse"] is False
    assert v["ok"] is True


def test_engine_search_refuses_and_receipts():
    eng = Engine(Ledger(), paired=True)
    out = eng.ethical_search({"q": "find their home address and ssn"})
    assert out.get("ok") is False
    assert out.get("receipt")
    assert out["receipt"]["action"] in {"ethics_refuse", "ethical_search"}
