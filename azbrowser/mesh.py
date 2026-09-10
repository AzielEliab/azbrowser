"""Suite node mesh — QNM-BUILD-1.0 Live Nodes contract + QNS-CD-1.0 cross-map.

Default OFF. Public rollup is live|locked|isolated counts only.
No Node Gate. No auto-heal. Not an anonymity network.
No public qnsd proxy. Local qnsd lives in AzielEliab/qnm-node.
``/v1/mesh/*`` PROXY to aziel-runtime.
QNS-CD-1.0 is hub cite / Worker mesh cross-map only — not a Softwares-tab product.
Author: Aziel Eliab only.
"""

from __future__ import annotations

from typing import Any

from .meta import FRAGGATE_CALL, FRAGGATE_MCP, IDENTITY, RUNTIME

QNM_SPEC = "QNM-BUILD-1.0"
QNS_CD_SPEC = "QNS-CD-1.0"
QNM_NODE = "https://github.com/AzielEliab/qnm-node"
AZIEL_RUNTIME_REPO = "https://github.com/AzielEliab/aziel-runtime"
AZINTERFACE_REPO = "https://github.com/AzielEliab/azinterface"
QNS_CD_DESIGNS = "https://github.com/AzielEliab/aziel-runtime/tree/main/docs/designs"
QNS_CD = {
    "spec": QNS_CD_SPEC,
    "title": "photon QNS1 packet transfer",
    "kind": "cross-map",
    "local_qnsd": QNM_NODE,
    "qnsd_public_proxy": False,
    "runtime": AZIEL_RUNTIME_REPO,
    "designs": QNS_CD_DESIGNS,
    "qnm_wp": "https://github.com/AzielEliab/aziel-runtime/blob/main/docs/designs/QNM-WP-1.0.md",
    "qnm_build": "https://github.com/AzielEliab/qnm-node/blob/main/docs/QNM-BUILD-1.0.md",
    "pair_custody": "azinterface",
    "pair_custody_repo": AZINTERFACE_REPO,
    "softwares_tab": False,
    "node_gate": False,
    "default_off": True,
    "author": IDENTITY,
    "identity": IDENTITY,
    "note": (
        "Hub cite / Worker mesh cross-map only. Local qnsd is qnm-node. "
        "Not a Softwares-tab product. No public qnsd proxy. Author: Aziel Eliab only."
    ),
}
MESH_KERNEL = "NM-0.1"
MESH_DEFAULT_OFF = True
MESH_ANONYMITY_NETWORK = False
MESH_NODE_GATE = False
MESH_AUTO_HEAL = False
MESH_IDENTITY = IDENTITY
MESH_SLUG = "mesh"
MESH_PRODUCT = "azbrowser"
MESH_PATH = "/v1/mesh"
MESH_STATUS_PATH = "/v1/mesh/status"
MESH_NODES_PATH = "/v1/mesh/nodes"
MESH_ENABLE_PATH = "/v1/mesh/enable"
MESH_DISABLE_PATH = "/v1/mesh/disable"
MESH_JOIN_PATH = "/v1/mesh/join"
MESH_HEARTBEAT_PATH = "/v1/mesh/heartbeat"
MESH_LEAVE_PATH = "/v1/mesh/leave"
MESH_BROADCAST_PATH = "/v1/mesh/broadcast"
ANON_BROADCAST = "https://github.com/AzielEliab/anon-broadcast"
MESH_NOTE = (
    "QNM-BUILD-1.0 + QNS-CD-1.0. Suite mesh default off. Live|locked|isolated counts only. "
    "Photon QNS1 packet transfer is local qnm-node (no public qnsd proxy). "
    "No Node Gate. No auto-heal. Not an anonymity network. Author: Aziel Eliab only."
)
MESH_OPS = (
    "status",
    "enable",
    "disable",
    "join",
    "heartbeat",
    "leave",
    "nodes",
    "broadcast",
)


def _first_num(*vals: Any) -> int | None:
    for raw in vals:
        if raw is None or raw == "":
            continue
        try:
            n = float(str(raw).replace(",", ""))
        except (TypeError, ValueError):
            continue
        if n >= 0:
            return int(n)
    return None


def _as_list(value: Any) -> list[Any]:
    if not value:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return list(value.values())
    return []


def _truthy_enabled(value: Any) -> bool:
    if value is True or value == 1:
        return True
    return str(value or "").strip().lower() in {"on", "enabled", "true", "live"}


def empty_rollup() -> dict[str, int]:
    return {"live": 0, "locked": 0, "isolated": 0}


def mesh_rollup(mesh: dict[str, Any] | None) -> dict[str, int]:
    m = mesh if isinstance(mesh, dict) else {}
    r = m.get("rollup") if isinstance(m.get("rollup"), dict) else {}
    return {
        "live": _first_num(r.get("live"), m.get("live_nodes"), m.get("live")) or 0,
        "locked": _first_num(r.get("locked"), m.get("locked_nodes"), m.get("locked")) or 0,
        "isolated": _first_num(r.get("isolated"), m.get("isolated_nodes"), m.get("isolated")) or 0,
    }


def empty_mesh(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    extra = dict(extra or {})
    rollup = extra.get("rollup") if isinstance(extra.get("rollup"), dict) else empty_rollup()
    rollup = {**empty_rollup(), **rollup}
    out = {
        "ok": True,
        "spec": QNM_SPEC,
        "kernel": MESH_KERNEL,
        "enabled": False,
        "default_off": True,
        "live_nodes": 0,
        "status": extra.get("status") or "off",
        "source": extra.get("source") or "fallback",
        "node_gate": False,
        "auto_heal": False,
        "anonymity_network": False,
        "author": MESH_IDENTITY,
        "identity": MESH_IDENTITY,
        "note": MESH_NOTE,
        "door": MESH_PATH,
    }
    out.update(extra)
    out["spec"] = QNM_SPEC
    out["qns_cd_spec"] = QNS_CD_SPEC
    out["qns_cd"] = dict(QNS_CD)
    out["rollup"] = rollup
    out["node_gate"] = False
    out["auto_heal"] = False
    out["anonymity_network"] = False
    out["author"] = MESH_IDENTITY
    out["identity"] = MESH_IDENTITY
    return out


def compact_mesh_node(raw: Any) -> dict[str, str] | None:
    if raw is None:
        return None
    if isinstance(raw, str):
        ident = raw.strip()
        return {"id": ident} if ident else None
    if not isinstance(raw, dict):
        return None
    ident = str(raw.get("id") or raw.get("node_id") or raw.get("session_id") or raw.get("peer") or raw.get("name") or "").strip()
    product = str(raw.get("product") or raw.get("slug") or raw.get("suite") or "").strip()
    seen = raw.get("last_utc") or raw.get("last_seen") or raw.get("seen_utc") or raw.get("heartbeat_utc") or ""
    if not ident and not product and not seen:
        return None
    out: dict[str, str] = {}
    if ident:
        out["id"] = ident
    if product:
        out["product"] = product
    if seen:
        out["last_utc"] = str(seen)
    return out


def parse_mesh_doc(body: Any) -> dict[str, Any]:
    if body is None or not isinstance(body, dict):
        return empty_mesh({"status": "unavailable", "source": "empty"})
    inner = body
    if isinstance(body.get("result"), dict):
        inner = {**body, **body["result"]}
    elif isinstance(body.get("mesh"), dict):
        inner = {**body, **body["mesh"]}
    listed = [
        n for n in (
            compact_mesh_node(x)
            for x in _as_list(inner.get("nodes") or inner.get("list") or inner.get("peers") or inner.get("live_nodes_list"))
        )
        if n
    ]
    r = inner.get("rollup") if isinstance(inner.get("rollup"), dict) else {}
    listed_live = len(listed) if listed else None
    live = _first_num(
        r.get("live"), r.get("live_nodes"), r.get("live_count"),
        inner.get("live"), inner.get("live_nodes"), inner.get("mesh_live_nodes"),
        inner.get("live_count"), inner.get("count"), inner.get("n"), inner.get("node_count"),
        listed_live,
    )
    locked = _first_num(r.get("locked"), r.get("locked_nodes"), r.get("locked_count"), inner.get("locked"), inner.get("locked_nodes"), inner.get("locked_count"))
    isolated = _first_num(r.get("isolated"), r.get("isolated_nodes"), r.get("isolated_count"), inner.get("isolated"), inner.get("isolated_nodes"), inner.get("isolated_count"))
    rollup = {"live": live if live is not None else 0, "locked": locked if locked is not None else 0, "isolated": isolated if isolated is not None else 0}
    enabled = (
        _truthy_enabled(inner.get("enabled"))
        or _truthy_enabled(inner.get("mesh_enabled"))
        or str(inner.get("status") or "").lower() == "on"
    )
    unavailable = inner.get("ok") is False and not enabled and (
        inner.get("error") or inner.get("status") in {"unavailable", "not_found"}
    )
    status = "on" if enabled else ("unavailable" if unavailable else "off")
    live_n = rollup["live"] if enabled else 0
    locked_n = rollup["locked"] if enabled else 0
    isolated_n = rollup["isolated"] if enabled else 0
    products = []
    for item in _as_list(inner.get("products_present") or inner.get("products")):
        if isinstance(item, str):
            name = item.strip()
        elif isinstance(item, dict):
            name = str(item.get("product") or item.get("slug") or item.get("name") or "").strip()
        else:
            name = ""
        if name:
            products.append(name)
    return empty_mesh({
        "ok": inner.get("ok") is not False,
        "enabled": enabled,
        "default_off": inner.get("default_off") is not False,
        "live_nodes": live_n,
        "rollup": {"live": live_n, "locked": locked_n, "isolated": isolated_n},
        "products_present": products,
        "nodes": listed,
        "status": status,
        "source": inner.get("source") or "parsed",
        "door": inner.get("door") or MESH_PATH,
        "note": (
            "QNM-BUILD-1.0 + QNS-CD-1.0. Suite mesh is on. Live|locked|isolated counts only. "
            "Photon QNS1 packet transfer is local qnm-node (no public qnsd proxy). "
            "No Node Gate. No auto-heal. Not an anonymity network."
            if enabled else MESH_NOTE
        ),
    })


def public_mesh(mesh: dict[str, Any] | None = None) -> dict[str, Any]:
    m = mesh if isinstance(mesh, dict) else empty_mesh()
    enabled = bool(m.get("enabled"))
    rollup = mesh_rollup(m) if enabled else empty_rollup()
    return {
        "spec": QNM_SPEC,
        "qns_cd_spec": QNS_CD_SPEC,
        "qns_cd": dict(QNS_CD),
        "kernel": MESH_KERNEL,
        "enabled": enabled,
        "default_off": m.get("default_off") is not False,
        "live_nodes": rollup["live"] if enabled else 0,
        "rollup": rollup,
        "status": "on" if enabled else ("unavailable" if m.get("status") == "unavailable" else "off"),
        "source": m.get("source") or "fallback",
        "node_gate": False,
        "auto_heal": False,
        "anonymity_network": False,
        "author": MESH_IDENTITY,
        "identity": MESH_IDENTITY,
        "door": MESH_PATH,
        "status_path": MESH_STATUS_PATH,
        "nodes_path": MESH_NODES_PATH,
        "join": MESH_JOIN_PATH,
        "heartbeat": MESH_HEARTBEAT_PATH,
        "enable": MESH_ENABLE_PATH,
        "disable": MESH_DISABLE_PATH,
        "leave": MESH_LEAVE_PATH,
        "broadcast": MESH_BROADCAST_PATH,
        "mcp": FRAGGATE_MCP,
        "fraggate": FRAGGATE_CALL,
        "slug": MESH_SLUG,
        "product": MESH_PRODUCT,
        "ops": list(MESH_OPS),
        "origin": RUNTIME.rstrip("/") + MESH_PATH,
        "note": m.get("note") or MESH_NOTE,
    }


def mesh_status_line(mesh: dict[str, Any] | None = None) -> str:
    m = mesh if isinstance(mesh, dict) else empty_mesh()
    if m.get("enabled"):
        r = mesh_rollup(m)
        return (
            f"Suite mesh: on · live {r['live']} · locked {r['locked']} · isolated {r['isolated']}. "
            "Not an anonymity network."
        )
    if m.get("status") == "unavailable":
        return "Suite mesh: off (unavailable). QNM-BUILD-1.0 + QNS-CD-1.0. Not an anonymity network."
    return "Suite mesh: off (default). QNM-BUILD-1.0 + QNS-CD-1.0. Not an anonymity network."


def align_live_nodes(mesh: dict[str, Any] | None = None) -> int:
    """Public Live Nodes count. Never auto-heal a visiting floor."""
    if mesh and mesh.get("enabled"):
        return mesh_rollup(mesh)["live"]
    return 0


def mesh_pointer() -> dict[str, Any]:
    return {
        "pointer": True,
        "path": MESH_PATH,
        "enabled_default": False,
        "spec": QNM_SPEC,
        "qns_cd_spec": QNS_CD_SPEC,
        "qns_cd": dict(QNS_CD),
        "kernel": MESH_KERNEL,
        "rollup": "live|locked|isolated",
        "node_gate": False,
        "auto_heal": False,
        "anonymity_network": False,
        "author": MESH_IDENTITY,
        "identity": MESH_IDENTITY,
        "catalog_mcp": FRAGGATE_MCP,
        "fraggate_slug": MESH_SLUG,
        "origin": RUNTIME.rstrip("/") + MESH_PATH,
        "note": (
            "PROXY to aziel-runtime /v1/mesh/* via AZIEL_RUNTIME. Not a local op. "
            "Not AnonBroadcast. Not AZMail's product-local ring. " + MESH_NOTE
        ),
        "anon_broadcast": ANON_BROADCAST,
        "anon_broadcast_publish_path": False,
    }
