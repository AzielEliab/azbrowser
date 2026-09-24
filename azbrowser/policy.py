"""Shell-written pages for isolation and local design mode.

These pages are not peer content. They do not store or forward the
material a check was about.

Author: Aziel Eliab only.
"""

from __future__ import annotations

from typing import Any


def _esc(value: Any) -> str:
    return (
        str(value if value is not None else "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def policy_page(handle: str, isolation: dict[str, Any] | None) -> str:
    row = isolation if isinstance(isolation, dict) else {}
    reason = str(row.get("reason") or "unspecified")
    check = str(row.get("check") or "unspecified")
    evidence = str(row.get("evidence_hash") or "")
    return f"""<article class="policy-page">
<h1>This handle is isolated</h1>
<p>FG-GATE-REFUSE · handle_isolated</p>
<p>Handle <strong>{_esc(handle)}</strong> is isolated from the mesh. This browser will not resolve its names or show its objects.</p>
<dl>
<dt>Reason code</dt><dd>{_esc(reason)}</dd>
<dt>Check</dt><dd>{_esc(check)}</dd>
<dt>Evidence</dt><dd>{_esc(evidence) or "none recorded"}</dd>
</dl>
<p>The evidence field is a hash only. This browser does not store the content and does not forward it.</p>
<p>Isolation does not delete data on the person's own machine. The local runtime can keep running. Relays that follow the policy refuse to relay or witness this handle.</p>
<p>A signed appeal record can ask for a re-check. This shell does not grant or deny that appeal.</p>
<p>Name checks, and the hosting node's local image and text checks, can miss and can false-positive. This page does not claim those checks catch everything. If a classifier is absent on the hosting node, publish stays blocked there. This browser does not run those classifiers.</p>
<p>Operators must follow the law in their jurisdiction, including US reporting of child sexual abuse material to NCMEC where that duty applies. This browser does not keep that material as evidence.</p>
</article>"""


def design_page(slots: dict[str, Any]) -> str:
    reserved = "".join(
        f"<li>{_esc(row.get('label'))} · {_esc(row.get('host'))} · reserved mirror · not user-nameable</li>"
        for row in slots.get("reserved") or []
    )
    user = "".join(
        f"<li>{_esc(row.get('id'))} · {_esc(row.get('name') or 'empty')} · {_esc(row.get('status'))}</li>"
        for row in slots.get("user") or []
    )
    auto = _esc(slots.get("automatic_name") or "unset")
    return f"""<article class="design-page">
<h1>Design mode</h1>
<p>This is a local tab on this machine. The site designer is hosted by qnm-node on 127.0.0.1. This shell opens that tab. It does not run the designer.</p>
<p>Templates, drag-and-drop blocks, and publish are not in this process. Publish stays refused here. The handle key stays on the local node, and this shell cannot unlock it.</p>
<p>Automatic name: {auto}</p>
<h2>Reserved slots</h2>
<ul>{reserved}</ul>
<h2>User slots</h2>
<ul>{user}</ul>
<p>Four reserved slots mirror the hub sites and are not yours to rename. Three user slots follow the existing claim rules. MirageGrid factory names are a separate layer and are unchanged.</p>
</article>"""


def design_remote_page() -> str:
    return """<article class="policy-page">
<h1>Design mode stays on the hosting node</h1>
<p>FG-GATE-REFUSE · design_mode_local_only</p>
<p>This chrome is not the hosting node. Design mode is bound to localhost on the machine that holds the handle key. Remote access is refused. Nothing was published.</p>
</article>"""
