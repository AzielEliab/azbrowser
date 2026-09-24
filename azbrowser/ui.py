"""Loopback research-browser chrome. 127.0.0.1 only. No telemetry."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .door import classify_v1_path, door_target_url
from .engine import OPS, Engine
from .meta import HOST, LIMITATION, SIGIL, __version__
from .receipts import Ledger

PORT = 8878
ENGINE = Engine(Ledger("./azbrowser_receipts.jsonl"))


def _chrome() -> str:
    ops = ", ".join(OPS)
    return f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AZBrowser — local research shell</title>
<style>
:root, html[data-theme="night"] {{ color-scheme: dark; --bg:#0b0b0b; --text:#f5f5f5; --muted:#c8c8c8; --bar:#141414; --panel:#111111; --line:#2c2c2c; --gold:#f5f5f5; --trim:#3a3a3a; --ink:#0b0b0b; --focus:#ffffff; --tab:#1c1c1c; --banner:#161616; }}
html[data-theme="day"] {{ color-scheme: light; --bg:#ffffff; --text:#141414; --muted:#333333; --bar:#f3f3f3; --panel:#f7f7f7; --line:#d4d4d4; --gold:#141414; --trim:#c8c8c8; --ink:#ffffff; --focus:#141414; --tab:#ffffff; --banner:#f3f3f3; }}
html[data-theme="aziel"] {{ color-scheme: dark; --bg:#0b0b0b; --text:#f6f1e4; --muted:#e4d2a0; --bar:#2a1454; --panel:#231246; --line:#6d4ea3; --gold:#f0d060; --trim:#8d6bc4; --ink:#1a1204; --focus:#f0d060; --tab:#3a1d6e; --banner:#2a1454; }}
* {{ box-sizing: border-box; }}
html,body {{ margin:0; height:100%; background:var(--bg); color:var(--text); font:15px/1.45 "Segoe UI", system-ui, sans-serif; }}
#chrome {{ display:flex; flex-direction:column; height:100%; background:var(--bg); }}
.tabs {{ display:flex; gap:6px; padding:8px 10px 0; background:var(--bar); border-bottom:1px solid var(--line); min-height:42px; }}
.tab {{ padding:8px 14px; border:1px solid transparent; border-bottom:none; border-radius:10px 10px 0 0; background:transparent; color:var(--muted); cursor:pointer; }}
.tab.active {{ background:var(--gold); color:var(--ink); }}
.plus {{ color:var(--text); cursor:pointer; padding:6px 10px; background:transparent; border:0; }}
.bar {{ display:flex; flex-wrap:wrap; align-items:center; gap:8px; padding:10px 12px; background:var(--bar); }}
.bar button, .node button, #bookmarks button {{ background:transparent; color:var(--text); border:1px solid var(--line); border-radius:8px; min-width:36px; height:34px; padding:0 10px; cursor:pointer; }}
.bar button:hover, .node button:hover {{ border-color:var(--focus); }}
.bar button:focus-visible, #omnibox:focus-visible, .node button:focus-visible {{ outline:2px solid var(--focus); outline-offset:2px; }}
#go, #azielMode[aria-pressed="true"] {{ background:var(--gold); color:var(--ink); border-color:var(--gold); }}
#home img {{ width:20px; height:20px; vertical-align:middle; }}
#omnibox {{ flex:1; min-width:200px; background:var(--bg); color:var(--text); border:1px solid var(--line); border-radius:999px; padding:9px 16px; font:15px/1.3 inherit; }}
#handleChip {{ font-size:12px; color:var(--muted); padding:0 4px; white-space:nowrap; }}
#bookmarks {{ display:flex; gap:8px; align-items:center; padding:6px 12px; background:var(--bar); border-top:1px solid var(--line); font-size:13px; }}
#bookmarks[hidden] {{ display:none; }}
#bookmarkList {{ display:flex; gap:8px; flex-wrap:wrap; }}
#ownerLine {{ padding:4px 14px 8px; min-height:1.2em; color:var(--muted); background:var(--bar); font-size:13px; }}
.mode {{ color:var(--muted); font-size:12px; letter-spacing:.04em; }}
main {{ flex:1; display:grid; grid-template-columns: 1fr 300px; min-height:0; }}
#stage {{ overflow:auto; padding:28px 32px; }}
aside {{ border-left:1px solid var(--line); overflow:auto; padding:16px; background:var(--panel); }}
h2 {{ color:var(--muted); font-size:12px; letter-spacing:.06em; text-transform:uppercase; margin:16px 0 8px; }}
.banner, .refusal {{ border:1px solid var(--line); background:var(--banner); color:var(--text); padding:16px 18px; border-radius:12px; margin-bottom:16px; }}
.refusal {{ max-width:40rem; }}
.refusal h1, .policy-page h1, .design-page h1 {{ font-size:1.7rem; font-weight:560; margin:0 0 8px; }}
pre {{ white-space:pre-wrap; word-break:break-word; font-size:12px; color:var(--muted); }}
.receipt {{ font-family:ui-monospace,monospace; font-size:11px; border-bottom:1px solid var(--line); padding:6px 0; }}
.status {{ border-top:1px solid var(--line); padding:8px 12px; font-size:12px; color:var(--muted); }}
#meshStrip {{ border-top:1px solid var(--line); padding:8px 12px; background:var(--panel); display:flex; flex-wrap:wrap; align-items:center; gap:10px 16px; font-size:12px; color:var(--muted); }}
#meshStrip .live b {{ color:var(--text); font-size:18px; margin-right:6px; }}
#meshStrip button {{ background:transparent; color:var(--text); border:1px solid var(--line); border-radius:6px; height:28px; padding:0 10px; cursor:pointer; }}
.node {{ display:flex; flex-wrap:wrap; gap:6px; margin-bottom:8px; }}
a {{ color:inherit; }}
.start h1 {{ font-size:1.7rem; font-weight:560; margin:0 0 8px; }}
#chrome, .bar, .tabs, aside, #stage {{ transition: background-color .12s ease, color .12s ease; }}
@media (max-width: 860px) {{
  main {{ grid-template-columns: 1fr; }}
  aside {{ border-left: 0; border-top: 1px solid var(--line); }}
}}
</style>
<script>
(function() {{
  var saved = null;
  try {{ saved = JSON.parse(localStorage.getItem('azbrowser-appearance') || 'null'); }} catch (e) {{}}
  var theme = 'night';
  if (saved && (saved.theme === 'day' || saved.theme === 'night' || saved.theme === 'aziel')) theme = saved.theme;
  else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) theme = 'day';
  document.documentElement.setAttribute('data-theme', theme);
  if (saved && saved.bookmarks) document.documentElement.setAttribute('data-bookmarks', 'on');
}})();
</script>
<div id="chrome">
  <div class="tabs" id="tabs"></div>
  <div class="bar">
    <button id="back" title="Back" type="button">◀</button>
    <button id="fwd" title="Forward" type="button">▶</button>
    <button id="reload" title="Reload" type="button">↻</button>
    <button id="home" title="Home" type="button"><img alt="Home" src="{SIGIL}"></button>
    <input id="omnibox" placeholder="Search Lamb Lens, a URL, or a .aziel name" spellcheck="false" aria-label="Address">
    <span id="handleChip"></span>
    <button id="go" type="button">Go</button>
    <button id="themeToggle" type="button" title="Switch day and night">Day</button>
    <button id="azielMode" type="button" title="Aziel mode. Gold, black, and royal purple." aria-pressed="false">Aziel</button>
    <button id="settingsBtn" type="button" title="Settings">Settings</button>
    <button id="designBtn" type="button" title="Open design mode as a local tab">Design</button>
  </div>
  <div id="bookmarks" hidden>
    <span>Bookmarks</span>
    <div id="bookmarkList"></div>
    <button id="bookmarkAdd" type="button">Bookmark this page</button>
  </div>
  <div id="ownerLine"></div>
  <main>
    <section id="stage"></section>
    <aside>
      <h2>This node</h2>
      <div class="node">
        <button id="airlockBtn" type="button">Airlock</button>
        <button id="promoteBtn" type="button" title="Operator override. Promotes quarantined mesh bytes on this node.">Promote</button>
        <button id="islandBtn" type="button" title="Drop this node's mesh peers. Local runtime stays up.">Island</button>
        <button id="blockBtn" type="button" title="Block the current mesh handle on this node only.">Block peer</button>
        <button id="trustBtn" type="button" title="Local trust for the current handle.">Trust</button>
        <button id="slotsBtn" type="button" title="Show this handle's domain slots">Slots</button>
      </div>
      <h2>Airlock</h2>
      <div id="airlockPanel"></div>
      <h2>Receipts</h2>
      <div id="receipts"></div>
    </aside>
  </main>
  <div id="meshStrip" aria-label="Suite Live Nodes">
    <div class="live"><b id="meshLiveCount">0</b> Live Nodes</div>
    <div id="meshLine">Suite mesh: off (default). QNM-BUILD-1.0 + QNS-CD-1.0. Not an anonymity network.</div>
    <div>live <b id="qnmLive">0</b> · locked <b id="qnmLocked">0</b> · isolated <b id="qnmIsolated">0</b></div>
    <div>No Node Gate · No auto-heal · Aziel Eliab only</div>
    <div>
      <button id="meshEnable" type="button">Enable</button>
      <button id="meshDisable" type="button">Disable</button>
      <button id="meshJoin" type="button">Join</button>
      <button id="meshLeave" type="button">Leave</button>
    </div>
    <div id="meshProducts">Catalog MCP mesh_* · FragGate slug=mesh · /v1/mesh/* PROXY · QNS-CD-1.0 cross-map</div>
  </div>
  <div class="status">AZBrowser {__version__} local · Phase 1 research shell · No receipt = no action · not Chromium</div>
</div>
<script>
const SIGIL = {json.dumps(SIGIL)};
async function op(name, payload) {{
  const r = await fetch('/v1/' + name, {{ method:'POST', headers:{{'content-type':'application/json','user-agent':'Mozilla/5.0'}}, body: JSON.stringify(payload||{{}}) }});
  return r.json();
}}
let lastHandle = '';
let islandOn = false;
function paintOwner(obj) {{
  const line = document.getElementById('ownerLine');
  if (!line) return;
  const chip = document.getElementById('handleChip');
  if (chip) chip.textContent = '';
  if (obj && obj.owner_handle) lastHandle = obj.owner_handle;
  if (obj && obj.name_status === 'PENDING') {{
    line.textContent = 'Pending · ' + (obj.name || obj.display_url || '') + ' · not a verified site';
    if (chip) chip.textContent = 'Pending';
    return;
  }}
  if (obj && obj.display && obj.display.title === 'Island mode') {{
    islandOn = obj.island_mode === true;
    line.textContent = islandOn
      ? 'Island mode · this node only · local runtime stays up'
      : 'Island mode off · this node rejoined';
    return;
  }}
  if (obj && obj.display && obj.display.title === 'Local trust') {{
    line.textContent = 'Local trust · ' + (obj.handle || '')
      + ' · chain age ' + obj.chain_age_seconds
      + ' · heartbeats ' + obj.heartbeats_witnessed
      + ' · hash matches ' + obj.hash_matches
      + ' · vouches ' + ((obj.vouches || []).join(',') || 'none')
      + ' · equivocation ' + obj.equivocating;
    return;
  }}
  if (obj && obj.code === 'FG-GATE-REFUSE') {{
    line.textContent = 'Blocked · FG-GATE-REFUSE · ' + (obj.reason || '');
    return;
  }}
  if (obj && obj.verified_owner && obj.owner_handle && obj.quarantine) {{
    line.textContent = 'Verified owner handle · ' + obj.owner_handle + ' · quarantined · scanner absent';
    if (chip) chip.textContent = obj.owner_handle;
    if (obj.display_url) document.getElementById('omnibox').value = obj.display_url;
    return;
  }}
  if (obj && obj.verified_owner && obj.owner_handle) {{
    line.textContent = 'Verified owner handle · ' + obj.owner_handle;
    if (chip) chip.textContent = obj.owner_handle;
    if (obj.display_url) document.getElementById('omnibox').value = obj.display_url;
    return;
  }}
  if (obj && obj.plane === 'local' && obj.origin) {{
    line.textContent = 'Local app · ' + obj.origin + ' · data stays on this machine';
    return;
  }}
  line.textContent = '';
}}
function noteReceipt(obj) {{
  if (!obj || !obj.receipt) return;
  const rec = document.getElementById('receipts');
  const el = document.createElement('div');
  el.className = 'receipt';
  el.textContent = obj.receipt.seq + ' ' + obj.receipt.action + ' ' + obj.receipt.hash;
  rec.prepend(el);
}}
function show(obj) {{
  const stage = document.getElementById('stage');
  const rec = document.getElementById('receipts');
  paintOwner(obj);
  noteReceipt(obj);
  const summary = (obj.display && obj.display.summary) || obj.note || '';
  if (obj && (obj.policy_page || obj.shell_page) && obj.html) {{
    stage.innerHTML = obj.html;
    return;
  }}
  if (obj && obj.code === 'FG-GATE-REFUSE') {{
    stage.innerHTML = '<section class="refusal"><h1>Blocked</h1><p>FG-GATE-REFUSE</p><p>' + (obj.reason || '') + '</p><p>' + summary + '</p></section>';
    return;
  }}
  let body = '<div class="banner">' + summary + '</div>';
  if (obj.name_status === 'PENDING') {{
    body += '<p>Pending · not a verified site</p>';
  }} else if (obj.quarantine && !obj.promoted) {{
    body += '<p>Quarantine · scanner absent · not promoted · not run</p>';
  }} else if (obj.html) {{
    body += '<iframe sandbox="" style="width:100%;min-height:240px;background:#fff;border:1px solid #8a7219" srcdoc="' + String(obj.html).replace(/"/g,'&quot;') + '"></iframe>';
  }}
  stage.innerHTML = body + '<pre>' + JSON.stringify(obj,null,2) + '</pre>';
  if (obj.stages) {{
    document.getElementById('airlockPanel').innerHTML = obj.stages.map(s => s.stage + ' · ' + (s.hash||'').slice(0,16)).join('<br>');
  }}
}}
async function paintTabs() {{
  const t = await op('tab_list', {{}});
  const box = document.getElementById('tabs');
  box.innerHTML = '';
  (t.tabs||[]).forEach(tab => {{
    const b = document.createElement('button');
    b.className = 'tab' + (tab.id === t.active ? ' active' : '');
    b.textContent = tab.title || 'Tab';
    b.onclick = async () => show(await op('tab_switch', {{tab_id: tab.id}}));
    box.appendChild(b);
  }});
  const plus = document.createElement('button');
  plus.className = 'plus';
  plus.textContent = '+';
  plus.onclick = async () => {{ show(await op('tab_new', {{}})); paintTabs(); }};
  box.appendChild(plus);
}}
document.getElementById('back').onclick = async () => show(await op('back', {{}}));
document.getElementById('fwd').onclick = async () => show(await op('forward', {{}}));
document.getElementById('reload').onclick = async () => show(await op('reload', {{}}));
document.getElementById('home').onclick = async () => {{ show(await op('home', {{}})); document.getElementById('omnibox').value=''; }};
document.getElementById('go').onclick = async () => {{
  const q = document.getElementById('omnibox').value.trim();
  const looksUrl = /\\.|:/.test(q) && !/\\s/.test(q);
  show(await op(looksUrl ? 'navigate' : 'ethical_search', looksUrl ? {{url:q}} : {{q}}));
}};
document.getElementById('omnibox').addEventListener('keydown', (e) => {{ if (e.key==='Enter') document.getElementById('go').click(); }});
document.getElementById('airlockBtn').onclick = async () => {{
  const q = document.getElementById('omnibox').value.trim();
  show(await op('airlock', {{url:q}}));
}};
document.getElementById('promoteBtn').onclick = async () => {{
  const q = document.getElementById('omnibox').value.trim();
  show(await op('navigate', {{url:q, operator_override:true}}));
}};
document.getElementById('islandBtn').onclick = async () => {{
  islandOn = !islandOn;
  show(await op('island_mode', {{enabled: islandOn}}));
}};
document.getElementById('blockBtn').onclick = async () => {{
  const handle = lastHandle || (document.getElementById('omnibox').value.trim().split('.')[0] || '');
  show(await op('peer_block', {{handle: handle}}));
}};
document.getElementById('trustBtn').onclick = async () => {{
  const handle = lastHandle || (document.getElementById('omnibox').value.trim().split('.')[0] || '');
  show(await op('trust', {{handle: handle}}));
}};
document.getElementById('designBtn').onclick = async () => {{
  const handle = lastHandle || (document.getElementById('omnibox').value.trim().split('.')[0] || '');
  show(await op('design_mode', {{handle: handle}}));
  paintTabs();
}};
document.getElementById('slotsBtn').onclick = async () => {{
  const handle = lastHandle || (document.getElementById('omnibox').value.trim().split('.')[0] || '');
  const obj = await op('slots', {{handle: handle}});
  show(obj);
  const stage = document.getElementById('stage');
  const reserved = (obj.reserved || []).map(row => '<li>' + row.label + ' · ' + row.host + ' · not user-nameable</li>').join('');
  const user = (obj.user || []).map(row => '<li>' + row.id + ' · ' + (row.name || 'empty') + ' · ' + row.status + '</li>').join('');
  stage.innerHTML = '<section class="refusal"><h1>Domain slots</h1><p>Automatic name: ' + (obj.automatic_name || 'unset') + '</p><h2>Reserved</h2><ul>' + reserved + '</ul><h2>User</h2><ul>' + user + '</ul><p>' + (obj.note || '') + '</p></section>';
}};
const APPEAR_KEY = 'azbrowser-appearance';
function readAppearance() {{
  var saved = null;
  try {{ saved = JSON.parse(localStorage.getItem(APPEAR_KEY) || 'null'); }} catch (e) {{}}
  if (saved && saved.theme) return saved;
  var day = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches;
  return {{ theme: day ? 'day' : 'night', mode: day ? 'day' : 'night', aziel: false, bookmarks: false }};
}}
function paintAppearance(state) {{
  const theme = state.aziel ? 'aziel' : state.mode;
  document.documentElement.setAttribute('data-theme', theme);
  document.getElementById('bookmarks').hidden = !state.bookmarks;
  document.getElementById('themeToggle').textContent = state.mode === 'day' ? 'Night' : 'Day';
  document.getElementById('azielMode').setAttribute('aria-pressed', state.aziel ? 'true' : 'false');
  localStorage.setItem(APPEAR_KEY, JSON.stringify({{ theme: theme, mode: state.mode, aziel: state.aziel, bookmarks: state.bookmarks }}));
  paintBookmarks();
}}
let appearance = readAppearance();
if (appearance.theme === 'aziel') appearance.aziel = true;
if (!appearance.mode) appearance.mode = appearance.theme === 'day' ? 'day' : 'night';
function paintBookmarks() {{
  const list = document.getElementById('bookmarkList');
  const rows = JSON.parse(localStorage.getItem('azbrowser-bookmarks') || '[]');
  list.innerHTML = '';
  rows.forEach(row => {{
    const b = document.createElement('button');
    b.type = 'button';
    b.textContent = row.title || row.url;
    b.onclick = () => {{ document.getElementById('omnibox').value = row.url; document.getElementById('go').click(); }};
    list.appendChild(b);
  }});
}}
document.getElementById('themeToggle').onclick = () => {{
  appearance.mode = appearance.mode === 'day' ? 'night' : 'day';
  appearance.aziel = false;
  paintAppearance(appearance);
}};
document.getElementById('azielMode').onclick = () => {{
  appearance.aziel = !appearance.aziel;
  paintAppearance(appearance);
}};
document.getElementById('bookmarkAdd').onclick = () => {{
  const url = document.getElementById('omnibox').value.trim();
  if (!url) return;
  const rows = JSON.parse(localStorage.getItem('azbrowser-bookmarks') || '[]');
  rows.push({{ title: url, url: url }});
  localStorage.setItem('azbrowser-bookmarks', JSON.stringify(rows.slice(-12)));
  paintBookmarks();
}};
document.getElementById('settingsBtn').onclick = () => {{
  const on = appearance.bookmarks ? ' checked' : '';
  document.getElementById('stage').innerHTML = '<section class="refusal"><h1>Settings</h1><p>Day and night flip immediately. Aziel mode uses gold, black, and royal purple. The choice is remembered on this machine.</p><label><input id="bookmarkPref" type="checkbox"' + on + '> Show bookmarks bar</label><p>Design mode opens as a local tab. Domain slots are four reserved hub mirrors and three user names.</p></section>';
  document.getElementById('bookmarkPref').onchange = (e) => {{
    appearance.bookmarks = e.target.checked;
    paintAppearance(appearance);
  }};
}};
paintAppearance(appearance);
if (document.documentElement.getAttribute('data-bookmarks') === 'on') {{
  appearance.bookmarks = true;
  document.getElementById('bookmarks').hidden = false;
}}
document.getElementById('stage').innerHTML = '<section class="start"><h1>AZBrowser</h1><p>Lamb Lens search, a URL, or a .aziel name.</p><div class="banner">{LIMITATION}</div><p>Counted Worker: <a href="{HOST}">{HOST}</a></p><img alt="sigil" src="'+SIGIL+'" width="96" height="96"></section>';
function meshNum() {{
  for (let i = 0; i < arguments.length; i++) {{
    const raw = arguments[i];
    if (raw == null || raw === "") continue;
    const n = typeof raw === "number" ? raw : Number(String(raw).replace(/,/g, ""));
    if (Number.isFinite(n) && n >= 0) return Math.floor(n);
  }}
  return 0;
}}
function unwrapMesh(j) {{
  if (!j || typeof j !== "object") return {{}};
  if (j.result && typeof j.result === "object") return Object.assign({{}}, j, j.result);
  if (j.mesh && typeof j.mesh === "object") return Object.assign({{}}, j, j.mesh);
  return j;
}}
function paintMesh(raw) {{
  const j = unwrapMesh(raw);
  const on = j.enabled === true || String(j.status || "").toLowerCase() === "on";
  const r = (j.rollup && typeof j.rollup === "object") ? j.rollup : {{}};
  const live = on ? meshNum(r.live, j.live_nodes, j.live) : 0;
  const locked = on ? meshNum(r.locked, j.locked_nodes, j.locked) : 0;
  const isolated = on ? meshNum(r.isolated, j.isolated_nodes, j.isolated) : 0;
  document.getElementById("meshLiveCount").textContent = String(live);
  document.getElementById("qnmLive").textContent = String(live);
  document.getElementById("qnmLocked").textContent = String(locked);
  document.getElementById("qnmIsolated").textContent = String(isolated);
  document.getElementById("meshLine").textContent = on
    ? ("Suite mesh: on · live " + live + " · locked " + locked + " · isolated " + isolated + ". Not an anonymity network.")
    : "Suite mesh: off (default). QNM-BUILD-1.0 + QNS-CD-1.0. Not an anonymity network.";
}}
async function refreshMesh() {{
  try {{
    paintMesh(await (await fetch("/v1/mesh", {{ headers: {{ "user-agent": "Mozilla/5.0" }} }})).json());
  }} catch (e) {{
    paintMesh({{ ok: false, enabled: false, status: "unavailable" }});
  }}
}}
document.getElementById("meshEnable").onclick = async () => {{ await fetch("/v1/mesh/enable", {{ method: "POST", headers: {{ "content-type": "application/json", "user-agent": "Mozilla/5.0" }}, body: "{{}}" }}); refreshMesh(); }};
document.getElementById("meshDisable").onclick = async () => {{ await fetch("/v1/mesh/disable", {{ method: "POST", headers: {{ "content-type": "application/json", "user-agent": "Mozilla/5.0" }}, body: "{{}}" }}); refreshMesh(); }};
document.getElementById("meshJoin").onclick = async () => {{
  const j = await (await fetch("/v1/mesh/join", {{ method: "POST", headers: {{ "content-type": "application/json", "user-agent": "Mozilla/5.0" }}, body: JSON.stringify({{ product: "azbrowser", label: "AZBrowser local" }}) }})).json();
  const inner = unwrapMesh(j);
  const id = inner.node_id || inner.id;
  if (id) sessionStorage.setItem("azbrowser_mesh_node", String(id));
  refreshMesh();
}};
document.getElementById("meshLeave").onclick = async () => {{
  const id = sessionStorage.getItem("azbrowser_mesh_node");
  if (id) await fetch("/v1/mesh/leave", {{ method: "POST", headers: {{ "content-type": "application/json", "user-agent": "Mozilla/5.0" }}, body: JSON.stringify({{ node_id: id }}) }});
  sessionStorage.removeItem("azbrowser_mesh_node");
  refreshMesh();
}};
refreshMesh();
setInterval(refreshMesh, 30000);
paintTabs();
</script>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: object) -> None:
        return

    def _send(self, status: int, body: bytes, ctype: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "private, no-store")
        self.end_headers()
        self.wfile.write(body)

    def _proxy_door(self, path: str) -> None:
        dest = door_target_url(path)
        if not dest:
            self._send(404, b'{"error":"not a door path"}', "application/json")
            return
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n) if n else b""
        headers = {"User-Agent": self.headers.get("User-Agent") or "Mozilla/5.0 AZBrowser/0.1.0"}
        ctype = self.headers.get("Content-Type")
        if ctype:
            headers["Content-Type"] = ctype
        try:
            req = Request(dest, data=raw or None, headers=headers, method=self.command)
            with urlopen(req, timeout=20) as res:  # noqa: S310 — public aziel-runtime door
                body = res.read()
                self._send(res.status, body, res.headers.get_content_type() or "application/json")
        except HTTPError as exc:
            body = exc.read() if exc.fp else b'{"error":"fraggate_proxy_failed"}'
            self._send(exc.code, body, "application/json")
        except (URLError, TimeoutError, OSError) as exc:
            payload = json.dumps({"ok": False, "error": "fraggate_proxy_failed", "detail": str(exc)[:240]})
            self._send(502, payload.encode("utf-8"), "application/json")

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path == "/":
            self._send(200, _chrome().encode("utf-8"), "text/html; charset=utf-8")
            return
        classified = classify_v1_path(path)
        if classified["kind"] == "door":
            self._proxy_door(path)
            return
        if path == "/v1/health":
            self._send(200, json.dumps(ENGINE.health({}), indent=2).encode(), "application/json")
            return
        self._send(404, b'{"error":"not found"}', "application/json")

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path.rstrip("/")
        classified = classify_v1_path(path)
        if classified["kind"] == "door":
            self._proxy_door(path)
            return
        if classified["kind"] == "multi":
            payload = json.dumps({
                "ok": False,
                "error": "not a local op",
                "code": "NOT_LOCAL_OP",
                "path": classified["path"],
                "hint": "Local ops are /v1/{op} only. FragGate door is /v1/fraggate/*.",
            })
            self._send(404, payload.encode("utf-8"), "application/json")
            return
        op = classified.get("op")
        if classified["kind"] != "local" or not op:
            self._send(404, b'{"error":"not found"}', "application/json")
            return
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n) if n else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._send(400, b'{"error":"JSON body required"}', "application/json")
            return
        out = ENGINE.call(op, payload if isinstance(payload, dict) else {})
        self._send(200 if out.get("ok", True) else 400, json.dumps(out, indent=2).encode(), "application/json")


def serve(host: str = "127.0.0.1", port: int = PORT) -> int:
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"AZBrowser local UI http://{host}:{port} (loopback only)")
    print(LIMITATION)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        return 0
    return 0
