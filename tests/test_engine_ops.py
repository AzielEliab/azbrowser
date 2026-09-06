from azbrowser.engine import Engine, dispatch
from azbrowser.receipts import Ledger


def test_unknown_op_refuses():
    out = dispatch("not_a_real_op", {}, Engine(Ledger(), paired=True))
    assert out["ok"] is False
    assert out["code"] == "FG-HALLUC-TOOL"


def test_aliases():
    eng = Engine(Ledger(), paired=True)
    a = eng.call("lamb_lens", {"q": "fraggate"})
    b = eng.call("search", {"q": "fraggate"})
    assert a.get("ok") and b.get("ok")
    assert a.get("receipt") and b.get("receipt")


def test_tabs_and_nav():
    eng = Engine(Ledger(), paired=True)
    t = eng.tab_new({})
    assert t["ok"]
    nav = eng.navigate({"url": "https://www.azieleliab.com/"})
    assert nav.get("receipt")
    assert nav.get("tab")
    back = eng.back({})
    assert back.get("receipt")
    home = eng.home({})
    assert "sigil.png" in home["sigil"]


def test_display_envelope():
    eng = Engine(Ledger(), paired=True)
    out = eng.health({})
    assert out["display"]["title"]
    assert out["display"]["summary"]
    assert out.get("pair_required") is True
    assert out.get("aznet") == "https://github.com/AzielEliab/aznet"
