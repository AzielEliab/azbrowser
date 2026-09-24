import { HOST, IDENTITY, SIGIL, VERSION } from "./engine.js";

const ASSET = "azbrowser-0.1.0.tar.gz";

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
<title>AZBrowser — ${IDENTITY}</title>
<meta name="description" content="AZBrowser is a research shell for search, tabs, and mesh names. Download the package or use the hosted shell.">
<meta name="author" content="${IDENTITY}">
<link rel="icon" href="${SIGIL}">
<style>
:root,html[data-theme="night"]{color-scheme:dark;--bg:#0b0b0b;--text:#f5f5f5;--muted:#c8c8c8;--panel:#111111;--bar:#141414;--line:#2c2c2c;--gold:#f5f5f5;--trim:#3a3a3a;--ink:#0b0b0b;--focus:#ffffff;--banner:#161616}
html[data-theme="day"]{color-scheme:light;--bg:#ffffff;--text:#141414;--muted:#333333;--panel:#f7f7f7;--bar:#f3f3f3;--line:#d4d4d4;--gold:#141414;--trim:#c8c8c8;--ink:#ffffff;--focus:#141414;--banner:#f3f3f3}
html[data-theme="aziel"]{color-scheme:dark;--bg:#0b0b0b;--text:#f6f1e4;--muted:#e4d2a0;--panel:#231246;--bar:#2a1454;--line:#6d4ea3;--gold:#f0d060;--trim:#8d6bc4;--ink:#1a1204;--focus:#f0d060;--banner:#2a1454}
*{box-sizing:border-box}
html,body{margin:0;min-height:100%;background:var(--bg);color:var(--text);font:16px/1.5 system-ui,"Segoe UI",sans-serif}
#win{display:flex;flex-direction:column;height:min(720px,78vh);min-height:420px;background:var(--bg);border:1px solid var(--line);border-radius:14px;overflow:hidden}
#tabs{display:flex;align-items:flex-end;gap:6px;padding:8px 10px 0;background:var(--bar);border-bottom:1px solid var(--line);min-height:44px}
.tab{display:flex;align-items:center;gap:8px;max-width:220px;padding:8px 12px;border:1px solid transparent;border-bottom:none;border-radius:10px 10px 0 0;background:transparent;color:var(--muted);cursor:pointer}
.tab.active{background:var(--gold);color:var(--ink);border-color:var(--gold)}
.tab .x{opacity:.6;border:0;background:transparent;color:inherit;cursor:pointer}
#newtab{color:var(--gold);background:transparent;border:1px solid var(--trim);border-radius:8px;width:28px;height:28px;cursor:pointer;margin:0 6px 6px}
#toolbar{display:flex;flex-wrap:wrap;align-items:center;gap:8px;padding:10px 12px;background:var(--bar)}
#toolbar button{background:transparent;color:var(--text);border:0;border-radius:8px;min-width:34px;height:34px;padding:0 8px;cursor:pointer}
#toolbar button:hover{background:var(--banner)}
#toolbar button:focus-visible,#omnibox:focus-visible,#startBox:focus-visible,.quick button:focus-visible,.node button:focus-visible,a.btn:focus-visible,footer a:focus-visible,a.skip:focus{outline:2px solid var(--focus);outline-offset:2px}
#toolbar #btnGo,#toolbar #btnGo:hover{background:var(--gold);color:var(--ink);border-radius:999px;padding:0 16px;min-width:52px}
#themeMenu button[aria-pressed="true"]{background:var(--gold);color:var(--ink)}
.node button{background:transparent;color:var(--text);border:1px solid var(--line);border-radius:8px;height:32px;padding:0 10px;cursor:pointer}
.start{min-height:100%;flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px;text-align:center;padding:28px 16px}
.start .start-name{font-size:1.35rem;font-weight:500;margin:0}
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
#omnibox{flex:1;min-width:200px;background:var(--bg);color:var(--text);border:1px solid var(--line);border-radius:999px;padding:9px 16px;font:16px/1.3 inherit}
#handleChip{font-size:12px;color:var(--muted);white-space:nowrap}
#bookmarks{display:flex;gap:8px;align-items:center;padding:6px 12px;background:var(--bar);border-top:1px solid var(--line);font-size:13px}
#bookmarks[hidden]{display:none}
#ownerLine{padding:4px 14px 8px;min-height:1.2em;color:var(--muted);background:var(--bar);font-size:13px}
.lens{color:var(--gold);font-size:11px;letter-spacing:.08em;text-transform:uppercase}
#body{flex:1;display:grid;grid-template-columns:1fr;min-height:0}
@media(max-width:860px){#body,html[data-panel="open"] #body{grid-template-columns:1fr}}
#stage{overflow:auto;padding:18px;display:flex;flex-direction:column}
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
#meshStrip{border-top:1px solid var(--line);padding:8px 14px;background:transparent;display:flex;flex-wrap:wrap;gap:12px 16px;align-items:center;font-size:12px;color:var(--muted)}
#meshStrip .live{color:var(--text)}
#meshStrip .live b{color:var(--gold);font-size:18px;margin-right:6px}
#meshStrip .rollup span{margin-right:10px}
#meshStrip .rollup b{color:var(--gold)}
#meshStrip button{background:transparent;color:var(--text);border:1px solid var(--trim);border-radius:6px;height:28px;padding:0 10px;cursor:pointer}
#meshStrip button:hover{background:var(--banner);color:var(--text);border-color:var(--focus)}
#meshProducts{flex-basis:100%;margin:0}
.node{display:flex;flex-wrap:wrap;gap:6px}
.node button{background:transparent;color:var(--text);border:1px solid var(--line);border-radius:8px;height:32px;padding:0 10px;cursor:pointer}
a.skip{position:absolute;left:-999px;top:0}
a.skip:focus{left:1rem;top:1rem;z-index:5;background:var(--gold);color:var(--ink);padding:.4rem .7rem;text-decoration:none}
.hero,.shell-wrap,footer.quiet{max-width:58rem;margin:0 auto}
.hero{padding:1.4rem 1.2rem .2rem}
.brandrow{display:flex;align-items:center;gap:12px;margin:0 0 12px}
.hero .brandmark{width:40px;height:40px;border-radius:10px;object-fit:cover;display:block;box-shadow:0 0 0 1px var(--line)}
.hero h1{font-size:2rem;font-weight:650;letter-spacing:.02em;margin:0 0 .2rem;line-height:1.15}
.motto{color:var(--gold);font-style:italic;margin:0 0 .7rem;font-size:1.08rem}
.lede{color:var(--muted);margin:0 0 1rem;max-width:46rem}
.kicker{display:block;margin:0 0 .45rem;font:.68rem/1.2 ui-monospace,Menlo,Consolas,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
a.btn.block.primary{display:block;width:100%;max-width:40rem;margin:0 0 .7rem;padding:1.05rem 1.2rem;border:1px solid transparent;border-radius:9px;background:var(--gold);color:var(--ink);text-align:center;text-decoration:none;font:700 1.25rem/1.1 ui-monospace,Menlo,Consolas,monospace;letter-spacing:.03em;cursor:pointer}
a.btn.block.primary:hover{filter:brightness(1.08)}
.asset-note{color:var(--muted);font-size:.9rem;margin:0 0 1rem}
.features{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.75rem 1.2rem;margin:0 0 1.2rem;padding:0;list-style:none;max-width:46rem}
.features li{margin:0}
.shell-wrap{padding:0 1.2rem}
footer.quiet{padding:1.15rem 1.2rem 2.8rem;color:var(--muted);font-size:.9rem}
footer.quiet p{margin:.35rem 0}
footer.quiet a{color:var(--text)}
code{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.92em}
@media(max-width:720px){
  .features{grid-template-columns:1fr}
  .hero{padding-top:1.15rem}
  a.btn.block.primary{max-width:none}
  #win{min-height:380px;border-radius:12px}
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
<a class="skip" href="#win">Skip to the shell</a>
<header class="hero">
  <div class="brandrow">
    <img class="brandmark" alt="" src="${SIGIL}" width="40" height="40">
  </div>
  <h1>AZBrowser</h1>
  <p class="motto">Search, tabs, and mesh names in one shell.</p>
  <p class="lede">v${esc(VERSION)} software by ${esc(IDENTITY)}. A search, a .aziel name, or a web address goes in one step.</p>
  <a class="btn block primary" id="downloadBtn" href="/download?asset=${esc(ASSET)}" aria-describedby="downloadNote">Download</a>
  <p class="asset-note" id="downloadNote">${esc(downloads)} downloads · ${esc(ASSET)} · counted on this Worker for every branch and fork</p>
  <ul class="features">
    <li>Search, a .aziel name, or a web address in one step</li>
    <li>A receipt kept for each action</li>
    <li>Night, Day, and Aziel, remembered on this machine</li>
  </ul>
  <p class="lede">On this computer: <code>curl -fsSL ${esc(HOST)}/install.sh | bash</code> then <code>azbrowser ui</code> at http://127.0.0.1:8878.</p>
</header>
<div class="shell-wrap">
  <p class="kicker">Hosted shell</p>
<div id="win">
  <div id="tabs"></div>
  <div id="toolbar">
    <button id="btnBack" type="button" title="Back">◀</button>
    <button id="btnFwd" type="button" title="Forward">▶</button>
    <button id="btnReload" type="button" title="Reload">↻</button>
    <button id="btnHome" type="button" title="Home"><span id="homeBtn"><img class="brandmark" alt="" src="${SIGIL}"></span></button>
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
    <button id="designBtn" class="iconbtn" type="button" title="Design mode" aria-label="Design mode">✎</button>
    <button id="panelToggle" class="iconbtn" type="button" title="Tools" aria-label="Tools" aria-expanded="false">☰</button>
  </div>
  <div id="bookmarks" hidden>
    <span>Bookmarks</span>
    <div id="bookmarkList"></div>
    <button id="bookmarkAdd" type="button">Bookmark this page</button>
  </div>
  <div id="ownerLine"></div>
  <div id="body">
    <section id="stage"></section>
    <aside id="sidePanel" hidden>
      <p class="cite">Views <strong id="views">${views}</strong> · Downloads <strong id="downloads">${downloads}</strong></p>
      <h2>Tools</h2>
      <div class="node">
        <button id="btnAirlock" type="button" title="Check the current address in the airlock">Airlock</button>
        <button id="btnPromote" type="button" title="Show a quarantined page on this machine">Promote</button>
        <button id="btnIsland" type="button" title="Leave mesh peers. Local apps and the web stay open">Island</button>
        <button id="btnBlock" type="button" title="Block the current handle on this machine">Block peer</button>
        <button id="btnTrust" type="button" title="Local trust for the current handle">Trust</button>
        <button id="slotsBtn" type="button" title="Reserved hub mirrors and your three sites">Slots</button>
      </div>
      <h2>Mesh</h2>
      <div class="node">
        <button id="meshEnable" type="button" title="Turn mesh presence on">Turn on</button>
        <button id="meshDisable" type="button" title="Turn mesh presence off">Turn off</button>
        <button id="meshJoin" type="button" title="Join this browser to the mesh">Join</button>
        <button id="meshLeave" type="button" title="Leave the mesh">Leave</button>
      </div>
      <p hidden>live <b id="qnmLive">0</b> locked <b id="qnmLocked">0</b> isolated <b id="qnmIsolated">0</b></p>
      <h2>Airlock</h2>
      <div id="airlockPanel"></div>
      <h2>Receipts</h2>
      <div id="receipts"></div>
    </aside>
  </div>
  <div id="meshStrip" class="statusline" aria-label="Mesh status">
    <span id="meshLine">Mesh off</span>
    <span>Nodes <b id="meshNodeCount">0</b></span>
    <span>Live Nodes <b id="meshLiveCount">0</b></span>
  </div>
</div>
</div>
<footer class="quiet">
  <p>Apache-2.0 · ${esc(IDENTITY)} · AZBrowser v${esc(VERSION)}</p>
  <p><a href="https://github.com/AzielEliab/azbrowser">GitHub</a> · <a href="/openapi.json">OpenAPI</a> · <a href="/mcp">MCP</a> · <a href="/cite.json">Cite</a></p>
</footer>
<script>
const SIGIL = ${JSON.stringify(SIGIL)};
let sessionId = "";
const clientTabs = [];
function addReceipt(rec) {
  if (!rec) return;
  const box = document.getElementById("receipts");
  const el = document.createElement("div");
  el.className = "receipt";
  el.textContent = (rec.seq||"") + " " + rec.action + " " + rec.hash;
  box.prepend(el);
}
function paintAirlock(stages) {
  if (!stages) return;
  document.getElementById("airlockPanel").innerHTML = stages.map(s =>
    '<div class="stage-row"><span>'+s.stage+'</span><span>'+String(s.hash||"").slice(0,16)+'</span></div>'
  ).join("");
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
  return '<section class="start"><img class="brandmark" alt="" src="'+SIGIL+'"><p class="start-name">AZBrowser</p>'
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
    line.textContent = "Pending · " + (j.name || j.display_url || "") + " · not a verified site";
    if (chip) chip.textContent = "Pending";
    return;
  }
  if (j && j.display && j.display.title === "Island mode") {
    islandOn = j.island_mode === true;
    line.textContent = islandOn
      ? "Island mode · this node only · local runtime stays up"
      : "Island mode off · this node rejoined";
    return;
  }
  if (j && j.display && j.display.title === "Local trust") {
    line.textContent = "Local trust · " + (j.handle || "")
      + " · chain age " + j.chain_age_seconds
      + " · heartbeats " + j.heartbeats_witnessed
      + " · hash matches " + j.hash_matches
      + " · vouches " + ((j.vouches || []).join(",") || "none")
      + " · equivocation " + j.equivocating;
    return;
  }
  if (j && j.code === "FG-GATE-REFUSE") {
    line.textContent = (j.clarity && j.clarity.plain) || ("Blocked · FG-GATE-REFUSE · " + (j.reason || ""));
    if (chip && j.reason === "handle_isolated") chip.textContent = "Isolated";
    return;
  }
  if (j && j.verified_owner && j.owner_handle && j.quarantine) {
    line.textContent = "Verified owner handle · " + j.owner_handle + " · quarantined · scanner absent";
    if (chip) chip.textContent = j.owner_handle;
    if (j.display_url) document.getElementById("omnibox").value = j.display_url;
    return;
  }
  if (j && j.verified_owner && j.owner_handle) {
    line.textContent = "Verified owner handle · " + j.owner_handle;
    if (chip) chip.textContent = j.owner_handle;
    if (j.display_url) document.getElementById("omnibox").value = j.display_url;
    return;
  }
  if (j && j.plane === "local" && j.origin) {
    line.textContent = "Local app · " + j.origin + " · data stays on this machine";
    return;
  }
  line.textContent = "";
}
function escText(value) {
  return String(value == null ? "" : value).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
function refusalHtml(j) {
  const c = (j && j.clarity) || {};
  const plain = c.plain || (j && j.reason) || "";
  const next = c.next || "";
  const code = (j && j.code) || "FG-GATE-REFUSE";
  return '<section class="refusal"><h1>Blocked</h1><p>' + escText(plain) + '</p><p>' + escText(next) + '</p><p class="cite">' + escText(code) + " · " + escText((j && j.reason) || "") + "</p></section>";
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
    stage.innerHTML = '<div class="banner">Pending · ' + (j.name || "") + ' · not a verified site</div>';
    return;
  }
  if (j && j.quarantine && !j.promoted) {
    stage.innerHTML = '<div class="banner">Quarantine · scanner absent · not promoted · not run</div><p class="cite">' + (j.display && j.display.summary ? j.display.summary : "") + '</p>';
    return;
  }
  if (j.action === "home" || (j.tab && j.tab.kind === "newtab" && !j.results && !j.html)) {
    stage.innerHTML = homePanel();
    bindStart();
    return;
  }
  if (j.code === "ETHICS_REFUSE" || (j.ethics && j.ethics.refuse && j.ok === false)) {
    stage.innerHTML = '<div class="banner">Lamb Lens refused. '+(j.ethics&&j.ethics.reasons?j.ethics.reasons.join(", "):"")+'</div><p>Advisory ethical gate. Not a guaranteed block.</p>';
    return;
  }
  if (j.results) {
    stage.innerHTML = '<div class="banner">'+(j.label||"Lamb Lens")+' — advisory. Cite sources.</div>'
      + j.results.map(h => '<div class="card"><a href="#" data-url="'+h.url+'">'+h.title+'</a><div class="cite">'+h.source+' · '+h.url+'</div><p>'+h.blurb+'</p></div>').join("");
    stage.querySelectorAll("a[data-url]").forEach(a => a.onclick = (e) => { e.preventDefault(); document.getElementById("omnibox").value = a.dataset.url; go(); });
    return;
  }
  if (j.html) {
    const who = j.verified_owner && j.owner_handle ? ("Verified owner handle " + j.owner_handle + ". ") : "";
    stage.innerHTML = '<div class="banner">' + who + 'Sandbox preview (iframe, no scripts). Not Chromium. '+(j.title||"")+'</div>'
      + '<iframe class="preview" sandbox="" srcdoc="'+String(j.html).replace(/"/g,"&quot;")+'"></iframe>'
      + '<p class="cite">'+(j.excerpt||"")+'</p>';
    return;
  }
  if (j.url && j.ok) {
    stage.innerHTML = '<div class="banner">Preview receipted. Fetch not run (metadata). Host: '+(j.host||"")+'</div>'
      + '<div class="card"><p>'+(j.note||"")+'</p><p class="cite">'+j.url+'</p><button type="button" id="fetchNow">Fetch sandbox preview</button></div>';
    const b = document.getElementById("fetchNow");
    if (b) b.onclick = async () => renderResult(await callOp("navigate", { url: j.url, fetch: true }));
    return;
  }
  stage.innerHTML = '<div class="banner">'+(j.display?j.display.summary:(j.note||j.error||"ok"))+'</div><pre style="white-space:pre-wrap">'+JSON.stringify(j,null,2)+'</pre>';
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
  const reserved = (obj.reserved || []).map((row) => "<li>" + row.label + " · " + row.host + " · not user-nameable</li>").join("");
  const user = (obj.user || []).map((row) => "<li>" + row.id + " · " + (row.name || "empty") + " · " + row.status + "</li>").join("");
  document.getElementById("stage").innerHTML = '<section class="refusal"><h1>Domain slots</h1><p>Automatic name: ' + (obj.automatic_name || "unset") + '</p><h2>Reserved</h2><ul>' + reserved + '</ul><h2>User</h2><ul>' + user + '</ul><p>' + (obj.note || "") + '</p></section>';
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
    + '<h2>Tools</h2><p>The tools icon opens Airlock, Promote, Island, Block peer, Trust, and Slots. Design mode on this hosted page stays on the machine that holds the handle key.</p>'
    + '<h2>About</h2>'
    + '<p>AZBrowser is a research shell for search, tabs, and mesh names. Version ${VERSION}. Author Aziel Eliab.</p>'
    + '<p>A search, a .aziel name, or a web address goes in one step. Local apps open on the machine that hosts them. Web addresses keep working.</p>'
    + '<p>A verified handle is named beside the address. A pending name is marked Pending and is not opened. An isolated handle explains what happened and what you can do next.</p>'
    + '<p>Mesh pages stay in quarantine until you choose Promote. This shell has no malware scanner, and it does not run page scripts. Handle keys stay on the local machine.</p>'
    + '<p>Island and Block peer apply on this machine. Each action keeps a receipt.</p>'
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
function paintMesh(raw) {
  const j = unwrapMesh(raw);
  const on = j.enabled === true || j.enabled === 1 || String(j.status || "").toLowerCase() === "on";
  const r = (j.rollup && typeof j.rollup === "object") ? j.rollup : {};
  const live = on ? meshNum(r.live, j.live_nodes, j.live) : 0;
  const locked = on ? meshNum(r.locked, j.locked_nodes, j.locked) : 0;
  const isolated = on ? meshNum(r.isolated, j.isolated_nodes, j.isolated) : 0;
  const nodes = live + locked + isolated;
  document.getElementById("meshLiveCount").textContent = String(live);
  const nodeCount = document.getElementById("meshNodeCount");
  if (nodeCount) nodeCount.textContent = String(nodes);
  document.getElementById("qnmLive").textContent = String(live);
  document.getElementById("qnmLocked").textContent = String(locked);
  document.getElementById("qnmIsolated").textContent = String(isolated);
  const line = document.getElementById("meshLine");
  line.textContent = islandOn ? "Island" : (on ? "Mesh connected" : "Mesh off");
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
