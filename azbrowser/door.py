"""FragGate / runtime door — classify /v1 paths.

``/v1/fraggate/*``, ``/v1/runtime/*``, and ``/v1/mesh/*`` PROXY to aziel-runtime.
Local engine ops are single-segment ``/v1/{op}`` only.
Multi-segment leftovers are never swallowed as op names.

Author: Aziel Eliab only.
"""

from __future__ import annotations

from urllib.parse import urljoin

from .meta import RUNTIME

DOOR_PREFIXES = ("fraggate", "runtime", "mesh")

DOOR_ALIASES = {
    "/v1/runtime/list": "/v1/fraggate/list",
    "/v1/runtime/call": "/v1/fraggate/call",
    "/v1/runtime/describe": "/v1/fraggate/describe",
    "/v1/runtime/verify": "/v1/fraggate/verify",
}


def normalize_v1_path(pathname: str) -> str:
    raw = str(pathname or "")
    path = raw.rstrip("/") or "/"
    return path if path.startswith("/") else "/" + path


def map_door_path(pathname: str) -> str | None:
    path = normalize_v1_path(pathname)
    if path in DOOR_ALIASES:
        return DOOR_ALIASES[path]
    if path == "/v1/fraggate" or path.startswith("/v1/fraggate/"):
        return path
    if path == "/v1/runtime" or path.startswith("/v1/runtime/"):
        return path
    if path == "/v1/mesh" or path.startswith("/v1/mesh/"):
        return path
    return None


def is_door_path(pathname: str) -> bool:
    return map_door_path(pathname) is not None


def local_op_from_path(pathname: str) -> str | None:
    path = normalize_v1_path(pathname)
    if not path.startswith("/v1/"):
        return None
    rest = path[4:]
    if not rest or "/" in rest:
        return None
    if rest in DOOR_PREFIXES:
        return None
    return rest


def classify_v1_path(pathname: str) -> dict[str, str]:
    path = normalize_v1_path(pathname)
    origin = map_door_path(path)
    if origin:
        return {"kind": "door", "path": path, "originPath": origin}
    op = local_op_from_path(path)
    if op:
        return {"kind": "local", "path": path, "op": op}
    if path in ("/v1", "/v1/"):
        return {"kind": "none", "path": "/v1"}
    if path.startswith("/v1/"):
        return {"kind": "multi", "path": path}
    return {"kind": "none", "path": path}


def door_target_url(pathname: str, origin: str | None = None) -> str | None:
    mapped = map_door_path(pathname)
    if not mapped:
        return None
    base = (origin or RUNTIME).rstrip("/") + "/"
    return urljoin(base, mapped.lstrip("/"))
