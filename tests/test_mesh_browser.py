"""Local-first edge mesh browser plane.

Covers .aziel resolution, handle resolution, .az allowlist versus DNS
fallthrough, hash mismatch, capability deny/grant, and normal web.
"""

from __future__ import annotations

import copy

from azbrowser.ed25519 import node_sign, public_from_seed
from azbrowser.engine import Engine
from azbrowser.hashgate import canonical, engine_digest_for, sha256_text
from azbrowser.meshledger import MeshDirectory
from azbrowser.names import classify_destination
from azbrowser.receipts import Ledger

PAGE = "<h1>Library</h1><p>Local-first shelf.</p>"


def signed_record(page: str = PAGE, *, name: str = "library.aziel", handle: str = "library", modules=None, connect=None, seed: bytes | None = None):
    seed = seed or bytes(range(32))
    public = public_from_seed(seed).hex()
    objects: dict[str, str] = {}
    page_hash = sha256_text(page)
    objects[page_hash] = page
    ref_modules = []
    for mod in modules or []:
        digest = sha256_text(mod["body"])
        objects[digest] = mod["body"]
        ref_modules.append(
            {
                "path": mod["path"],
                "hash": digest,
                "signed": mod.get("signed", True),
                "kind": mod.get("kind", "script"),
            }
        )
    ref = {
        "name": name,
        "handle": handle,
        "public_key": public,
        "object": page_hash,
        "seq": 1,
        "prev": "0" * 64,
        "modules": ref_modules,
    }
    ref["engine_digest"] = engine_digest_for(ref)
    signature = node_sign(seed, canonical(ref).encode("utf-8")).hex()
    return {
        "name": name,
        "handle": handle,
        "public_key": public,
        "ref": ref,
        "signature": signature,
        "connect": connect or {"mode": "direct", "peer": handle, "relay": None},
        "objects": objects,
    }


def engine_with(record, **kwargs) -> Engine:
    directory = MeshDirectory([record], http=False)
    return Engine(Ledger(), mesh=directory)


def test_aziel_resolves_with_owner_handle():
    record = signed_record()
    eng = engine_with(record)
    out = eng.navigate({"url": "library.aziel/shelf"})
    assert out["ok"] is True
    assert out["plane"] == "mesh"
    assert out["owner_handle"] == "library"
    assert out["verified_owner"] is True
    assert out["name"] == "library.aziel"
    assert out["icann"] is False
    assert out["regular_browsers_resolve_aziel"] is False
    assert out["ca"] is False
    assert out["keys_leave_node"] is False
    assert out["signature_ok"] is True
    assert out["hash_ok"] is True
    assert out["connect"]["mode"] == "direct"
    assert out["connect"]["socket"] is False
    assert out["tab"]["kind"] == "mesh"
    assert out["scripts_executed"] is False
    assert "Library" in out["html"]
    assert out["receipt"]["action"] == "navigate"


def test_handle_name_resolution():
    record = signed_record()
    eng = engine_with(record)
    out = eng.resolve({"handle": "library"})
    assert out["ok"] is True
    assert out["name"] == "library.aziel"
    assert out["owner_handle"] == "library"
    assert out["public_key"] == record["public_key"]
    assert out["signature_ok"] is True
    assert out["keys_leave_node"] is False


def test_az_allowlist_versus_dns_fallthrough():
    record = signed_record()
    eng = engine_with(record)
    fall = eng.navigate({"url": "example.az/path"})
    assert fall["ok"] is True
    assert fall["plane"] == "dns"
    assert fall["url"].startswith("https://example.az/")
    assert fall.get("code") != "FG-GATE-REFUSE"
    assert fall["icann"] is True
    decoy = classify_destination("azbooth.az")
    assert decoy["plane"] == "dns"
    assert decoy["allowlisted"] is False
    allow = eng.navigate({"url": "AZ.AzielEliab.AZ"})
    assert allow["plane"] == "mesh"
    assert allow["code"] == "FG-GATE-REFUSE"
    assert allow["reason"] == "name_not_in_ledger"
    assert allow["allowlisted"] is True
    cap7 = classify_destination("azgrid.az")
    assert cap7["plane"] == "mesh"
    assert cap7["allowlisted"] is True
    assert cap7["icann"] is False


def test_hash_mismatch_is_fg_gate_refuse():
    record = signed_record()
    bad = copy.deepcopy(record)
    bad["objects"][record["ref"]["object"]] = "<p>tampered</p>"
    eng = Engine(Ledger(), mesh=MeshDirectory([bad], http=False))
    out = eng.navigate({"url": "https://library.aziel/"})
    assert out["ok"] is False
    assert out["code"] == "FG-GATE-REFUSE"
    assert out["reason"] == "hash_mismatch"
    assert out["html"] == ""
    assert "tampered" not in str(out)
    assert out["display"]["summary"].startswith("FG-GATE-REFUSE")


def test_unsigned_module_refuses():
    page = '<p>ok</p><script src="/app.js"></script>'
    record = signed_record(page)
    eng = engine_with(record)
    out = eng.navigate({"url": "library.aziel"})
    assert out["code"] == "FG-GATE-REFUSE"
    assert out["reason"] == "unsigned_module"


def test_bad_signature_refuses():
    record = signed_record()
    record["signature"] = "ab" + record["signature"][2:]
    eng = engine_with(record)
    out = eng.navigate({"url": "library.aziel"})
    assert out["code"] == "FG-GATE-REFUSE"
    assert out["reason"] == "bad_handle_signature"


def test_secret_key_never_enters_the_browser():
    record = signed_record()
    record["private_key"] = "seed-must-not-leak"
    directory = MeshDirectory([record], http=False)
    assert "library.aziel" not in directory.by_name
    directory.by_name["library.aziel"] = record
    eng = Engine(Ledger(), mesh=directory)
    out = eng.navigate({"url": "library.aziel"})
    assert out["code"] == "FG-GATE-REFUSE"
    assert out["reason"] == "keys_must_stay_on_node"
    assert "seed-must-not-leak" not in str(out)


def test_ungranted_network_blocked_and_grant_has_receipt():
    record = signed_record()
    eng = engine_with(record)
    origin = "aziel://library"
    blocked = eng.capability_check({"origin": origin, "kind": "network", "target": "https://tracker.example/pixel"})
    assert blocked["ok"] is False
    assert blocked["code"] == "FG-GATE-REFUSE"
    assert blocked["reason"] == "network_not_granted"
    grant = eng.capability_grant({"origin": origin, "capability": "network", "resource": "https://tracker.example"})
    assert grant["ok"] is True
    assert grant["receipt"]["action"] == "capability_grant"
    assert grant["keys_leave_node"] is False
    allowed = eng.capability_check({"origin": origin, "kind": "network", "target": "https://tracker.example/pixel"})
    assert allowed["ok"] is True
    assert allowed["receipt"]["hash"] == grant["receipt"]["hash"]
    assert allowed["receipt"]["action"] == "capability_grant"
    assert eng.receipt_verify({})["ok"] is True


def test_local_app_sandbox_and_normal_web():
    record = signed_record()
    eng = engine_with(record)
    app = eng.local_app({"slug": "notes", "source": "qnm", "content": "<p>on this drive</p>"})
    assert app["ok"] is True
    assert app["tab"]["kind"] == "local-app"
    assert app["data_stays_local"] is True
    assert app["uploaded"] is False
    assert app["origin"] == "azbrowser://local/notes"
    assert "on this drive" in app["html"]
    denied = eng.capability_check({"origin": app["origin"], "kind": "network", "target": "https://ads.example/a"})
    assert denied["reason"] == "network_not_granted"
    outside = eng.capability_check({"origin": "aziel://library", "kind": "storage", "target": "aziel://other/key"})
    assert outside["reason"] == "storage_outside_origin"
    own = eng.capability_check({"origin": "aziel://library", "kind": "storage", "target": "aziel://library/key"})
    assert own["ok"] is True
    files = eng.capability_check({"origin": "aziel://library", "kind": "file", "target": "/tmp/secret.txt"})
    assert files["reason"] == "file_not_granted"
    web = eng.navigate({"url": "https://www.azieleliab.com/"})
    assert web["ok"] is True
    assert web["plane"] == "dns"
    assert web.get("code") != "FG-GATE-REFUSE"
    assert "azieleliab.com" in web["url"]
    assert web["tls"] == "standard"
    assert web["receipt"]["action"] == "navigate"


def test_qnm_connect_adapter_direct_lan_relay():
    record = signed_record(connect={"mode": "relay", "peer": "library", "relay": "relay-1"})
    calls = []

    def post(url, body, timeout):
        calls.append((url, body, timeout))
        return {"ok": True, "connected": True, "mode": body["mode"], "peer": body["peer"], "relay": body["relay"]}

    eng = Engine(Ledger(), mesh=MeshDirectory([record], http=True, post=post))
    out = eng.navigate({"url": "library.aziel"})
    assert out["ok"] is True
    assert out["connect"]["mode"] == "relay"
    assert out["connect"]["connected"] is True
    assert out["connect"]["socket"] is True
    assert out["connect"]["via"] == "qnm-node"
    assert out["connect"]["keys_leave_node"] is False
    assert calls[0][0].endswith("/local/connect")
    assert calls[0][1]["mode"] == "relay"
    assert calls[0][1]["relay"] == "relay-1"
    assert "private_key" not in calls[0][1]
