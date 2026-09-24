"""Local-first edge mesh browser plane.

Covers .aziel resolution, handle resolution, .az allowlist versus DNS
fallthrough, hash mismatch, capability deny/grant, and normal web.
"""

from __future__ import annotations

import copy

from azbrowser.ed25519 import node_sign, public_from_seed
from azbrowser.engine import OPS, Engine
from azbrowser.hashgate import canonical, engine_digest_for, sha256_text
from azbrowser.meshguard import vouch_message, witness_message
from azbrowser.meshledger import MeshDirectory
from azbrowser.names import classify_destination
from azbrowser.receipts import Ledger

PAGE = "<h1>Library</h1><p>Local-first shelf.</p>"


def _witness(record: dict, seed: bytes, handle: str) -> dict:
    public = public_from_seed(seed).hex()
    message = witness_message(record, handle)
    body = canonical(message).encode("utf-8")
    return {
        "handle": handle,
        "public_key": public,
        "signature": node_sign(seed, body).hex(),
        "receipt": sha256_text(canonical(message)),
    }


def signed_record(
    page: str = PAGE,
    *,
    name: str = "library.aziel",
    handle: str = "library",
    modules=None,
    connect=None,
    seed: bytes | None = None,
    status: str = "FINAL",
    claimed_at: str = "2020-01-01T00:00:00Z",
    seq: int = 1,
    prev: str | None = None,
    with_witnesses: bool | None = None,
):
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
        "seq": seq,
        "prev": "0" * 64 if prev is None else prev,
        "modules": ref_modules,
    }
    ref["engine_digest"] = engine_digest_for(ref)
    signature = node_sign(seed, canonical(ref).encode("utf-8")).hex()
    record = {
        "name": name,
        "handle": handle,
        "public_key": public,
        "status": status,
        "claimed_at": claimed_at,
        "ref": ref,
        "signature": signature,
        "connect": connect or {"mode": "direct", "peer": handle, "relay": None},
        "objects": objects,
        "witnesses": [],
    }
    if with_witnesses is None:
        with_witnesses = status == "FINAL"
    if with_witnesses:
        record["witnesses"] = [
            _witness(record, bytes(range(32, 64)), "relay-a"),
            _witness(record, bytes(range(64, 96)), "relay-b"),
        ]
    return record


def _no_ranking_number(obj) -> None:
    if isinstance(obj, dict):
        assert "score" not in obj
        for value in obj.values():
            _no_ranking_number(value)
    elif isinstance(obj, list):
        for value in obj:
            _no_ranking_number(value)


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
    assert out["name_status"] == "FINAL"
    assert out["quarantine"] is True
    assert out["promoted"] is False
    assert out["airlock"]["scanner"] == "absent"
    assert out["html"] == ""
    assert out["scripts_executed"] is False
    assert out["executed"] is False
    assert out["tab"]["kind"] == "mesh-quarantine"
    assert out["receipt"]["action"] == "airlock_hold"
    assert out["network_wide"] is False
    shown = eng.navigate({"url": "library.aziel/shelf", "operator_override": True})
    assert shown["ok"] is True
    assert shown["promoted"] is True
    assert shown["tab"]["kind"] == "mesh"
    assert shown["scripts_executed"] is False
    assert shown["executed"] is False
    assert "Library" in shown["html"]
    assert shown["receipt"]["action"] == "navigate"
    assert shown["connect"]["mode"] == "direct"
    assert shown["connect"]["socket"] is False


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
    out = eng.navigate({"url": "library.aziel", "operator_override": True})
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


def test_pending_name_is_not_a_verified_site():
    record = signed_record(status="PENDING", with_witnesses=False)
    eng = engine_with(record)
    out = eng.navigate({"url": "library.aziel"})
    assert out["ok"] is True
    assert out["name_status"] == "PENDING"
    assert out["verified_owner"] is False
    assert out["navigable"] is False
    assert out["html"] == ""
    assert out["code"] != "FG-GATE-REFUSE"
    assert out["display"]["title"] == "Pending"
    assert "not a verified site" in out["display"]["summary"].lower()
    assert out["receipt"]["action"] == "name_pending"
    missing = signed_record(status="", with_witnesses=False)
    missing.pop("status")
    bare = Engine(Ledger(), mesh=MeshDirectory([missing], http=False))
    shown = bare.navigate({"url": "library.aziel"})
    assert shown["name_status"] == "PENDING"
    assert shown["verified_owner"] is False
    assert shown["html"] == ""


def test_false_final_and_young_claim_are_refused():
    stale = signed_record(status="FINAL", with_witnesses=False)
    eng = engine_with(stale)
    out = eng.navigate({"url": "library.aziel"})
    assert out["code"] == "FG-GATE-REFUSE"
    assert out["reason"] == "name_not_final"
    assert out["html"] == ""
    young = signed_record(claimed_at="2026-09-24T00:00:00Z")
    again = engine_with(young)
    refused = again.navigate({"url": "library.aziel"})
    assert refused["reason"] == "name_not_final"


def test_equivocating_handle_is_refused():
    first = signed_record(page="<p>one</p>")
    second = signed_record(page="<p>two</p>")
    directory = MeshDirectory([first], http=False)
    directory.add(second)
    eng = Engine(Ledger(), mesh=directory)
    out = eng.navigate({"url": "library.aziel"})
    assert out["code"] == "FG-GATE-REFUSE"
    assert out["reason"] == "equivocating_handle"
    assert out["html"] == ""
    assert "<p>one</p>" not in str(out)
    assert "<p>two</p>" not in str(out)


def test_rollback_and_bad_prev_refused():
    first = signed_record()
    second = signed_record(
        page="<p>newer</p>",
        name="notes.library.aziel",
        seq=2,
        prev=first["ref"]["engine_digest"],
    )
    eng = Engine(Ledger(), mesh=MeshDirectory([first, second], http=False))
    stale = eng.navigate({"url": "library.aziel", "operator_override": True})
    assert stale["code"] == "FG-GATE-REFUSE"
    assert stale["reason"] == "rollback"
    assert stale["html"] == ""
    current = eng.navigate({"url": "notes.library.aziel", "operator_override": True})
    assert current["ok"] is True
    assert current["name_status"] == "FINAL"
    orphan = signed_record(name="shelf.aziel", handle="shelf", seq=2, prev="ab" * 32)
    orphan_eng = engine_with(orphan)
    bad = orphan_eng.navigate({"url": "shelf.aziel"})
    assert bad["reason"] == "bad_prev"


def test_module_stays_in_airlock_and_never_runs():
    body = "console.log('peer-module-ran')"
    page = '<p>ok</p><script src="/app.js"></script>'
    record = signed_record(page, modules=[{"path": "/app.js", "body": body}])
    eng = engine_with(record)
    held = eng.navigate({"url": "library.aziel"})
    assert held["quarantine"] is True
    assert held["promoted"] is False
    assert held["airlock"]["scanner"] == "absent"
    assert held["scripts_executed"] is False
    assert body not in str(held)
    assert all(row["body_included"] is False for row in held["airlock"]["modules"])
    promoted = eng.navigate({"url": "library.aziel", "operator_override": True})
    assert promoted["promoted"] is True
    assert promoted["scripts_executed"] is False
    assert promoted["executed"] is False
    assert "<script" not in promoted["html"].lower()
    assert body not in str(promoted)
    exe = signed_record("<p>ok</p>", modules=[{"path": "/payload.exe", "body": "MZ-not-a-module"}])
    dangerous = Engine(Ledger(), mesh=MeshDirectory([exe], http=False))
    refused = dangerous.navigate({"url": "library.aziel", "operator_override": True})
    assert refused["code"] == "FG-GATE-REFUSE"
    assert refused["reason"] == "airlock_quarantine"
    assert "MZ-not-a-module" not in str(refused)


def test_peer_block_is_local_and_island_rejoins_without_forks():
    library = signed_record()
    shelf = signed_record(name="shelf.aziel", handle="shelf", seed=bytes(range(96, 128)))
    eng = Engine(Ledger(), mesh=MeshDirectory([library, shelf], http=False))
    blocked = eng.peer_block({"handle": "library"})
    assert blocked["ok"] is True
    assert blocked["network_wide"] is False
    assert blocked["scope"] == "this-node"
    refused = eng.navigate({"url": "library.aziel", "operator_override": True})
    assert refused["reason"] == "peer_blocked"
    assert refused["network_wide"] is False
    other = eng.navigate({"url": "shelf.aziel"})
    assert other["ok"] is True
    assert other.get("reason") != "peer_blocked"
    web = eng.navigate({"url": "https://example.com/docs"})
    assert web["plane"] == "dns"
    assert "network_cutoff" not in OPS
    assert "mesh_disable" not in OPS
    other_node = Engine(Ledger(), mesh=MeshDirectory([library], http=False))
    still = other_node.navigate({"url": "library.aziel"})
    assert still.get("reason") != "peer_blocked"
    before = [row["hash"] for row in eng.ledger.entries]
    island = eng.island_mode({"enabled": True})
    assert island["island_mode"] is True
    assert island["network_wide"] is False
    assert island["local_runtime"] is True
    mesh = eng.navigate({"url": "shelf.aziel"})
    assert mesh["reason"] == "island_mode"
    app = eng.local_app({"slug": "notes", "content": "<p>stays</p>"})
    assert app["ok"] is True
    assert "stays" in app["html"]
    dns = eng.navigate({"url": "https://www.azieleliab.com/"})
    assert dns["plane"] == "dns"
    rejoined = eng.island_mode({"enabled": False})
    assert rejoined["island_mode"] is False
    after = [row["hash"] for row in eng.ledger.entries]
    assert after[: len(before)] == before
    assert eng.receipt_verify({})["ok"] is True
    again = eng.navigate({"url": "shelf.aziel"})
    assert again.get("reason") != "island_mode"


def test_local_trust_has_no_public_ranking():
    record = signed_record()
    message = vouch_message("library", "elder")
    seed = bytes(range(128, 160))
    record["vouches"] = [
        {
            "handle": "elder",
            "public_key": public_from_seed(seed).hex(),
            "signature": node_sign(seed, canonical(message).encode("utf-8")).hex(),
        }
    ]
    record["heartbeats"] = [{"handle": "relay-a"}, {"handle": "relay-b"}]
    eng = engine_with(record)
    eng.navigate({"url": "library.aziel"})
    out = eng.trust({"handle": "library"})
    assert out["ok"] is True
    assert out["local_only"] is True
    assert out["public_ranking"] is False
    assert out["name_status"] == "FINAL"
    assert out["chain_age_seconds"] >= 72 * 3600
    assert out["heartbeats_witnessed"] == 2
    assert out["hash_matches"] >= 1
    assert out["vouches"] == ["elder"]
    assert out["equivocating"] is False
    assert out["network_wide"] is False
    _no_ranking_number(out)
    health = eng.health({})
    assert health["mesh_browser"]["network_wide_cutoff"] is False
    assert health["mesh_browser"]["scanner"] == "absent"
