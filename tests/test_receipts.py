from azbrowser.engine import Engine, OPS
from azbrowser.receipts import Ledger, ZERO


def test_chain_and_verify(tmp_path):
    led = Ledger(tmp_path / "r.jsonl")
    eng = Engine(led)
    eng.home({})
    eng.ethical_search({"q": "library"})
    eng.tab_new({})
    v = eng.receipt_verify({})
    assert v["ok"] is True
    assert v["count"] >= 3
    assert led.tip != ZERO


def test_tamper_breaks(tmp_path):
    led = Ledger(tmp_path / "r.jsonl")
    led.append("home", {"ok": True})
    led.append("navigate", {"url": "https://example.com"})
    led.entries[1]["payload_hash"] = "deadbeef"
    assert led.verify()["ok"] is False


def test_ops_cover_ui_actions():
    needed = {
        "navigate",
        "ethical_search",
        "lamb_lens",
        "airlock",
        "receipts",
        "tab_new",
        "back",
        "forward",
        "reload",
        "home",
    }
    assert needed <= set(OPS)
