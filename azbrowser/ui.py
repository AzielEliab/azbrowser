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
:root {{ color-scheme: dark; --bg:#0b0b0b; --gold:#c9a227; --trim:#8a7219; --text:#f5f5f5; --muted:#c8c0b0; }}
* {{ box-sizing: border-box; }}
html,body {{ margin:0; height:100%; background:var(--bg); color:var(--text); font:14px/1.4 system-ui,sans-serif; }}
#chrome {{ display:flex; flex-direction:column; height:100%; border:2px solid var(--gold); }}
.tabs {{ display:flex; gap:4px; padding:6px 8px 0; background:#111; border-bottom:1px solid var(--gold); }}
.tab {{ padding:6px 12px; border:1px solid var(--trim); border-bottom:none; border-radius:8px 8px 0 0; background:#1a1a1a; color:var(--text); cursor:pointer; }}
.tab.active {{ background:#0b0b0b; color:var(--gold); }}
.plus {{ color:var(--gold); cursor:pointer; padding:6px 10px; }}
.bar {{ display:flex; align-items:center; gap:6px; padding:8px; background:#111; border-bottom:1px solid var(--gold); }}
.bar button {{ background:#161616; color:var(--text); border:1px solid var(--gold); border-radius:6px; min-width:36px; height:32px; cursor:pointer; }}
.bar button:hover {{ background:#241c0d; color:var(--gold); }}
#home img {{ width:22px; height:22px; vertical-align:middle; }}
#omnibox {{ flex:1; background:#0b0b0b; color:var(--text); border:1px solid var(--gold); border-radius:16px; padding:8px 14px; }}
.mode {{ color:var(--gold); font-size:12px; letter-spacing:.06em; }}
main {{ flex:1; display:grid; grid-template-columns: 1fr 320px; min-height:0; }}
#stage {{ overflow:auto; padding:16px; }}
aside {{ border-left:1px solid var(--gold); overflow:auto; padding:12px; background:#101010; }}
h2 {{ color:var(--gold); font-size:13px; margin:0 0 8px; }}
.banner {{ border:1px solid var(--trim); background:#241c0d; color:#f0d78c; padding:10px; border-radius:8px; margin-bottom:12px; }}
pre {{ white-space:pre-wrap; word-break:break-word; font-size:12px; }}
.receipt {{ font-family:ui-monospace,monospace; font-size:11px; border-bottom:1px solid #333; padding:6px 0; }}
.status {{ border-top:1px solid var(--gold); padding:6px 10px; font-size:12px; color:var(--muted); }}
#meshStrip {{ border-top:1px solid var(--gold); padding:8px 10px; background:#0e0e0e; display:flex; flex-wrap:wrap; align-items:center; gap:10px 16px; font-size:12px; color:var(--muted); }}
#meshStrip .live b {{ color:var(--gold); font-size:18px; margin-right:6px; }}
#meshStrip button {{ background:#161616; color:var(--text); border:1px solid var(--trim); border-radius:6px; height:28px; padding:0 10px; cursor:pointer; }}
a {{ color:var(--gold); }}
</style>
<div id="chrome">
  <div class="tabs" id="tabs"></div>
  <div class="bar">
    <button id="back" title="Back" type="button">◀</button>
    <button id="fwd" title="Forward" type="button">▶</button>
    <button id="reload" title="Reload" type="button">↻</button>
    <button id="home" title="Home" type="button"><img alt="Home" src="{SIGIL}"></button>
    <input id="omnibox" placeholder="Search AZNet or enter a URL" spellcheck="false">
    <button id="go" type="button">Go</button>
    <span class="mode">AZNet</span>
    <button id="airlockBtn" type="button">Airlock</button>
  </div>
  <main>
    <section id="stage"></section>
    <aside>
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
function show(obj) {{
  const stage = document.getElementById('stage');
  const rec = document.getElementById('receipts');
  stage.innerHTML = '<div class="banner">' + (obj.display ? obj.display.summary : (obj.note||'')) + '</div><pre>' + JSON.stringify(obj,null,2) + '</pre>';
  if (obj.receipt) {{
    const el = document.createElement('div');
    el.className = 'receipt';
    el.textContent = obj.receipt.seq + ' ' + obj.receipt.action + ' ' + obj.receipt.hash;
    rec.prepend(el);
  }}
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
document.getElementById('stage').innerHTML = '<div class="banner">{LIMITATION}</div><p>Local loopback UI. Counted Worker: <a href="{HOST}">{HOST}</a></p><p>Ops: {ops}</p><img alt="sigil" src="'+SIGIL+'" width="96" height="96">';
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
