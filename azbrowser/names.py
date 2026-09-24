"""Name plane for the local-first edge mesh.

``.aziel`` is a mesh name. It is not an ICANN TLD. Ordinary browsers do
not resolve it. ``.az`` is Azerbaijan's country domain and stays on
normal DNS unless the host is on the operator's explicit Cap-7 / AZ.*
allowlist.

Author: Aziel Eliab only.
"""

from __future__ import annotations

import os
import re
from typing import Any
from urllib.parse import urlparse

SPEC = "FED-MESH-BROWSER-1.0"
REFUSE = "FG-GATE-REFUSE"

# Factory real duplications (CAP7-SHUFFLE-1.0). False sites are not listed.
CAP7_ALLOWLIST = frozenset({"azgrid.az", "azcloak.az", "azvault.az", "azshift.az"})
# Operator AZ.* display names. Case-folded. Not an ICANN purchase.
AZ_STAR_ALLOWLIST = frozenset(
    {
        "az.azieleliab.az",
        "az.godlock.az",
        "az.azielcorpuslibrary.az",
        "az.hedidntjump.az",
    }
)
# Cloak decoys. They are .az names and therefore use normal DNS.
CAP7_FALSE_SITES = frozenset({"azbooth.az", "azflag.az", "azstandby.az"})

LOCAL_QNM_PORT = 8891
LOCAL_FRAGGATE_PORT = 8787
_HANDLE = re.compile(r"^[a-z0-9](?:[a-z0-9._-]{0,62}[a-z0-9])?$")
_HOST = re.compile(r"^[a-z0-9.-]+$")


def allowlist() -> frozenset[str]:
    """Operator allowlist. Env extends it; it does not add every .az name."""
    extra = os.environ.get("AZBROWSER_AZ_ALLOWLIST", "")
    found = {part.strip().lower().rstrip(".") for part in extra.split(",") if part.strip()}
    return frozenset(CAP7_ALLOWLIST | AZ_STAR_ALLOWLIST | found)


def _handle_ok(label: str) -> bool:
    return bool(label) and bool(_HANDLE.match(label)) and ".." not in label


def classify_destination(raw: str) -> dict[str, Any]:
    """Classify an address-bar string. Does not contact the network."""
    text = str(raw or "").strip()
    if not text:
        return {"ok": False, "plane": "search", "error": "url required", "url": ""}
    if any(ch.isspace() for ch in text):
        return {"ok": False, "plane": "search", "error": "not_a_url", "url": text, "suggest_search": True}

    lowered = text
    if "://" not in lowered and not lowered.startswith("/"):
        lowered = lowered
    parsed_input = lowered
    if "://" not in parsed_input:
        parsed_input = "https://" + parsed_input
    parsed = urlparse(parsed_input)
    scheme = (parsed.scheme or "").lower()
    if scheme in {"javascript", "data", "file", "vbscript"}:
        return {"ok": False, "plane": "dns", "error": "blocked_scheme", "scheme": scheme, "url": text}

    if scheme == "aziel":
        handle = (parsed.netloc or "").lower()
        path = parsed.path or "/"
        if not _handle_ok(handle):
            return _refuse_name(text, "bad_handle")
        name = f"{handle}.aziel"
        return _mesh(name, handle, path, text, allowlisted=False)

    if scheme == "azbrowser" and (parsed.netloc or "").lower() in {"local", "app"}:
        slug = (parsed.path or "/").strip("/") or "app"
        return _local(slug, "azbrowser", text)

    host = (parsed.hostname or "").lower().rstrip(".")
    port = parsed.port
    path = parsed.path or "/"
    if parsed.query:
        path = path + "?" + parsed.query

    if host in {"127.0.0.1", "localhost"} and port in {LOCAL_QNM_PORT, LOCAL_FRAGGATE_PORT}:
        source = "qnm" if port == LOCAL_QNM_PORT else "fraggate"
        parts = [p for p in (parsed.path or "").split("/") if p]
        slug = parts[-1] if parts else "app"
        return _local(slug, source, text, port=port, path=parsed.path or "/")

    if not host or not _HOST.match(host):
        return {"ok": False, "plane": "search", "error": "not_a_url", "url": text, "suggest_search": True}

    if host.endswith(".aziel"):
        labels = host.split(".")
        if len(labels) < 2 or labels[-1] != "aziel":
            return _refuse_name(text, "bad_handle")
        handle = labels[-2]
        if not _handle_ok(handle) or not all(_handle_ok(part) for part in labels[:-1]):
            return _refuse_name(text, "bad_handle")
        return _mesh(host, handle, path if path.startswith("/") else "/" + path, text, allowlisted=False)

    if host.endswith(".az"):
        listed = host in allowlist()
        if listed and host not in CAP7_FALSE_SITES:
            labels = host.split(".")
            # AZ.Name.AZ → owner label is the middle name. Cap-7 factory names are label.az.
            handle = labels[1] if len(labels) >= 3 and labels[0] == "az" else labels[0]
            return _mesh(host, handle, path if path.startswith("/") else "/" + path, text, allowlisted=True)
        url = _https(host, parsed.port, parsed.path or "/", parsed.query)
        return {
            "ok": True,
            "plane": "dns",
            "url": url,
            "host": host,
            "path": parsed.path or "/",
            "dns": True,
            "tls": "standard",
            "icann": True,
            "allowlisted": False,
            "regular_browsers_resolve_aziel": False,
            "note": ".az is Azerbaijan's country domain. This host is not on the Cap-7 / AZ.* allowlist, so it uses normal DNS and standard TLS.",
        }

    if scheme not in {"https", "http", ""}:
        return {"ok": False, "plane": "dns", "error": "https_only", "scheme": scheme, "url": text}

    url = _https(host, parsed.port, parsed.path or "/", parsed.query)
    return {
        "ok": True,
        "plane": "dns",
        "url": url,
        "host": host,
        "path": parsed.path or "/",
        "dns": True,
        "tls": "standard",
        "icann": True,
        "allowlisted": False,
        "regular_browsers_resolve_aziel": False,
    }


def _https(host: str, port: int | None, path: str, query: str) -> str:
    # Loopback local-app ports are classified earlier. Other http(s) uses https.
    suffix = ""
    if port and port not in {80, 443}:
        suffix = f":{port}"
    if not path.startswith("/"):
        path = "/" + path
    q = f"?{query}" if query else ""
    return f"https://{host}{suffix}{path}{q}"


def _mesh(name: str, handle: str, path: str, raw: str, *, allowlisted: bool) -> dict[str, Any]:
    if not path.startswith("/"):
        path = "/" + path
    return {
        "ok": True,
        "plane": "mesh",
        "name": name,
        "handle": handle,
        "path": path,
        "url": f"aziel://{handle}{path if path != '/' else '/'}",
        "display_url": name + ("" if path == "/" else path),
        "raw": raw,
        "dns": False,
        "tls": "handle-key",
        "ca": False,
        "icann": False,
        "allowlisted": allowlisted,
        "regular_browsers_resolve_aziel": False,
        "keys_leave_node": False,
    }


def _local(slug: str, source: str, raw: str, port: int | None = None, path: str = "/") -> dict[str, Any]:
    safe = re.sub(r"[^a-z0-9._-]", "", slug.lower()) or "app"
    return {
        "ok": True,
        "plane": "local",
        "slug": safe,
        "source": source,
        "port": port,
        "path": path,
        "origin": f"azbrowser://local/{safe}",
        "url": f"azbrowser://local/{safe}",
        "display_url": f"azbrowser://local/{safe}",
        "raw": raw,
        "dns": False,
        "icann": False,
        "data_stays_local": True,
        "keys_leave_node": False,
    }


def _refuse_name(raw: str, reason: str) -> dict[str, Any]:
    return {
        "ok": False,
        "plane": "mesh",
        "code": REFUSE,
        "reason": reason,
        "url": raw,
        "icann": False,
        "regular_browsers_resolve_aziel": False,
        "keys_leave_node": False,
    }
