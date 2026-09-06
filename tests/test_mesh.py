from azbrowser.mesh import (
    MESH_ANONYMITY_NETWORK,
    MESH_AUTO_HEAL,
    MESH_DEFAULT_OFF,
    MESH_NODE_GATE,
    QNM_SPEC,
    align_live_nodes,
    empty_mesh,
    mesh_pointer,
    mesh_status_line,
    parse_mesh_doc,
    public_mesh,
)
from azbrowser.door import classify_v1_path, local_op_from_path, map_door_path
from azbrowser.engine import Engine
from azbrowser.meta import HOST, RUNTIME
from azbrowser.receipts import Ledger


def test_qnm_contract_default_off():
    assert QNM_SPEC == "QNM-BUILD-1.0"
    assert MESH_DEFAULT_OFF is True
    assert MESH_ANONYMITY_NETWORK is False
    assert MESH_NODE_GATE is False
    assert MESH_AUTO_HEAL is False
    empty = empty_mesh()
    assert empty["enabled"] is False
    assert empty["identity"] == "Aziel Eliab"
    assert empty["author"] == "Aziel Eliab"
    assert empty["rollup"] == {"live": 0, "locked": 0, "isolated": 0}
    assert empty["node_gate"] is False
    assert empty["auto_heal"] is False
    assert empty["anonymity_network"] is False


def test_parse_qnm_rollup_and_zero_when_off():
    on = parse_mesh_doc({
        "spec": "QNM-BUILD-1.0",
        "enabled": True,
        "rollup": {"live": 2, "locked": 1, "isolated": 3},
        "nodes": [{"id": "a"}, {"id": "b"}, {"id": "c"}],
    })
    assert on["enabled"] is True
    assert on["live_nodes"] == 2
    assert on["rollup"] == {"live": 2, "locked": 1, "isolated": 3}
    assert on["node_gate"] is False
    assert on["auto_heal"] is False
    off = parse_mesh_doc({"enabled": False, "live_nodes": 9, "nodes": [{"id": "stale"}]})
    assert off["enabled"] is False
    assert off["live_nodes"] == 0
    assert off["rollup"] == {"live": 0, "locked": 0, "isolated": 0}


def test_public_mesh_and_status_line():
    pub = public_mesh(parse_mesh_doc({"enabled": True, "live_nodes": 2}))
    assert pub["spec"] == "QNM-BUILD-1.0"
    assert pub["identity"] == "Aziel Eliab"
    assert "nodes" not in pub
    assert pub["mcp"].endswith("/mcp")
    assert pub["slug"] == "mesh"
    assert "live 2" in mesh_status_line(pub)
    assert "off (default)" in mesh_status_line(empty_mesh())
    assert align_live_nodes({"enabled": True, "rollup": {"live": 4, "locked": 1, "isolated": 0}}) == 4
    assert align_live_nodes({"enabled": False, "live_nodes": 9}) == 0
    pointer = mesh_pointer()
    assert pointer["enabled_default"] is False
    assert pointer["rollup"] == "live|locked|isolated"
    assert pointer["fraggate_slug"] == "mesh"
    assert pointer["origin"] == RUNTIME.rstrip("/") + "/v1/mesh"


def test_mesh_paths_are_door_not_local_ops():
    assert classify_v1_path("/v1/mesh")["kind"] == "door"
    assert classify_v1_path("/v1/mesh")["originPath"] == "/v1/mesh"
    assert classify_v1_path("/v1/mesh/nodes")["kind"] == "door"
    assert classify_v1_path("/v1/mesh/enable")["originPath"] == "/v1/mesh/enable"
    assert local_op_from_path("/v1/mesh") is None
    assert local_op_from_path("/v1/mesh/status") is None
    assert map_door_path("/v1/mesh/status") == "/v1/mesh/status"


def test_local_chrome_has_live_nodes_strip():
    from azbrowser.ui import _chrome
    html = _chrome()
    assert 'id="meshStrip"' in html
    assert "QNM-BUILD-1.0" in html
    assert "No Node Gate" in html
    assert "/v1/mesh" in html
    assert 'id="node-gate"' not in html
    assert HOST in html


def test_engine_refuses_mesh_slash_status_as_op():
    out = Engine(Ledger()).call("mesh/status", {})
    assert out["code"] == "FG-HALLUC-TOOL"
    health = Engine(Ledger()).call("health", {})
    assert health["mesh"]["enabled_default"] is False
    assert health["mesh"]["node_gate"] is False
    assert health["mesh"]["identity"] == "Aziel Eliab"
