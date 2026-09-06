/**
 * AZBrowser hosted runtime: /v1 ops, OpenAPI, MCP JSON-RPC, FragGate pointers.
 * /v1 never touches DOWNLOADS KV. Dual surface — not UI-only.
 */
import {
  ALIASES,
  AZMAIL,
  AZMAIL_WORKER,
  FRAGGATE,
  FRAGGATE_CALL,
  FRAGGATE_MCP,
  HOST,
  IDENTITY,
  LIMITATION,
  OPS,
  PRODUCT,
  RUNTIME,
  SIGIL,
  SKILL_MD,
  SPEC,
  VERSION,
  dispatch,
} from "./engine.js";

const ALLOW_PROXY = new Set([
  "aziel-corpus",
  "decisiongate",
  "godlock",
  "forgereceipts",
  "azbrowser",
]);

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Accept, MCP-Protocol-Version, mcp-session-id, User-Agent, Authorization",
  };
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...corsHeaders() },
  });
}

function originOf(request) {
  try {
    return new URL(request.url).origin;
  } catch {
    return HOST;
  }
}

function toolDefs() {
  const desc = {
    health: "Liveness. Does not increment downloads.",
    skill: "Return AZBrowser skill markdown.",
    navigate: "Sandbox navigate / controlled fetch preview. Same as address-bar Go.",
    preview: "Alias of navigate.",
    reload: "Reload the active tab preview.",
    back: "Tab history back.",
    forward: "Tab history forward.",
    home: "Home — everblooming sigil new-tab panel.",
    tab_new: "Open an isolated tab.",
    tab_close: "Close a tab.",
    tab_switch: "Switch active tab.",
    tab_list: "List tabs.",
    ethical_search: "AZNet / Lamb Lens ethical search. Cite sources. Refuse doxxing/creds/malware.",
    lamb_lens: "Alias of ethical_search.",
    search: "Alias of ethical_search.",
    airlock: "download → scan → scrub → verify → vault. Receipt hashes per stage.",
    airlock_status: "Show airlock pipeline stages.",
    receipt: "Append a manual integrity receipt.",
    receipts: "List append-only receipts.",
    receipt_verify: "Walk the hash chain.",
    scrub: "Strip scripts/embeds from HTML.",
    ethics_gate: "Classify a query without searching.",
  };
  return OPS.map((name) => ({
    name: "azbrowser_" + name,
    description: desc[name] || name,
    inputSchema: {
      type: "object",
      properties: {
        url: { type: "string" },
        q: { type: "string" },
        query: { type: "string" },
        tab_id: { type: "string" },
        session_id: { type: "string" },
        content: { type: "string" },
        filename: { type: "string" },
        html: { type: "string" },
        fetch: { type: "boolean" },
        limit: { type: "integer" },
        action: { type: "string" },
        payload: { type: "object" },
      },
    },
  }));
}

function openapiSpec(origin) {
  const paths = {
    "/v1/health": { get: { operationId: "azbrowser_health", summary: "Liveness. Does not increment downloads.", responses: { "200": { description: "ok" } } } },
    "/v1/skill": { get: { operationId: "azbrowser_skill", summary: "Skill markdown.", responses: { "200": { description: "markdown" } } } },
    "/openapi.json": { get: { operationId: "azbrowser_openapi", summary: "OpenAPI 3.1 — first-class backend.", responses: { "200": { description: "spec" } } } },
    "/mcp": {
      get: { operationId: "azbrowser_mcp_docs", summary: "MCP docs + FragGate pointer.", responses: { "200": { description: "docs" } } },
      post: { operationId: "azbrowser_mcp", summary: "JSON-RPC MCP-over-HTTP (tools/list, tools/call). Same ops as UI.", responses: { "200": { description: "rpc" } } },
    },
  };
  for (const op of OPS) {
    if (op === "health" || op === "skill") continue;
    paths["/v1/" + op] = {
      post: {
        operationId: "azbrowser_" + op,
        summary: (ALIASES[op] ? "Alias of " + ALIASES[op] + ". " : "") + "UI action + MCP/FragGate op.",
        requestBody: { content: { "application/json": { schema: { type: "object" } } } },
        responses: { "200": { description: "display + result + receipt" } },
      },
    };
  }
  paths["/v1/runtime/call"] = {
    post: {
      operationId: "azbrowser_runtime_call",
      summary: "FragGate-shaped call. slug=azbrowser runs local engine; allowlisted siblings proxy to aziel-runtime.",
      requestBody: { content: { "application/json": { schema: { type: "object" } } } },
      responses: { "200": { description: "result" } },
    },
  };
  paths["/v1/runtime/list"] = {
    get: {
      operationId: "azbrowser_runtime_list",
      summary: "Local op list + pointer to FragGate list.",
      responses: { "200": { description: "list" } },
    },
  };
  return {
    openapi: "3.1.0",
    info: {
      title: "AZBrowser runtime",
      version: VERSION,
      summary: "Dual surface. Human UI is this Worker. Agents use FragGate slug=azbrowser or this OpenAPI / POST /mcp.",
      description: LIMITATION + " Agent door: POST " + FRAGGATE_CALL + " {slug:azbrowser,op,payload}. Catalog MCP: POST " + FRAGGATE_MCP + ". This host implements the same ops so the backend is first-class.",
      license: { name: "Apache-2.0", identifier: "Apache-2.0" },
      contact: { name: IDENTITY, url: "https://github.com/AzielEliab/azbrowser" },
    },
    servers: [{ url: origin }, { url: RUNTIME, description: "aziel-runtime FragGate catalog" }],
    paths,
  };
}

function mcpDocs(origin) {
  return {
    ok: true,
    product: PRODUCT,
    door: "fraggate",
    slug: "azbrowser",
    identity: IDENTITY,
    agent_path: FRAGGATE_CALL,
    catalog_mcp: FRAGGATE_MCP,
    this_mcp: origin + "/mcp",
    openapi: origin + "/openapi.json",
    note: "Preferred AI path is FragGate (aziel-runtime /mcp + POST /v1/fraggate/call slug=azbrowser). This Worker also implements JSON-RPC tools/list and tools/call for the same ops — not UI-only. Catalog listing of azbrowser lands in a sibling runtime PR.",
    ops: OPS,
    tools: toolDefs().map((t) => t.name),
    limitation: LIMITATION,
    kernel: FRAGGATE,
  };
}

async function handleMcpPost(request) {
  let body;
  try {
    body = await request.json();
  } catch {
    return json({ jsonrpc: "2.0", error: { code: -32700, message: "Parse error" }, id: null }, 400);
  }
  const id = body.id ?? null;
  const method = body.method;
  if (method === "initialize") {
    return json({
      jsonrpc: "2.0",
      id,
      result: {
        protocolVersion: "2024-11-05",
        capabilities: { tools: {} },
        serverInfo: { name: "azbrowser", version: VERSION },
        instructions: "AZBrowser dual surface. Prefer FragGate slug=azbrowser. Display display.title/summary/fields. " + LIMITATION,
      },
    });
  }
  if (method === "tools/list" || method === "notifications/initialized") {
    if (method === "notifications/initialized") return new Response(null, { status: 204, headers: corsHeaders() });
    return json({ jsonrpc: "2.0", id, result: { tools: toolDefs() } });
  }
  if (method === "tools/call") {
    const tname = String((body.params && body.params.name) || "");
    const op = tname.replace(/^azbrowser_/, "");
    const args = (body.params && body.params.arguments) || {};
    const result = await dispatch(op, args, args.session_id);
    return json({
      jsonrpc: "2.0",
      id,
      result: {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
        structuredContent: result,
        isError: result.ok === false,
      },
    });
  }
  if (method === "ping") return json({ jsonrpc: "2.0", id, result: {} });
  return json({
    jsonrpc: "2.0",
    id,
    error: {
      code: -32601,
      message: "Method not found. Prefer FragGate POST " + FRAGGATE_CALL + " slug=azbrowser. This host supports initialize, tools/list, tools/call.",
    },
  });
}

async function proxyFragGate(body) {
  const slug = String((body && (body.slug || body.name)) || "");
  const op = String((body && body.op) || "health");
  const payload = (body && body.payload) || {};
  if (slug === "azbrowser" || !slug) return dispatch(op, payload, payload.session_id);
  if (!ALLOW_PROXY.has(slug)) {
    return { ok: false, code: "FG-HALLUC-TOOL", error: "slug not allowlisted on this Worker", slug, door: "fraggate", agent_path: FRAGGATE_CALL };
  }
  try {
    const res = await fetch(FRAGGATE_CALL, {
      method: "POST",
      headers: { "content-type": "application/json", "User-Agent": "Mozilla/5.0 AZBrowser/0.1.0" },
      body: JSON.stringify({ slug, op, payload, claim: body.claim }),
    });
    return await res.json();
  } catch (exc) {
    return { ok: false, error: "fraggate_proxy_failed", detail: String(exc).slice(0, 240), agent_path: FRAGGATE_CALL };
  }
}

function aiHtml(origin) {
  return `<!doctype html><html lang="en"><meta charset="utf-8"><title>AZBrowser — AI / MCP</title>
<style>body{font:16px/1.45 system-ui;max-width:46rem;margin:3rem auto;padding:0 1.25rem;background:#0b0b0b;color:#e8e0d0}a{color:#c9a227}.banner{border:1px solid #5c4a1a;background:#241c0d;color:#f0d78c;padding:.85rem 1rem;border-radius:8px}pre{background:#141414;padding:.85rem 1rem;overflow:auto;border-radius:8px}</style>
<h1>AZBrowser dual surface</h1>
<p class="banner">${LIMITATION}</p>
<p>Human UI is the Worker homepage (browser chrome). AI / MCP path is FragGate:</p>
<pre>POST ${FRAGGATE_CALL}
{"slug":"azbrowser","op":"ethical_search","payload":{"q":"FragGate"}}</pre>
<p>Catalog MCP: <code>POST ${FRAGGATE_MCP}</code> · this Worker MCP: <code>POST ${origin}/mcp</code> (tools/list, tools/call).</p>
<p>OpenAPI: <a href="${origin}/openapi.json">${origin}/openapi.json</a></p>
<p>Kernel: <a href="${FRAGGATE}">${FRAGGATE}</a> · AZMail sibling: <a href="${AZMAIL}">${AZMAIL}</a></p>
<p><a href="/">Downloads + browser UI</a></p>
</html>`;
}

export { SKILL_MD };

export async function handleRuntimeApi(request, url) {
  const path = url.pathname.replace(/\/+$/, "") || "/";
  if (path === "/mcp" && request.method === "GET") return json(mcpDocs(originOf(request)));
  if (path === "/mcp" && request.method === "POST") return handleMcpPost(request);

  if (path === "/v1/health" && request.method === "GET") return json(await dispatch("health", {}));
  if (path === "/v1/skill" && request.method === "GET") {
    return new Response(SKILL_MD, {
      status: 200,
      headers: { "Content-Type": "text/markdown; charset=utf-8", "Cache-Control": "private, no-store", ...corsHeaders() },
    });
  }
  if (path === "/openapi.json" && request.method === "GET") return json(openapiSpec(originOf(request)));
  if ((path === "/ai" || url.pathname === "/ai/") && request.method === "GET") {
    return new Response(aiHtml(originOf(request)), { headers: { "Content-Type": "text/html; charset=utf-8", ...corsHeaders() } });
  }
  if (path === "/llms.txt" || path === "/ai.txt") {
    return new Response(
      `AZBrowser ${VERSION} by ${IDENTITY}. Apache-2.0. ${LIMITATION}\nAgent path (FragGate): POST ${FRAGGATE_CALL} {"slug":"azbrowser","op":"…","payload":{}}\nCatalog MCP: POST ${FRAGGATE_MCP}\nThis Worker MCP: POST ${originOf(request)}/mcp\nHuman UI: ${originOf(request)}/\nSkill: ${originOf(request)}/v1/skill\nOpenAPI: ${originOf(request)}/openapi.json\nAZMail sibling: ${AZMAIL}\n`,
      { headers: { "Content-Type": "text/plain; charset=utf-8", ...corsHeaders() } },
    );
  }
  if (path === "/v1/runtime/list" && request.method === "GET") {
    return json({
      ok: true,
      door: "fraggate",
      slug: "azbrowser",
      ops: OPS,
      live_ops: OPS.map((o) => "azbrowser/" + o),
      agent_path: FRAGGATE_CALL,
      catalog_list: RUNTIME + "/v1/fraggate/list",
      note: "Local AZBrowser ops. Discover the full mesh with FragGate list.",
      azmail: AZMAIL_WORKER,
      sigil: SIGIL,
    });
  }
  if (path === "/v1/runtime/call" && request.method === "POST") {
    let body;
    try {
      body = await request.json();
    } catch {
      return json({ error: "JSON body required", limitation: LIMITATION }, 400);
    }
    return json(await proxyFragGate(body));
  }
  if (path.startsWith("/v1/") && request.method === "POST") {
    const op = path.slice(4);
    let body = {};
    try {
      const n = request.headers.get("content-length");
      if (n !== "0") body = await request.json();
    } catch {
      body = {};
    }
    const out = await dispatch(op, body || {}, body && body.session_id);
    return json(out, out.ok === false && out.code === "FG-HALLUC-TOOL" ? 404 : 200);
  }
  if (path.startsWith("/v1/") || path === "/v1") {
    return json({ error: "not found", hint: "GET /v1/health GET /v1/skill POST /v1/{op} GET /openapi.json POST /mcp", ops: OPS, limitation: LIMITATION }, 404);
  }
  return null;
}
