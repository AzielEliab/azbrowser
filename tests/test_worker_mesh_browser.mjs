/**
 * Worker dual-surface gates for the local-first edge mesh plane.
 * Live peer sockets stay on the local shell. This file checks the same
 * decisions the Worker ops return.
 */
import assert from "node:assert/strict";
import { generateKeyPairSync, sign } from "node:crypto";
import { dispatch, setMeshLedger } from "../workers/download-tracker/src/engine.js";
import { canonical, classifyDestination, engineDigestFor, meshRelayBases, pullRelayName, pullRelayNames, setRelayReadImpl, sha256Hex, witnessMessage, DEFAULT_RELAY_ORIGIN } from "../workers/download-tracker/src/mesh-browser.js";
import { createHash } from "node:crypto";

const PAGE = "<h1>Library</h1><p>Local-first shelf.</p>";

async function signedRecord(page = PAGE, { name = "library.aziel", handle = "library", modules = [], connect } = {}) {
  const { publicKey, privateKey } = generateKeyPairSync("ed25519");
  const spki = publicKey.export({ format: "der", type: "spki" });
  const raw = spki.subarray(spki.length - 32).toString("hex");
  const objects = {};
  const pageHash = await sha256Hex(page);
  objects[pageHash] = page;
  const refModules = [];
  for (const mod of modules) {
    const digest = await sha256Hex(mod.body);
    objects[digest] = mod.body;
    refModules.push({ path: mod.path, hash: digest, signed: mod.signed !== false, kind: mod.kind || "script" });
  }
  const ref = {
    name,
    handle,
    public_key: raw,
    object: pageHash,
    seq: 1,
    prev: "0".repeat(64),
    modules: refModules,
  };
  ref.engine_digest = await engineDigestFor(ref);
  const signature = sign(null, Buffer.from(canonical(ref)), privateKey).toString("hex");
  const record = {
    name,
    handle,
    public_key: raw,
    status: "FINAL",
    claimed_at: "2020-01-01T00:00:00Z",
    ref,
    signature,
    connect: connect || { mode: "direct", peer: handle, relay: null },
    objects,
    witnesses: [],
  };
  for (const witnessHandle of ["relay-a", "relay-b"]) {
    const witnessKeys = generateKeyPairSync("ed25519");
    const wspki = witnessKeys.publicKey.export({ format: "der", type: "spki" });
    const wraw = wspki.subarray(wspki.length - 32).toString("hex");
    const message = canonical(witnessMessage(record, witnessHandle));
    const signatureHex = sign(null, Buffer.from(message), witnessKeys.privateKey).toString("hex");
    record.witnesses.push({
      handle: witnessHandle,
      public_key: wraw,
      signature: signatureHex,
      receipt: createHash("sha256").update(Buffer.from(message)).digest("hex"),
    });
  }
  return record;
}

const record = await signedRecord();
setMeshLedger([record]);

const aziel = await dispatch("navigate", { url: "library.aziel/shelf" }, "mesh-sess");
assert.equal(aziel.ok, true);
assert.equal(aziel.plane, "mesh");
assert.equal(aziel.owner_handle, "library");
assert.equal(aziel.verified_owner, true);
assert.equal(aziel.icann, false);
assert.equal(aziel.regular_browsers_resolve_aziel, false);
assert.equal(aziel.keys_leave_node, false);
assert.equal(aziel.ca, false);
assert.equal(aziel.name_status, "FINAL");
assert.equal(aziel.quarantine, true);
assert.equal(aziel.promoted, false);
assert.equal(aziel.airlock.scanner, "absent");
assert.equal(aziel.html, "");
assert.equal(aziel.scripts_executed, false);
assert.equal(aziel.tab.kind, "mesh-quarantine");
assert.equal(aziel.network_wide, false);
assert.match(aziel.display.summary, /library/);
const shown = await dispatch("navigate", { url: "library.aziel/shelf", operator_override: true }, aziel.session_id);
assert.equal(shown.promoted, true);
assert.equal(shown.tab.kind, "mesh");
assert.equal(shown.scripts_executed, false);
assert.match(shown.html, /Library/);
assert.equal(shown.connect.socket, false);
assert.equal(shown.connect.qnsd_public_proxy, false);

const handle = await dispatch("resolve", { handle: "library" }, aziel.session_id);
assert.equal(handle.ok, true);
assert.equal(handle.name, "library.aziel");
assert.equal(handle.owner_handle, "library");
assert.equal(handle.public_key, record.public_key);

const dns = await dispatch("navigate", { url: "example.az/path" }, aziel.session_id);
assert.equal(dns.ok, true);
assert.equal(dns.plane, "dns");
assert.ok(dns.url.startsWith("https://example.az/"));
assert.notEqual(dns.code, "FG-GATE-REFUSE");

const decoy = classifyDestination("azbooth.az");
assert.equal(decoy.plane, "cap7");
assert.equal(decoy.false_site, true);
assert.equal(decoy.icann, false);
assert.equal(decoy.resolves_to_hub, false);

const allow = await dispatch("navigate", { url: "AZ.AzielEliab.AZ" }, aziel.session_id);
assert.equal(allow.plane, "cite");
assert.equal(allow.code, "UNCLAIMED");
assert.equal(allow.mesh_answer, false);
assert.equal(allow.icann_registration_by_this_code, false);
assert.equal(allow.hub, "https://www.azieleliab.com/");
assert.equal(allow.html, "");
assert.equal(allow.url, "");
assert.equal(allow.receipt.action, "cite");
const grid = classifyDestination("azgrid.az");
assert.equal(grid.plane, "cap7");
assert.equal(grid.allowlisted, true);
assert.equal(grid.icann, false);
assert.equal(grid.canonical_name, "azgrid.aziel");
const cap = await dispatch("navigate", { url: "azgrid.az" }, "cap7-sess");
assert.equal(cap.code, "RESOLVER_ABSENT");
assert.equal(cap.resolves_to_hub, false);
assert.equal(cap.public_icann, false);
assert.equal(cap.html, "");
assert.equal(cap.worker_dials_local_node, false);
assert.equal(cap.receipt.action, "cap7");
assert.equal(cap.softwares_frozen, true);
const hub = classifyDestination("https://www.azieleliab.com/");
assert.equal(hub.plane, "dns");
assert.equal(hub.layer, "L0");
const door = classifyDestination("http://127.0.0.1:8787/");
assert.equal(door.plane, "local");
assert.equal(door.layer, "L0");
assert.equal(door.source, "fraggate");

const bad = structuredClone(record);
bad.objects[record.ref.object] = "<p>tampered</p>";
setMeshLedger([bad]);
const mismatch = await dispatch("navigate", { url: "library.aziel" }, "mismatch-sess");
assert.equal(mismatch.ok, false);
assert.equal(mismatch.code, "FG-GATE-REFUSE");
assert.equal(mismatch.reason, "hash_mismatch");
assert.equal(mismatch.html, "");
assert.match(mismatch.display.summary, /do not match the signed hash/i);
assert.equal(mismatch.clarity.code, "FG-GATE-REFUSE");
assert.match(mismatch.clarity.next, /hash matches/);

const unsigned = await signedRecord('<p>ok</p><script src="/app.js"></script>');
setMeshLedger([unsigned]);
const unsignedOut = await dispatch("navigate", { url: "library.aziel" }, "unsigned-sess");
assert.equal(unsignedOut.code, "FG-GATE-REFUSE");
assert.equal(unsignedOut.reason, "unsigned_module");

setMeshLedger([record]);
const origin = "aziel://library";
const blocked = await dispatch("capability_check", { origin, kind: "network", target: "https://tracker.example/pixel" }, "cap-sess");
assert.equal(blocked.code, "FG-GATE-REFUSE");
assert.equal(blocked.reason, "network_not_granted");
const grant = await dispatch("capability_grant", { origin, capability: "network", resource: "https://tracker.example" }, blocked.session_id);
assert.equal(grant.ok, true);
assert.equal(grant.receipt.action, "capability_grant");
assert.equal(grant.keys_leave_node, false);
const allowed = await dispatch("capability_check", { origin, kind: "network", target: "https://tracker.example/pixel" }, blocked.session_id);
assert.equal(allowed.ok, true);
assert.equal(allowed.receipt.hash, grant.receipt.hash);
assert.equal(allowed.receipt.action, "capability_grant");

const app = await dispatch("local_app", { slug: "notes", source: "qnm", content: "<p>on this drive</p>" }, "local-sess");
assert.equal(app.ok, true);
assert.equal(app.tab.kind, "local-app");
assert.equal(app.data_stays_local, true);
assert.equal(app.uploaded, false);
assert.equal(app.origin, "azbrowser://local/notes");
assert.match(app.html, /on this drive/);
const localDeny = await dispatch("capability_check", { origin: app.origin, kind: "network", target: "https://ads.example/a" }, app.session_id);
assert.equal(localDeny.reason, "network_not_granted");

const web = await dispatch("navigate", { url: "https://www.azieleliab.com/" }, "web-sess");
assert.equal(web.ok, true);
assert.equal(web.plane, "dns");
assert.notEqual(web.code, "FG-GATE-REFUSE");
assert.match(web.url, /azieleliab\.com/);
assert.equal(web.tls, "standard");

const pending = await signedRecord();
pending.status = "PENDING";
pending.witnesses = [];
setMeshLedger([pending]);
const pendingOut = await dispatch("navigate", { url: "library.aziel" }, "pending-sess");
assert.equal(pendingOut.ok, true);
assert.equal(pendingOut.name_status, "PENDING");
assert.equal(pendingOut.verified_owner, false);
assert.equal(pendingOut.html, "");
assert.notEqual(pendingOut.code, "FG-GATE-REFUSE");
assert.match(pendingOut.display.summary, /not a verified site/i);

const conflictA = await signedRecord("<p>one</p>");
const conflictB = await signedRecord("<p>two</p>");
setMeshLedger([conflictA, conflictB]);
const equiv = await dispatch("navigate", { url: "library.aziel" }, "equiv-sess");
assert.equal(equiv.code, "FG-GATE-REFUSE");
assert.equal(equiv.reason, "equivocating_handle");
assert.equal(equiv.html, "");

setMeshLedger([record]);
const peer = await dispatch("peer_block", { handle: "library" }, "peer-sess");
assert.equal(peer.ok, true);
assert.equal(peer.network_wide, false);
assert.equal(peer.scope, "this-node");
const peerNav = await dispatch("navigate", { url: "library.aziel", operator_override: true }, peer.session_id);
assert.equal(peerNav.reason, "peer_blocked");
const island = await dispatch("island_mode", { enabled: true }, peer.session_id);
assert.equal(island.island_mode, true);
assert.equal(island.network_wide, false);
const before = (await dispatch("receipts", {}, island.session_id)).receipts.map((row) => row.hash);
const local = await dispatch("local_app", { slug: "notes", content: "<p>stays</p>" }, island.session_id);
assert.equal(local.ok, true);
assert.match(local.html, /stays/);
const dnsStill = await dispatch("navigate", { url: "https://example.com/docs" }, island.session_id);
assert.equal(dnsStill.plane, "dns");
const rejoined = await dispatch("island_mode", { enabled: false }, island.session_id);
assert.equal(rejoined.island_mode, false);
const after = (await dispatch("receipts", {}, island.session_id)).receipts.map((row) => row.hash);
assert.deepEqual(after.slice(0, before.length), before);
const verified = await dispatch("receipt_verify", {}, island.session_id);
assert.equal(verified.ok, true);
const trust = await dispatch("trust", { handle: "library" }, "trust-sess");
assert.equal(trust.local_only, true);
assert.equal(trust.public_ranking, false);
assert.equal(trust.network_wide, false);
assert.equal(JSON.stringify(trust).includes('"score"'), false);
const health = await dispatch("health", {}, "trust-sess");
assert.equal(health.mesh_browser.network_wide_cutoff, false);
assert.equal(health.mesh_browser.scanner, "absent");
assert.equal(health.aznet, false);
assert.equal(health.client_of, "aznet");
assert.equal(health.sidenet.softwares_frozen, true);
assert.equal(health.sidenet.l0_unbroken, true);
assert.equal(health.sidenet.aznet_http_resolve, false);
assert.equal(health.sidenet.cap7_public_icann, false);
assert.equal(health.mesh_browser.aznet_resolver, null);
assert.equal(health.ops.includes("pair"), false);
assert.equal(health.mesh_browser.security_model, "single-node-security-awareness");
assert.equal(health.mesh_browser.loopback_isolation, false);
assert.equal(health.mesh_browser.public_hostname_resurrection, false);

setMeshLedger([record]);
const other = "ab".repeat(32);
assert.notEqual(other, record.ref.object);
const crossed = await dispatch("navigate", {
  url: "library.aziel",
  relay: {
    record: {
      name: "library.aziel",
      owner: "library",
      status: "final",
      final: true,
      statement_hash: "cd".repeat(32),
      target: { type: "hash", value: other },
    },
  },
}, "cross-sess");
assert.equal(crossed.code, "FG-GATE-REFUSE");
assert.equal(crossed.reason, "hash_mismatch");
assert.equal(crossed.html, "");
assert.equal(crossed.dns, false);
assert.equal(crossed.icann, false);
assert.equal(crossed.node_path_isolated, true);
assert.equal(crossed.loopback_isolation, false);
assert.equal(crossed.forced_loopback, false);
assert.equal(crossed.browse_plane, "open");
assert.equal(crossed.phoenix.state, "local-wait");
assert.equal(crossed.phoenix.public_hostname_resurrection, false);
assert.equal(String(crossed.url).includes("127.0.0.1"), false);
const still = await dispatch("navigate", { url: "https://example.com/still-open" }, crossed.session_id);
assert.equal(still.plane, "dns");
assert.notEqual(still.code, "FG-GATE-REFUSE");
assert.ok(still.url.startsWith("https://example.com/"));
assert.equal(still.url.includes("127.0.0.1"), false);
setMeshLedger([record]);
const resealed = await dispatch("navigate", { url: "library.aziel" }, crossed.session_id);
assert.equal(resealed.hash_ok, true);
assert.equal(resealed.node_path, "resealed");
assert.equal(resealed.node_path_isolated, false);
assert.equal(resealed.phoenix.state, "resealed");

setMeshLedger([]);
const relayOnly = await dispatch("home", {
  name: "shelf.aziel",
  relay: {
    record: {
      name: "shelf.aziel",
      owner: "shelf",
      status: "final",
      final: true,
      statement_hash: "aa".repeat(32),
      target: { type: "hash", value: "bb".repeat(32) },
    },
  },
}, "relay-sess");
assert.equal(relayOnly.code, "FG-GATE-REFUSE");
assert.equal(relayOnly.reason, "object_missing");
assert.equal(relayOnly.name_resolved, true);
assert.equal(relayOnly.dns, false);
assert.equal(relayOnly.ledger_source, "fed-mesh-relay");
assert.equal(relayOnly.html, "");
assert.equal(relayOnly.forced_loopback, false);

const token = "pair-token-value";
const brokenPair = await dispatch("navigate", { url: "library.aziel", aznet_verify: true, pair_token: token }, "pair-sess");
assert.equal(brokenPair.code, "AZN-PAIR-REQUIRED");
assert.equal(brokenPair.pair_ui, "broken");
assert.equal(brokenPair.pair_token_echoed, false);
assert.equal(brokenPair.tunnel, false);
assert.equal(JSON.stringify(brokenPair).includes(token), false);
setMeshLedger([record]);
const paired = await dispatch("navigate", {
  url: "library.aziel",
  aznet_verify: true,
  pair_token: token,
  pair_flag: "azbrowser",
}, brokenPair.session_id);
assert.notEqual(paired.code, "AZN-PAIR-REQUIRED");
assert.equal(paired.pair_ui, "hidden");
assert.equal(JSON.stringify(paired).includes(token), false);

const fetched = await pullRelayName("library.aziel", async () => ({
  json: async () => ({
    ok: true,
    record: {
      name: "library.aziel",
      owner: "library",
      status: "pending",
      statement_hash: "ee".repeat(32),
    },
  }),
}), "https://aziel-runtime.vibelock.workers.dev");
assert.equal(fetched.found, true);
assert.equal(fetched.row.name, "library.aziel");
assert.equal(String(fetched.endpoint).includes("/v1/mesh/relay/name?name=library.aziel"), true);
setRelayReadImpl(async () => fetched);
setMeshLedger([]);
const viaReader = await dispatch("navigate", { url: "library.aziel" }, "reader-sess");
assert.equal(viaReader.name_status, "PENDING");
assert.equal(viaReader.dns, false);
assert.equal(viaReader.source, "fed-mesh-relay");
setRelayReadImpl(null);

assert.deepEqual(meshRelayBases(""), [DEFAULT_RELAY_ORIGIN]);
assert.deepEqual(
  meshRelayBases("http://127.0.0.1:8780/v1/mesh/relay,http://127.0.0.1:8780/v1/mesh/relay http://10.0.0.8:8783"),
  ["http://127.0.0.1:8780", "http://10.0.0.8:8783", DEFAULT_RELAY_ORIGIN],
);
const dropped = meshRelayBases("https://library.aziel/v1/mesh/relay,http://127.0.0.1:8783/v1/mesh/relay");
assert.equal(dropped[0], "http://127.0.0.1:8783");
assert.equal(dropped[dropped.length - 1], DEFAULT_RELAY_ORIGIN);
assert.equal(dropped.some((base) => new URL(base).hostname.endsWith(".aziel")), false);

const failoverCalls = [];
const failover = await pullRelayNames("shelf.aziel", async (url) => {
  failoverCalls.push(url);
  const host = new URL(url).hostname;
  assert.equal(host.endsWith(".aziel"), false);
  if (host === "127.0.0.1" && new URL(url).port === "8780") throw new Error("down");
  if (host.endsWith("vibelock.workers.dev")) throw new Error("cf down");
  return { json: async () => ({ record: { name: "shelf.aziel", owner: "shelf", status: "pending", statement_hash: "aa".repeat(32) } }) };
}, { configured: "http://127.0.0.1:8780/v1/mesh/relay,http://127.0.0.1:8783/v1/mesh/relay" });
assert.equal(failover.found, true);
assert.equal(failover.dns, false);
assert.equal(failover.aznet_replaces_internet, false);
assert.equal(failover.public_l1_live, false);
assert.equal(failover.l1_configured, true);
assert.equal(Object.hasOwn(failover, "l1_live"), false);
assert.equal(String(failover.endpoint).includes("127.0.0.1:8783"), true);
assert.equal(failoverCalls.some((url) => url.includes("vibelock")), false);

const unread = await pullRelayNames("missing-name.aziel", async () => {
  throw new Error("down");
}, { configured: "" });
assert.equal(unread.found, false);
assert.equal(unread.unread, true);
assert.equal(unread.l1_configured, false);
assert.equal(unread.public_l1_live, false);
assert.equal(unread.aznet_replaces_internet, false);
assert.equal(unread.dns, false);

console.log("worker mesh browser ok");
