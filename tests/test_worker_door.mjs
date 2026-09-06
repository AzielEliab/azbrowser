/**
 * Prove FragGate / runtime door paths are proxied — never local ops.
 * Live bug: POST /v1/fraggate/call → FG-HALLUC-TOOL op=fraggate/call
 */
import assert from "node:assert/strict";
import {
  classifyV1Path,
  DEFAULT_RUNTIME_ORIGIN,
  doorTargetUrl,
  localOpFromPath,
  mapDoorPath,
} from "../workers/download-tracker/src/door.js";
import { handleRuntimeApi } from "../workers/download-tracker/src/runtime.js";
import { dispatch } from "../workers/download-tracker/src/engine.js";

assert.deepEqual(classifyV1Path("/v1/fraggate/call"), {
  kind: "door",
  path: "/v1/fraggate/call",
  originPath: "/v1/fraggate/call",
});
assert.deepEqual(classifyV1Path("/v1/fraggate/list"), {
  kind: "door",
  path: "/v1/fraggate/list",
  originPath: "/v1/fraggate/list",
});
assert.deepEqual(classifyV1Path("/v1/runtime/list"), {
  kind: "door",
  path: "/v1/runtime/list",
  originPath: "/v1/fraggate/list",
});
assert.deepEqual(classifyV1Path("/v1/runtime/call"), {
  kind: "door",
  path: "/v1/runtime/call",
  originPath: "/v1/fraggate/call",
});
assert.deepEqual(classifyV1Path("/v1/runtime"), {
  kind: "door",
  path: "/v1/runtime",
  originPath: "/v1/runtime",
});
assert.deepEqual(classifyV1Path("/v1/mesh"), {
  kind: "door",
  path: "/v1/mesh",
  originPath: "/v1/mesh",
});
assert.deepEqual(classifyV1Path("/v1/mesh/nodes"), {
  kind: "door",
  path: "/v1/mesh/nodes",
  originPath: "/v1/mesh/nodes",
});
assert.equal(localOpFromPath("/v1/mesh"), null);
assert.deepEqual(classifyV1Path("/v1/navigate"), {
  kind: "local",
  path: "/v1/navigate",
  op: "navigate",
});
assert.equal(classifyV1Path("/v1/fraggate/call").kind, "door");
assert.equal(localOpFromPath("/v1/fraggate/call"), null);
assert.equal(localOpFromPath("/v1/runtime/list"), null);
assert.equal(localOpFromPath("/v1/ethical_search"), "ethical_search");
assert.equal(localOpFromPath("/v1/tab_list"), "tab_list");
assert.equal(mapDoorPath("/v1/runtime/list"), "/v1/fraggate/list");
assert.equal(
  doorTargetUrl("/v1/fraggate/call", "https://azbrowser-download-tracker.vibelock.workers.dev/v1/fraggate/call"),
  DEFAULT_RUNTIME_ORIGIN + "/v1/fraggate/call",
);
assert.equal(
  doorTargetUrl("/v1/runtime/list", "https://example.test/v1/runtime/list?x=1"),
  DEFAULT_RUNTIME_ORIGIN + "/v1/fraggate/list?x=1",
);
assert.equal(classifyV1Path("/v1/not/a/door").kind, "multi");
assert.equal(classifyV1Path("/count").kind, "none");
assert.equal(classifyV1Path("/stats").kind, "none");
assert.equal(classifyV1Path("/download").kind, "none");

const envOrigin = "https://aziel-runtime.example.test";
assert.equal(
  doorTargetUrl("/v1/fraggate/call", "https://local/v1/fraggate/call", { AZIEL_RUNTIME_ORIGIN: envOrigin }),
  envOrigin + "/v1/fraggate/call",
);

const engineRefuse = await dispatch("fraggate/call", {});
assert.equal(engineRefuse.code, "FG-HALLUC-TOOL");
assert.equal(engineRefuse.op, "fraggate/call");

const fetches = [];
const previousFetch = globalThis.fetch;
globalThis.fetch = async (input, init) => {
  const url = typeof input === "string" ? input : input.url;
  fetches.push({ url, method: (init && init.method) || (input && input.method) || "GET" });
  return new Response(JSON.stringify({ ok: true, door: "fraggate", proxied: true, origin: url }), {
    status: 200,
    headers: { "content-type": "application/json; charset=utf-8" },
  });
};

try {
  const callReq = new Request("https://azbrowser-download-tracker.vibelock.workers.dev/v1/fraggate/call", {
    method: "POST",
    headers: { "content-type": "application/json", "user-agent": "Mozilla/5.0" },
    body: JSON.stringify({ slug: "azbrowser", op: "health", payload: {} }),
  });
  const callRes = await handleRuntimeApi(callReq, new URL(callReq.url), {});
  assert.ok(callRes, "door path must be handled");
  const callBody = await callRes.json();
  assert.notEqual(callBody.code, "FG-HALLUC-TOOL");
  assert.notEqual(callBody.op, "fraggate/call");
  assert.notEqual(callBody.error, "unknown op");
  assert.equal(callBody.ok, true);
  assert.equal(callBody.proxied, true);
  assert.equal(callRes.headers.get("X-Aziel-Door"), "proxy");
  assert.ok(fetches.some((f) => f.url === DEFAULT_RUNTIME_ORIGIN + "/v1/fraggate/call" && f.method === "POST"));

  fetches.length = 0;
  const listReq = new Request("https://azbrowser-download-tracker.vibelock.workers.dev/v1/runtime/list", {
    method: "GET",
    headers: { "user-agent": "Mozilla/5.0" },
  });
  const listRes = await handleRuntimeApi(listReq, new URL(listReq.url), {});
  const listBody = await listRes.json();
  assert.notEqual(listBody.code, "FG-HALLUC-TOOL");
  assert.notEqual(listBody.op, "runtime/list");
  assert.equal(listBody.ok, true);
  assert.ok(fetches.some((f) => f.url === DEFAULT_RUNTIME_ORIGIN + "/v1/fraggate/list"));

  fetches.length = 0;
  const aliasReq = new Request("https://azbrowser-download-tracker.vibelock.workers.dev/v1/runtime/call", {
    method: "POST",
    headers: { "content-type": "application/json", "user-agent": "Mozilla/5.0" },
    body: JSON.stringify({ slug: "azbrowser", op: "ethical_search", payload: { q: "FragGate" } }),
  });
  const aliasRes = await handleRuntimeApi(aliasReq, new URL(aliasReq.url), {});
  const aliasBody = await aliasRes.json();
  assert.notEqual(aliasBody.code, "FG-HALLUC-TOOL");
  assert.notEqual(aliasBody.op, "runtime/call");
  assert.ok(fetches.some((f) => f.url === DEFAULT_RUNTIME_ORIGIN + "/v1/fraggate/call"));

  const bindingFetches = [];
  const bindingEnv = {
    AZIEL_RUNTIME: {
      fetch: async (input) => {
        const url = typeof input === "string" ? input : input.url;
        bindingFetches.push(url);
        return new Response(JSON.stringify({ ok: true, via: "binding" }), {
          headers: { "content-type": "application/json" },
        });
      },
    },
  };
  const bindReq = new Request("https://azbrowser-download-tracker.vibelock.workers.dev/v1/fraggate/call", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ slug: "azbrowser", op: "skill", payload: {} }),
  });
  const bindRes = await handleRuntimeApi(bindReq, new URL(bindReq.url), bindingEnv);
  const bindBody = await bindRes.json();
  assert.equal(bindBody.via, "binding");
  assert.ok(bindingFetches[0].endsWith("/v1/fraggate/call"));

  const localReq = new Request("https://azbrowser-download-tracker.vibelock.workers.dev/v1/ethical_search", {
    method: "POST",
    headers: { "content-type": "application/json", "user-agent": "Mozilla/5.0" },
    body: JSON.stringify({ q: "FragGate kernel" }),
  });
  const localRes = await handleRuntimeApi(localReq, new URL(localReq.url), {});
  const localBody = await localRes.json();
  assert.equal(localBody.ok, true);
  assert.equal(localBody.action, "ethical_search");
  assert.ok(localBody.receipt);

  const healthReq = new Request("https://azbrowser-download-tracker.vibelock.workers.dev/v1/health", {
    method: "GET",
    headers: { "user-agent": "Mozilla/5.0" },
  });
  const healthRes = await handleRuntimeApi(healthReq, new URL(healthReq.url), {});
  const healthBody = await healthRes.json();
  assert.equal(healthBody.ok, true);
  assert.equal(healthBody.product, "azbrowser");

  const multiReq = new Request("https://azbrowser-download-tracker.vibelock.workers.dev/v1/not/a/door", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: "{}",
  });
  const multiRes = await handleRuntimeApi(multiReq, new URL(multiReq.url), {});
  const multiBody = await multiRes.json();
  assert.equal(multiBody.code, "NOT_LOCAL_OP");
  assert.notEqual(multiBody.code, "FG-HALLUC-TOOL");
  assert.notEqual(multiBody.op, "not/a/door");

  for (const path of ["/count", "/stats", "/download", "/"]) {
    const req = new Request("https://azbrowser-download-tracker.vibelock.workers.dev" + path, { method: "GET" });
    const res = await handleRuntimeApi(req, new URL(req.url), {});
    assert.equal(res, null, path + " must stay on the download tracker, not the runtime router");
  }
} finally {
  globalThis.fetch = previousFetch;
}

console.log("worker door proxy smoke ok");
