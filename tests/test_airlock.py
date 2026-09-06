from azbrowser.airlock import STAGES, airlock
from azbrowser.engine import Engine
from azbrowser.preview import scrub_html
from azbrowser.receipts import Ledger


def test_pipeline_stages():
    out = airlock(content="<script>x</script><p>hi</p>", filename="note.html")
    assert [s["stage"] for s in out["stages"]] == list(STAGES)
    assert out["content_hash"]
    assert "script" in (out["stages"][2].get("stripped_kinds") or [])


def test_scrub_strips_script():
    s = scrub_html("<script>alert(1)</script><p>ok</p>")
    assert "script" in s["stripped_kinds"]
    assert "<script" not in s["html"].lower()


def test_quarantine_exe_name():
    out = airlock(content=b"MZ\x90\x00not-a-real-pe", filename="lure.exe")
    assert out["scan"]["verdict"] == "quarantine"
    assert out["ok"] is False


def test_engine_airlock_has_receipt():
    eng = Engine(Ledger())
    out = eng.airlock({"content": "hello vault", "filename": "a.txt"})
    assert out.get("receipt")
    assert out["receipt"]["action"] == "airlock"
    assert len(out["stages"]) == 5
