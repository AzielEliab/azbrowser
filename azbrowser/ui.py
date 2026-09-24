"""Loopback research-browser chrome. 127.0.0.1 only. No telemetry."""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .door import classify_v1_path, door_target_url
from .engine import Engine
from .meta import HOST, __version__
from .receipts import Ledger

_SIGIL_PATH = Path(__file__).resolve().parents[1] / "workers" / "download-tracker" / "public" / "sigil.png"


def sigil_png() -> bytes:
    return _SIGIL_PATH.read_bytes()

PORT = 8878
ENGINE = Engine(Ledger("./azbrowser_receipts.jsonl"))


def bind_message(host: str, port: int) -> str:
    return f"Open http://{host}:{port}/"


def _chrome() -> str:
    return f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AZBrowser — local research shell</title>
<style>
:root, html[data-theme="night"] {{ color-scheme: dark; --bg:#0b0b0b; --text:#f5f5f5; --muted:#c8c8c8; --bar:#141414; --panel:#111111; --line:#2c2c2c; --gold:#f5f5f5; --trim:#3a3a3a; --ink:#0b0b0b; --focus:#c9a227; --tab:#1c1c1c; --banner:#161616; }}
html[data-theme="day"] {{ color-scheme: light; --bg:#ffffff; --text:#141414; --muted:#333333; --bar:#f3f3f3; --panel:#f7f7f7; --line:#d4d4d4; --gold:#141414; --trim:#c8c8c8; --ink:#ffffff; --focus:#c9a227; --tab:#ffffff; --banner:#f3f3f3; }}
html[data-theme="aziel"] {{ color-scheme: dark; --bg:#0b0b0b; --text:#f6f1e4; --muted:#e4d2a0; --bar:#2a1454; --panel:#231246; --line:#6d4ea3; --gold:#f0d060; --trim:#8d6bc4; --ink:#1a1204; --focus:#f0d060; --tab:#3a1d6e; --banner:#2a1454; }}
* {{ box-sizing: border-box; }}
html,body {{ margin:0; height:100%; background:var(--bg); color:var(--text); font:15px/1.45 "Segoe UI", system-ui, sans-serif; overflow-x:clip; }}
#chrome {{ display:flex; flex-direction:column; height:100%; min-width:0; max-width:100%; background:var(--bg); }}
.tabs {{ display:flex; gap:6px; padding:8px 10px 0; background:var(--bar); border-bottom:1px solid var(--line); min-height:42px; min-width:0; max-width:100%; overflow-x:auto; }}
.tab {{ padding:8px 14px; border:1px solid transparent; border-bottom:none; border-radius:10px 10px 0 0; background:transparent; color:var(--muted); cursor:pointer; max-width:12rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; flex:0 0 auto; }}
.tab.active {{ background:var(--gold); color:var(--ink); }}
.plus {{ color:var(--text); cursor:pointer; padding:6px 10px; background:transparent; border:0; flex:0 0 auto; }}
.bar {{ display:flex; flex-wrap:wrap; align-items:center; gap:8px; padding:10px 12px; background:var(--bar); min-width:0; max-width:100%; }}
.bar button, #bookmarks button, #startGo {{ background:transparent; color:var(--text); border:0; border-radius:8px; min-width:34px; height:34px; padding:0 8px; cursor:pointer; font:inherit; }}
.node button, .quick button, .hit {{ background:transparent; color:var(--text); border:1px solid var(--line); border-radius:8px; min-width:36px; height:auto; min-height:34px; padding:6px 10px; cursor:pointer; font:inherit; }}
.bar button:hover {{ background:var(--banner); }}
.node button:hover, .quick button:hover {{ border-color:var(--focus); color:var(--text); }}
button:focus-visible, a:focus-visible, input:focus-visible, summary:focus-visible {{ outline:2px solid var(--focus); outline-offset:2px; }}
#go, #startGo {{ background:var(--gold); color:var(--ink); border-radius:999px; padding:0 16px; min-width:52px; height:42px; font-weight:600; }}
#themeMenu button[aria-pressed="true"] {{ background:var(--gold); color:var(--ink); }}
#home img {{ width:20px; height:20px; vertical-align:middle; }}
#omnibox {{ flex:1 1 12rem; min-width:0; background:var(--bg); color:var(--text); border:1px solid var(--line); border-radius:999px; padding:9px 16px; font:15px/1.3 inherit; }}
#handleChip {{ font-size:12px; color:var(--muted); padding:0 4px; max-width:100%; overflow:hidden; text-overflow:ellipsis; }}
#bookmarks {{ display:flex; gap:8px; align-items:center; padding:6px 12px; background:var(--bar); border-top:1px solid var(--line); font-size:13px; }}
#bookmarks[hidden] {{ display:none; }}
#bookmarkList {{ display:flex; gap:8px; flex-wrap:wrap; }}
#ownerLine {{ padding:4px 14px 8px; min-height:1.2em; color:var(--muted); background:var(--bar); font-size:13px; }}
.mode {{ color:var(--muted); font-size:12px; letter-spacing:.04em; }}
main {{ flex:1; display:grid; grid-template-columns: 1fr; min-height:0; min-width:0; max-width:100%; }}
#stage {{ overflow:auto; padding:28px 32px; min-width:0; max-width:100%; }}
aside {{ border-left:1px solid var(--line); overflow:auto; padding:16px; background:var(--panel); min-width:0; max-width:100%; }}
h2 {{ color:var(--muted); font-size:12px; letter-spacing:.06em; text-transform:uppercase; margin:16px 0 8px; }}
.banner, .refusal {{ border:1px solid var(--line); background:var(--banner); color:var(--text); padding:16px 18px; border-radius:12px; margin-bottom:16px; }}
.refusal {{ max-width:40rem; }}
.refusal h1, .policy-page h1, .design-page h1 {{ font-size:1.7rem; font-weight:560; margin:0 0 8px; }}
.policy-page details {{ margin-top:16px; }}
.policy-page summary {{ cursor:pointer; }}
pre {{ white-space:pre-wrap; word-break:break-word; overflow-wrap:anywhere; font-size:12px; color:var(--muted); max-width:100%; }}
.receipt {{ font-family:ui-monospace,monospace; font-size:11px; border-bottom:1px solid var(--line); padding:6px 0; }}
.status {{ border-top:1px solid var(--line); padding:8px 12px; font-size:12px; color:var(--muted); }}
#meshStrip {{ border-top:1px solid var(--line); padding:8px 14px; background:transparent; display:flex; flex-wrap:wrap; align-items:center; gap:8px 16px; font-size:12px; color:var(--muted); min-width:0; max-width:100%; }}
#meshStrip .live b {{ color:var(--text); font-size:18px; margin-right:6px; }}
#meshStrip button {{ background:transparent; color:var(--text); border:1px solid var(--line); border-radius:6px; height:28px; padding:0 10px; cursor:pointer; }}
.node {{ display:flex; flex-wrap:wrap; gap:6px; margin-bottom:8px; }}
a {{ color:inherit; }}
.start {{ min-height:62vh; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:18px; text-align:center; padding:48px 20px 32px; max-width:100%; }}
.start h1 {{ font-size:1.35rem; font-weight:500; margin:0; letter-spacing:0; }}
.start p {{ margin:0; max-width:36rem; color:var(--muted); }}
.start img {{ width:84px; height:84px; display:block; }}
.start-form {{ width:min(560px, 100%); display:flex; gap:8px; align-items:center; }}
#startBox {{ flex:1; min-width:0; width:auto; background:var(--bg); color:var(--text); border:1px solid var(--line); border-radius:999px; padding:12px 18px; font:16px/1.3 inherit; }}
.quick {{ display:flex; flex-wrap:wrap; gap:6px 8px; justify-content:center; max-width:min(640px, 100%); }}
.quick button {{ background:transparent; color:var(--muted); border:0; border-radius:8px; padding:6px 10px; cursor:pointer; font:14px/1.3 inherit; }}
.quick button:hover {{ color:var(--text); background:var(--banner); }}
.page, .settings-page, .refusal, .banner {{ overflow-wrap:anywhere; max-width:40rem; }}
.page h1 {{ font-size:1.7rem; font-weight:560; margin:0 0 8px; }}
.hits {{ list-style:none; padding:0; margin:16px 0; }}
.hits li {{ margin:0 0 14px; text-align:left; }}
.hit {{ display:inline-block; text-align:left; }}
.fields {{ display:grid; grid-template-columns:minmax(6rem, 9rem) 1fr; gap:4px 12px; margin:12px 0; }}
.fields dt {{ color:var(--muted); }}
.fields dd {{ margin:0; }}
details.more {{ margin-top:18px; }}
#themeToggle {{ min-width:4.5rem; }}
.theme {{ position:relative; }}
#themeMenu {{ position:absolute; right:0; top:40px; z-index:4; background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:6px; display:flex; flex-direction:column; min-width:132px; }}
#themeMenu[hidden] {{ display:none; }}
#themeMenu button {{ text-align:left; width:100%; }}
#sidePanel[hidden] {{ display:none !important; }}
main {{ grid-template-columns: 1fr; }}
html[data-panel="open"] main {{ grid-template-columns: 1fr 280px; }}
.statusline {{ border-top:1px solid var(--line); padding:8px 14px; font-size:12px; color:var(--muted); display:flex; flex-wrap:wrap; gap:8px 16px; align-items:center; min-width:0; max-width:100%; }}
.settings-page {{ max-width:40rem; }}
.settings-page h1 {{ font-size:1.7rem; font-weight:560; margin:0 0 12px; }}
#ownerLine:empty {{ display:none; }}
.iconbtn {{ font-size:16px; }}
#chrome, .bar, .tabs, aside, #stage {{ transition: background-color .12s ease, color .12s ease; }}
@media (max-width: 860px) {{
  html[data-panel="open"] main {{ grid-template-columns: 1fr; }}
  html[data-panel="open"] #sidePanel {{ border-left: 0; border-top: 1px solid var(--line); order: -1; }}
}}
@media (max-width: 480px) {{
  .bar {{ padding:8px; }}
  #omnibox {{ flex-basis:100%; }}
  #stage {{ padding:16px 12px; }}
  .start {{ padding:20px 12px 16px; min-height:auto; }}
  .start-form {{ flex-direction:column; align-items:stretch; }}
  #startGo, #go {{ height:42px; }}
  .fields {{ grid-template-columns:1fr; }}
}}
</style>
<script>
(function() {{
  var saved = null;
  try {{ saved = JSON.parse(localStorage.getItem('azbrowser-appearance') || 'null'); }} catch (e) {{}}
  var theme = 'night';
  if (saved && (saved.theme === 'day' || saved.theme === 'night' || saved.theme === 'aziel')) theme = saved.theme;
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
    <button id="home" title="Home" type="button"><img class="brandmark" alt="" src="/sigil.png"></button>
    <input id="omnibox" placeholder="Search or enter a .aziel name or web address" spellcheck="false" aria-label="Address">
    <span id="handleChip"></span>
    <button id="go" type="button" title="Go">Go</button>
    <div class="theme">
      <button id="themeToggle" type="button" title="Theme. Night, Day, or Aziel." aria-haspopup="true" aria-expanded="false">Night</button>
      <div id="themeMenu" hidden>
        <button type="button" data-theme-choice="night">Night</button>
        <button type="button" data-theme-choice="day">Day</button>
        <button id="azielMode" type="button" data-theme-choice="aziel" title="Aziel mode. Gold, black, and royal purple." aria-pressed="false">Aziel</button>
      </div>
    </div>
    <button id="settingsBtn" type="button" title="Settings" aria-label="Settings">Settings</button>
    <button id="panelToggle" type="button" title="Advanced" aria-label="Advanced" aria-expanded="false">Advanced</button>
  </div>
  <div id="bookmarks" hidden>
    <span>Bookmarks</span>
    <div id="bookmarkList"></div>
    <button id="bookmarkAdd" type="button">Bookmark this page</button>
  </div>
  <div id="ownerLine"></div>
  <main>
    <section id="stage"></section>
    <aside id="sidePanel" hidden>
      <h2>Advanced</h2>
      <div class="node">
        <button id="airlockBtn" type="button" title="Check the current address in the airlock">Airlock</button>
        <button id="promoteBtn" type="button" title="Show a quarantined page on this machine">Promote</button>
        <button id="islandBtn" type="button" title="Leave mesh peers. Local apps and the web stay open">Island</button>
        <button id="blockBtn" type="button" title="Block the current handle on this machine">Block peer</button>
        <button id="trustBtn" type="button" title="Local trust for the current handle">Trust</button>
        <button id="slotsBtn" type="button" title="Four reserved hub mirrors and three user sites">Slots</button>
        <button id="designBtn" type="button" title="Design mode on this machine. Publish stays on the local node.">Design</button>
      </div>
      <h2>Mesh</h2>
      <div class="node">
        <button id="meshEnable" type="button" title="Turn mesh presence on">Turn on</button>
        <button id="meshDisable" type="button" title="Turn mesh presence off">Turn off</button>
        <button id="meshJoin" type="button" title="Join this browser to the mesh">Join</button>
        <button id="meshLeave" type="button" title="Leave the mesh">Leave</button>
      </div>
      <p class="cite" hidden>live <b id="qnmLive">0</b> locked <b id="qnmLocked">0</b> isolated <b id="qnmIsolated">0</b></p>
      <h2>Airlock</h2>
      <div id="airlockPanel"></div>
      <h2>Receipts</h2>
      <div id="receipts"></div>
    </aside>
  </main>
  <div id="meshStrip" class="statusline" aria-label="Mesh status">
    <span id="meshLine">Mesh off</span>
    <span>Nodes <b id="meshNodeCount">0</b></span>
    <span>Live Nodes <b id="meshLiveCount">0</b></span>
  </div>
</div>
<script>
const SIGIL = "/sigil.png";
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
    const plain = (obj.clarity && obj.clarity.plain) || ('Blocked · FG-GATE-REFUSE · ' + (obj.reason || ''));
    line.textContent = plain;
    if (chip && obj.reason === 'handle_isolated') chip.textContent = 'Isolated';
    else if (chip && obj.reason === 'name_pending') chip.textContent = 'Pending';
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
function escText(value) {{
  return String(value == null ? '' : value).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}}
function refusalHtml(obj, summary) {{
  const c = (obj && obj.clarity) || {{}};
  const plain = c.plain || summary || obj.reason || '';
  const next = c.next || '';
  const code = obj.code || 'FG-GATE-REFUSE';
  return '<section class="refusal"><h1>Blocked</h1><p>' + escText(plain) + '</p><p>' + escText(next) + '</p><p>' + escText(code) + ' · ' + escText(obj.reason || '') + '</p></section>';
}}
function fieldList(obj) {{
  const fields = (obj.display && obj.display.fields) || [];
  if (!fields.length) return '';
  return '<dl class="fields">' + fields.map(row => '<dt>' + escText(row.label) + '</dt><dd>' + escText(row.value) + '</dd>').join('') + '</dl>';
}}
function resultList(results) {{
  return '<ul class="hits">' + results.map(hit => {{
    const url = hit.url || '';
    const title = hit.title || url || 'Result';
    const blurb = hit.blurb || '';
    const open = url ? '<button type="button" class="hit" data-url="' + escText(url) + '">' + escText(title) + '</button>' : '<strong>' + escText(title) + '</strong>';
    return '<li>' + open + (blurb ? '<p>' + escText(blurb) + '</p>' : '') + (url ? '<p class="cite">' + escText(url) + '</p>' : '') + '</li>';
  }}).join('') + '</ul>';
}}
function bindHits() {{
  document.querySelectorAll('#stage [data-url]').forEach(btn => {{
    btn.onclick = () => {{
      document.getElementById('omnibox').value = btn.getAttribute('data-url');
      document.getElementById('go').click();
    }};
  }});
}}
function humanPage(obj, summary) {{
  const searching = obj.action === 'ethical_search';
  const title = searching ? 'Search' : ((obj.display && obj.display.title) || 'Result');
  const lead = searching
    ? ('Advisory results for “' + (obj.query || '') + '”. Cite the source.')
    : summary;
  let body = '<article class="page"><h1>' + escText(title) + '</h1>';
  if (lead) body += '<p>' + escText(lead) + '</p>';
  if (obj.name_status === 'PENDING') body += '<p>Pending. No page was loaded.</p>';
  else if (obj.quarantine && !obj.promoted) body += '<p>Held in quarantine. This shell has no malware scanner. Choose Promote under Advanced to view the scrubbed page. Scripts do not run.</p>';
  if (Array.isArray(obj.results) && obj.results.length) body += resultList(obj.results);
  if (obj.note && obj.note !== summary && obj.note !== lead) body += '<p>' + escText(obj.note) + '</p>';
  if (obj.html) {{
    body += '<iframe sandbox="" title="Page preview" style="width:100%;min-height:240px;background:#fff;border:1px solid var(--line);border-radius:12px" srcdoc="' + String(obj.html).replace(/"/g,'&quot;') + '"></iframe>';
  }}
  body += '<details class="more"><summary>Details</summary>' + fieldList(obj) + '<pre>' + escText(JSON.stringify(obj, null, 2)) + '</pre></details></article>';
  return body;
}}
function show(obj) {{
  const stage = document.getElementById('stage');
  paintOwner(obj);
  noteReceipt(obj);
  const summary = (obj.display && obj.display.summary) || obj.note || '';
  if (obj && (obj.policy_page || obj.shell_page) && obj.html) {{
    stage.innerHTML = obj.html;
    return;
  }}
  if (obj && obj.code === 'FG-GATE-REFUSE') {{
    stage.innerHTML = refusalHtml(obj, summary);
    return;
  }}
  if (obj && obj.code === 'ETHICS_REFUSE') {{
    stage.innerHTML = refusalHtml(obj, summary);
    return;
  }}
  if (obj && (obj.action === 'home' || (obj.tab && obj.tab.kind === 'newtab' && !obj.html && !obj.results && obj.action !== 'navigate'))) {{
    stage.innerHTML = startPage();
    bindStart();
    return;
  }}
  stage.innerHTML = humanPage(obj, summary);
  bindHits();
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
  plus.type = 'button';
  plus.textContent = '+';
  plus.title = 'New tab';
  plus.setAttribute('aria-label', 'New tab');
  plus.onclick = async () => {{ await op('tab_new', {{}}); document.getElementById('stage').innerHTML = startPage(); bindStart(); paintTabs(); }};
  box.appendChild(plus);
}}
document.getElementById('back').onclick = async () => show(await op('back', {{}}));
document.getElementById('fwd').onclick = async () => show(await op('forward', {{}}));
document.getElementById('reload').onclick = async () => show(await op('reload', {{}}));
document.getElementById('home').onclick = async () => {{ show(await op('home', {{}})); document.getElementById('omnibox').value=''; }};
document.getElementById('go').onclick = async () => {{
  const q = document.getElementById('omnibox').value.trim();
  if (!q) {{
    document.getElementById('stage').innerHTML = startPage();
    bindStart();
    const box = document.getElementById('startBox');
    if (box) box.focus();
    return;
  }}
  const looksUrl = /\\.|:/.test(q) && !/\\s/.test(q);
  show(await op(looksUrl ? 'navigate' : 'ethical_search', looksUrl ? {{url:q}} : {{q}}));
  paintTabs();
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
  refreshMesh();
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
  return {{ theme: 'night', mode: 'night', aziel: false, bookmarks: false }};
}}
function paintAppearance(state) {{
  const theme = state.aziel ? 'aziel' : (state.mode || 'night');
  document.documentElement.setAttribute('data-theme', theme);
  document.getElementById('bookmarks').hidden = !state.bookmarks;
  const mark = theme === 'day' ? 'Day' : (theme === 'aziel' ? 'Aziel' : 'Night');
  const toggle = document.getElementById('themeToggle');
  toggle.textContent = mark;
  toggle.title = theme === 'aziel' ? 'Theme. Aziel. Gold, black, and royal purple.' : (theme === 'day' ? 'Theme. Day.' : 'Theme. Night.');
  document.querySelectorAll('[data-theme-choice]').forEach(btn => {{
    const choice = btn.getAttribute('data-theme-choice');
    const on = choice === 'aziel' ? !!state.aziel : (!state.aziel && state.mode === choice);
    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
  }});
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
function chooseTheme(choice) {{
  if (choice === 'aziel') {{
    appearance.aziel = true;
    if (!appearance.mode) appearance.mode = 'night';
  }} else {{
    appearance.aziel = false;
    appearance.mode = choice === 'day' ? 'day' : 'night';
  }}
  paintAppearance(appearance);
  const menu = document.getElementById('themeMenu');
  menu.hidden = true;
  document.getElementById('themeToggle').setAttribute('aria-expanded', 'false');
}}
document.getElementById('themeToggle').onclick = (e) => {{
  e.stopPropagation();
  const menu = document.getElementById('themeMenu');
  menu.hidden = !menu.hidden;
  document.getElementById('themeToggle').setAttribute('aria-expanded', menu.hidden ? 'false' : 'true');
}};
document.querySelectorAll('#themeMenu [data-theme-choice]').forEach(btn => {{
  btn.onclick = (e) => {{ e.stopPropagation(); chooseTheme(btn.getAttribute('data-theme-choice')); }};
}});
document.addEventListener('click', () => {{
  const menu = document.getElementById('themeMenu');
  if (menu) menu.hidden = true;
}});
document.getElementById('panelToggle').onclick = () => {{
  const panel = document.getElementById('sidePanel');
  panel.hidden = !panel.hidden;
  document.documentElement.setAttribute('data-panel', panel.hidden ? 'closed' : 'open');
  document.getElementById('panelToggle').setAttribute('aria-expanded', panel.hidden ? 'false' : 'true');
}};
document.getElementById('bookmarkAdd').onclick = () => {{
  const url = document.getElementById('omnibox').value.trim();
  if (!url) return;
  const rows = JSON.parse(localStorage.getItem('azbrowser-bookmarks') || '[]');
  rows.push({{ title: url, url: url }});
  localStorage.setItem('azbrowser-bookmarks', JSON.stringify(rows.slice(-12)));
  paintBookmarks();
}};
function settingsPage() {{
  const on = appearance.bookmarks ? ' checked' : '';
  return '<section class="settings-page"><h1>Settings</h1>'
    + '<h2>Appearance</h2><p>Night is the first look: black background, white text. Day is white with black text. Aziel is gold, black, and royal purple. The choice is remembered on this machine.</p>'
    + '<div class="node"><button type="button" data-theme-choice="night">Night</button><button type="button" data-theme-choice="day">Day</button><button type="button" data-theme-choice="aziel">Aziel</button></div>'
    + '<label><input id="bookmarkPref" type="checkbox"' + on + '> Show bookmarks bar</label>'
    + '<h2>Advanced</h2><p>Advanced holds Airlock, Promote, Island, Block peer, Trust, Slots, and Design. Mesh on, off, join, and leave are in that same panel. Design mode stays on this machine.</p>'
    + '<h2>About</h2>'
    + '<p>AZBrowser is a research shell for search, tabs, and mesh names. Version {__version__}. Author Aziel Eliab.</p>'
    + '<p>A search, a .aziel name, or a web address goes in one step. Local apps open here. Web addresses keep working.</p>'
    + '<p>A verified handle is named beside the address. A pending name is marked Pending and is not opened. An isolated handle explains what happened and what you can do next.</p>'
    + '<p>Mesh pages stay in quarantine until you choose Promote. This shell has no malware scanner, and it does not run page scripts. Handle keys stay on this machine.</p>'
    + '<p>Island and Block peer apply on this machine. Each action keeps a receipt here.</p>'
    + '<p>There are no ads, no tracking, and no telemetry.</p>'
    + '<p>AZMail and AZNet are separate programs. This node has four reserved hub mirrors and three user sites. MirageGrid decoy names stay on their own list.</p>'
    + '<p>The public copy is at {HOST}.</p>'
    + '</section>';
}}
document.getElementById('settingsBtn').onclick = () => {{
  document.getElementById('stage').innerHTML = settingsPage();
  document.getElementById('bookmarkPref').onchange = (e) => {{
    appearance.bookmarks = e.target.checked;
    paintAppearance(appearance);
  }};
  document.querySelectorAll('.settings-page [data-theme-choice]').forEach(btn => {{
    btn.onclick = () => chooseTheme(btn.getAttribute('data-theme-choice'));
  }});
}};
paintAppearance(appearance);
if (document.documentElement.getAttribute('data-bookmarks') === 'on') {{
  appearance.bookmarks = true;
  document.getElementById('bookmarks').hidden = false;
}}
function startPage() {{
  return '<section class="start"><img class="brandmark" alt="" src="'+SIGIL+'" width="84" height="84"><h1>AZBrowser</h1>'
    + '<p>Search, open a .aziel name, or type a web address.</p>'
    + '<form id="startForm" class="start-form"><input id="startBox" aria-label="Search" placeholder="Search or enter a .aziel name or web address" spellcheck="false"><button id="startGo" type="submit">Go</button></form>'
    + '<nav class="quick" aria-label="Shortcuts">'
    + '<button type="button" id="quickSites">Your sites</button>'
    + '<button type="button" data-go="az.azieleliab.az">Aziel</button>'
    + '<button type="button" data-go="az.azielcorpuslibrary.az">Corpus</button>'
    + '<button type="button" data-go="az.godlock.az">Godlock</button>'
    + '<button type="button" data-go="az.hedidntjump.az">HeDidntJump</button>'
    + '</nav></section>';
}}
function bindStart() {{
  const form = document.getElementById('startForm');
  if (!form) return;
  form.onsubmit = (e) => {{
    e.preventDefault();
    document.getElementById('omnibox').value = document.getElementById('startBox').value.trim();
    document.getElementById('go').click();
  }};
  document.querySelectorAll('#stage [data-go]').forEach(btn => {{
    btn.onclick = () => {{
      document.getElementById('omnibox').value = btn.getAttribute('data-go');
      document.getElementById('go').click();
    }};
  }});
  const sites = document.getElementById('quickSites');
  if (sites) sites.onclick = () => document.getElementById('slotsBtn').click();
}}
document.getElementById('stage').innerHTML = startPage();
bindStart();
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
  const nodes = live + locked + isolated;
  document.getElementById("meshLiveCount").textContent = String(live);
  document.getElementById("meshNodeCount").textContent = String(nodes);
  document.getElementById("qnmLive").textContent = String(live);
  document.getElementById("qnmLocked").textContent = String(locked);
  document.getElementById("qnmIsolated").textContent = String(isolated);
  document.getElementById("meshLine").textContent = islandOn ? "Island" : (on ? "Mesh connected" : "Mesh off");
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
        if path == "/sigil.png":
            self._send(200, sigil_png(), "image/png")
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
    try:
        httpd = ThreadingHTTPServer((host, port), Handler)
    except OSError:
        print(f"Port {port} is already in use.", file=sys.stderr)
        print(f"Next: open http://{host}:{port}/ if AZBrowser is already running.", file=sys.stderr)
        return 1
    print(bind_message(host, port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        return 0
    return 0
