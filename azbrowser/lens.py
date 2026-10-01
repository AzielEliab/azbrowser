"""Lamb Lens lock for this shell.

Order is Service, then Clarity, then Peace. A feature that drops one of
the three fails review. This module is the plain-language half of Clarity:
every refusal names what happened and what the person can do next.

Author: Aziel Eliab only.
"""

from __future__ import annotations

ORDER = ("Service", "Clarity", "Peace")
LOCK = "A feature that sacrifices Service, Clarity, or Peace fails review."

# reason code -> (plain, next)
_REASONS: dict[str, tuple[str, str]] = {
    "name_not_in_ledger": (
        "This name is not in the local ledger, so there is nothing to open.",
        "Check the spelling, or open a name this node already has.",
    ),
    "resolver_absent": (
        "AZNet's name library is not installed on this machine, so this Cap-7 name was not resolved.",
        "Install AZNet beside this browser, then try the name again. It was not sent to public DNS.",
    ),
    "ledger_absent": (
        "AZNet is installed, and its name ledger file is not on this machine.",
        "Open AZNet so the local name ledger exists, then try the Cap-7 name again. It was not sent to public DNS.",
    ),
    "hub_cite": (
        "This AZ.* name cites a hub site. It is not a mesh page and this shell did not register .az.",
        "Open the hub address if you want that public site. Cap-7 names are the mesh pairing.",
    ),
    "cap7_ok": (
        "AZNet returned a Cap-7 name record. This shell did not load page bytes.",
        "The record is a hash or a handle. It is not a public DNS site and it does not open a hub.",
    ),
    "cap7_unclaimed": (
        "AZNet has no anchored claim for this Cap-7 name.",
        "Nothing was opened. The name was not sent to public DNS.",
    ),
    "cap7_pending": (
        "AZNet has this Cap-7 claim, and it is not final yet.",
        "Wait until it is final, or open a different name. No page bytes were loaded.",
    ),
    "cap7_isolated": (
        "AZNet will not serve this Cap-7 name because the handle is isolated.",
        "Open a different name. This shell does not decide that isolation.",
    ),
    "cap7_fork": (
        "AZNet has two Cap-7 claims that share an anchor time. Neither was merged.",
        "Open a different name. This shell will not pick a side.",
    ),
    "cap7_equivocation": (
        "AZNet refused this Cap-7 name because the handle signed two statements at one sequence.",
        "Open a different name.",
    ),
    "cap7_expired": (
        "AZNet says this Cap-7 name is expired.",
        "Open a different name. Nothing was loaded.",
    ),
    "cap7_revoked": (
        "AZNet says the owner released this Cap-7 name.",
        "Open a different name. Nothing was loaded.",
    ),
    "cap7_self_cert": (
        "AZNet answered this name with the handle itself. The key is not proven by a claim record.",
        "No page bytes were loaded. This is not a public DNS site.",
    ),
    "cap7_reserved": (
        "AZNet reserves this Cap-7 label. It is not a user claim.",
        "Nothing was opened. The name was not sent to public DNS.",
    ),
    "name_not_final": (
        "This name is not final. It has not aged, or it does not have enough witnesses.",
        "Wait until it is final, or open a different name. A pending name is not a verified site.",
    ),
    "name_pending": (
        "This name is pending. It is not a verified site.",
        "Wait for age and witnesses, or open a final name. No page bytes were loaded.",
    ),
    "equivocating_handle": (
        "This handle has two conflicting records for the same sequence. Neither page is shown.",
        "Open a different handle. This node will not pick a side.",
    ),
    "rollback": (
        "This record is older than the latest sequence for that handle.",
        "Open the current name for this handle.",
    ),
    "bad_prev": (
        "This record does not link to the previous one in its chain.",
        "Open a record whose chain is intact.",
    ),
    "handle_isolated": (
        "This handle is isolated from the mesh. Its pages are not shown.",
        "Go back, or open a different site. If this is your handle, you can file a signed appeal to ask for a re-check. This browser does not decide that appeal, and it does not delete local data.",
    ),
    "design_mode_local_only": (
        "Design mode opens only on the machine that holds the handle key.",
        "Open AZBrowser on that machine. Nothing was published.",
    ),
    "peer_blocked": (
        "This handle is blocked on this node.",
        "Unblock it here if you want it back. Other handles still open. No other node was cut off.",
    ),
    "island_mode": (
        "This node is in island mode, so mesh names stay closed.",
        "Turn island mode off to rejoin, or keep using local apps and ordinary web addresses.",
    ),
    "keys_must_stay_on_node": (
        "A private key was in this record. It was refused and not shown.",
        "Keep the handle key on the local node and send only the public record.",
    ),
    "bad_handle": (
        "That handle is not a valid name.",
        "Use letters, numbers, and . _ - , then try again.",
    ),
    "bad_grant": (
        "This capability request needs an origin, a kind, and a resource.",
        "Name all three. Kinds are network, fetch, storage, and file.",
    ),
    "bad_island": (
        "Island mode needs true or false.",
        "Send enabled true to leave the mesh, or false to rejoin. Local apps and the ordinary web stay available either way.",
    ),
    "airlock_quarantine": (
        "These bytes look executable or use a blocked type. They stay in quarantine.",
        "Do not run them. Promote does not release this kind of file.",
    ),
    "scanner_absent": (
        "The handle key matched, and the page is held because this shell has no malware scanner.",
        "Choose Promote on this node to view the scrubbed page. Scripts still do not run.",
    ),
    "object_missing": (
        "The signed page is not on this node.",
        "Pull that object on the local node, then try the name again.",
    ),
    "hash_mismatch": (
        "The page bytes do not match the signed hash.",
        "Do not trust this copy. Open a record whose hash matches. This node path waits and re-seals locally. Ordinary web addresses stay open.",
    ),
    "unsigned_module": (
        "A module on this page is not signed, so the page is not shown.",
        "Use a record whose modules are signed.",
    ),
    "engine_digest_mismatch": (
        "The record digest does not match its contents.",
        "Do not open this copy. Use a record whose digest matches.",
    ),
    "bad_handle_signature": (
        "The handle signature does not match this record.",
        "Do not open it. Use a record signed by that handle key.",
    ),
    "network_not_granted": (
        "This app asked for the network, and no grant allows that resource.",
        "Leave it blocked, or grant that exact resource if you mean to allow it. Grants are receipted and rare.",
    ),
    "file_not_granted": (
        "This app asked for a local file, and no grant allows that path.",
        "Leave it blocked, or grant that exact path if you mean to allow it.",
    ),
    "cross_origin_not_granted": (
        "This app asked for another origin, and no grant allows it.",
        "Leave it blocked, or grant that exact origin if you mean to allow it.",
    ),
    "storage_outside_origin": (
        "This app asked to store data outside its own origin.",
        "That stays denied. Storage inside its own origin does not ask.",
    ),
    "bad_record": (
        "This ledger row has no name or handle.",
        "Skip it. A usable record names both.",
    ),
}


def clarify(reason: str, code: str = "FG-GATE-REFUSE") -> dict[str, object]:
    plain, nxt = _REASONS.get(
        reason,
        (
            f"This was refused ({reason or 'unspecified'}).",
            "Try another address, or read the receipt for this action.",
        ),
    )
    return {
        "order": list(ORDER),
        "lock": LOCK,
        "code": code,
        "reason": reason,
        "plain": plain,
        "next": nxt,
    }


def ethics_clarity(reasons: list[str] | None) -> dict[str, object]:
    named = ", ".join(str(item) for item in (reasons or [])) or "the ethical gate"
    return {
        "order": list(ORDER),
        "lock": LOCK,
        "code": "ETHICS_REFUSE",
        "reason": "ethics_refuse",
        "plain": f"This was refused before anything was fetched. The advisory gate matched {named}.",
        "next": "Try a different query. This gate does not claim to catch every harmful request.",
    }


def lens_status() -> dict[str, object]:
    return {
        "order": list(ORDER),
        "lock": LOCK,
        "service": "One request opens a local app, a mesh name, or an ordinary web address.",
        "clarity": "Verified handles, pending names, and isolated handles stay distinct. Every refusal says what happened and what to do next.",
        "peace": "No ads, no tracking, no telemetry, and no notification spam. Capability grants are receipted and rare.",
        "search_engine": "AZ Search",
        "product_name": "AZ Browser",
        "sidenet": "AZNet",
        "ads": False,
        "tracking": False,
        "telemetry": "off",
        "notifications": False,
        "miragegrid_decoys": "separate",
    }
