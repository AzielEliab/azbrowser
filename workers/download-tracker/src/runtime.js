/**
 * AZBrowser hosted runtime: /v1 ops, OpenAPI, MCP pointer, FragGate door proxy.
 * /v1 never touches DOWNLOADS KV. Dual surface — not UI-only.
 *
 * Door paths (`/v1/fraggate/*`, `/v1/runtime/*`) PROXY to aziel-runtime.
 * Local ops are single-segment `/v1/{op}` only.
 */
import {
  ALIASES,
  AZMAIL,
  AZNET,
  FRAGGATE,
  FRAGGATE_CALL,
  FRAGGATE_MCP,
  HOST,
  IDENTITY,
  LIMITATION,
  OPS,
  PRODUCT,
  RUNTIME,
  SKILL_MD,
  VERSION,
  dispatch,
} from "./engine.js";
import { classifyV1Path, doorTargetUrl } from "./door.js";

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
  paths["/v1/fraggate/call"] = {
    post: {
      operationId: "azbrowser_fraggate_call_proxy",
      summary: "PROXY to aziel-runtime POST /v1/fraggate/call. Not a local op.",
      requestBody: { content: { "application/json": { schema: { type: "object" } } } },
      responses: { "200": { description: "FragGate ResultEnvelope" } },
    },
  };
  paths["/v1/fraggate/list"] = {
    get: {
      operationId: "azbrowser_fraggate_list_proxy",
      summary: "PROXY to aziel-runtime GET /v1/fraggate/list. Not a local op.",
      responses: { "200": { description: "hashed registry" } },
    },
  };
  paths["/v1/runtime/call"] = {
    post: {
      operationId: "azbrowser_runtime_call_proxy",
      summary: "Alias PROXY → origin /v1/fraggate/call. Not a local op.",
      requestBody: { content: { "application/json": { schema: { type: "object" } } } },
      responses: { "200": { description: "FragGate ResultEnvelope" } },
    },
  };
  paths["/v1/runtime/list"] = {
    get: {
      operationId: "azbrowser_runtime_list_proxy",
      summary: "Alias PROXY → origin /v1/fraggate/list. Not a local op.",
      responses: { "200": { description: "hashed registry" } },
    },
  };
  return {
    openapi: "3.1.0",
    info: {
      title: "AZBrowser runtime",
      version: VERSION,
    summary: "Dual surface. Human UI is this Worker /v1. AI / MCP path is FragGate only (slug=azbrowser).",
    description: LIMITATION + " Agent door is FragGate only: POST " + FRAGGATE_CALL + " {slug:azbrowser,op,payload}. Catalog MCP: POST " + FRAGGATE_MCP + ". This host /mcp is a pointer, not a second agent brand. Human chrome uses same-origin /v1.",
      license: { name: "Apache-2.0", identifier: "Apache-2.0" },
      contact: { name: IDENTITY, url: "https://github.com/AzielEliab/azbrowser" },
    },
    servers: [{ url: origin }, { url: RUNTIME, description: "aziel-runtime FragGate catalog" }],
    paths,
  };
}

function mcpDocs(origin) {
  return {
    ok: false,
    error: "not a product MCP",
    product: PRODUCT,
    door: "fraggate",
    slug: "azbrowser",
    identity: IDENTITY,
    agent_path: FRAGGATE_CALL,
    catalog_mcp: FRAGGATE_MCP,
    body: { slug: "azbrowser", op: "ethical_search", payload: { q: "FragGate" } },
    openapi: origin + "/openapi.json",
    note: "AI / MCP path is FragGate only. This host /v1/fraggate/* and /v1/runtime/* PROXY to aziel-runtime. Local ops are /v1/{op} only. Catalog MCP: POST " + FRAGGATE_MCP + ". AZNet is a sibling functional pair, not this product.",
    ops: OPS,
    tools: toolDefs().map((t) => t.name),
    limitation: LIMITATION,
    kernel: FRAGGATE,
  };
}

function handleMcpPost() {
  return json(mcpDocs(HOST));
}

function runtimeFetcher(env) {
  if (env && env.AZIEL_RUNTIME && typeof env.AZIEL_RUNTIME.fetch === "function") return env.AZIEL_RUNTIME;
  return null;
}

async function proxyDoor(request, url, env) {
  const dest = doorTargetUrl(url.pathname, request.url, env);
  if (!dest) {
    return json({ ok: false, error: "not a door path", path: url.pathname, limitation: LIMITATION }, 404);
  }
  const headers = new Headers();
  const pass = ["content-type", "accept", "authorization", "user-agent", "mcp-protocol-version", "mcp-session-id", "x-aziel-runtime-token"];
  for (const name of pass) {
    const v = request.headers.get(name);
    if (v) headers.set(name, v);
  }
  if (!headers.has("User-Agent")) headers.set("User-Agent", "Mozilla/5.0 AZBrowser/0.1.0");
  const init = { method: request.method, headers, redirect: "follow" };
  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = request.body;
    init.duplex = "half";
  }
  try {
    const fetcher = runtimeFetcher(env);
    const res = fetcher ? await fetcher.fetch(dest, init) : await fetch(dest, init);
    const outHeaders = new Headers(res.headers);
    for (const [k, v] of Object.entries(corsHeaders())) outHeaders.set(k, v);
    outHeaders.set("X-Aziel-Door", "proxy");
    outHeaders.set("X-Aziel-Door-Origin", dest);
    return new Response(res.body, { status: res.status, statusText: res.statusText, headers: outHeaders });
  } catch (exc) {
    return json({
      ok: false,
      error: "fraggate_proxy_failed",
      detail: String(exc).slice(0, 240),
      origin: dest,
      agent_path: FRAGGATE_CALL,
      limitation: LIMITATION,
    }, 502);
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
<p>Catalog MCP: <code>POST ${FRAGGATE_MCP}</code>. This Worker <code>/mcp</code> is a pointer, not a second MCP.</p>
<p>OpenAPI: <a href="${origin}/openapi.json">${origin}/openapi.json</a></p>
<p>Kernel: <a href="${FRAGGATE}">${FRAGGATE}</a> · AZMail sibling: <a href="${AZMAIL}">${AZMAIL}</a> · AZNet sibling (functional pair): <a href="${AZNET}">${AZNET}</a></p>
<p><a href="/">Downloads + browser UI</a></p>
</html>`;
}

export { SKILL_MD };

export async function handleRuntimeApi(request, url, env) {
  const path = url.pathname.replace(/\/+$/, "") || "/";
  if (path === "/mcp" && request.method === "GET") return json(mcpDocs(originOf(request)));
  if (path === "/mcp" && request.method === "POST") return handleMcpPost();

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
      `AZBrowser ${VERSION} by ${IDENTITY}. Apache-2.0. ${LIMITATION}\nAgent path is FragGate only: POST ${FRAGGATE_CALL} {"slug":"azbrowser","op":"…","payload":{}}\nThis Worker /v1/fraggate/* and /v1/runtime/* PROXY to aziel-runtime. Local ops are /v1/{op} only.\nCatalog MCP: POST ${FRAGGATE_MCP}\nThis Worker /mcp is a pointer, not a second MCP.\nHuman UI: ${originOf(request)}/\nSkill: ${originOf(request)}/v1/skill\nOpenAPI: ${originOf(request)}/openapi.json\nAZMail sibling: ${AZMAIL}\nAZNet sibling (functional pair): ${AZNET}\n`,
      { headers: { "Content-Type": "text/plain; charset=utf-8", ...corsHeaders() } },
    );
  }

  const classified = classifyV1Path(url.pathname);
  if (classified.kind === "door") {
    return proxyDoor(request, url, env);
  }
  if (classified.kind === "multi") {
    return json({
      ok: false,
      error: "not a local op",
      code: "NOT_LOCAL_OP",
      path: classified.path,
      hint: "Local ops are POST|GET /v1/{op} only (single segment). FragGate door is /v1/fraggate/* (proxied to aziel-runtime). /v1/runtime/list and /v1/runtime/call alias that door.",
      agent_path: FRAGGATE_CALL,
      ops: OPS,
      limitation: LIMITATION,
    }, 404);
  }
  if (classified.kind === "local" && request.method === "POST") {
    let body = {};
    try {
      const n = request.headers.get("content-length");
      if (n !== "0") body = await request.json();
    } catch {
      body = {};
    }
    const out = await dispatch(classified.op, body || {}, body && body.session_id);
    return json(out, out.ok === false && out.code === "FG-HALLUC-TOOL" ? 404 : 200);
  }
  if (path.startsWith("/v1/") || path === "/v1") {
    return json({ error: "not found", hint: "GET /v1/health GET /v1/skill POST /v1/{op} GET /v1/fraggate/list POST /v1/fraggate/call GET /openapi.json POST /mcp", ops: OPS, limitation: LIMITATION }, 404);
  }
  return null;
}
