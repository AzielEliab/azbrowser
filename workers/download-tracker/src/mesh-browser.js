/**
 * Local-first edge mesh plane for the Worker chrome.
 * Same gates as the Python shell. This Worker does not dial 127.0.0.1
 * and does not proxy qnsd. Live peer sockets stay on the local shell.
 * .aziel is not an ICANN TLD. Ordinary browsers do not resolve it.
 * Author: Aziel Eliab only.
 */

import { clarify } from "./lens.js";

export const MESH_SPEC = "FED-MESH-BROWSER-1.0";
export const REFUSE = "FG-GATE-REFUSE";
export const NAME_MIN_AGE_SECONDS = 72 * 3600;
export const NAME_MIN_WITNESSES = 2;
export const CAP7_ALLOWLIST = ["azgrid.az", "azcloak.az", "azvault.az", "azshift.az"];
export const AZ_STAR_ALLOWLIST = ["az.azieleliab.az", "az.godlock.az", "az.azielcorpuslibrary.az", "az.hedidntjump.az"];
export const CAP7_FALSE_SITES = ["azbooth.az", "azflag.az", "azstandby.az"];
const SECRET = new Set([
  "private_key", "privatekey", "secret_key", "secretkey", "signing_key", "signingkey",
  "seed", "priv", "privkey", "ed25519_secret", "sk", "secret",
]);
const HANDLE = /^[a-z0-9](?:[a-z0-9._-]{0,62}[a-z0-9])?$/;

let ledger = [];
let indexBuilt = false;
const equivocations = new Set();
const maxSeq = new Map();
const digestAt = new Map();
const seenSeq = new Map();

export function setMeshLedger(records) {
  ledger = (records || []).filter((row) => row && !containsSecret(row));
  indexBuilt = false;
  equivocations.clear();
  maxSeq.clear();
  digestAt.clear();
  seenSeq.clear();
}

export function meshRecords() {
  return ledger.slice();
}

export function meshEquivocating(handle) {
  return equivocations.has(String(handle || "").toLowerCase());
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

export function witnessMessage(record, witnessHandle) {
  const ref = (record && record.ref) || {};
  const seq = Number.isInteger(ref.seq) ? ref.seq : 0;
  return {
    claimed_at: String(record.claimed_at || ""),
    engine_digest: String(ref.engine_digest || ""),
    handle: String(ref.handle || ""),
    name: String(ref.name || ""),
    object: String(ref.object || ""),
    seq,
    witness: String(witnessHandle),
  };
}

export function vouchMessage(ownerHandle, vouchHandle) {
  return { handle: String(ownerHandle), vouch: String(vouchHandle) };
}

function noteVerified(record) {
  const ref = record.ref || {};
  const handle = String(record.handle || "").toLowerCase();
  if (!handle || !Number.isInteger(ref.seq)) return;
  const digest = String(ref.engine_digest || "") + "|" + String(ref.object || "");
  const key = handle + "#" + ref.seq;
  const previous = seenSeq.get(key);
  if (previous != null && previous !== digest) equivocations.add(handle);
  else seenSeq.set(key, digest);
  digestAt.set(key, String(ref.engine_digest || ""));
  maxSeq.set(handle, Math.max(maxSeq.get(handle) ?? ref.seq, ref.seq));
}

function chainCheck(record) {
  const ref = record.ref || {};
  const handle = String(record.handle || "").toLowerCase();
  if (equivocations.has(handle)) return { ok: false, reason: "equivocating_handle" };
  if (!Number.isInteger(ref.seq) || ref.seq < 1) return { ok: false, reason: "bad_prev" };
  const prev = String(ref.prev || "");
  if (ref.seq === 1) {
    if (prev !== "0".repeat(64)) return { ok: false, reason: "bad_prev" };
  } else {
    const parent = digestAt.get(handle + "#" + (ref.seq - 1));
    if (!parent || prev !== parent) return { ok: false, reason: "bad_prev" };
  }
  const known = maxSeq.get(handle) ?? ref.seq;
  if (ref.seq < known) return { ok: false, reason: "rollback" };
  return { ok: true, reason: "" };
}

export async function refreshMeshIndex() {
  await ensureIndex();
}

async function ensureIndex() {
  if (indexBuilt) return;
  for (const row of ledger) {
    const checked = await verifyRecord(row);
    if (checked.ok) noteVerified(row);
  }
  indexBuilt = true;
}

async function verifiedWitnesses(record) {
  const raw = Array.isArray(record.witnesses) ? record.witnesses : [];
  const owner = String(record.handle || "").toLowerCase();
  const found = [];
  for (const item of raw) {
    if (!item || typeof item !== "object") continue;
    const handle = String(item.handle || "").trim().toLowerCase();
    if (!handle || handle === owner || found.includes(handle)) continue;
    const message = witnessMessage(record, handle);
    const digest = await sha256Hex(canonical(message));
    if (String(item.receipt || "") !== digest) continue;
    const ok = await verifyHandle(item.public_key, canonical(message), item.signature);
    if (!ok) continue;
    found.push(handle);
  }
  return found;
}

export async function evaluateName(record, nowMs) {
  const moment = Number.isFinite(nowMs) ? nowMs : Date.now();
  const status = String(record.status || "").trim().toUpperCase();
  const claimed = Date.parse(String(record.claimed_at || ""));
  const age = Number.isNaN(claimed) ? null : Math.floor((moment - claimed) / 1000);
  const witnesses = await verifiedWitnesses(record);
  const aged = age != null && age >= NAME_MIN_AGE_SECONDS;
  const witnessed = witnesses.length >= NAME_MIN_WITNESSES;
  const base = {
    witnesses,
    witness_count: witnesses.length,
    chain_age_seconds: age,
    min_age_seconds: NAME_MIN_AGE_SECONDS,
    min_witnesses: NAME_MIN_WITNESSES,
    status_declared: status,
  };
  if (status === "FINAL" && aged && witnessed) return { ...base, state: "FINAL", reason: "" };
  if (status === "FINAL") return { ...base, state: "REFUSED", reason: "name_not_final" };
  return { ...base, state: "PENDING", reason: "name_pending" };
}

export async function verifiedVouches(record) {
  const raw = Array.isArray(record.vouches) ? record.vouches : [];
  const owner = String(record.handle || "").toLowerCase();
  const found = [];
  for (const item of raw) {
    if (!item) continue;
    const handle = String(item.handle || "").trim().toLowerCase();
    if (!handle || handle === owner || found.includes(handle)) continue;
    const ok = await verifyHandle(item.public_key, canonical(vouchMessage(owner, handle)), item.signature);
    if (!ok) continue;
    found.push(handle);
  }
  return found;
}

function meshVerdict(flags) {
  const hard = flags.filter((flag) => flag === "suspicious_magic" || (flag.startsWith("suspicious_extension:") && flag !== "suspicious_extension:.js"));
  if (hard.length) return "quarantine";
  if (flags.length) return "hold";
  return "clean";
}

function advisoryFlags(filename, bytes) {
  const flags = [];
  const lower = String(filename || "").toLowerCase();
  for (const ext of [".exe", ".dll", ".scr", ".js", ".vbs", ".ps1", ".bat", ".cmd", ".apk", ".msi"]) {
    if (lower.endsWith(ext)) flags.push("suspicious_extension:" + ext);
  }
  const text = new TextDecoder("utf-8", { fatal: false }).decode(bytes.slice(0, 4000)).toLowerCase();
  if (text.includes("eval(") || text.includes("<script")) flags.push("script_like");
  if (/powershell|cmd\.exe|wget http/.test(text)) flags.push("shell_lure");
  if (bytes.length >= 2 && bytes[0] === 0x4d && bytes[1] === 0x5a) flags.push("suspicious_magic");
  if (bytes.length >= 4 && bytes[0] === 0x7f && bytes[1] === 0x45 && bytes[2] === 0x4c && bytes[3] === 0x46) flags.push("suspicious_magic");
  return flags;
}

export async function promoteObjects(page, modules, objects, operatorOverride) {
  let flags = advisoryFlags("page.html", page);
  let verdict = meshVerdict(flags);
  const moduleRows = [];
  for (const item of modules || []) {
    const digest = String(item.hash || "");
    const blob = objects[digest];
    if (!blob) continue;
    const path = String(item.path || "module");
    const name = path.split("/").pop() || "module";
    const moduleFlags = advisoryFlags(name, blob);
    const moduleVerdict = meshVerdict(moduleFlags);
    if (moduleVerdict === "quarantine") verdict = "quarantine";
    else if (moduleVerdict === "hold" && verdict === "clean") verdict = "hold";
    flags = flags.concat(moduleFlags);
    moduleRows.push({ path, hash: digest, quarantined: true, verdict: moduleVerdict, body_included: false });
  }
  let promoted = false;
  let reason = "";
  if (verdict === "quarantine") reason = "airlock_quarantine";
  else if (operatorOverride === true) promoted = true;
  else reason = "scanner_absent";
  return {
    scanner: "absent",
    scanner_version: null,
    clamav: false,
    yara: false,
    advisory: true,
    verdict,
    flags,
    content_hash: await sha256Bytes(page),
    operator_override: operatorOverride === true,
    promoted,
    scripts_executed: false,
    executed: false,
    modules: moduleRows,
    reason,
    pipeline: ["download", "scan", "scrub", "verify", "vault"],
  };
}

export async function localTrust({ handle, record, equivocating, hashMatches, peerBlocked, islandMode }) {
  const status = record ? await evaluateName(record) : null;
  let beats = 0;
  let vouches = [];
  if (record) {
    if (Array.isArray(record.heartbeats)) {
      const seen = [];
      for (const item of record.heartbeats) {
        const who = String((item && item.handle) || "").trim().toLowerCase();
        if (who && !seen.includes(who)) seen.push(who);
      }
      beats = seen.length;
    } else if (status) beats = status.witness_count;
    vouches = await verifiedVouches(record);
  }
  return {
    ok: true,
    local_only: true,
    public_ranking: false,
    handle,
    name_status: status ? status.state : null,
    chain_age_seconds: status ? status.chain_age_seconds : null,
    heartbeats_witnessed: beats,
    hash_matches: Number(hashMatches || 0),
    vouches,
    equivocating: !!equivocating,
    peer_blocked: !!peerBlocked,
    island_mode: !!islandMode,
    network_wide: false,
    spec_note: "Local trust view. Relays, proof-of-work, and witness gossip are not decided here. This node does not publish a ranking.",
  };
}

function isolationFor(handle) {
  const who = String(handle || "").toLowerCase();
  if (!who) return null;
  for (const row of ledger) {
    if (String(row.handle || "").toLowerCase() !== who) continue;
    const isolation = row.isolation;
    if (isolation && String(isolation.state || "").toUpperCase() === "ISOLATED") return isolation;
  }
  return null;
}

function policyPage(handle, isolation) {
  const row = isolation || {};
  const esc = (value) => String(value == null ? "" : value)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  const reason = String(row.reason || "unspecified");
  const check = String(row.check || "unspecified");
  const evidence = String(row.evidence_hash || "");
  return `<article class="policy-page">
<h1>This handle is isolated</h1>
<p>Handle <strong>${esc(handle)}</strong> is isolated from the mesh. Its pages are not shown. This browser will not resolve its names or show its objects.</p>
<p>What you can do next: go back, or open a different site. If this is your handle, you can file a signed appeal to ask for a re-check.</p>
<p>Isolation does not delete data on this machine. This browser does not store or forward the reported content, and it does not decide the appeal.</p>
<details>
<summary>Details</summary>
<p>FG-GATE-REFUSE · handle_isolated</p>
<dl>
<dt>Reason code</dt><dd>${esc(reason)}</dd>
<dt>Check</dt><dd>${esc(check)}</dd>
<dt>Evidence</dt><dd>${esc(evidence) || "none recorded"}</dd>
</dl>
<p>The evidence field is a hash only. Relays that follow the policy refuse to relay or witness this handle. The local runtime can keep running.</p>
<p>Name checks, and the hosting node's local image and text checks, can miss and can false-positive. This page does not claim those checks catch everything. If a classifier is absent on the hosting node, publish stays blocked there. This browser does not run those classifiers.</p>
<p>Operators must follow the law in their jurisdiction, including US reporting of child sexual abuse material to NCMEC where that duty applies. This browser does not keep that material as evidence.</p>
</details>
</article>`;
}

export function designRemotePage() {
  return `<article class="policy-page">
<h1>Design mode stays on the hosting node</h1>
<p>FG-GATE-REFUSE · design_mode_local_only</p>
<p>This chrome is not the hosting node. Design mode is bound to localhost on the machine that holds the handle key. Remote access is refused. Nothing was published.</p>
<p>What you can do next: open AZBrowser on that machine. This page does not publish.</p>
</article>`;
}

export const RESERVED_SLOTS = [
  { id: "ae", label: "AZ.AzielEliab.AZ", host: "az.azieleliab.az", user_nameable: false, role: "hub-mirror" },
  { id: "corpus", label: "AZ.AzielCorpusLibrary.AZ", host: "az.azielcorpuslibrary.az", user_nameable: false, role: "hub-mirror" },
  { id: "godlock", label: "AZ.Godlock.AZ", host: "az.godlock.az", user_nameable: false, role: "hub-mirror" },
  { id: "hdj", label: "AZ.HeDidntJump.AZ", host: "az.hedidntjump.az", user_nameable: false, role: "hub-mirror" },
];

function userSlotIndex(value) {
  if (typeof value === "boolean") return null;
  if (Number.isInteger(value) && value >= 1 && value <= 3) return value - 1;
  const text = String(value || "").trim().toLowerCase();
  if (["1", "2", "3", "user-1", "user-2", "user-3"].includes(text)) return Number(text.slice(-1)) - 1;
  return null;
}

export function slotsFor(records, handle) {
  const who = String(handle || "").trim().toLowerCase();
  const user = [1, 2, 3].map((n) => ({ id: "user-" + n, name: null, status: "empty", user_nameable: true, conflict: false }));
  for (const record of records || []) {
    if (!record) continue;
    if (who && String(record.handle || "").trim().toLowerCase() !== who) continue;
    const index = userSlotIndex(record.slot);
    if (index == null) continue;
    const name = String(record.name || "") || null;
    const status = String(record.status || "PENDING").toUpperCase() || "PENDING";
    if (user[index].name && user[index].name !== name) {
      user[index].conflict = true;
      continue;
    }
    user[index].name = name;
    user[index].status = status;
  }
  return {
    ok: true,
    handle: who,
    automatic_name: who ? who + ".aziel" : "",
    reserved: RESERVED_SLOTS.map((row) => ({ ...row })),
    user,
    reserved_count: 4,
    user_count: 3,
    user_nameable_reserved: false,
    miragegrid: {
      separate_layer: true,
      changed: false,
      real: ["azcloak.az", "azgrid.az", "azshift.az", "azvault.az"],
      decoy: ["azbooth.az", "azflag.az", "azstandby.az"],
      note: "MirageGrid global Cap-7 factory names are a separate layer and are unchanged.",
    },
    note: "Four reserved slots mirror the hub names and are not user-nameable. Three user slots are claimed with the existing name rules. The automatic handle name is separate from those three.",
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
    clarity: clarify(reason),
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

function pendingView(classified, record, status) {
  const name = record.name || classified.name || "";
  return {
    ok: true,
    action: "name_pending",
    code: "",
    reason: "name_pending",
    plane: "mesh",
    spec: MESH_SPEC,
    name,
    name_status: "PENDING",
    status_declared: status.status_declared || "",
    url: classified.url,
    display_url: classified.display_url,
    owner_handle: record.handle || classified.handle || "",
    verified_owner: false,
    navigable: false,
    promoted: false,
    quarantine: false,
    html: "",
    scripts_executed: false,
    executed: false,
    icann: false,
    ca: false,
    allowlisted: !!classified.allowlisted,
    regular_browsers_resolve_aziel: false,
    keys_leave_node: false,
    witness_count: status.witness_count || 0,
    chain_age_seconds: status.chain_age_seconds,
    network_wide: false,
    qnsd_public_proxy: false,
    socket: false,
    note: "Pending name " + name + ". Not a verified site. A name stays pending until it has aged and enough independent witnesses exist, and the record says FINAL. Ordinary browsers do not resolve .aziel names.",
  };
}

export async function openMesh(classified, guard = {}) {
  if (!classified.ok) return blocked(classified.reason || "bad_handle", classified);
  const handle = String(classified.handle || "").toLowerCase();
  if (guard.island) {
    return {
      ...blocked("island_mode", classified),
      island_mode: true,
      network_wide: false,
      note: "This node dropped its mesh peers and relays. Local apps and normal DNS still run. No other node was cut off.",
    };
  }
  const blockedSet = guard.blocked instanceof Set ? guard.blocked : new Set(guard.blocked || []);
  if (handle && blockedSet.has(handle)) {
    return {
      ...blocked("peer_blocked", classified),
      peer_blocked: true,
      network_wide: false,
      note: "This handle is blocked on this node only. Other peers stay reachable.",
    };
  }
  await ensureIndex();
  const record = lookup(classified.name, "");
  if (!record) return blocked("name_not_in_ledger", classified);
  if (containsSecret(record)) return blocked("keys_must_stay_on_node", classified);
  const owner = String(record.handle || handle || "");
  const isolation = isolationFor(owner);
  if (isolation) {
    return {
      ...blocked("handle_isolated", classified),
      policy_page: true,
      html: policyPage(owner, isolation),
      isolation: {
        state: "ISOLATED",
        reason: String(isolation.reason || "unspecified"),
        check: String(isolation.check || "unspecified"),
        evidence_hash: String(isolation.evidence_hash || ""),
        content_stored: false,
        content_forwarded: false,
        deletes_local_data: false,
        local_runtime: true,
      },
      executed: false,
      network_wide: false,
      note: "This handle is isolated from the mesh. The page is this shell's policy refusal. Peer bytes were not loaded.",
    };
  }
  const checked = await verifyRecord(record);
  if (!checked.ok) return blocked(checked.reason, classified);
  noteVerified(record);
  const chain = chainCheck(record);
  if (!chain.ok) return { ...blocked(chain.reason, classified), html: "", executed: false };
  const status = await evaluateName(record, guard.nowMs);
  if (status.state === "PENDING") return pendingView(classified, record, status);
  if (status.state !== "FINAL") return { ...blocked(status.reason || "name_not_final", classified), name_status: "REFUSED", html: "" };
  const objects = objectsOf(record);
  const page = objects[String(record.ref && record.ref.object)];
  if (!page) return blocked("object_missing", classified);
  const gated = await gateBytes(record, page, objects);
  if (!gated.ok) return blocked(gated.reason, classified);
  const modules = Array.isArray(record.ref.modules) ? record.ref.modules : [];
  const air = await promoteObjects(page, modules, objects, guard.operator_override === true);
  const common = {
    plane: "mesh",
    spec: MESH_SPEC,
    name: record.name,
    url: classified.url,
    display_url: classified.display_url,
    host: record.name,
    owner_handle: record.handle,
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
    name_status: "FINAL",
    sandbox: { network: false, cross_origin: false, storage: "origin", file: false, tracker_detection: false },
    origin: "aziel://" + record.handle,
    title: record.name,
    scripts_executed: false,
    executed: false,
    not_chromium: true,
    airlock: air,
    network_wide: false,
    qnsd_public_proxy: false,
    socket: false,
  };
  if (!air.promoted) {
    const reason = air.reason || "scanner_absent";
    if (reason === "airlock_quarantine") {
      return { ...blocked(reason, classified), ...common, ok: false, verified_owner: false, html: "", promoted: false, quarantine: true };
    }
    return {
      ...common,
      ok: true,
      action: "airlock_hold",
      verified_owner: true,
      navigable: false,
      promoted: false,
      quarantine: true,
      html: "",
      excerpt: "",
      renderer: "mesh-quarantine",
      bytes_from: "quarantine",
      reason,
      clarity: clarify(reason),
      note: "FINAL name. Handle key and content hash matched. Bytes are in non-executable quarantine. Malware scanner is absent (no ClamAV, no YARA). They are not shown and not run until an explicit operator override. This Worker does not dial the local node.",
    };
  }
  const hint = record.connect || {};
  const mode = ["direct", "lan", "relay"].includes(hint.mode) ? hint.mode : "direct";
  const text = new TextDecoder("utf-8", { fatal: false }).decode(page);
  return {
    ...common,
    ok: true,
    action: "navigate",
    verified_owner: true,
    navigable: true,
    promoted: true,
    quarantine: false,
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
      note: "Worker verified the handle key and content hash, then promoted the bytes after an explicit operator override. It did not open a peer socket. Scanner is absent. Live direct / LAN / relay connect is the local shell to qnm-node.",
    },
    html: text.slice(0, 80000),
    renderer: "mesh-hash-gate",
    bytes_from: "worker-ledger",
    note: "Mesh site promoted out of quarantine by an explicit operator override. Scanner is absent. Handle key, not a certificate authority. .aziel is not registered with ICANN. Ordinary browsers do not resolve .aziel names. This Worker does not dial the local node and does not execute scripts.",
  };
}

export function lookupRecord(name, handle) {
  return lookup(name, handle);
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
