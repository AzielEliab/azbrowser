from azbrowser.door import classify_v1_path, door_target_url, local_op_from_path, map_door_path
from azbrowser.engine import Engine
from azbrowser.meta import RUNTIME
from azbrowser.receipts import Ledger


def test_fraggate_call_is_door_not_local_op():
    hit = classify_v1_path("/v1/fraggate/call")
    assert hit["kind"] == "door"
    assert hit["originPath"] == "/v1/fraggate/call"
    assert local_op_from_path("/v1/fraggate/call") is None


def test_runtime_aliases_map_to_fraggate():
    assert map_door_path("/v1/runtime/list") == "/v1/fraggate/list"
    assert map_door_path("/v1/runtime/call") == "/v1/fraggate/call"
    assert classify_v1_path("/v1/runtime/list")["kind"] == "door"
    assert local_op_from_path("/v1/runtime/list") is None


def test_local_ops_are_single_segment_only():
    assert classify_v1_path("/v1/navigate") == {
        "kind": "local",
        "path": "/v1/navigate",
        "op": "navigate",
    }
    assert classify_v1_path("/v1/ethical_search")["op"] == "ethical_search"
    assert classify_v1_path("/v1/tab_list")["op"] == "tab_list"
    assert classify_v1_path("/v1/not/a/door")["kind"] == "multi"


def test_counters_are_not_v1_ops():
    for path in ("/count", "/stats", "/download", "/"):
        assert classify_v1_path(path)["kind"] == "none"


def test_door_target_url():
    assert door_target_url("/v1/fraggate/call") == RUNTIME.rstrip("/") + "/v1/fraggate/call"
    assert door_target_url("/v1/runtime/list") == RUNTIME.rstrip("/") + "/v1/fraggate/list"


def test_engine_still_refuses_fraggate_slash_call_as_op():
    out = Engine(Ledger()).call("fraggate/call", {})
    assert out["code"] == "FG-HALLUC-TOOL"
    assert out["op"] == "fraggate/call"


def test_fraggate_live_op_aliases():
    eng = Engine(Ledger())
    assert eng.call("lamb_lens_search", {"q": "FragGate"})["ok"] is True
    assert eng.call("tab_open", {})["ok"] is True
