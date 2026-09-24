import { IDENTITY, SIGIL, VERSION } from "./engine.js";

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

export function homeHtml({ views = 0, downloads = 0 } = {}) {
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AZBrowser — research shell — ${IDENTITY}</title>
<link rel="icon" href="${SIGIL}">
<style>
:root,html[data-theme="night"]{color-scheme:dark;--bg:#0b0b0b;--text:#f5f5f5;--muted:#c8c8c8;--panel:#111111;--bar:#141414;--line:#2c2c2c;--gold:#f5f5f5;--trim:#3a3a3a;--ink:#0b0b0b;--focus:#ffffff;--banner:#161616}
html[data-theme="day"]{color-scheme:light;--bg:#ffffff;--text:#141414;--muted:#333333;--panel:#f7f7f7;--bar:#f3f3f3;--line:#d4d4d4;--gold:#141414;--trim:#c8c8c8;--ink:#ffffff;--focus:#141414;--banner:#f3f3f3}
html[data-theme="aziel"]{color-scheme:dark;--bg:#0b0b0b;--text:#f6f1e4;--muted:#e4d2a0;--panel:#231246;--bar:#2a1454;--line:#6d4ea3;--gold:#f0d060;--trim:#8d6bc4;--ink:#1a1204;--focus:#f0d060;--banner:#2a1454}
*{box-sizing:border-box}
html,body{margin:0;height:100%;background:var(--bg);color:var(--text);font:15px/1.45 "Segoe UI",system-ui,sans-serif}
#win{display:flex;flex-direction:column;height:100%;background:var(--bg)}
#tabs{display:flex;align-items:flex-end;gap:6px;padding:8px 10px 0;background:var(--bar);border-bottom:1px solid var(--line);min-height:44px}
.tab{display:flex;align-items:center;gap:8px;max-width:220px;padding:8px 12px;border:1px solid transparent;border-bottom:none;border-radius:10px 10px 0 0;background:transparent;color:var(--muted);cursor:pointer}
.tab.active{background:var(--gold);color:var(--ink);border-color:var(--gold)}
.tab .x{opacity:.6;border:0;background:transparent;color:inherit;cursor:pointer}
#newtab{color:var(--gold);background:transparent;border:1px solid var(--trim);border-radius:8px;width:28px;height:28px;cursor:pointer;margin:0 6px 6px}
#toolbar{display:flex;flex-wrap:wrap;align-items:center;gap:8px;padding:10px 12px;background:var(--bar)}
#toolbar button{background:transparent;color:var(--text);border:0;border-radius:8px;min-width:34px;height:34px;padding:0 8px;cursor:pointer}
#toolbar button:hover{background:var(--banner)}
#toolbar button:focus-visible,#omnibox:focus-visible,#startBox:focus-visible,.quick button:focus-visible,.node button:focus-visible{outline:2px solid var(--focus);outline-offset:2px}
#toolbar #btnGo,#toolbar #btnGo:hover{background:var(--gold);color:var(--ink);border-radius:999px;padding:0 16px;min-width:52px}
#themeMenu button[aria-pressed="true"]{background:var(--gold);color:var(--ink)}
.node button{background:transparent;color:var(--text);border:1px solid var(--line);border-radius:8px;height:32px;padding:0 10px;cursor:pointer}
.start{min-height:62vh;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px;text-align:center;padding:48px 20px 32px}
.start h1{font-size:1.35rem;font-weight:500;margin:0}
.start img{width:84px;height:84px;display:block}
#startBox{width:min(560px,92vw);background:var(--bg);color:var(--text);border:1px solid var(--line);border-radius:999px;padding:12px 18px;font:16px/1.3 inherit}
.quick{display:flex;flex-wrap:wrap;gap:6px 8px;justify-content:center;max-width:640px}
.quick button{background:transparent;color:var(--muted);border:0;border-radius:8px;padding:6px 10px;cursor:pointer;font:14px/1.3 inherit}
.quick button:hover{color:var(--text);background:var(--banner)}
.theme{position:relative}
#themeMenu{position:absolute;right:0;top:40px;z-index:4;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:6px;display:flex;flex-direction:column;min-width:132px}
#themeMenu[hidden]{display:none}
#themeMenu button{text-align:left;width:100%}
#sidePanel[hidden]{display:none !important}
#body{grid-template-columns:1fr}
html[data-panel="open"] #body{grid-template-columns:1fr 300px}
.statusline{border-top:1px solid var(--line);padding:8px 14px;font-size:12px;color:var(--muted);display:flex;gap:16px;align-items:center}
.settings-page{max-width:40rem}
.settings-page h1{font-size:1.7rem;font-weight:560;margin:0 0 12px}
#ownerLine:empty{display:none}
.iconbtn{font-size:16px}
#homeBtn img{width:20px;height:20px;vertical-align:middle}
#omnibox{flex:1;min-width:200px;background:var(--bg);color:var(--text);border:1px solid var(--line);border-radius:999px;padding:9px 16px;font:15px/1.3 inherit}
#handleChip{font-size:12px;color:var(--muted);white-space:nowrap}
#bookmarks{display:flex;gap:8px;align-items:center;padding:6px 12px;background:var(--bar);border-top:1px solid var(--line);font-size:13px}
#bookmarks[hidden]{display:none}
#ownerLine{padding:4px 14px 8px;min-height:1.2em;color:var(--muted);background:var(--bar);font-size:13px}
.lens{color:var(--gold);font-size:11px;letter-spacing:.08em;text-transform:uppercase}
#body{flex:1;display:grid;grid-template-columns:1fr;min-height:0}
@media(max-width:860px){#body,html[data-panel="open"] #body{grid-template-columns:1fr}}
#stage{overflow:auto;padding:18px}
#side{border-left:1px solid var(--line);overflow:auto;padding:16px;background:var(--panel)}
h2{color:var(--muted);font-size:12px;letter-spacing:.06em;text-transform:uppercase;margin:16px 0 8px}
.banner,.refusal{border:1px solid var(--line);background:var(--banner);color:var(--text);padding:16px 18px;border-radius:12px;margin-bottom:16px}
.refusal{max-width:40rem}
.refusal h1,.policy-page h1,.design-page h1{font-size:1.7rem;font-weight:560;margin:0 0 8px}
.policy-page details{margin-top:16px}
.policy-page summary{cursor:pointer}
.card{border:1px solid var(--line);background:var(--banner);padding:12px;border-radius:10px;margin:0 0 10px}
.card a{color:var(--gold)}
.cite{font-size:11px;color:var(--muted)}
.stage-row{display:flex;justify-content:space-between;gap:8px;font-family:ui-monospace,monospace;font-size:11px;border-bottom:1px solid var(--line);padding:6px 0}
.receipt{font-family:ui-monospace,monospace;font-size:11px;border-bottom:1px solid var(--line);padding:6px 0;word-break:break-all}
#status{border-top:1px solid var(--line);padding:8px 12px;font-size:12px;color:var(--muted);display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
iframe.preview{width:100%;min-height:420px;border:1px solid var(--trim);background:#fff;border-radius:8px}
.sigil-home{text-align:center;padding:24px 8px}
.sigil-home img{width:112px;height:112px}
.count a{color:var(--gold);margin-left:8px}
#meshStrip{border-top:1px solid var(--line);padding:8px 14px;background:transparent;display:flex;gap:16px;align-items:center;font-size:12px;color:var(--muted)}
#meshStrip .live{color:var(--text)}
#meshStrip .live b{color:var(--gold);font-size:18px;margin-right:6px}
#meshStrip .rollup span{margin-right:10px}
#meshStrip .rollup b{color:var(--gold)}
#meshStrip button{background:transparent;color:var(--text);border:1px solid var(--trim);border-radius:6px;height:28px;padding:0 10px;cursor:pointer}
#meshStrip button:hover{background:var(--banner);color:var(--text);border-color:var(--focus)}
#meshProducts{flex-basis:100%;margin:0}
.node{display:flex;flex-wrap:wrap;gap:6px}
.node button{background:transparent;color:var(--text);border:1px solid var(--line);border-radius:8px;height:32px;padding:0 10px;cursor:pointer}
</style>
<style id="shell-chrome">
:root,html[data-theme="night"]{--focus:#f0d060}
html[data-theme="day"]{--focus:#7a5c00}
html[data-theme="aziel"]{--focus:#f0d060}
html,body{overflow-x:clip;max-width:100%}
#win,#body,#stage,#toolbar,#tabs,#meshStrip,#sidePanel{min-width:0;max-width:100%}
#tabs{overflow-x:auto}
.tab{flex:0 0 auto}
#omnibox,#handleChip{min-width:0}
#omnibox{flex:1 1 180px}
#handleChip{white-space:normal}
#meshStrip{flex-wrap:wrap;row-gap:6px}
#sidePanel{border-left:1px solid var(--line);overflow:auto;padding:16px 16px 24px;background:var(--panel)}
#sidePanel .hint{color:var(--muted);font-size:13px;margin:0 0 8px}
#sidePanel h2{margin-top:0}
#sidePanel details{border-top:1px solid var(--line);padding:2px 0 8px}
#sidePanel summary{cursor:pointer;min-height:44px;display:flex;align-items:center;font-weight:600}
#sidePanel .node{display:flex;flex-direction:column;align-items:stretch;gap:8px}
#sidePanel .node button{min-height:44px;width:100%;text-align:left;padding:0 12px}
#sidePanel details.raw{border-top:0;margin-top:8px;padding-top:0}
#sidePanel details.raw summary{font-weight:500;color:var(--muted)}
summary:focus-visible,#newtab:focus-visible,.tab button:focus-visible,#sidePanel button:focus-visible,#toolbar button:focus-visible,#omnibox:focus-visible,#startBox:focus-visible,.quick button:focus-visible{
  outline:2px solid var(--focus);outline-offset:2px
}
.stage-row{font-family:inherit;font-size:13px;align-items:baseline}
.receipt{font-family:inherit;font-size:13px}
@media(max-width:860px){
  html[data-panel="open"] #body{grid-template-rows:auto minmax(0,1fr)}
  html[data-panel="open"] #sidePanel{order:-1;max-height:52vh;border-left:0;border-bottom:1px solid var(--line)}
}
@media(max-width:480px){
  #toolbar{gap:4px;padding:8px}
  #toolbar button,#newtab,.tab .x{min-width:44px;min-height:44px}
  #toolbar #btnGo{min-height:44px}
  #omnibox,#startBox{min-height:44px}
  #omnibox{flex:1 1 calc(100% - 72px)}
  .quick button{min-height:44px;padding:10px 12px}
  .tab{min-height:44px}
}
</style>
<script>
(function() {
  var saved = null;
  try { saved = JSON.parse(localStorage.getItem("azbrowser-appearance") || "null"); } catch (e) {}
  var theme = "night";
  if (saved && (saved.theme === "day" || saved.theme === "night" || saved.theme === "aziel")) theme = saved.theme;
  document.documentElement.setAttribute("data-theme", theme);
})();
</script>
</head>
<body>
<div id="win">
  <div id="tabs"></div>
  <div id="toolbar">
    <button id="btnBack" type="button" title="Back" aria-label="Back">◀</button>
    <button id="btnFwd" type="button" title="Forward" aria-label="Forward">▶</button>
    <button id="btnReload" type="button" title="Reload" aria-label="Reload">↻</button>
    <button id="btnHome" type="button" title="Home" aria-label="Home"><span id="homeBtn"><img class="brandmark" alt="" src="${SIGIL}"></span></button>
    <input id="omnibox" placeholder="Search or enter a .aziel name or web address" spellcheck="false" autocomplete="off" aria-label="Address">
    <span id="handleChip"></span>
    <button id="btnGo" type="button" title="Go / ethical search">Go</button>
    <div class="theme">
      <button id="themeToggle" class="iconbtn" type="button" title="Theme. Night, day, or Aziel." aria-haspopup="true" aria-expanded="false">☾</button>
      <div id="themeMenu" hidden>
        <button type="button" data-theme-choice="night">Night</button>
        <button type="button" data-theme-choice="day">Day</button>
        <button id="azielMode" type="button" data-theme-choice="aziel" title="Aziel mode. Gold, black, and royal purple." aria-pressed="false">Aziel</button>
      </div>
    </div>
    <button id="settingsBtn" class="iconbtn" type="button" title="Settings" aria-label="Settings">⚙</button>
    <button id="panelToggle" class="iconbtn" type="button" title="Tools" aria-label="Tools" aria-controls="sidePanel" aria-expanded="false">☰</button>
  </div>
  <div id="bookmarks" hidden>
    <span>Bookmarks</span>
    <div id="bookmarkList"></div>
    <button id="bookmarkAdd" type="button">Bookmark this page</button>
  </div>
  <div id="ownerLine"></div>
  <div id="body">
    <section id="stage"></section>
    <aside id="sidePanel" hidden aria-label="Tools">
      <p class="cite">Views <strong id="views">${views}</strong> · Downloads <strong id="downloads">${downloads}</strong></p>
      <h2>Tools</h2>
      <p class="hint">Search and open from the address bar. These are optional.</p>
      <details open>
        <summary>This page</summary>
        <p class="hint">Check the address before it opens. A held page stays here until you show it.</p>
        <div class="node">
          <button id="btnAirlock" type="button" title="Run download, scan, clean, check, and store on the address in the bar">Check this address</button>
          <button id="btnPromote" type="button" title="Show a held page on this machine. Scripts still do not run">Show held page</button>
        </div>
      </details>
      <details>
        <summary>This machine</summary>
        <p class="hint">These choices stay on this machine.</p>
        <div class="node">
          <button id="btnIsland" type="button" title="Leave mesh peers. Local apps and the web stay open">This machine only</button>
          <button id="btnBlock" type="button" title="Block the current handle on this machine">Block this handle</button>
          <button id="btnTrust" type="button" title="Local trust for the current handle">Trust this handle</button>
          <button id="slotsBtn" type="button" title="Reserved hub mirrors and your three sites">Your sites</button>
          <button id="designBtn" type="button" title="Design mode stays on the machine that holds the handle key">Design on this machine</button>
        </div>
      </details>
      <details>
        <summary>Mesh</summary>
        <p class="hint" id="meshPlain">Mesh is off. Counts stay at zero until presence is on.</p>
        <div class="node">
          <button id="meshEnable" type="button" title="Turn suite mesh presence on">Turn presence on</button>
          <button id="meshDisable" type="button" title="Turn suite mesh presence off">Turn presence off</button>
          <button id="meshJoin" type="button" title="List this browser on the mesh">Join this browser</button>
          <button id="meshLeave" type="button" title="Remove this browser from the mesh">Leave</button>
        </div>
        <details class="raw">
          <summary>Count detail</summary>
          <p class="cite">Reachable <b id="qnmLive">0</b> · Locked <b id="qnmLocked">0</b> · Isolated <b id="qnmIsolated">0</b></p>
          <p class="cite">Raw names: live, locked, isolated.</p>
        </details>
      </details>
      <details>
        <summary>Check record</summary>
        <p class="hint" id="airlockStatus">No check yet.</p>
        <div id="airlockPanel"></div>
      </details>
      <details>
        <summary>Receipts</summary>
        <p class="hint">Each action keeps a short hash here.</p>
        <div id="receipts"></div>
      </details>
    </aside>
  </div>
  <div id="meshStrip" class="statusline" aria-label="Mesh status">
    <span id="meshLine">Mesh off</span>
    <span>Nodes <b id="meshNodeCount">0</b></span>
    <span>Live Nodes <b id="meshLiveCount">0</b></span>
  </div>
</div>
<script>
const SIGIL = ${JSON.stringify(SIGIL)};
let sessionId = "";
const clientTabs = [];
const ACTION_PLAIN = {
  tab_list: "Listed tabs",
  tab_new: "Opened a tab",
  tab_close: "Closed a tab",
  tab_switch: "Switched tab",
  home: "Home",
  navigate: "Opened an address",
  ethical_search: "Searched",
  lamb_lens_search: "Searched",
  airlock: "Checked an address",
  airlock_status: "Checked status",
  back: "Back",
  forward: "Forward",
  reload: "Reloaded",
  island_mode: "This machine only",
  peer_block: "Blocked a handle",
  peer_unblock: "Unblocked a handle",
  trust: "Local trust",
  slots: "Your sites",
  design_mode: "Design",
  resolve: "Resolved a name",
  gate_refuse: "Blocked",
  name_pending: "Pending name",
  airlock_hold: "Held a page"
};
function actionPlain(action) {
  const key = String(action || "");
  return ACTION_PLAIN[key] || key || "Action";
}
function addReceipt(rec) {
  if (!rec) return;
  const box = document.getElementById("receipts");
  const el = document.createElement("div");
  el.className = "receipt";
  const name = document.createElement("span");
  name.textContent = actionPlain(rec.action);
  const code = document.createElement("span");
  code.className = "cite";
  const hash = String(rec.hash || "");
  code.textContent = hash ? " " + hash.slice(0, 12) : "";
  code.title = (rec.action ? rec.action + " " : "") + hash;
  el.appendChild(name);
  el.appendChild(code);
  box.prepend(el);
}
const STAGE_PLAIN = { download: "Downloaded", scan: "Scanned", scrub: "Cleaned", verify: "Checked", vault: "Stored" };
function paintAirlock(stages) {
  if (!stages) return;
  const box = document.getElementById("airlockPanel");
  const status = document.getElementById("airlockStatus");
  box.innerHTML = stages.map((s) => {
    const raw = String(s.stage || "");
    const label = STAGE_PLAIN[raw] || raw || "Step";
    const hash = String(s.hash || "");
    const short = hash.slice(0, 12);
    const state = s.ok === false ? "Needs attention" : "Recorded";
    return '<div class="stage-row"><span>' + escText(label) + '</span><span class="cite" title="' + escText(raw + " " + hash) + '">' + escText(state + (short ? " · " + short : "")) + "</span></div>";
  }).join("");
  if (status) {
    const failed = stages.some((s) => s.ok === false);
    status.textContent = failed ? "The check stopped on a step. Short codes are beside each step." : "Check finished. " + stages.length + (stages.length === 1 ? " step recorded." : " steps recorded.");
  }
}
async function callOp(op, payload) {
  const body = Object.assign({ session_id: sessionId }, payload||{});
  const r = await fetch("/v1/"+op, { method:"POST", headers:{ "content-type":"application/json", "user-agent":"Mozilla/5.0" }, body: JSON.stringify(body) });
  const j = await r.json();
  if (j.session_id) sessionId = j.session_id;
  addReceipt(j.receipt);
  paintAirlock(j.stages);
  return j;
}
async function fraggate(slug, op, payload) {
  const r = await fetch("/v1/fraggate/call", { method:"POST", headers:{ "content-type":"application/json", "user-agent":"Mozilla/5.0" }, body: JSON.stringify({ slug, op, payload: payload||{} }) });
  return r.json();
}
function homePanel() {
  return '<section class="start"><img class="brandmark" alt="" src="'+SIGIL+'"><h1>AZBrowser</h1>'
    + '<form id="startForm"><input id="startBox" aria-label="Search" placeholder="Search or enter a .aziel name or web address" spellcheck="false"></form>'
    + '<nav class="quick" aria-label="Quick links">'
    + '<button type="button" data-go="azbrowser://local/design">Local apps</button>'
    + '<button type="button" id="quickSites">Your sites</button>'
    + '<button type="button" data-go="az.azieleliab.az">Aziel</button>'
    + '<button type="button" data-go="az.azielcorpuslibrary.az">Corpus</button>'
    + '<button type="button" data-go="az.godlock.az">Godlock</button>'
    + '<button type="button" data-go="az.hedidntjump.az">HeDidntJump</button>'
    + '</nav></section>';
}
function bindStart() {
  const form = document.getElementById("startForm");
  if (!form) return;
  form.onsubmit = (e) => {
    e.preventDefault();
    document.getElementById("omnibox").value = document.getElementById("startBox").value.trim();
    go();
  };
  document.querySelectorAll("#stage [data-go]").forEach((btn) => {
    btn.onclick = () => {
      document.getElementById("omnibox").value = btn.getAttribute("data-go");
      go();
    };
  });
  const sites = document.getElementById("quickSites");
  if (sites) sites.onclick = () => document.getElementById("slotsBtn").click();
}
let lastHandle = "";
let islandOn = false;
function paintOwner(j) {
  const line = document.getElementById("ownerLine");
  if (!line) return;
  const chip = document.getElementById("handleChip");
  if (chip) chip.textContent = "";
  if (j && j.owner_handle) lastHandle = j.owner_handle;
  if (j && j.name_status === "PENDING") {
    line.textContent = "Pending. " + (j.name || j.display_url || "") + " is not a verified site.";
    if (chip) chip.textContent = "Pending";
    return;
  }
  if (j && j.display && j.display.title === "Island mode") {
    islandOn = j.island_mode === true;
    line.textContent = (j.display && j.display.summary) || (islandOn ? "This machine only." : "This machine is no longer set aside.");
    return;
  }
  if (j && j.display && j.display.title === "Local trust") {
    line.textContent = (j.display && j.display.summary) || ("Local trust for " + (j.handle || "") + ".");
    return;
  }
  if (j && j.code === "FG-GATE-REFUSE") {
    line.textContent = (j.clarity && j.clarity.plain) || ("Blocked. " + (j.reason || ""));
    if (chip && j.reason === "handle_isolated") chip.textContent = "Isolated";
    return;
  }
  if (j && j.verified_owner && j.owner_handle && j.quarantine) {
    line.textContent = "Verified handle " + j.owner_handle + ". The page is held. This shell has no scanner.";
    if (chip) chip.textContent = j.owner_handle;
    if (j.display_url) document.getElementById("omnibox").value = j.display_url;
    return;
  }
  if (j && j.verified_owner && j.owner_handle) {
    line.textContent = "Verified handle " + j.owner_handle + ".";
    if (chip) chip.textContent = j.owner_handle;
    if (j.display_url) document.getElementById("omnibox").value = j.display_url;
    return;
  }
  if (j && j.plane === "local" && j.origin) {
    line.textContent = "Local app. " + j.origin + ". Data stays on this machine.";
    return;
  }
  line.textContent = "";
}
function escText(value) {
  return String(value == null ? "" : value).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
function refusalHtml(j) {
  const c = (j && j.clarity) || {};
  const reasons = j && j.ethics && j.ethics.reasons ? j.ethics.reasons.join(", ") : "";
  const plain = c.plain || (j && j.reason) || reasons || "";
  const next = c.next || "";
  const code = (j && j.code) || (j && j.ethics && j.ethics.refuse ? "ETHICS_REFUSE" : "FG-GATE-REFUSE");
  return '<section class="refusal"><h1>Blocked</h1><p>' + escText(plain) + '</p><p>' + escText(next) + '</p><p class="cite">' + escText(code) + " · " + escText((j && j.reason) || reasons) + "</p></section>";
}
function renderResult(j) {
  const stage = document.getElementById("stage");
  paintOwner(j);
  if (j && (j.policy_page || j.shell_page) && j.html) {
    stage.innerHTML = j.html;
    return;
  }
  if (j && (j.code === "FG-GATE-REFUSE" || j.code === "ETHICS_REFUSE")) {
    stage.innerHTML = refusalHtml(j);
    return;
  }
  if (j && j.name_status === "PENDING") {
    stage.innerHTML = '<div class="banner">Pending. ' + escText(j.name || "") + ' is not a verified site.</div>';
    return;
  }
  if (j && j.quarantine && !j.promoted) {
    const extra = j.display && j.display.summary ? j.display.summary : "";
    stage.innerHTML = '<div class="banner"><p>This page is held. This shell has no malware scanner, so it stays here until you choose Show held page. Scripts do not run.</p></div>'
      + (extra ? '<p class="cite">' + escText(extra) + "</p>" : "");
    return;
  }
  if (j.action === "home" || (j.tab && j.tab.kind === "newtab" && !j.results && !j.html)) {
    stage.innerHTML = homePanel();
    bindStart();
    return;
  }
  if (j.code === "ETHICS_REFUSE" || (j.ethics && j.ethics.refuse && j.ok === false)) {
    stage.innerHTML = refusalHtml(j);
    return;
  }
  if (j.results) {
    stage.innerHTML = '<div class="banner">'+(j.label||"Lamb Lens")+' — advisory. Cite sources.</div>'
      + j.results.map(h => '<div class="card"><a href="#" data-url="'+h.url+'">'+h.title+'</a><div class="cite">'+h.source+' · '+h.url+'</div><p>'+h.blurb+'</p></div>').join("");
    stage.querySelectorAll("a[data-url]").forEach(a => a.onclick = (e) => { e.preventDefault(); document.getElementById("omnibox").value = a.dataset.url; go(); });
    return;
  }
  if (j.html) {
    const who = j.verified_owner && j.owner_handle ? ("Verified handle " + j.owner_handle + ". ") : "";
    stage.innerHTML = '<div class="banner">' + escText(who + "Preview. Scripts do not run." + (j.title ? " " + j.title : "")) + '</div>'
      + '<iframe class="preview" sandbox="" srcdoc="'+String(j.html).replace(/"/g,"&quot;")+'"></iframe>'
      + '<p class="cite">'+escText(j.excerpt||"")+'</p>';
    return;
  }
  if (j.url && j.ok) {
    stage.innerHTML = '<div class="banner">The address is noted. The page has not been fetched yet. Host: '+escText(j.host||"")+'</div>'
      + '<div class="card"><p>'+escText(j.note||"")+'</p><p class="cite">'+escText(j.url)+'</p><button type="button" id="fetchNow">Fetch preview</button></div>';
    const b = document.getElementById("fetchNow");
    if (b) b.onclick = async () => renderResult(await callOp("navigate", { url: j.url, fetch: true }));
    return;
  }
  const title = j && j.display && j.display.title ? "<h1>" + escText(j.display.title) + "</h1>" : "";
  const summary = (j && j.display && j.display.summary) || (j && (j.note || j.error)) || "Done";
  stage.innerHTML = '<section class="refusal">' + title + "<p>" + escText(summary) + '</p><details><summary>Record</summary><pre>' + escText(JSON.stringify(j, null, 2)) + "</pre></details></section>";
}
async function paintTabs() {
  const t = await callOp("tab_list", {});
  const box = document.getElementById("tabs");
  box.innerHTML = "";
  (t.tabs||[]).forEach(tab => {
    const b = document.createElement("div");
    b.className = "tab" + (tab.id === t.active ? " active" : "");
    const label = document.createElement("span");
    label.textContent = tab.title || "Tab";
    label.onclick = async () => { renderResult(await callOp("tab_switch", { tab_id: tab.id })); paintTabs(); };
    const x = document.createElement("button");
    x.className = "x";
    x.type = "button";
    x.textContent = "×";
    x.onclick = async (e) => { e.stopPropagation(); renderResult(await callOp("tab_close", { tab_id: tab.id })); paintTabs(); };
    b.appendChild(label);
    b.appendChild(x);
    box.appendChild(b);
  });
  const plus = document.createElement("button");
  plus.id = "newtab";
  plus.type = "button";
  plus.title = "New tab";
  plus.textContent = "+";
  plus.onclick = async () => { renderResult(await callOp("tab_new", {})); document.getElementById("stage").innerHTML = homePanel(); bindStart(); paintTabs(); };
  box.appendChild(plus);
}
async function go() {
  const q = document.getElementById("omnibox").value.trim();
  if (!q) { renderResult(await callOp("home", {})); return; }
  const looksUrl = (/^[a-z]+:/i.test(q) || (/[.]/.test(q) && !/\\s/.test(q)));
  renderResult(await callOp(looksUrl ? "navigate" : "ethical_search", looksUrl ? { url: q } : { q }));
  paintTabs();
}
document.getElementById("btnBack").onclick = async () => { renderResult(await callOp("back", {})); };
document.getElementById("btnFwd").onclick = async () => { renderResult(await callOp("forward", {})); };
document.getElementById("btnReload").onclick = async () => { renderResult(await callOp("reload", {})); };
document.getElementById("btnHome").onclick = async () => { document.getElementById("omnibox").value = ""; renderResult(await callOp("home", {})); paintTabs(); };
document.getElementById("btnGo").onclick = go;
document.getElementById("omnibox").addEventListener("keydown", (e) => { if (e.key === "Enter") go(); });
document.getElementById("btnPromote").onclick = async () => {
  const q = document.getElementById("omnibox").value.trim();
  renderResult(await callOp("navigate", { url: q, operator_override: true }));
};
document.getElementById("btnIsland").onclick = async () => {
  islandOn = !islandOn;
  renderResult(await callOp("island_mode", { enabled: islandOn }));
  refreshMesh();
};
document.getElementById("btnBlock").onclick = async () => {
  const handle = lastHandle || (document.getElementById("omnibox").value.trim().split(".")[0] || "");
  renderResult(await callOp("peer_block", { handle }));
};
document.getElementById("btnTrust").onclick = async () => {
  const handle = lastHandle || (document.getElementById("omnibox").value.trim().split(".")[0] || "");
  renderResult(await callOp("trust", { handle }));
};
document.getElementById("designBtn").onclick = async () => {
  renderResult(await callOp("design_mode", { handle: lastHandle || "" }));
};
document.getElementById("slotsBtn").onclick = async () => {
  const handle = lastHandle || (document.getElementById("omnibox").value.trim().split(".")[0] || "");
  const obj = await callOp("slots", { handle });
  const reserved = (obj.reserved || []).map((row) => "<li>" + escText(row.label) + " · " + escText(row.host) + " · reserved</li>").join("");
  const user = (obj.user || []).map((row) => "<li>" + escText(row.id) + " · " + escText(row.name || "empty") + " · " + escText(row.status) + "</li>").join("");
  document.getElementById("stage").innerHTML = '<section class="refusal"><h1>Your sites</h1><p>Automatic name: ' + escText(obj.automatic_name || "unset") + '</p><h2>Reserved mirrors</h2><ul>' + reserved + '</ul><h2>Your names</h2><ul>' + user + '</ul><p>' + escText(obj.note || "") + "</p></section>";
};
const APPEAR_KEY = "azbrowser-appearance";
function readAppearance() {
  var saved = null;
  try { saved = JSON.parse(localStorage.getItem(APPEAR_KEY) || "null"); } catch (e) {}
  if (saved && saved.theme) return saved;
  return { theme: "night", mode: "night", aziel: false, bookmarks: false };
}
function paintAppearance(state) {
  const theme = state.aziel ? "aziel" : (state.mode || "night");
  document.documentElement.setAttribute("data-theme", theme);
  document.getElementById("bookmarks").hidden = !state.bookmarks;
  const mark = theme === "day" ? "☀" : (theme === "aziel" ? "✦" : "☾");
  const toggle = document.getElementById("themeToggle");
  toggle.textContent = mark;
  toggle.title = theme === "aziel" ? "Theme. Aziel mode." : (theme === "day" ? "Theme. Day." : "Theme. Night.");
  document.querySelectorAll("[data-theme-choice]").forEach((btn) => {
    const choice = btn.getAttribute("data-theme-choice");
    const on = choice === "aziel" ? !!state.aziel : (!state.aziel && state.mode === choice);
    btn.setAttribute("aria-pressed", on ? "true" : "false");
  });
  localStorage.setItem(APPEAR_KEY, JSON.stringify({ theme, mode: state.mode, aziel: state.aziel, bookmarks: !!state.bookmarks }));
}
function chooseTheme(choice) {
  if (choice === "aziel") {
    appearance.aziel = true;
    if (!appearance.mode) appearance.mode = "night";
  } else {
    appearance.aziel = false;
    appearance.mode = choice === "day" ? "day" : "night";
  }
  paintAppearance(appearance);
  const menu = document.getElementById("themeMenu");
  if (menu) menu.hidden = true;
  document.getElementById("themeToggle").setAttribute("aria-expanded", "false");
}
let appearance = readAppearance();
if (appearance.theme === "aziel") appearance.aziel = true;
if (!appearance.mode) appearance.mode = appearance.theme === "day" ? "day" : "night";
document.getElementById("themeToggle").onclick = (e) => {
  e.stopPropagation();
  const menu = document.getElementById("themeMenu");
  menu.hidden = !menu.hidden;
  document.getElementById("themeToggle").setAttribute("aria-expanded", menu.hidden ? "false" : "true");
};
document.querySelectorAll("#themeMenu [data-theme-choice]").forEach((btn) => {
  btn.onclick = (e) => { e.stopPropagation(); chooseTheme(btn.getAttribute("data-theme-choice")); };
});
document.addEventListener("click", () => {
  const menu = document.getElementById("themeMenu");
  if (menu) menu.hidden = true;
});
document.getElementById("panelToggle").onclick = () => {
  const panel = document.getElementById("sidePanel");
  panel.hidden = !panel.hidden;
  document.documentElement.setAttribute("data-panel", panel.hidden ? "closed" : "open");
  document.getElementById("panelToggle").setAttribute("aria-expanded", panel.hidden ? "false" : "true");
};
document.getElementById("bookmarkAdd").onclick = () => {
  const url = document.getElementById("omnibox").value.trim();
  if (!url) return;
  const rows = JSON.parse(localStorage.getItem("azbrowser-bookmarks") || "[]");
  rows.push({ title: url, url });
  localStorage.setItem("azbrowser-bookmarks", JSON.stringify(rows.slice(-12)));
};
document.getElementById("settingsBtn").onclick = () => {
  const on = appearance.bookmarks ? " checked" : "";
  document.getElementById("stage").innerHTML = '<section class="settings-page"><h1>Settings</h1>'
    + '<h2>Appearance</h2><p>Night is the first look: black background, white text. Day is white with black text. Aziel is gold, black, and royal purple. The choice is remembered on this machine.</p>'
    + '<div class="node"><button type="button" data-theme-choice="night">Night</button><button type="button" data-theme-choice="day">Day</button><button type="button" data-theme-choice="aziel">Aziel</button></div>'
    + '<label><input id="bookmarkPref" type="checkbox"' + on + '> Show bookmarks bar</label>'
    + '<h2>Tools</h2><p>The tools icon opens checks for this page, choices for this machine, and mesh presence. Design on this hosted page stays on the machine that holds the handle key.</p>'
    + '<h2>About</h2>'
    + '<p>AZBrowser is a research shell for search, tabs, and mesh names. Version ${VERSION}. Author Aziel Eliab.</p>'
    + '<p>A search, a .aziel name, or a web address goes in one step. Local apps open on the machine that hosts them. Web addresses keep working.</p>'
    + '<p>A verified handle is named beside the address. A pending name is marked Pending and is not opened. An isolated handle explains what happened and what you can do next.</p>'
    + '<p>Mesh pages stay held until you choose Show held page. This shell has no malware scanner, and it does not run page scripts. Handle keys stay on the local machine.</p>'
    + '<p>This machine only and Block this handle apply on this machine. Each action keeps a receipt.</p>'
    + '<p>There are no ads, no tracking, and no telemetry.</p>'
    + '<p>AZMail and AZNet are separate programs. This node has four reserved hub mirrors and three user sites. MirageGrid decoy names stay on their own list.</p>'
    + '</section>';
  document.getElementById("bookmarkPref").onchange = (e) => {
    appearance.bookmarks = e.target.checked;
    paintAppearance(appearance);
  };
  document.querySelectorAll(".settings-page [data-theme-choice]").forEach((btn) => {
    btn.onclick = () => chooseTheme(btn.getAttribute("data-theme-choice"));
  });
};
paintAppearance(appearance);
document.getElementById("btnAirlock").onclick = async () => {
  const q = document.getElementById("omnibox").value.trim();
  renderResult(await callOp("airlock", { url: q }));
};
window.fraggate = fraggate;
function meshNum() {
  for (let i = 0; i < arguments.length; i++) {
    const raw = arguments[i];
    if (raw == null || raw === "") continue;
    const n = typeof raw === "number" ? raw : Number(String(raw).replace(/,/g, ""));
    if (Number.isFinite(n) && n >= 0) return Math.floor(n);
  }
  return 0;
}
function unwrapMesh(j) {
  if (!j || typeof j !== "object") return {};
  if (j.result && typeof j.result === "object") return Object.assign({}, j, j.result);
  if (j.mesh && typeof j.mesh === "object") return Object.assign({}, j, j.mesh);
  return j;
}
function meshWords(on, unavailable) {
  if (unavailable) return { line: "Mesh status unavailable", plain: "Mesh status could not be read. Counts stay hidden until it can." };
  if (islandOn) return { line: "This machine only", plain: "This machine only. Local apps and the web stay open." };
  if (!on) return { line: "Mesh off", plain: "Mesh is off. Counts stay at zero until presence is on." };
  let joined = false;
  try { joined = !!sessionStorage.getItem("azbrowser_mesh_node"); } catch (e) {}
  if (joined) return { line: "This browser is listed", plain: "Mesh is on. This browser is listed." };
  return { line: "Mesh on", plain: "Mesh is on. This browser has not joined." };
}
function paintCount(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}
function paintMesh(raw) {
  const j = unwrapMesh(raw);
  const unavailable = !raw || j.ok === false || String(j.status || "") === "unavailable" || j.error === "mesh_unavailable";
  const on = !unavailable && (j.enabled === true || j.enabled === 1 || String(j.status || "").toLowerCase() === "on");
  const r = (j.rollup && typeof j.rollup === "object") ? j.rollup : {};
  const live = on ? meshNum(r.live, j.live_nodes, j.live) : 0;
  const locked = on ? meshNum(r.locked, j.locked_nodes, j.locked) : 0;
  const isolated = on ? meshNum(r.isolated, j.isolated_nodes, j.isolated) : 0;
  const words = meshWords(on, unavailable);
  const shown = unavailable ? "—" : String(live);
  const shownNodes = unavailable ? "—" : String(live + locked + isolated);
  paintCount("meshLiveCount", shown);
  paintCount("meshNodeCount", shownNodes);
  paintCount("qnmLive", unavailable ? "—" : String(live));
  paintCount("qnmLocked", unavailable ? "—" : String(locked));
  paintCount("qnmIsolated", unavailable ? "—" : String(isolated));
  const line = document.getElementById("meshLine");
  if (line) line.textContent = words.line;
  const plain = document.getElementById("meshPlain");
  if (plain) plain.textContent = words.plain;
}
async function meshGet(path) {
  const r = await fetch(path, { headers: { "user-agent": "Mozilla/5.0", accept: "application/json" } });
  return r.json();
}
async function meshPost(path, payload) {
  const r = await fetch(path, { method: "POST", headers: { "content-type": "application/json", "user-agent": "Mozilla/5.0" }, body: JSON.stringify(payload || {}) });
  return r.json();
}
async function refreshMesh() {
  try {
    const status = await meshGet("/v1/mesh");
    let merged = status;
    const on = status && (status.enabled === true || (status.result && status.result.enabled === true));
    if (on) {
      try {
        const nodes = await meshGet("/v1/mesh/nodes");
        merged = Object.assign({}, unwrapMesh(status), unwrapMesh(nodes));
      } catch (e) { /* status is enough */ }
    }
    paintMesh(merged);
    const nodeId = sessionStorage.getItem("azbrowser_mesh_node");
    if (on && nodeId) {
      try { await meshPost("/v1/mesh/heartbeat", { node_id: nodeId }); } catch (e) { /* no auto-heal */ }
    }
  } catch (e) {
    paintMesh({ ok: false, enabled: false, status: "unavailable", error: "mesh_unavailable" });
  }
}
document.getElementById("meshEnable").onclick = async () => { paintMesh(await meshPost("/v1/mesh/enable", {})); refreshMesh(); };
document.getElementById("meshDisable").onclick = async () => { sessionStorage.removeItem("azbrowser_mesh_node"); paintMesh(await meshPost("/v1/mesh/disable", {})); refreshMesh(); };
document.getElementById("meshJoin").onclick = async () => {
  const j = await meshPost("/v1/mesh/join", { product: "azbrowser", label: "AZBrowser Worker" });
  const inner = unwrapMesh(j);
  const id = inner.node_id || inner.id || (inner.session && inner.session.node_id);
  if (id) sessionStorage.setItem("azbrowser_mesh_node", String(id));
  paintMesh(j);
  refreshMesh();
};
document.getElementById("meshLeave").onclick = async () => {
  const id = sessionStorage.getItem("azbrowser_mesh_node");
  if (id) await meshPost("/v1/mesh/leave", { node_id: id });
  sessionStorage.removeItem("azbrowser_mesh_node");
  refreshMesh();
};
window.addEventListener("pagehide", () => {
  const id = sessionStorage.getItem("azbrowser_mesh_node");
  if (!id || typeof navigator.sendBeacon !== "function") return;
  try { navigator.sendBeacon("/v1/mesh/leave", new Blob([JSON.stringify({ node_id: id })], { type: "application/json" })); } catch (e) { /* leave expires in 5 minutes */ }
});
refreshMesh();
setInterval(refreshMesh, 30000);
document.addEventListener("visibilitychange", () => { if (!document.hidden) refreshMesh(); });
document.getElementById("stage").innerHTML = homePanel();
bindStart();
paintTabs();
</script>
</body>
</html>`;
}
