/**
 * Local-first edge mesh plane for the Worker chrome.
 * Same gates as the Python shell. This Worker does not dial 127.0.0.1
 * and does not proxy qnsd. Live peer sockets stay on the local shell.
 * .aziel is not an ICANN TLD. Ordinary browsers do not resolve it.
 * Author: Aziel Eliab only.
 */

export const MESH_SPEC = "FED-MESH-BROWSER-1.0";
export const REFUSE = "FG-GATE-REFUSE";
export const CAP7_ALLOWLIST = ["azgrid.az", "azcloak.az", "azvault.az", "azshift.az"];
export const AZ_STAR_ALLOWLIST = ["az.azieleliab.az", "az.godlock.az", "az.azielcorpuslibrary.az", "az.hedidntjump.az"];
export const CAP7_FALSE_SITES = ["azbooth.az", "azflag.az", "azstandby.az"];
const SECRET = new Set([
  "private_key", "privatekey", "secret_key", "secretkey", "signing_key", "signingkey",
  "seed", "priv", "privkey", "ed25519_secret", "sk", "secret",
]);
const HANDLE = /^[a-z0-9](?:[a-z0-9._-]{0,62}[a-z0-9])?$/;

let ledger = [];

export function setMeshLedger(records) {
  ledger = (records || []).filter((row) => row && !containsSecret(row));
}

export function allowlist() {
  return new Set([...CAP7_ALLOWLIST, ...AZ_STAR_ALLOWLIST]);
}

export function canonical(obj) {
  if (obj === null || typeof obj !== "object") return JSON.stringify(obj);
  if (Array.isArray(obj)) return "[" + obj.map((item) => canonical(item)).join(",") + "]";
  const keys = Object.keys(obj).sort();
  return "{" + keys.map((key) => JSON.stringify(key) + ":" + canonical(obj[key])).join(",") + "}";
}

export async function sha256Hex(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(String(text)));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

export async function sha256Bytes(bytes) {
  const buf = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function containsSecret(obj) {
  if (!obj || typeof obj !== "object") return false;
  if (Array.isArray(obj)) return obj.some((item) => containsSecret(item));
  for (const [key, value] of Object.entries(obj)) {
    if (SECRET.has(String(key).toLowerCase().replace(/-/g, "_"))) return true;
    if (containsSecret(value)) return true;
  }
  return false;
}

function hexToBytes(hex) {
  const text = String(hex || "");
  if (text.length % 2) return null;
  const out = new Uint8Array(text.length / 2);
  for (let i = 0; i < out.length; i++) {
    const byte = Number.parseInt(text.slice(i * 2, i * 2 + 2), 16);
    if (Number.isNaN(byte)) return null;
    out[i] = byte;
  }
  return out;
}

export async function verifyHandle(publicKeyHex, message, signatureHex) {
  const raw = hexToBytes(publicKeyHex);
  const sig = hexToBytes(signatureHex);
  if (!raw || !sig || raw.length !== 32 || sig.length !== 64) return false;
  try {
    const key = await crypto.subtle.importKey("raw", raw, { name: "Ed25519" }, false, ["verify"]);
    return await crypto.subtle.verify({ name: "Ed25519" }, key, sig, new TextEncoder().encode(message));
  } catch {
    return false;
  }
}

export async function engineDigestFor(ref) {
  const body = {};
  for (const [key, value] of Object.entries(ref || {})) {
    if (key !== "engine_digest") body[key] = value;
  }
  return sha256Hex(canonical(body));
}

export function classifyDestination(raw) {
  const text = String(raw || "").trim();
  if (!text) return { ok: false, plane: "search", error: "url required", url: "" };
  if (/\s/.test(text)) return { ok: false, plane: "search", error: "not_a_url", url: text, suggest_search: true };
  let input = text;
  if (!input.includes("://")) input = "https://" + input;
  let parsed;
  try {
    parsed = new URL(input);
  } catch {
    return { ok: false, plane: "search", error: "not_a_url", url: text, suggest_search: true };
  }
  const scheme = parsed.protocol.replace(":", "").toLowerCase();
  if (["javascript", "data", "file", "vbscript"].includes(scheme)) {
    return { ok: false, plane: "dns", error: "blocked_scheme", scheme, url: text };
  }
  if (scheme === "aziel") {
    const handle = parsed.hostname.toLowerCase();
    if (!HANDLE.test(handle)) return refuseName(text, "bad_handle");
    return mesh(handle + ".aziel", handle, parsed.pathname || "/", text, false);
  }
  if (scheme === "azbrowser" && ["local", "app"].includes(parsed.hostname.toLowerCase())) {
    const slug = (parsed.pathname || "/").replace(/^\/+|\/+$/g, "") || "app";
    return local(slug, "azbrowser", text);
  }
  const host = parsed.hostname.toLowerCase().replace(/\.$/, "");
  const port = parsed.port ? Number(parsed.port) : null;
  if ((host === "127.0.0.1" || host === "localhost") && (port === 8891 || port === 8787)) {
    const parts = parsed.pathname.split("/").filter(Boolean);
    return local(parts[parts.length - 1] || "app", port === 8891 ? "qnm" : "fraggate", text, port, parsed.pathname || "/");
  }
  if (host.endsWith(".aziel")) {
    const labels = host.split(".");
    const handle = labels[labels.length - 2] || "";
    if (!labels.slice(0, -1).every((part) => HANDLE.test(part))) return refuseName(text, "bad_handle");
    return mesh(host, handle, parsed.pathname || "/", text, false);
  }
  if (host.endsWith(".az")) {
    const listed = allowlist().has(host) && !CAP7_FALSE_SITES.includes(host);
    if (listed) {
      const labels = host.split(".");
      const handle = labels.length >= 3 && labels[0] === "az" ? labels[1] : labels[0];
      return mesh(host, handle, parsed.pathname || "/", text, true);
    }
    return dns(host, port, parsed.pathname || "/", parsed.search, ".az is Azerbaijan's country domain. This host is not on the Cap-7 / AZ.* allowlist, so it uses normal DNS and standard TLS.");
  }
  if (scheme !== "https" && scheme !== "http") return { ok: false, plane: "dns", error: "https_only", scheme, url: text };
  return dns(host, port, parsed.pathname || "/", parsed.search, "");
}

function dns(host, port, path, search, note) {
  const suffix = port && port !== 443 && port !== 80 ? ":" + port : "";
  const pathname = path.startsWith("/") ? path : "/" + path;
  return {
    ok: true,
    plane: "dns",
    url: "https://" + host + suffix + pathname + (search || ""),
    host,
    path: pathname,
    dns: true,
    tls: "standard",
    icann: true,
    allowlisted: false,
    regular_browsers_resolve_aziel: false,
    note: note || "Normal DNS and standard TLS.",
  };
}

function mesh(name, handle, path, raw, allowlisted) {
  const pathname = path.startsWith("/") ? path : "/" + path;
  return {
    ok: true,
    plane: "mesh",
    name,
    handle,
    path: pathname,
    url: "aziel://" + handle + pathname,
    display_url: name + (pathname === "/" ? "" : pathname),
    raw,
    dns: false,
    tls: "handle-key",
    ca: false,
    icann: false,
    allowlisted,
    regular_browsers_resolve_aziel: false,
    keys_leave_node: false,
  };
}

function local(slug, source, raw, port, path) {
  const safe = String(slug || "app").toLowerCase().replace(/[^a-z0-9._-]/g, "") || "app";
  return {
    ok: true,
    plane: "local",
    slug: safe,
    source,
    port: port || null,
    path: path || "/",
    origin: "azbrowser://local/" + safe,
    url: "azbrowser://local/" + safe,
    display_url: "azbrowser://local/" + safe,
    raw,
    dns: false,
    icann: false,
    data_stays_local: true,
    keys_leave_node: false,
  };
}

function refuseName(raw, reason) {
  return {
    ok: false,
    plane: "mesh",
    code: REFUSE,
    reason,
    url: raw,
    icann: false,
    regular_browsers_resolve_aziel: false,
    keys_leave_node: false,
  };
}

function lookup(name, handle) {
  const nameL = String(name || "").toLowerCase();
  const handleL = String(handle || "").toLowerCase();
  if (nameL) {
    const found = ledger.find((row) => String(row.name || "").toLowerCase() === nameL);
    if (found) return found;
  }
  if (!nameL && handleL) {
    return ledger.find((row) => String(row.name || "").toLowerCase() === handleL + ".aziel")
      || ledger.find((row) => String(row.handle || "").toLowerCase() === handleL)
      || null;
  }
  return null;
}

function objectsOf(record) {
  const raw = record.objects || {};
  const out = {};
  for (const [key, value] of Object.entries(raw)) {
    if (typeof value === "string") out[key] = new TextEncoder().encode(value);
  }
  return out;
}

export async function verifyRecord(record) {
  if (!record || containsSecret(record)) return { ok: false, code: REFUSE, reason: "keys_must_stay_on_node" };
  const ref = record.ref;
  if (!ref || typeof ref !== "object") return { ok: false, code: REFUSE, reason: "bad_handle_signature" };
  if (String(record.handle || "") !== String(ref.handle || "")) return { ok: false, code: REFUSE, reason: "bad_handle_signature" };
  if (String(record.name || "") !== String(ref.name || "")) return { ok: false, code: REFUSE, reason: "bad_handle_signature" };
  if (String(record.public_key || "") !== String(ref.public_key || "")) return { ok: false, code: REFUSE, reason: "bad_handle_signature" };
  const expect = await engineDigestFor(ref);
  if (String(ref.engine_digest || "") !== expect) return { ok: false, code: REFUSE, reason: "engine_digest_mismatch" };
  const ok = await verifyHandle(record.public_key, canonical(ref), record.signature);
  if (!ok) return { ok: false, code: REFUSE, reason: "bad_handle_signature" };
  return { ok: true, engine_digest: expect };
}

export async function gateBytes(record, pageBytes, objects) {
  const checked = await verifyRecord(record);
  if (!checked.ok) return checked;
  const pageHash = await sha256Bytes(pageBytes);
  if (pageHash !== String(record.ref.object || "")) return { ok: false, code: REFUSE, reason: "hash_mismatch" };
  const modules = Array.isArray(record.ref.modules) ? record.ref.modules : [];
  const byPath = new Map(modules.map((item) => [String(item.path || ""), item]));
  const byHash = new Map(modules.map((item) => [String(item.hash || ""), item]));
  const text = new TextDecoder("utf-8", { fatal: false }).decode(pageBytes);
  const srcs = [...text.matchAll(/<script\b[^>]*\bsrc\s*=\s*['"]([^'"]+)['"][^>]*>/gi)].map((m) => m[1]);
  for (const src of srcs) {
    const item = byPath.get(src);
    if (!item || item.signed !== true) return { ok: false, code: REFUSE, reason: "unsigned_module" };
    const blob = objects[String(item.hash || "")];
    if (!blob || (await sha256Bytes(blob)) !== String(item.hash || "")) return { ok: false, code: REFUSE, reason: "hash_mismatch" };
  }
  const inlines = [...text.matchAll(/<script\b(?![^>]*\bsrc\s*=)[^>]*>([\s\S]*?)<\/script\s*>/gi)].map((m) => m[1].trim()).filter(Boolean);
  for (const inline of inlines) {
    const digest = await sha256Hex(inline);
    const item = byHash.get(digest);
    if (!item || item.signed !== true) return { ok: false, code: REFUSE, reason: "unsigned_module" };
    const blob = objects[digest];
    if (!blob || (await sha256Bytes(blob)) !== digest) return { ok: false, code: REFUSE, reason: "hash_mismatch" };
  }
  for (const item of modules) {
    if (item.signed !== true) return { ok: false, code: REFUSE, reason: "unsigned_module" };
    const blob = objects[String(item.hash || "")];
    if (blob && (await sha256Bytes(blob)) !== String(item.hash || "")) return { ok: false, code: REFUSE, reason: "hash_mismatch" };
  }
  return { ok: true, content_hash: pageHash, engine_digest: checked.engine_digest };
}

function blocked(reason, classified) {
  return {
    ok: false,
    code: REFUSE,
    reason,
    plane: classified.plane || "mesh",
    owner_handle: classified.handle || "",
    verified_owner: false,
    url: classified.display_url || classified.url || "",
    display_url: classified.display_url || classified.url || "",
    icann: false,
    ca: false,
    allowlisted: !!classified.allowlisted,
    regular_browsers_resolve_aziel: false,
    keys_leave_node: false,
    spec: MESH_SPEC,
    html: "",
    scripts_executed: false,
    qnsd_public_proxy: false,
    socket: false,
  };
}

export async function openMesh(classified) {
  if (!classified.ok) return blocked(classified.reason || "bad_handle", classified);
  const record = lookup(classified.name, "");
  if (!record) return blocked("name_not_in_ledger", classified);
  if (containsSecret(record)) return blocked("keys_must_stay_on_node", classified);
  const objects = objectsOf(record);
  const page = objects[String(record.ref && record.ref.object)];
  if (!page) return blocked("object_missing", classified);
  const gated = await gateBytes(record, page, objects);
  if (!gated.ok) return blocked(gated.reason, classified);
  const hint = record.connect || {};
  const mode = ["direct", "lan", "relay"].includes(hint.mode) ? hint.mode : "direct";
  const text = new TextDecoder("utf-8", { fatal: false }).decode(page);
  return {
    ok: true,
    action: "navigate",
    plane: "mesh",
    spec: MESH_SPEC,
    name: record.name,
    url: classified.url,
    display_url: classified.display_url,
    host: record.name,
    owner_handle: record.handle,
    verified_owner: true,
    public_key: record.public_key,
    identity: "handle-key",
    ca: false,
    icann: false,
    allowlisted: !!classified.allowlisted,
    regular_browsers_resolve_aziel: false,
    keys_leave_node: false,
    content_hash: gated.content_hash,
    engine_digest: gated.engine_digest,
    hash_ok: true,
    signature_ok: true,
    connect: {
      mode,
      peer: hint.peer || record.handle,
      relay: mode === "relay" ? hint.relay || null : null,
      resolved: true,
      connected: false,
      socket: false,
      via: "worker-ledger",
      keys_leave_node: false,
      qnsd_public_proxy: false,
      note: "Worker verified the handle key and content hash. It did not open a peer socket. Live direct / LAN / relay connect is the local shell to qnm-node.",
    },
    sandbox: { network: false, cross_origin: false, storage: "origin", file: false, tracker_detection: false },
    origin: "aziel://" + record.handle,
    title: record.name,
    html: text.slice(0, 80000),
    scripts_executed: false,
    renderer: "mesh-hash-gate",
    not_chromium: true,
    bytes_from: "worker-ledger",
    note: "Mesh site. Handle key, not a certificate authority. .aziel is not registered with ICANN. Ordinary browsers do not resolve .aziel names. This Worker does not dial the local node.",
  };
}

export function originOf(target) {
  const text = String(target || "").trim();
  if (!text.includes("://")) return text.replace(/\/$/, "");
  try {
    const parsed = new URL(text);
    if (parsed.protocol === "aziel:" || parsed.protocol === "azbrowser:") return parsed.protocol + "//" + parsed.host;
    return parsed.protocol + "//" + parsed.host;
  } catch {
    return text.replace(/\/$/, "");
  }
}

export function capabilityDecision(grants, origin, kind, target) {
  const map = { network: "network", net: "network", fetch: "fetch", cross_origin: "fetch", storage: "storage", file: "file" };
  const norm = map[String(kind || "").toLowerCase()] || "";
  const originN = originOf(origin);
  const targetS = String(target || "").trim();
  if (!norm || !originN || !targetS) return { ok: false, code: REFUSE, reason: "bad_grant" };
  const targetOrigin = originOf(targetS);
  if (norm === "storage" && originN === targetOrigin) return { ok: true, allowed: true, origin: originN, kind: "storage" };
  if (norm === "storage") return { ok: false, code: REFUSE, reason: "storage_outside_origin", origin: originN, kind: norm, target: targetS };
  if (norm === "fetch" && originN === targetOrigin) return { ok: true, allowed: true, origin: originN, kind: "fetch" };
  const grant = (grants || []).find((row) => {
    if (row.origin !== originN || row.capability !== norm) return false;
    const resource = row.resource;
    return resource === targetS || resource === targetOrigin || resource === "*" || targetS.startsWith(String(resource).replace(/\/$/, "") + "/") || targetS === String(resource).replace(/\/$/, "");
  });
  if (norm === "fetch" && !grant) return { ok: false, code: REFUSE, reason: "cross_origin_not_granted", origin: originN, kind: norm, target: targetS };
  if (norm === "file" && !grant) return { ok: false, code: REFUSE, reason: "file_not_granted", origin: originN, kind: norm, target: targetS };
  if (norm === "network" && originN !== targetOrigin && !grant) {
    return { ok: false, code: REFUSE, reason: "network_not_granted", origin: originN, kind: norm, target: targetS };
  }
  if (norm === "network" && originN === targetOrigin) return { ok: true, allowed: true, origin: originN, kind: "network" };
  if (!grant) return { ok: false, code: REFUSE, reason: "network_not_granted", origin: originN, kind: norm, target: targetS };
  return { ok: true, allowed: true, origin: originN, kind: norm, target: targetS, grant };
}
