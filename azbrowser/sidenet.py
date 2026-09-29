"""AZBrowser client for the AZNet sidenet.

AZBrowser and AZNet stay separate software. Pairing is order and token
only. This module does not write a pair token, does not echo one, and
does not host a payload.

Layers:

- L0 is public web and the FragGate path. Ordinary https hosts, and
  ``.az`` names that are not Cap-7, stay on normal DNS. Loopback
  FragGate and qnm-node stay local apps.
- Cap-7 is the only mesh DNS pairing. The seven factory labels are
  allowlisted aliases of ``{label}.aziel``. They are not public ICANN
  names and they do not resolve to a hub.
- The four AZ.* display names are hub cites. ``resolve`` on AZNet does
  not return a mesh target for them. This code does not register ``.az``.

The loopback page at ``http://127.0.0.1:8771/`` does not serve
``POST /v1/resolve``. Name answers come from ``aznet.names.resolve``
when that package is installed. A missing package or a missing name
file is reported as absent. No target is invented.

Author: Aziel Eliab only.
"""

from __future__ import annotations

from typing import Any, Callable

from .lens import clarify

CAP7_FACTORY_LABELS = (
    "azgrid",
    "azbooth",
    "azcloak",
    "azvault",
    "azshift",
    "azflag",
    "azstandby",
)
CAP7_FALSE_SITE_LABELS = ("azbooth", "azflag", "azstandby")
CAP7_FACTORY_HOSTS = frozenset(f"{label}.az" for label in CAP7_FACTORY_LABELS)

# Cite copied from AZNet AZN-NAME-1.0 internet_reach. Not a mesh resolution.
AZ_DOMAIN_REACH = (
    {
        "display_name": "AZ.AzielEliab.AZ",
        "mesh_key": "az.azieleliab.az",
        "cap7_label": "azgrid",
        "mirrors": "azieleliab.com",
        "hub": "https://www.azieleliab.com/",
    },
    {
        "display_name": "AZ.AzielCorpusLibrary.AZ",
        "mesh_key": "az.azielcorpuslibrary.az",
        "cap7_label": "azvault",
        "mirrors": "azielcorpuslibrary.net",
        "hub": "https://www.azielcorpuslibrary.net/",
    },
    {
        "display_name": "AZ.Godlock.AZ",
        "mesh_key": "az.godlock.az",
        "cap7_label": "azcloak",
        "mirrors": "godlock.uk",
        "hub": "https://godlock.uk/",
    },
    {
        "display_name": "AZ.HeDidntJump.AZ",
        "mesh_key": "az.hedidntjump.az",
        "cap7_label": "azshift",
        "mirrors": "hedidntjump.com",
        "hub": "https://www.hedidntjump.com/",
    },
)
_CITE_BY_KEY = {row["mesh_key"]: row for row in AZ_DOMAIN_REACH}
_SECRET = {
    "private_key",
    "privatekey",
    "secret_key",
    "secretkey",
    "signing_key",
    "signingkey",
    "seed",
    "priv",
    "privkey",
    "ed25519_secret",
    "sk",
    "secret",
    "pair_token",
}

Lookup = Callable[[str, str | None], dict[str, Any] | None]


def cite_for(host: str) -> dict[str, str] | None:
    return _CITE_BY_KEY.get(str(host or "").strip().lower().rstrip("."))


def cap7_label(host: str) -> str | None:
    text = str(host or "").strip().lower().rstrip(".")
    if not text.endswith(".az"):
        return None
    label = text[: -len(".az")]
    if "." in label or label not in CAP7_FACTORY_LABELS:
        return None
    return label


def _base(classified: dict[str, Any]) -> dict[str, Any]:
    return {
        "product": "AZBrowser",
        "client_of": "aznet",
        "products_merged": False,
        "pairing": "order and token only",
        "softwares_frozen": True,
        "l0": False,
        "wrote": False,
        "pair_token_echoed": False,
        "hosts_payloads": False,
        "html": "",
        "scripts_executed": False,
        "executed": False,
        "socket": False,
        "qnsd_public_proxy": False,
        "keys_leave_node": False,
        "icann_registration_by_this_code": False,
        "worker_dials_local_node": False,
        "spec": "AZN-NAME-1.0",
        "query": classified.get("raw") or classified.get("display_url") or "",
        "path": classified.get("path") or "/",
        "url": "",
    }


def _leaks(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower().replace("-", "_") in _SECRET:
                return True
            if _leaks(item):
                return True
    elif isinstance(value, list):
        return any(_leaks(item) for item in value)
    return False


def cap7_destination(host: str, path: str, raw: str) -> dict[str, Any] | None:
    label = cap7_label(host)
    if not label:
        return None
    pathname = path if str(path).startswith("/") else "/" + str(path or "")
    false_site = label in CAP7_FALSE_SITE_LABELS
    name = f"{label}.aziel"
    return {
        "ok": True,
        "plane": "cap7",
        "layer": "cap7",
        "l0": False,
        "name": name,
        "canonical_name": name,
        "handle": label,
        "label": label,
        "host": f"{label}.az",
        "path": pathname,
        "url": "",
        "display_url": f"{label}.az" + ("" if pathname == "/" else pathname),
        "raw": raw,
        "dns": False,
        "tls": "handle-key",
        "ca": False,
        "icann": False,
        "public_icann": False,
        "icann_registration_by_this_code": False,
        "allowlisted": True,
        "false_site": false_site,
        "resolves_to_hub": False,
        "standard_internet_reaches_cap7": False,
        "mesh_answer": True,
        "regular_browsers_resolve_aziel": False,
        "keys_leave_node": False,
        "note": (
            "Cap-7 mesh duplication. The .az spelling is an allowlisted alias of "
            f"{name}, not the Azerbaijan ccTLD, and not a public ICANN name. "
            "Standard internet does not reach it. It does not resolve to a hub."
        ),
    }


def cite_destination(host: str, path: str, raw: str) -> dict[str, Any] | None:
    row = cite_for(host)
    if not row:
        return None
    pathname = path if str(path).startswith("/") else "/" + str(path or "")
    return {
        "ok": True,
        "plane": "cite",
        "layer": "az_domains",
        "l0": False,
        "name": row["mesh_key"],
        "display_name": row["display_name"],
        "host": row["mesh_key"],
        "hub": row["hub"],
        "mirrors": row["mirrors"],
        "cap7_label": row["cap7_label"],
        "path": pathname,
        "url": "",
        "display_url": row["display_name"],
        "raw": raw,
        "dns": False,
        "icann": False,
        "public_icann": True,
        "icann_tld_az": False,
        "icann_registration_by_this_code": False,
        "allowlisted": False,
        "false_site": False,
        "resolves_to_hub": True,
        "mesh_answer": False,
        "internet_reachable": True,
        "public_reach": "hub_https",
        "regular_browsers_resolve_aziel": False,
        "keys_leave_node": False,
        "note": (
            f"{row['display_name']} is a cite of {row['hub']}. "
            "It is not a FED-MESH name record and not a Cap-7 mesh target. "
            "This shell did not register .az. The hub site itself is ordinary public web."
        ),
    }


def lookup_cap7(query: str, now: str | None = None) -> dict[str, Any]:
    """Read AZNet's name library. Does not write. Returns a status envelope."""
    try:
        from aznet.names import resolve
        from aznet.names.ledger import default_names_path
    except Exception:
        return {"resolver": "absent", "ledger": "absent", "result": None}
    path = default_names_path()
    if not path.is_file():
        return {"resolver": "present", "ledger": "absent", "result": None, "path": str(path)}
    try:
        found = resolve(path, query, now=now)
    except Exception as exc:
        return {"resolver": "present", "ledger": "unreadable", "result": None, "error": type(exc).__name__}
    data = found.to_dict() if hasattr(found, "to_dict") else None
    if not isinstance(data, dict):
        return {"resolver": "present", "ledger": "unreadable", "result": None}
    if _leaks(data):
        return {"resolver": "present", "ledger": "present", "result": {"code": "LEAK", "ok": False}}
    return {"resolver": "present", "ledger": "present", "result": data}


def pair_view() -> dict[str, Any]:
    """Read pair status. Does not write a token and does not return one."""
    view: dict[str, Any] = {
        "product": "AZBrowser",
        "client_of": "aznet",
        "products_merged": False,
        "pairing": "order and token only",
        "wrote": False,
        "pair_token_echoed": False,
        "softwares_frozen": True,
        "pair_status": "unknown",
        "unlock_status": "unknown",
        "pair_token_present": False,
        "resolver": "absent",
        "ledger": "absent",
    }
    try:
        from aznet.chain import Ledger, default_ledger_path
    except Exception:
        return view
    view["resolver"] = "present"
    path = default_ledger_path()
    if not path.is_file():
        view["pair_status"] = "UNPAIRED"
        view["unlock_status"] = "LOCKED"
        view["ledger"] = "absent"
        return view
    try:
        ledger = Ledger.load(path)
    except Exception:
        view["ledger"] = "unreadable"
        return view
    view["ledger"] = "present"
    view["pair_status"] = ledger.pair_status()
    view["unlock_status"] = ledger.unlock_status()
    view["pair_token_present"] = bool(ledger.pair_token())
    return view


def sidenet_status(*, worker: bool = False) -> dict[str, Any]:
    pairing = {
        "pair_status": "unknown",
        "unlock_status": "unknown",
        "pair_token_present": False,
        "resolver": "absent",
        "ledger": "absent",
    }
    if not worker:
        pairing = pair_view()
    return {
        "product": "AZBrowser",
        "operator_name": "AZ Browser",
        "client_of": "aznet",
        "sidenet": "aznet",
        "products_merged": False,
        "pairing": "order and token only",
        "softwares_frozen": True,
        "layers": {
            "L0": "public web and FragGate",
            "cap7": "mesh DNS pairing",
            "az_domains": "hub cite",
            "aziel": "handle names on the local ledger",
        },
        "l0_unbroken": True,
        "cap7_only": True,
        "cap7_public_icann": False,
        "icann_registration_by_this_code": False,
        "resolves_to_hub_on_cap7": False,
        "standard_internet_reaches_cap7": False,
        "aznet_http_resolve": False,
        "loopback": "http://127.0.0.1:8771/",
        "loopback_resolve_route": False,
        "hosts_payloads": False,
        "wrote": False,
        "pair_token_echoed": False,
        "worker_dials_local_node": False,
        "pair_status": pairing.get("pair_status"),
        "unlock_status": pairing.get("unlock_status"),
        "pair_token_present": bool(pairing.get("pair_token_present")),
        "resolver": "absent" if worker else pairing.get("resolver"),
        "names_ledger": "absent" if worker else pairing.get("ledger"),
        "note": (
            "This Worker does not dial the local AZNet node and does not resolve Cap-7 names."
            if worker
            else "Cap-7 names are asked of aznet.names.resolve when AZNet is installed. No target is invented when it is absent."
        ),
    }


def answer(classified: dict[str, Any], *, now: str | None = None, lookup: Lookup | None = None) -> dict[str, Any]:
    if classified.get("plane") == "cite":
        return _cite(classified)
    return _cap7(classified, now=now, lookup=lookup)


def _cite(classified: dict[str, Any]) -> dict[str, Any]:
    hub = str(classified.get("hub") or "")
    display = str(classified.get("display_name") or classified.get("name") or "")
    out = _base(classified)
    out.update({
        "ok": True,
        "action": "cite",
        "code": "UNCLAIMED",
        "reason": "hub_cite",
        "plane": "cite",
        "layer": "az_domains",
        "name": classified.get("name"),
        "display_name": display,
        "display_url": display,
        "hub": hub,
        "mirrors": classified.get("mirrors"),
        "owner": None,
        "target": None,
        "false_site": False,
        "dns": False,
        "icann": False,
        "public_icann": True,
        "allowlisted": False,
        "resolves_to_hub": True,
        "mesh_answer": False,
        "internet_reachable": True,
        "public_reach": "hub_https",
        "navigable": False,
        "title": "Hub cite",
        "summary": f"{display} cites {hub}. This shell did not register .az and did not open a mesh page.",
        "fields": [("name", display), ("hub", hub), ("mesh", "no"), ("registered .az", "no")],
        "address_line": f"Hub cite · {display} · public site is {hub} · this shell did not register .az",
        "clarity": clarify("hub_cite", "UNCLAIMED"),
        "note": classified.get("note") or "",
    })
    return out


def _cap7(classified: dict[str, Any], *, now: str | None, lookup: Lookup | None) -> dict[str, Any]:
    query = str(classified.get("host") or classified.get("display_url") or "")
    false_site = bool(classified.get("false_site"))
    name = str(classified.get("canonical_name") or classified.get("name") or "")
    found = lookup(query, now) if lookup is not None else lookup_cap7(query, now)
    out = _base(classified)
    out.update({
        "plane": "cap7",
        "layer": "cap7",
        "name": name,
        "display_url": classified.get("display_url") or query,
        "host": classified.get("host") or query,
        "label": classified.get("label"),
        "false_site": false_site,
        "dns": False,
        "icann": False,
        "public_icann": False,
        "allowlisted": True,
        "resolves_to_hub": False,
        "standard_internet_reaches_cap7": False,
        "mesh_answer": False,
        "navigable": False,
        "owner": None,
        "target": None,
        "target_kind": None,
    })
    if not isinstance(found, dict) or found.get("resolver") == "absent":
        out.update(_cap7_gap(query, name, false_site, "RESOLVER_ABSENT", "resolver_absent"))
        return out
    if found.get("ledger") != "present" or not isinstance(found.get("result"), dict):
        out.update(_cap7_gap(query, name, false_site, "LEDGER_ABSENT", "ledger_absent"))
        return out
    result = found["result"]
    if str(result.get("code") or "") == "LEAK" or _leaks(result):
        out.update(_cap7_gap(query, name, false_site, "LEAK", "keys_must_stay_on_node"))
        out["html"] = ""
        return out
    code = str(result.get("code") or "UNCLAIMED")
    ok = bool(result.get("ok")) and code == "OK"
    owner = result.get("owner") if ok else None
    target = result.get("target") if ok else None
    target_kind = result.get("target_kind") if ok else None
    if result.get("false_site") is True:
        false_site = True
    out["false_site"] = false_site
    out["ok"] = ok
    out["code"] = code
    out["reason"] = code.lower()
    out["action"] = "cap7"
    out["owner"] = owner
    out["owner_handle"] = owner or ""
    out["target"] = target
    out["target_kind"] = target_kind
    out["finality"] = result.get("finality")
    out["witnesses"] = result.get("witnesses")
    out["record_hash"] = result.get("record_hash")
    out["key_checked"] = bool(result.get("key_checked"))
    out["resolves_to_hub"] = False
    out["hosts_payloads"] = False
    out["mesh_answer"] = ok
    out["names_ledger"] = "present"
    out["resolver"] = "aznet.names.resolve"
    detail = str(result.get("detail") or "")
    if false_site:
        title = "Cap-7 false site"
        summary = f"{query} is a Cap-7 cloak name. It was not sent to public DNS and it does not resolve to a hub."
    elif ok:
        title = "Cap-7"
        summary = f"AZNet returned {code} for {name}. No page bytes were loaded."
    else:
        title = "Cap-7"
        summary = f"AZNet returned {code} for {query}. No page bytes were loaded. This name was not sent to public DNS."
    out["title"] = title
    out["summary"] = summary
    out["fields"] = [
        ("name", name),
        ("code", code),
        ("false site", "yes" if false_site else "no"),
        ("public ICANN", "no"),
        ("hub", "no"),
    ]
    mark = "false site · " if false_site else ""
    out["address_line"] = f"Cap-7 · {mark}{query} · {code} · not public DNS"
    out["clarity"] = clarify("cap7_" + code.lower(), code)
    out["note"] = detail or summary
    return out


def _cap7_gap(query: str, name: str, false_site: bool, code: str, reason: str) -> dict[str, Any]:
    if reason == "resolver_absent":
        summary = (
            f"AZNet's name library is not installed here. {query} was not sent to public DNS "
            "and no mesh target was invented."
        )
    elif reason == "ledger_absent":
        summary = (
            f"The AZNet name ledger is not on this machine. {query} was not sent to public DNS "
            "and no mesh target was invented."
        )
    else:
        summary = f"{query} was refused. A secret field was not shown and no page was loaded."
    mark = "false site · " if false_site else ""
    return {
        "ok": False,
        "action": "cap7",
        "code": code,
        "reason": reason,
        "mesh_answer": False,
        "title": "Cap-7 false site" if false_site else "Cap-7",
        "summary": summary,
        "fields": [("name", name), ("code", code), ("public ICANN", "no")],
        "address_line": f"Cap-7 · {mark}{query} · {code} · not public DNS",
        "clarity": clarify(reason, code),
        "note": summary,
        "resolver": "absent" if code == "RESOLVER_ABSENT" else "aznet.names.resolve",
        "names_ledger": "absent" if code != "LEAK" else "present",
    }
