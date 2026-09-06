import { AZNET, IDENTITY, LIMITATION, SIGIL, VERSION } from "./engine.js";

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

export function homeHtml({ views = 0, downloads = 0, github = {} } = {}) {
  const stars = github.stars || 0;
  const forks = github.forks || 0;
  const watchers = github.watchers || 0;
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AZBrowser — research shell — ${IDENTITY}</title>
<link rel="icon" href="${SIGIL}">
<style>
:root{color-scheme:dark;--bg:#0b0b0b;--gold:#c9a227;--trim:#8a7219;--text:#ffffff;--muted:#d8d0c0;--panel:#101010;--bar:#121212}
*{box-sizing:border-box}
html,body{margin:0;height:100%;background:var(--bg);color:var(--text);font:13px/1.4 system-ui,-apple-system,Segoe UI,sans-serif}
#win{display:flex;flex-direction:column;height:100%;border:2px solid var(--gold);background:var(--bg)}
#tabs{display:flex;align-items:flex-end;gap:4px;padding:8px 8px 0;background:#0e0e0e;border-bottom:1px solid var(--gold);min-height:42px}
.tab{display:flex;align-items:center;gap:8px;max-width:220px;padding:7px 10px;border:1px solid var(--trim);border-bottom:none;border-radius:8px 8px 0 0;background:#1a1a1a;color:var(--text);cursor:pointer}
.tab.active{background:var(--bg);color:var(--gold);border-color:var(--gold)}
.tab .x{opacity:.6;border:0;background:transparent;color:inherit;cursor:pointer}
#newtab{color:var(--gold);background:transparent;border:1px solid var(--trim);border-radius:8px;width:28px;height:28px;cursor:pointer;margin:0 6px 6px}
#toolbar{display:flex;align-items:center;gap:6px;padding:8px;background:var(--bar);border-bottom:1px solid var(--gold)}
#toolbar button{background:#161616;color:var(--text);border:1px solid var(--gold);border-radius:8px;min-width:36px;height:34px;cursor:pointer}
#toolbar button:hover{background:#241c0d;color:var(--gold)}
#homeBtn img{width:20px;height:20px;vertical-align:middle}
#omnibox{flex:1;background:#0b0b0b;color:var(--text);border:1px solid var(--gold);border-radius:18px;padding:8px 16px;font:14px/1.3 inherit}
#omnibox:focus{outline:2px solid var(--gold)}
.lens{color:var(--gold);font-size:11px;letter-spacing:.08em;text-transform:uppercase}
#body{flex:1;display:grid;grid-template-columns:1fr 340px;min-height:0}
@media(max-width:860px){#body{grid-template-columns:1fr}}
#stage{overflow:auto;padding:18px}
#side{border-left:1px solid var(--gold);overflow:auto;padding:12px;background:var(--panel)}
h2{color:var(--gold);font-size:12px;letter-spacing:.06em;text-transform:uppercase;margin:16px 0 8px}
.banner{border:1px solid var(--trim);background:#241c0d;color:#f0d78c;padding:10px 12px;border-radius:8px;margin-bottom:14px}
.card{border:1px solid #3a3014;background:#141414;padding:12px;border-radius:10px;margin:0 0 10px}
.card a{color:var(--gold)}
.cite{font-size:11px;color:var(--muted)}
.stage-row{display:flex;justify-content:space-between;gap:8px;font-family:ui-monospace,monospace;font-size:11px;border-bottom:1px solid #2a2a2a;padding:6px 0}
.receipt{font-family:ui-monospace,monospace;font-size:11px;border-bottom:1px solid #2a2a2a;padding:6px 0;word-break:break-all}
#status{border-top:1px solid var(--gold);padding:6px 10px;font-size:12px;color:var(--muted);display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
iframe.preview{width:100%;min-height:420px;border:1px solid var(--trim);background:#fff;border-radius:8px}
.sigil-home{text-align:center;padding:24px 8px}
.sigil-home img{width:112px;height:112px}
.count a{color:var(--gold);margin-left:8px}
#meshStrip{border-top:1px solid var(--gold);padding:8px 10px;background:#0e0e0e;display:flex;flex-wrap:wrap;align-items:center;gap:10px 16px;font-size:12px;color:var(--muted)}
#meshStrip .live{color:var(--text)}
#meshStrip .live b{color:var(--gold);font-size:18px;margin-right:6px}
#meshStrip .rollup span{margin-right:10px}
#meshStrip .rollup b{color:var(--gold)}
#meshStrip button{background:#161616;color:var(--text);border:1px solid var(--trim);border-radius:6px;height:28px;padding:0 10px;cursor:pointer}
#meshStrip button:hover{background:#241c0d;color:var(--gold);border-color:var(--gold)}
#meshProducts{flex-basis:100%;margin:0}
</style>
</head>
<body>
<div id="win">
  <div id="tabs"></div>
  <div id="toolbar">
    <button id="btnBack" type="button" title="Back">◀</button>
    <button id="btnFwd" type="button" title="Forward">▶</button>
    <button id="btnReload" type="button" title="Reload">↻</button>
    <button id="btnHome" type="button" title="Home — everblooming sigil"><span id="homeBtn"><img alt="Home" src="${SIGIL}"></span></button>
    <input id="omnibox" placeholder="Search Lamb Lens ethically or enter a URL" spellcheck="false" autocomplete="off">
    <button id="btnGo" type="button" title="Go / ethical search">Go</button>
    <span class="lens">Lamb Lens</span>
    <button id="btnAirlock" type="button" title="Airlock current URL">Airlock</button>
  </div>
  <div id="body">
    <section id="stage"></section>
    <aside id="side">
      <div class="count">Views <strong id="views">${views}</strong> · Downloads <strong id="downloads">${downloads}</strong>
        <a href="/download?asset=azbrowser-0.1.0.tar.gz">tarball</a>
        <a href="/count">/count</a>
      </div>
      <h2>Airlock pipeline</h2>
      <div id="airlockPanel"><p class="cite">download → scan → scrub → verify → vault</p></div>
      <h2>Integrity receipts</h2>
      <div id="receipts"></div>
      <h2>FragGate</h2>
      <div class="card cite">
        AI path is FragGate only: <code>POST /v1/fraggate/call</code> slug=<b>azbrowser</b><br>
        Door paths (<code>/v1/fraggate/*</code>, <code>/v1/runtime/*</code>, <code>/v1/mesh/*</code>) proxy to aziel-runtime. Local ops are <code>/v1/{op}</code> only.<br>
        Suite mesh default OFF. QNM-BUILD-1.0 live|locked|isolated. No Node Gate. No auto-heal. Not anonymity.<br>
        <a href="/openapi.json">OpenAPI</a> · <a href="/mcp">/mcp pointer</a> · <a href="/ai">AI</a> · <a href="/v1/skill">skill</a><br>
        Siblings: <a href="https://github.com/AzielEliab/azmail">AZMail</a> · <a href="${AZNET}">AZNet (separate product)</a><br>
        AZNet is a separate product/engine; pairing order/token only — not shared Phase-1 UI.
      </div>
    </aside>
  </div>
  <div id="meshStrip" aria-label="Suite Live Nodes">
    <div class="live"><b id="meshLiveCount">0</b> Live Nodes</div>
    <div id="meshLine">Suite mesh: off (default). QNM-BUILD-1.0. Not an anonymity network.</div>
    <div class="rollup">live <b id="qnmLive">0</b> · locked <b id="qnmLocked">0</b> · isolated <b id="qnmIsolated">0</b></div>
    <div>No Node Gate · No auto-heal · Aziel Eliab only</div>
    <div>
      <button id="meshEnable" type="button" title="Enable suite mesh (global kill switch; default off)">Enable</button>
      <button id="meshDisable" type="button" title="Disable suite mesh (always allowed)">Disable</button>
      <button id="meshJoin" type="button" title="Join as azbrowser. Refused while mesh is OFF. No auto-join.">Join</button>
      <button id="meshLeave" type="button" title="Leave this node. No auto-heal.">Leave</button>
    </div>
    <div id="meshProducts" class="cite">Catalog MCP mesh_* · FragGate slug=mesh · /v1/mesh/* PROXY · not AnonBroadcast · not AZMail ring</div>
  </div>
  <div id="status">
    <span>AZBrowser ${VERSION} · Phase 1 research shell · not Chromium · No receipt = no action</span>
    <span>GitHub ★ ${stars} · forks ${forks} · watchers ${watchers}</span>
  </div>
</div>
<script>
const SIGIL = ${JSON.stringify(SIGIL)};
const LIMITATION = ${JSON.stringify(LIMITATION)};
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
  return '<div class="sigil-home"><img alt="everblooming sigil" src="'+SIGIL+'"><h1 style="color:#c9a227;font-weight:500">AZBrowser</h1><p>Lamb Lens ethical search · Phase 1 research shell</p></div>'
    + '<div class="banner">'+LIMITATION+'</div>'
    + '<div class="card"><p>New-tab search is Lamb Lens: cite sources, refuse doxxing / credential harvest / malware lure. Advisory. AZNet is a separate product/engine; pairing order/token only — not shared Phase-1 UI.</p>'
    + '<p>Type a query or HTTPS URL in the address bar. Home button is the everblooming sigil.</p></div>';
}
function renderResult(j) {
  const stage = document.getElementById("stage");
  if (j.action === "home" || (j.tab && j.tab.kind === "newtab" && !j.results && !j.html)) {
    stage.innerHTML = homePanel();
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
    stage.innerHTML = '<div class="banner">Sandbox preview (iframe, no scripts). Not Chromium. '+(j.title||"")+'</div>'
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
  plus.onclick = async () => { renderResult(await callOp("tab_new", {})); document.getElementById("stage").innerHTML = homePanel(); paintTabs(); };
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
  document.getElementById("meshLiveCount").textContent = String(live);
  document.getElementById("qnmLive").textContent = String(live);
  document.getElementById("qnmLocked").textContent = String(locked);
  document.getElementById("qnmIsolated").textContent = String(isolated);
  const line = document.getElementById("meshLine");
  if (on) line.textContent = "Suite mesh: on · live " + live + " · locked " + locked + " · isolated " + isolated + ". Not an anonymity network.";
  else if (j.status === "unavailable" || (j.ok === false && j.error)) line.textContent = "Suite mesh: off (unavailable). QNM-BUILD-1.0. Not an anonymity network.";
  else line.textContent = "Suite mesh: off (default). QNM-BUILD-1.0. Not an anonymity network.";
  const products = j.products_present || j.products || [];
  const names = Array.isArray(products) ? products.map(p => (typeof p === "string" ? p : (p && (p.product || p.slug)) || "")).filter(Boolean) : [];
  const nodes = Array.isArray(j.nodes) ? j.nodes : [];
  const extra = names.length ? " · products " + names.join(", ") : (nodes.length ? " · " + nodes.length + " node labels" : "");
  document.getElementById("meshProducts").textContent = "Catalog MCP mesh_* · FragGate slug=mesh · /v1/mesh/* PROXY · not AnonBroadcast · not AZMail ring" + extra;
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
paintTabs();
fetch("/v1/fraggate/list", { headers: { "user-agent": "Mozilla/5.0" } }).then(r => r.json()).then(j => {
  const ops = (j.allowlist && j.allowlist.azbrowser) || (j.result && j.result.allowlist && j.result.allowlist.azbrowser) || j.ops || [];
  const el = document.createElement("div");
  el.className = "cite";
  el.textContent = "FragGate door proxied. azbrowser ops: " + ops.length;
  document.getElementById("side").appendChild(el);
}).catch(() => {});
</script>
</body>
</html>`;
}
