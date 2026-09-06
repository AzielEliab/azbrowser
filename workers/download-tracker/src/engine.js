/**
 * AZBrowser Phase 1 engine — same ops as Python / MCP / FragGate slug=azbrowser.
 * Dual surface: Worker UI and agents call these verbs. Not Chromium.
 */

export const VERSION = "0.1.0";
export const SPEC = "azbrowser-phase-1";
export const PRODUCT = "azbrowser";
export const IDENTITY = "Aziel Eliab";
export const RUNTIME = "https://aziel-runtime.vibelock.workers.dev";
export const FRAGGATE = "https://github.com/AzielEliab/fraggate";
export const FRAGGATE_CALL = "https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call";
export const FRAGGATE_MCP = "https://aziel-runtime.vibelock.workers.dev/mcp";
export const HOST = "https://azbrowser-download-tracker.vibelock.workers.dev";
export const SIGIL = "https://www.azielcorpuslibrary.net/sigil.png";
export const AZMAIL = "https://github.com/AzielEliab/azmail";
export const AZMAIL_WORKER = "https://azmail-download-tracker.vibelock.workers.dev";
export { AZNET, AZNET_GARDEN, AZNET_WORKER, STATICCLOCK } from "./pair.js";
import { AZNET, resolvePair, sidenetView } from "./pair.js";
export const LIMITATION =
  "THIS IS: a Phase 1 research-browser shell (browser-chrome UX) with controlled fetch/proxy preview, receipted airlock, and Lamb Lens ethical search. AZNet is a sibling side-net (https://github.com/AzielEliab/aznet) — AZBrowser views it and requires pairing to run. THIS IS NOT: a Chromium replacement, a VPN, AZ-OS, Lumen, AZInterface, or an AZNet protocol fork. FragGate unlocks; StaticClock times. AZMail is a separate sibling. No receipt = no action. Author: Aziel Eliab only.";

export const PAIR_REQUIRED_OPS = ["navigate", "ethical_search", "airlock", "scrub"];

export const OPS = [
  "health",
  "skill",
  "pair_status",
  "sidenet_view",
  "navigate",
  "preview",
  "reload",
  "back",
  "forward",
  "home",
  "tab_new",
  "tab_close",
  "tab_switch",
  "tab_list",
  "ethical_search",
  "lamb_lens",
  "search",
  "airlock",
  "airlock_status",
  "receipt",
  "receipts",
  "receipt_verify",
  "scrub",
  "ethics_gate",
];

export const ALIASES = {
  preview: "navigate",
  lamb_lens: "ethical_search",
  search: "ethical_search",
};

export const STAGES = ["download", "scan", "scrub", "verify", "vault"];
const ZERO = "0".repeat(64);
const MAX_BYTES = 256000;

const DOXX = [
  /\bdoxx(?:ing|ed)?\b/i,
  /\bhome address\b/i,
  /\blives at\b/i,
  /\bwhere does\b.+\blive\b/i,
  /\bfind(?:ing)?\b.+\b(?:home )?address\b/i,
  /\bssn\b/i,
  /\bsocial security(?: number)?\b/i,
  /\bphone number of\b/i,
  /\breal name of\b/i,
  /\bprivate address of\b/i,
];
const CREDS = [
  /\bcredential harvest/i,
  /\bharvest (?:login|password|credential|cookie|token)s?\b/i,
  /\bsteal (?:passwords?|cookies?|tokens?|sessions?|logins?)\b/i,
  /\bpassword dump\b/i,
  /\bapi[_ -]?key\s*[:=]/i,
  /\bphishing kit\b/i,
  /\bcapture (?:login|password|credential)s?\b/i,
];
const MALWARE = [
  /\bmalware (?:lure|kit|dropper|payload)\b/i,
  /\bransomware\b/i,
  /\bexploit kit\b/i,
  /\bc2 (?:payload|server|beacon)\b/i,
  /\bhow to hack\b/i,
  /\b0-?day exploit\b/i,
  /\bwrite (?:a |an )?(?:virus|trojan|worm)\b/i,
  /\bdrive-?by download\b/i,
];

const CATALOG = [
  { title: "Aziel Digital Library", url: "https://www.azielcorpuslibrary.net/", source: "aziel-corpus", blurb: "Public MASTER library. FragGate slug=aziel-corpus op=search.", tags: "library corpus aziel research" },
  { title: "FragGate kernel", url: "https://github.com/AzielEliab/fraggate", source: "github", blurb: "One door — discover, route, refuse. FG-0.1.", tags: "fraggate mcp door kernel" },
  { title: "aziel-runtime", url: "https://github.com/AzielEliab/aziel-runtime", source: "github", blurb: "Catalog + FragGate + MCP.", tags: "runtime mcp openapi catalog" },
  { title: "AZNet (sibling side-net)", url: "https://github.com/AzielEliab/aznet", source: "github", blurb: "Silent verification network. Viewer/garden only here — protocol lives in AZNet.", tags: "aznet sidenet pair garden sibling" },
  { title: "AZMail (sibling)", url: "https://github.com/AzielEliab/azmail", source: "github", blurb: "APP 1.0 Mail Airlock. Optional deep-link only.", tags: "azmail mail airlock sibling" },
  { title: "GodLock", url: "https://godlock.uk/", source: "godlock.uk", blurb: "Offline ABAD / hardening score. Not a VPN.", tags: "godlock abad hardening" },
  { title: "Aziel Eliab", url: "https://www.azieleliab.com/", source: "author", blurb: "Public identity: Aziel Eliab only.", tags: "author identity aziel eliab" },
  { title: "Wikipedia", url: "https://en.wikipedia.org/wiki/Main_Page", source: "wikipedia", blurb: "Cite the article.", tags: "encyclopedia wiki research" },
  { title: "MDN Web Docs", url: "https://developer.mozilla.org/", source: "mdn", blurb: "Public web-platform documentation.", tags: "html css javascript http browser" },
];

export function classifyQuery(text) {
  const blob = String(text || "");
  const reasons = [];
  if (DOXX.some((p) => p.test(blob))) reasons.push("doxxing");
  if (CREDS.some((p) => p.test(blob))) reasons.push("credential_harvest");
  if (MALWARE.some((p) => p.test(blob))) reasons.push("malware_lure");
  return {
    ok: reasons.length === 0,
    refuse: reasons.length > 0,
    reasons,
    advisory: true,
    label: "Lamb Lens — advisory ethical gate",
    limitation: "Lamb Lens ethical search is advisory. Cite sources. Refuse doxxing, credential harvest, and malware lure.",
    query_len: blob.length,
  };
}

export function scrubHtml(raw) {
  const stripped = [];
  let text = String(raw || "");
  const drop = (re, label) => {
    if (re.test(text)) {
      stripped.push(label);
      text = text.replace(re, "");
    }
  };
  drop(/<script\b[^>]*>[\s\S]*?<\/script\s*>/gi, "script");
  drop(/<(?:iframe|object|embed|form)\b[^>]*>[\s\S]*?<\/(?:iframe|object|embed|form)\s*>/gi, "embed");
  drop(/<meta\b[^>]*http-equiv\s*=\s*['"]?refresh[^>]*>/gi, "meta_refresh");
  if (/\son[a-z]+\s*=/i.test(text)) {
    stripped.push("event_handler");
    text = text.replace(/\s+on[a-z]+\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+)/gi, "");
  }
  if (/href\s*=\s*['"]\s*javascript:/i.test(text)) {
    stripped.push("javascript_href");
    text = text.replace(/href\s*=\s*['"]\s*javascript:[^'"]*['"]/gi, 'href="#azbrowser-blocked-javascript"');
  }
  return { html: text, stripped, stripped_kinds: [...new Set(stripped)], changed: text !== String(raw || "") };
}

export function sanitizeUrl(url) {
  let raw = String(url || "").trim();
  if (!raw) return { ok: false, error: "url required", url: "" };
  if (!raw.includes("://") && !raw.startsWith("/")) {
    if (/^[a-z0-9.-]+\.[a-z]{2,}(\/|$)/i.test(raw)) raw = "https://" + raw;
    else return { ok: false, error: "not_a_url", url: raw, suggest_search: true };
  }
  let parsed;
  try {
    parsed = new URL(raw);
  } catch {
    return { ok: false, error: "bad_url", url: raw };
  }
  const scheme = parsed.protocol.replace(":", "").toLowerCase();
  if (["javascript", "data", "file", "vbscript"].includes(scheme)) return { ok: false, error: "blocked_scheme", scheme, url: raw };
  if (scheme !== "https" && scheme !== "http") return { ok: false, error: "https_only", scheme, url: raw };
  if (scheme === "http") raw = "https://" + raw.slice("http://".length);
  return { ok: true, url: raw, host: new URL(raw).hostname };
}

async function sha256Hex(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(String(text)));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function displayOf(title, summary, fields) {
  return {
    title,
    summary,
    fields: (fields || []).map(([label, value]) => ({ label, value: String(value) })),
    next: "Show this output to the user, then take the next input.",
  };
}

function newTab(title) {
  return {
    id: "tab-" + crypto.randomUUID().slice(0, 10),
    title: title || "New Tab",
    url: "azbrowser://newtab",
    history: ["azbrowser://newtab"],
    index: 0,
    kind: "newtab",
  };
}

export function createSession() {
  const home = newTab("Home");
  return {
    id: "sess-" + crypto.randomUUID().slice(0, 12),
    tabs: { [home.id]: home },
    active: home.id,
    receipts: [],
  };
}

const SESSIONS = new Map();

export function getSession(id) {
  if (id && SESSIONS.has(id)) return SESSIONS.get(id);
  const s = createSession();
  SESSIONS.set(s.id, s);
  if (SESSIONS.size > 32) {
    const first = SESSIONS.keys().next().value;
    SESSIONS.delete(first);
  }
  return s;
}

async function appendReceipt(session, action, payload) {
  const ts = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
  const seq = session.receipts.length + 1;
  const prev = session.receipts.length ? session.receipts[session.receipts.length - 1].hash : ZERO;
  const payloadHash = await sha256Hex(JSON.stringify(payload || {}));
  const hash = await sha256Hex(`${seq}|${prev}|${action}|${payloadHash}|${ts}`);
  const row = {
    kind: "azbrowser.receipt",
    seq,
    ts,
    action,
    tab_id: session.active,
    prev,
    payload_hash: payloadHash,
    hash,
    payload,
    author: IDENTITY,
  };
  session.receipts.push(row);
  if (session.receipts.length > 64) session.receipts.shift();
  return row;
}

function extractTitle(html) {
  const m = String(html || "").match(/<title[^>]*>([\s\S]*?)<\/title>/i);
  return m ? m[1].replace(/<[^>]+>/g, "").trim().slice(0, 200) : "";
}

function extractText(html, limit) {
  return String(html || "")
    .replace(/<[^>]+>/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, limit || 2400);
}

function rank(query, item) {
  const q = query.toLowerCase().split(/\s+/);
  const blob = [item.title, item.blurb, item.tags].join(" ").toLowerCase();
  return q.reduce((n, w) => n + (w && blob.includes(w) ? 1 : 0), 0);
}

export function ethicalSearch(query, limit) {
  const ethics = classifyQuery(query);
  if (ethics.refuse) {
    return {
      ok: false,
      code: "ETHICS_REFUSE",
      action: "ethical_search",
      alias: "lamb_lens",
      query,
      ethics,
      results: [],
      citations: [],
      advisory: true,
      label: "Lamb Lens — refused. Advisory ethical gate.",
    };
  }
  const scored = [...CATALOG].sort((a, b) => rank(query, b) - rank(query, a));
  let hits = scored.filter((it) => rank(query, it) > 0).slice(0, Math.max(1, Math.min(limit || 8, 16)));
  if (!hits.length) {
    const q = encodeURIComponent(query);
    hits = [
      { title: "Wikipedia search: " + query, url: "https://en.wikipedia.org/w/index.php?search=" + q, source: "wikipedia", blurb: "Cite the article. Advisory.", tags: "wikipedia" },
      { title: "Library lookup: " + query, url: "https://www.azielcorpuslibrary.net/", source: "aziel-corpus", blurb: "FragGate slug=aziel-corpus op=search.", tags: "library" },
    ];
  }
  return {
    ok: true,
    action: "ethical_search",
    alias: "lamb_lens",
    mode: "lamb_lens",
    query,
    ethics,
    results: hits,
    citations: hits.map((h) => ({ title: h.title, url: h.url, source: h.source })),
    advisory: true,
    label: "Lamb Lens — ethical internet search. Advisory. Cite sources.",
    note: "Not a guaranteed index. Not doxxing. Not a malware lure.",
  };
}

function scanBytes(name, data, url) {
  const flags = [];
  const lower = String(name || url || "").toLowerCase();
  for (const ext of [".exe", ".dll", ".scr", ".js", ".vbs", ".ps1", ".bat", ".cmd", ".apk", ".msi"]) {
    if (lower.endsWith(ext)) flags.push("suspicious_extension:" + ext);
  }
  const text = new TextDecoder("utf-8", { fatal: false }).decode(data.slice(0, 4000)).toLowerCase();
  if (text.includes("eval(") || text.includes("<script")) flags.push("script_like");
  if (/powershell|cmd\.exe|wget http/.test(text)) flags.push("shell_lure");
  if (data.length >= 2 && data[0] === 0x4d && data[1] === 0x5a) flags.push("suspicious_magic");
  const risk = Math.min(100, 20 * flags.length);
  let verdict = flags.length ? "hold" : "clean";
  if (flags.includes("suspicious_magic") || flags.some((f) => f.startsWith("suspicious_extension"))) verdict = "quarantine";
  return { flags, risk, verdict, advisory: true };
}

export async function runAirlock({ url = "", content = "", filename = "", fetchLive = false }) {
  const ethics = classifyQuery([url, filename, String(content).slice(0, 200)].join(" "));
  const stages = [];
  const mark = async (name, extra) => {
    const row = { stage: name, ok: extra.ok !== false, ...extra };
    row.hash = await sha256Hex(JSON.stringify(row));
    stages.push(row);
    return row;
  };
  if (ethics.refuse) {
    await mark("download", { ok: false, error: "ETHICS_REFUSE", ethics });
    return { ok: false, code: "ETHICS_REFUSE", stages, ethics, pipeline: STAGES };
  }
  let data = new Uint8Array();
  let safeUrl = "";
  if (content) {
    data = new TextEncoder().encode(String(content));
    await mark("download", { source: "inline", bytes: data.length, filename });
  } else if (url) {
    const safe = sanitizeUrl(url);
    if (!safe.ok) {
      await mark("download", { ok: false, error: safe.error, url });
      return { ok: false, stages, pipeline: STAGES, ...safe };
    }
    safeUrl = safe.url;
    if (fetchLive) {
      try {
        const res = await fetch(safeUrl, { headers: { "User-Agent": "Mozilla/5.0 AZBrowser/0.1.0" }, redirect: "follow" });
        const buf = new Uint8Array(await res.arrayBuffer());
        const truncated = buf.length > MAX_BYTES;
        data = buf.slice(0, MAX_BYTES);
        filename = filename || (new URL(res.url).pathname.split("/").pop() || "download.bin");
        await mark("download", { source: "fetch", url: safeUrl, bytes: data.length, truncated, filename });
      } catch (exc) {
        await mark("download", { ok: false, error: "fetch_failed", detail: String(exc).slice(0, 240), url: safeUrl });
        return { ok: false, stages, pipeline: STAGES, url: safeUrl };
      }
    } else {
      await mark("download", { source: "url-only", url: safeUrl, bytes: 0, filename, note: "metadata preview" });
    }
  } else {
    await mark("download", { ok: false, error: "url_or_content_required" });
    return { ok: false, stages, pipeline: STAGES, error: "url_or_content_required" };
  }
  const scan = scanBytes(filename, data, safeUrl || url);
  await mark("scan", scan);
  let scrubbed = { html: "", stripped_kinds: [], changed: false };
  const asText = new TextDecoder("utf-8", { fatal: false }).decode(data);
  if (asText.includes("<") || /\.html?$/i.test(filename)) scrubbed = scrubHtml(asText);
  await mark("scrub", { stripped_kinds: scrubbed.stripped_kinds, changed: scrubbed.changed });
  const digest = await sha256Hex(asText);
  await mark("verify", { content_hash: digest, bytes: data.length, hash: digest });
  const vault = {
    held: scan.verdict !== "clean",
    verdict: scan.verdict,
    content_hash: digest,
    filename: filename || "untitled",
    stored_bytes: false,
    note: "v0.1 vault is receipt + metadata. Bytes are not persisted on the hosted Worker.",
  };
  await mark("vault", vault);
  const ok = stages.every((s) => s.ok !== false) && scan.verdict !== "quarantine";
  return { ok, pipeline: STAGES, stages, ethics, scan, content_hash: digest, filename: vault.filename, url: safeUrl || url, bytes: data.length, vault, advisory: true, note: "download → scan → scrub → verify → vault. No receipt = no action." };
}

export async function previewUrl(url, fetchLive) {
  const ethics = classifyQuery(url);
  if (ethics.refuse) {
    return { ok: false, code: "ETHICS_REFUSE", action: "navigate", ethics, url, note: "No receipt = no action. Refused before fetch." };
  }
  const safe = sanitizeUrl(url);
  if (!safe.ok) return { ok: false, action: "navigate", ethics, ...safe };
  const out = {
    ok: true,
    action: "navigate",
    url: safe.url,
    host: safe.host,
    ethics,
    sandbox: true,
    renderer: "controlled-fetch-preview",
    not_chromium: true,
    fetched: false,
    title: safe.host || safe.url,
    excerpt: "",
    html: "",
    content_hash: "",
    bytes: 0,
    note: "Phase 1 sandbox preview. Not a replace-your-OS-browser claim.",
  };
  if (!fetchLive) return out;
  try {
    const res = await fetch(safe.url, {
      headers: { "User-Agent": "Mozilla/5.0 AZBrowser/0.1.0", Accept: "text/html,application/xhtml+xml;q=0.9,*/*;q=0.1" },
      redirect: "follow",
    });
    const buf = new Uint8Array(await res.arrayBuffer());
    const truncated = buf.length > MAX_BYTES;
    const raw = buf.slice(0, MAX_BYTES);
    const text = new TextDecoder("utf-8", { fatal: false }).decode(raw);
    const scrubbed = scrubHtml(text);
    out.fetched = true;
    out.final_url = res.url;
    out.content_type = res.headers.get("content-type") || "";
    out.truncated = truncated;
    out.bytes = raw.length;
    out.title = extractTitle(text) || new URL(res.url).hostname || safe.url;
    out.excerpt = extractText(scrubbed.html);
    out.html = scrubbed.html.slice(0, 80000);
    out.stripped_kinds = scrubbed.stripped_kinds;
    out.content_hash = await sha256Hex(text);
    return out;
  } catch (exc) {
    out.ok = false;
    out.error = "fetch_failed";
    out.detail = String(exc).slice(0, 240);
    return out;
  }
}

function current(session) {
  return session.tabs[session.active];
}

function pushTab(session, url, title, kind) {
  const tab = current(session);
  const hist = tab.history.slice(0, tab.index + 1);
  hist.push(url);
  tab.history = hist.slice(-32);
  tab.index = tab.history.length - 1;
  tab.url = url;
  tab.title = title;
  tab.kind = kind || "preview";
  return tab;
}

export async function dispatch(op, payload, sessionId) {
  const name = ALIASES[op] || op;
  const session = getSession(sessionId || (payload && payload.session_id));
  if (!OPS.includes(name) && !OPS.includes(op)) {
    return {
      ok: false,
      code: "FG-HALLUC-TOOL",
      error: "unknown op",
      op,
      ops: OPS,
      door: "fraggate",
      slug: "azbrowser",
      session_id: session.id,
      display: displayOf("Unknown op", "Refused. Discover first.", [["op", op]]),
    };
  }

  const requirePair = async () => {
    const status = await resolvePair(session, payload || {});
    if (status.paired) return null;
    const rec = await appendReceipt(session, "pair_required", { code: "PAIR_REQUIRED" });
    return {
      ok: false,
      code: "PAIR_REQUIRED",
      pair: status,
      receipt: rec,
      session_id: session.id,
      display: displayOf(
        "AZNet pairing required",
        "AZBrowser and AZNet must both be paired. FragGate unlocks; StaticClock times.",
        [
          ["aznet", status.links.aznet_github],
          ["garden", status.links.aznet_garden],
          ["worker", status.links.aznet_worker],
          ["receipt", rec.hash.slice(0, 16)],
        ],
      ),
      limitation: LIMITATION,
    };
  };

  const refuse = async (text) => {
    const ethics = classifyQuery(text);
    if (!ethics.refuse) return null;
    const rec = await appendReceipt(session, "ethics_refuse", { reasons: ethics.reasons, text_len: String(text).length });
    return {
      ok: false,
      code: "ETHICS_REFUSE",
      ethics,
      receipt: rec,
      session_id: session.id,
      display: displayOf("Lamb Lens refused", "Advisory ethical gate refused this input.", [["reasons", ethics.reasons.join(",")], ["receipt", rec.hash.slice(0, 16)]]),
      limitation: LIMITATION,
    };
  };

  if (name === "health") {
    return {
      ok: true,
      product: PRODUCT,
      name: "AZBrowser",
      version: VERSION,
      spec: SPEC,
      identity: IDENTITY,
      author: IDENTITY,
      ops: OPS,
      door: "fraggate",
      slug: "azbrowser",
      agent_path: FRAGGATE_CALL,
      mcp: FRAGGATE_MCP,
      runtime: RUNTIME,
      kernel: FRAGGATE,
      host: HOST,
      sigil: SIGIL,
      azmail: AZMAIL,
      aznet: AZNET,
      pair_required: true,
      sidenet_viewer: true,
      protocol_embedded: false,
      kv_increment: false,
      stored: false,
      chromium: false,
      session_id: session.id,
      limitation: LIMITATION,
      display: displayOf("AZBrowser health", "Phase 1 research shell. Dual surface. AZNet pairing required.", [["version", VERSION], ["ops", OPS.length], ["pair_required", true]]),
    };
  }

  if (name === "pair_status") {
    session.pairCache = null;
    const status = await resolvePair(session, payload || {});
    const rec = await appendReceipt(session, "pair_status", { paired: status.paired, code: status.code });
    status.receipt = rec;
    status.session_id = session.id;
    status.limitation = LIMITATION;
    status.display = displayOf("Pair status", status.note || "", [["paired", status.paired], ["fraggate_unlock", status.fraggate_unlock], ["receipt", rec.hash.slice(0, 16)]]);
    return status;
  }

  if (name === "sidenet_view") {
    const out = sidenetView();
    const rec = await appendReceipt(session, "sidenet_view", { garden: out.garden });
    out.receipt = rec;
    out.pair = await resolvePair(session, payload || {});
    out.session_id = session.id;
    out.limitation = LIMITATION;
    out.display = displayOf("AZNet side-net viewer", "Viewer only. Protocol lives in the AZNet repo.", [["garden", out.garden], ["github", out.github], ["receipt", rec.hash.slice(0, 16)]]);
    return out;
  }

  if (name === "navigate") {
    const url = String((payload && (payload.url || payload.q)) || "").trim();
    if (!url) return { ok: false, error: "url required", limitation: LIMITATION, session_id: session.id };
    const locked = await requirePair();
    if (locked) return locked;
    const blocked = await refuse(url);
    if (blocked) return blocked;
    const safe = sanitizeUrl(url);
    if (safe.suggest_search) return dispatch("ethical_search", { q: url, session_id: session.id }, session.id);
    const preview = await previewUrl(url, !!(payload && payload.fetch));
    if (!preview.ok && preview.code === "ETHICS_REFUSE") {
      preview.receipt = await appendReceipt(session, "ethics_refuse", { url });
      preview.session_id = session.id;
      preview.display = displayOf("Navigate refused", "Ethics gate.", [["url", url]]);
      return preview;
    }
    const tab = pushTab(session, preview.url || url, preview.title || url, "preview");
    const rec = await appendReceipt(session, "navigate", { url: preview.url || url, ok: preview.ok, hash: preview.content_hash || "" });
    preview.tab = tab;
    preview.receipt = rec;
    preview.session_id = session.id;
    preview.limitation = LIMITATION;
    preview.display = displayOf(preview.title || "Preview", "Sandbox preview (not Chromium).", [["url", preview.url], ["receipt", rec.hash.slice(0, 16)], ["ok", preview.ok]]);
    return preview;
  }

  if (name === "reload") {
    const tab = current(session);
    const url = String((payload && payload.url) || tab.url || "");
    if (url.startsWith("azbrowser://")) {
      const rec = await appendReceipt(session, "reload", { url });
      return { ok: true, action: "reload", tab, receipt: rec, session_id: session.id, display: displayOf("Reload", "Home shell reloaded.", [["receipt", rec.hash.slice(0, 16)]]) };
    }
    return dispatch("navigate", { url, fetch: payload && payload.fetch, session_id: session.id }, session.id);
  }

  if (name === "back" || name === "forward") {
    const tab = current(session);
    let ok = true;
    let error = "";
    if (name === "back") {
      if (tab.index <= 0) {
        ok = false;
        error = "no_back";
      } else {
        tab.index -= 1;
        tab.url = tab.history[tab.index];
      }
    } else if (tab.index >= tab.history.length - 1) {
      ok = false;
      error = "no_forward";
    } else {
      tab.index += 1;
      tab.url = tab.history[tab.index];
    }
    const rec = await appendReceipt(session, name, { ok, url: tab.url });
    return { ok, error: error || undefined, tab, receipt: rec, session_id: session.id, display: displayOf(name, "Tab history.", [["ok", ok], ["receipt", rec.hash.slice(0, 16)]]) };
  }

  if (name === "home") {
    pushTab(session, "azbrowser://newtab", "Home", "newtab");
    const rec = await appendReceipt(session, "home", { url: "azbrowser://newtab" });
    return { ok: true, action: "home", sigil: SIGIL, tab: current(session), receipt: rec, session_id: session.id, display: displayOf("Home", "Everblooming sigil home.", [["sigil", SIGIL], ["receipt", rec.hash.slice(0, 16)]]), limitation: LIMITATION };
  }

  if (name === "tab_new") {
    const tab = newTab((payload && payload.title) || "New Tab");
    session.tabs[tab.id] = tab;
    session.active = tab.id;
    const rec = await appendReceipt(session, "tab_new", { tab_id: tab.id });
    return { ok: true, tab, active: session.active, receipt: rec, session_id: session.id, display: displayOf("New tab", "Isolated tab UX.", [["id", tab.id], ["receipt", rec.hash.slice(0, 16)]]) };
  }

  if (name === "tab_close") {
    const tabId = (payload && payload.tab_id) || session.active;
    const ids = Object.keys(session.tabs);
    let ok = true;
    let error;
    if (!session.tabs[tabId]) {
      ok = false;
      error = "unknown_tab";
    } else if (ids.length === 1) {
      ok = false;
      error = "last_tab";
    } else {
      delete session.tabs[tabId];
      if (session.active === tabId) session.active = Object.keys(session.tabs)[0];
    }
    const rec = await appendReceipt(session, "tab_close", { ok });
    return { ok, error, active: session.active, tabs: Object.values(session.tabs), receipt: rec, session_id: session.id, display: displayOf("Close tab", "Tab closed or refused.", [["ok", ok], ["receipt", rec.hash.slice(0, 16)]]) };
  }

  if (name === "tab_switch") {
    const tabId = (payload && payload.tab_id) || "";
    const ok = !!session.tabs[tabId];
    if (ok) session.active = tabId;
    const rec = await appendReceipt(session, "tab_switch", { ok, tab_id: tabId });
    return { ok, error: ok ? undefined : "unknown_tab", tab: session.tabs[session.active], active: session.active, receipt: rec, session_id: session.id, display: displayOf("Switch tab", "Active tab changed.", [["ok", ok], ["receipt", rec.hash.slice(0, 16)]]) };
  }

  if (name === "tab_list") {
    const tabs = Object.values(session.tabs);
    const rec = await appendReceipt(session, "tab_list", { count: tabs.length });
    return { ok: true, active: session.active, tabs, receipt: rec, session_id: session.id, display: displayOf("Tabs", tabs.length + " open.", [["active", session.active], ["receipt", rec.hash.slice(0, 16)]]) };
  }

  if (name === "ethical_search") {
    const q = String((payload && (payload.q || payload.query || payload.url)) || "").trim();
    if (!q) return { ok: false, error: "q required", limitation: LIMITATION, session_id: session.id };
    const locked = await requirePair();
    if (locked) return locked;
    const blocked = await refuse(q);
    if (blocked) return blocked;
    const out = ethicalSearch(q, (payload && payload.limit) || 8);
    const rec = await appendReceipt(session, "ethical_search", { q, ok: out.ok, n: (out.results || []).length });
    out.receipt = rec;
    out.session_id = session.id;
    out.limitation = LIMITATION;
    out.display = displayOf("Lamb Lens", out.label || "Ethical search.", [["query", q], ["results", (out.results || []).length], ["receipt", rec.hash.slice(0, 16)]]);
    return out;
  }

  if (name === "airlock") {
    const locked = await requirePair();
    if (locked) return locked;
    const url = String((payload && payload.url) || "");
    const content = payload && payload.content;
    const filename = String((payload && payload.filename) || "");
    const blocked = await refuse([url, filename, String(content || "").slice(0, 200)].join(" "));
    if (blocked) return blocked;
    const out = await runAirlock({ url, content, filename, fetchLive: !!(payload && payload.fetch) });
    const rec = await appendReceipt(session, "airlock", { url, ok: out.ok, hash: out.content_hash || "", verdict: (out.scan || {}).verdict });
    out.receipt = rec;
    out.session_id = session.id;
    out.limitation = LIMITATION;
    const hashes = (out.stages || []).map((s) => String(s.hash || "").slice(0, 12));
    out.display = displayOf("Airlock", "download → scan → scrub → verify → vault", [["ok", out.ok], ["stages", hashes.join(" ")], ["receipt", rec.hash.slice(0, 16)]]);
    return out;
  }

  if (name === "airlock_status") {
    const rec = await appendReceipt(session, "airlock_status", { pipeline: STAGES });
    return { ok: true, pipeline: STAGES, receipt: rec, session_id: session.id, display: displayOf("Airlock status", "Five stages.", [["pipeline", STAGES.join(" → ")]]), limitation: LIMITATION };
  }

  if (name === "receipt") {
    const rec = await appendReceipt(session, String((payload && payload.action) || "note"), (payload && payload.payload) || { note: (payload && payload.note) || "manual" });
    return { ok: true, receipt: rec, session_id: session.id, display: displayOf("Receipt", "Appended.", [["hash", rec.hash]]), limitation: LIMITATION };
  }

  if (name === "receipts") {
    const limit = Math.max(1, Math.min((payload && payload.limit) || 64, 64));
    const rows = session.receipts.slice(-limit);
    return { ok: true, count: session.receipts.length, tip: session.receipts.length ? session.receipts[session.receipts.length - 1].hash : ZERO, receipts: rows, session_id: session.id, display: displayOf("Receipts", session.receipts.length + " append-only.", [["tip", (session.receipts.length ? session.receipts[session.receipts.length - 1].hash : ZERO).slice(0, 16)]]), limitation: LIMITATION };
  }

  if (name === "receipt_verify") {
    let prev = ZERO;
    let ok = true;
    let broken_at = null;
    for (let i = 0; i < session.receipts.length; i++) {
      const row = session.receipts[i];
      const expected = await sha256Hex(`${i + 1}|${prev}|${row.action}|${row.payload_hash}|${row.ts}`);
      if (row.seq !== i + 1 || row.prev !== prev || row.hash !== expected) {
        ok = false;
        broken_at = i + 1;
        break;
      }
      prev = row.hash;
    }
    return { ok, broken_at, count: session.receipts.length, tip: prev, session_id: session.id, display: displayOf("Verify receipts", "Chain walk.", [["ok", ok], ["count", session.receipts.length]]), limitation: LIMITATION };
  }

  if (name === "scrub") {
    const locked = await requirePair();
    if (locked) return locked;
    const out = scrubHtml(String((payload && (payload.html || payload.text)) || ""));
    const rec = await appendReceipt(session, "scrub", { kinds: out.stripped_kinds });
    return { ok: true, ...out, receipt: rec, session_id: session.id, limitation: LIMITATION, display: displayOf("Scrub", "Scripts/embeds stripped.", [["kinds", (out.stripped_kinds || []).join(",")]]) };
  }

  if (name === "ethics_gate") {
    const q = String((payload && (payload.q || payload.text || payload.url)) || "");
    const ethics = classifyQuery(q);
    const rec = await appendReceipt(session, "ethics_gate", { refuse: ethics.refuse, reasons: ethics.reasons });
    return { ok: true, ethics, receipt: rec, session_id: session.id, display: displayOf("Ethics gate", "Advisory Lamb Lens.", [["refuse", ethics.refuse], ["reasons", ethics.reasons.join(",")]]), limitation: LIMITATION };
  }

  return { ok: false, error: "unhandled", op: name, session_id: session.id };
}

export const SKILL_MD = `---
name: AZBrowser
description: >-
  Use when researching through AZBrowser — navigate preview, Lamb Lens
  ethical search, receipted airlock, tabs, AZNet side-net viewer.
  Pairing with sibling AZNet is required. Phase 1 research shell, not
  Chromium. Author Aziel Eliab.
---

# AZBrowser

Secure research browser / hardened investigation platform (Phase 1).
AZNet is a **sibling side-net** (https://github.com/AzielEliab/aznet).
AZBrowser **views** it and **requires pairing** to run. FragGate unlocks;
StaticClock times. AZNet branding here is the sidenet viewer — not a
second whitepaper fork.

Author: **Aziel Eliab** only.

**THIS IS:** browser-chrome UX + controlled fetch/proxy preview +
receipted airlock (\`download → scan → scrub → verify → vault\`) +
Lamb Lens ethical search + AZNet side-net viewer + append-only
integrity receipts.

**THIS IS NOT:** Chromium, Firefox, Safari, or Edge. Not AZ-OS, Lumen,
or AZInterface. Not an AZNet protocol implementation. AZMail is a
**sibling** (https://github.com/AzielEliab/azmail). AZNet is a
**sibling** (https://github.com/AzielEliab/aznet).

Always send \`User-Agent: Mozilla/5.0\`.

**Agent path is FragGate only.** MCP / agents call aziel-runtime — not a
separate browser MCP brand.

\`POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call\`
body \`{"slug":"azbrowser","op":"<op>","payload":{}}\`

Same door as MCP \`fraggate_call\` (\`slug=azbrowser\`). Kernel:
https://github.com/AzielEliab/fraggate. Catalog listing lands in a
sibling aziel-runtime PR. Human chrome uses this Worker \`/v1/{op}\`.
\`GET|POST /mcp\` here is a pointer, not a second MCP.

**Human UI stays on this Worker.** AI path is FragGate + this OpenAPI.

Research ops (\`navigate\`, \`ethical_search\`, \`airlock\`, \`scrub\`)
return \`PAIR_REQUIRED\` until AZNet pair-status is true **and** FragGate
unlocks via StaticClock. Pair/viewer ops stay open so the gate works.

## Ops (UI action = MCP / FragGate op)

| UI chrome | op |
|-----------|-----|
| Address Go / preview | \`navigate\` / \`preview\` |
| Lamb Lens search | \`ethical_search\` / \`lamb_lens\` / \`search\` |
| Side-net viewer | \`sidenet_view\` |
| Pair status | \`pair_status\` |
| Back / Forward / Reload | \`back\` \`forward\` \`reload\` |
| Home (everblooming sigil) | \`home\` |
| New / close / switch tab | \`tab_new\` \`tab_close\` \`tab_switch\` \`tab_list\` |
| Airlock panel | \`airlock\` \`airlock_status\` |
| Receipts list | \`receipts\` \`receipt\` \`receipt_verify\` |
| Ethics gate | \`ethics_gate\` |
| HTML scrub | \`scrub\` |
| Liveness / skill | \`health\` \`skill\` |

No receipt = no action. Every mutating op appends a hash-chained receipt.

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude
(Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot /
Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence
surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other
MCP/OpenAPI-capable assistants — **through FragGate only**.

Agents display \`display.title\`, \`display.summary\`, and
\`display.fields\` in chat, then take the next input. No technical MCP
UI is required for the human.

## How to call

\`\`\`bash
curl -s -A 'Mozilla/5.0' -X POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call \\
  -H 'content-type: application/json' \\
  -d '{"slug":"azbrowser","op":"pair_status","payload":{}}'
curl -s -A 'Mozilla/5.0' -X POST https://azbrowser-download-tracker.vibelock.workers.dev/v1/sidenet_view \\
  -H 'content-type: application/json' \\
  -d '{}'
curl -s -A 'Mozilla/5.0' https://aziel-runtime.vibelock.workers.dev/v1/fraggate/list
\`\`\`

Apache-2.0. Forks are welcome and always allowed.
`;
