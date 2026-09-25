"""Local doctor: receipts chain, ethics refuse, airlock stages."""

from __future__ import annotations

import json

from .meta import SPEC, __version__
from .engine import Engine, OPS
from .names import classify_destination
from .receipts import Ledger


def doctor(as_json: bool = False) -> int:
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
    mesh = h.get("mesh_browser") or {}
    checks.append(("no_network_cutoff", mesh.get("network_wide_cutoff") is False and mesh.get("scanner") == "absent"))
    checks.append(("mesh_guard_ops", all(op in OPS for op in ("peer_block", "island_mode", "trust"))))
    slots = eng.slots({"handle": "library"})
    checks.append(("domain_slots", slots.get("reserved_count") == 4 and slots.get("user_count") == 3 and (slots.get("miragegrid") or {}).get("changed") is False))
    design = eng.design_mode({})
    checks.append(("design_local", design.get("ok") is True and design.get("publish") is False and design.get("origin") == "azbrowser://local/design"))
    lens = h.get("lamb_lens") or {}
    checks.append(("lamb_lens", lens.get("order") == ["Service", "Clarity", "Peace"] and lens.get("telemetry") == "off" and lens.get("ads") is False and lens.get("miragegrid_decoys") == "separate"))
    missing = eng.navigate({"url": "missing-name.aziel"})
    clarity = missing.get("clarity") or {}
    checks.append(("clarity_next", missing.get("code") == "FG-GATE-REFUSE" and bool(clarity.get("plain")) and bool(clarity.get("next"))))
    web = eng.navigate({"url": "https://example.com/library"})
    local = eng.local_app({"slug": "notes", "content": "<p>notes</p>"})
    checks.append(("service_one_step", web.get("plane") == "dns" and web.get("code") != "FG-GATE-REFUSE" and local.get("ok") is True and local.get("plane") == "local"))

    ok = all(p for _, p in checks)
    if as_json:
        print(json.dumps({
            "ok": ok,
            "name": "AZBrowser",
            "version": __version__,
            "spec": SPEC,
            "author": "Aziel Eliab",
            "checks": [{"name": name, "ok": passed} for name, passed in checks],
        }, indent=2))
        return 0 if ok else 1
    print(f"AZBrowser doctor {__version__}")
    for name, passed in checks:
        print(f"  {'ok' if passed else 'FAIL':<4} {name}")
    print("No receipt = no action." if ok else "Doctor failed. Try: azbrowser doctor")
    return 0 if ok else 1
