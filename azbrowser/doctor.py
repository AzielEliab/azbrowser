"""Local doctor: receipts chain, ethics refuse, airlock stages."""

from __future__ import annotations

from .meta import LIMITATION, SPEC, __version__
from .engine import Engine, OPS
from .names import classify_destination
from .receipts import Ledger


def doctor() -> int:
    eng = Engine(Ledger())
    checks = []

    h = eng.health({})
    checks.append(("health", bool(h.get("ok")) and h.get("version") == __version__))

    refused = eng.ethical_search({"q": "doxx their home address and ssn"})
    checks.append(("ethics_refuse", refused.get("code") == "ETHICS_REFUSE" or refused.get("ok") is False))

    search = eng.ethical_search({"q": "aziel digital library fraggate"})
    checks.append(("ethical_search", bool(search.get("ok")) and search.get("receipt")))

    air = eng.airlock({"content": "<script>alert(1)</script><p>hello</p>", "filename": "note.html"})
    stages = [s.get("stage") for s in air.get("stages") or []]
    checks.append(("airlock_stages", stages == ["download", "scan", "scrub", "verify", "vault"]))
    checks.append(("airlock_receipt", bool(air.get("receipt"))) )

    nav = eng.navigate({"url": "https://www.azieleliab.com/"})
    checks.append(("navigate_receipt", bool(nav.get("receipt"))))
    checks.append(("normal_web_dns", nav.get("plane") == "dns" and nav.get("code") != "FG-GATE-REFUSE"))
    aziel = classify_destination("library.aziel")
    checks.append(("aziel_is_mesh", aziel.get("plane") == "mesh" and aziel.get("icann") is False))
    az_dns = classify_destination("example.az")
    checks.append(("az_dns_fallthrough", az_dns.get("plane") == "dns" and az_dns.get("url", "").startswith("https://example.az/")))
    az_list = classify_destination("AZ.AzielEliab.AZ")
    checks.append(("az_allowlist", az_list.get("plane") == "mesh" and az_list.get("allowlisted") is True))

    home = eng.home({})
    checks.append(("home_sigil", "sigil.png" in str(home.get("sigil"))))

    tabs = eng.tab_new({})
    checks.append(("tab_new", bool(tabs.get("ok"))))

    v = eng.receipt_verify({})
    checks.append(("receipt_verify", bool(v.get("ok"))))

    checks.append(("ops_count", len(OPS) >= 16))

    ok = all(p for _, p in checks)
    print(f"AZBrowser doctor {__version__} spec={SPEC}")
    for name, passed in checks:
        print(f"  {'ok' if passed else 'FAIL':<4} {name}")
    print(LIMITATION)
    print("No receipt = no action." if ok else "Doctor failed.")
    return 0 if ok else 1
