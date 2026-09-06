"""Local doctor: receipts chain, ethics refuse, airlock stages, pair gate."""

from __future__ import annotations

from .engine import OPS, Engine
from .meta import AZNET, LIMITATION, SPEC, __version__
from .pair import pair_status
from .receipts import Ledger


def doctor() -> int:
    eng = Engine(Ledger(), paired=True)
    checks = []

    h = eng.health({})
    checks.append(("health", bool(h.get("ok")) and h.get("version") == __version__))
    checks.append(("pair_required_flag", h.get("pair_required") is True))
    checks.append(("pair_ops", "pair_status" in OPS and "sidenet_view" in OPS))

    refused = eng.ethical_search({"q": "doxx their home address and ssn"})
    checks.append(("ethics_refuse", refused.get("code") == "ETHICS_REFUSE" or refused.get("ok") is False))

    search = eng.ethical_search({"q": "aziel digital library fraggate"})
    checks.append(("ethical_search", bool(search.get("ok")) and search.get("receipt")))

    air = eng.airlock({"content": "<script>alert(1)</script><p>hello</p>", "filename": "note.html"})
    stages = [s.get("stage") for s in air.get("stages") or []]
    checks.append(("airlock_stages", stages == ["download", "scan", "scrub", "verify", "vault"]))
    checks.append(("airlock_receipt", bool(air.get("receipt"))))

    nav = eng.navigate({"url": "https://www.azieleliab.com/"})
    checks.append(("navigate_receipt", bool(nav.get("receipt"))))

    home = eng.home({})
    checks.append(("home_sigil", "sigil.png" in str(home.get("sigil"))))

    tabs = eng.tab_new({})
    checks.append(("tab_new", bool(tabs.get("ok"))))

    v = eng.receipt_verify({})
    checks.append(("receipt_verify", bool(v.get("ok"))))

    checks.append(("ops_count", len(OPS) >= 18))

    unpaired = Engine(Ledger(), paired=False)
    locked = unpaired.ethical_search({"q": "aziel digital library fraggate"})
    checks.append(("unpaired_search_refuses", locked.get("code") == "PAIR_REQUIRED"))
    locked_air = unpaired.airlock({"content": "hello", "filename": "a.txt"})
    checks.append(("unpaired_airlock_refuses", locked_air.get("code") == "PAIR_REQUIRED"))

    side = eng.sidenet_view({})
    checks.append(("sidenet_viewer_only", side.get("protocol_embedded") is False and side.get("viewer") is True))

    live = pair_status(fetch=True)
    print(f"AZBrowser doctor {__version__} spec={SPEC}")
    for name, passed in checks:
        print(f"  {'ok' if passed else 'FAIL':<4} {name}")
    print(f"  live pair: paired={live.get('paired')} code={live.get('code')} (honest; AZNet Worker may be down)")
    print(f"  AZNet sibling: {AZNET}")
    print(LIMITATION)
    print("No receipt = no action." if all(p for _, p in checks) else "Doctor failed.")
    return 0 if all(p for _, p in checks) else 1
