/**
 * AZNet sibling pair-status client.
 * Does not embed the AZNet protocol. Viewer + pair-status only.
 * FragGate unlocks; StaticClock times. Both products required.
 */

export const AZNET = "https://github.com/AzielEliab/aznet";
export const AZNET_WORKER = "https://aznet-download-tracker.vibelock.workers.dev";
export const AZNET_GARDEN = "https://aznet-download-tracker.vibelock.workers.dev/garden";
export const STATICCLOCK = "https://github.com/AzielEliab/staticclock";
export const FRAGGATE = "https://github.com/AzielEliab/fraggate";
export const FRAGGATE_CALL = "https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call";
export const RUNTIME = "https://aziel-runtime.vibelock.workers.dev";

const UA = "Mozilla/5.0 AZBrowser/0.1.0 (pair-status; sibling-client)";

export function links() {
  return {
    aznet_github: AZNET,
    aznet_worker: AZNET_WORKER,
    aznet_garden: AZNET_GARDEN,
    fraggate: FRAGGATE,
    fraggate_call: FRAGGATE_CALL,
    runtime: RUNTIME,
    staticclock: STATICCLOCK,
  };
}

export function pairBase() {
  return {
    action: "pair_status",
    peer: "azbrowser",
    sibling: "aznet",
    required: true,
    viewer: true,
    protocol_embedded: false,
    links: links(),
    note: "AZBrowser views the AZNet side-net. Pairing is required to run. Protocol lives in AZNet. FragGate unlocks; StaticClock times.",
  };
}

export function stubPair(paired) {
  const base = pairBase();
  if (paired) {
    return {
      ...base,
      ok: true,
      paired: true,
      code: "PAIRED",
      aznet: { reachable: true, paired: true, source: "stub" },
      fraggate_unlock: true,
      staticclock: { source: "stub", note: "Tests do not call StaticClock." },
    };
  }
  return {
    ...base,
    ok: true,
    paired: false,
    code: "PAIR_REQUIRED",
    aznet: { reachable: false, paired: false, source: "stub" },
    fraggate_unlock: false,
    staticclock: {},
  };
}

async function getJson(url) {
  try {
    const res = await fetch(url, { headers: { "User-Agent": UA, Accept: "application/json" } });
    const text = await res.text();
    try {
      return { ok: res.ok, body: JSON.parse(text) };
    } catch {
      return { ok: res.ok, body: { ok: res.ok, text: text.slice(0, 200) } };
    }
  } catch (exc) {
    return { ok: false, body: { error: String(exc).slice(0, 240) } };
  }
}

export async function livePairStatus() {
  const base = pairBase();
  const health = await getJson(AZNET_WORKER.replace(/\/$/, "") + "/v1/health");
  const pair = await getJson(AZNET_WORKER.replace(/\/$/, "") + "/v1/pair?peer=azbrowser");
  const aznetReachable = Boolean(health.ok || pair.ok);
  const blob = pair.ok ? pair.body : health.body;
  let aznetPaired = false;
  if (blob && typeof blob === "object" && (blob.paired === true || (blob.ok === true && blob.peer === "azbrowser"))) {
    aznetPaired = true;
  }

  let fgOk = false;
  let sc = {};
  try {
    const res = await fetch(FRAGGATE_CALL, {
      method: "POST",
      headers: { "User-Agent": UA, "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ slug: "staticclock", op: "advise", payload: { geo: "UTC" } }),
    });
    const fg = await res.json();
    fgOk = Boolean(res.ok);
    const inner = (fg && fg.result && fg.result.result) || (fg && fg.result) || {};
    if (inner && typeof inner === "object") {
      sc = {
        optimal_time: inner.optimal_time,
        optimal_date: inner.optimal_date,
        motto: inner.motto,
        source: "fraggate/staticclock",
      };
    }
    fgOk = Boolean(fgOk && fg && (fg.ok === true || (fg.result && fg.result.ok === true) || sc.optimal_time || sc.motto));
  } catch (exc) {
    sc = { error: String(exc).slice(0, 240) };
    fgOk = false;
  }

  const paired = Boolean(aznetPaired && fgOk);
  return {
    ...base,
    ok: true,
    paired,
    code: paired ? "PAIRED" : "PAIR_REQUIRED",
    aznet: { reachable: aznetReachable, paired: aznetPaired, detail: blob, source: "worker" },
    fraggate_unlock: fgOk,
    staticclock: sc,
  };
}

export function sidenetView() {
  return {
    ok: true,
    action: "sidenet_view",
    viewer: true,
    protocol_embedded: false,
    garden: AZNET_GARDEN,
    worker: AZNET_WORKER,
    github: AZNET,
    links: links(),
    note: "AZNet branding here is the side-net viewer. The protocol and whitepaper live in https://github.com/AzielEliab/aznet.",
  };
}

export async function resolvePair(session, payload) {
  if (payload && typeof payload.paired === "boolean") session.pairStub = payload.paired;
  if (session.pairStub === true) return stubPair(true);
  if (session.pairStub === false) return stubPair(false);
  if (session.pairCache) return session.pairCache;
  const status = await livePairStatus();
  session.pairCache = status;
  return status;
}
