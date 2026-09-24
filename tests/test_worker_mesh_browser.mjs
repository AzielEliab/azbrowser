/**
 * Worker dual-surface gates for the local-first edge mesh plane.
 * Live peer sockets stay on the local shell. This file checks the same
 * decisions the Worker ops return.
 */
import assert from "node:assert/strict";
import { generateKeyPairSync, sign } from "node:crypto";
import { dispatch, setMeshLedger } from "../workers/download-tracker/src/engine.js";
import { canonical, classifyDestination, engineDigestFor, sha256Hex } from "../workers/download-tracker/src/mesh-browser.js";

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
  return { name, handle, public_key: raw, ref, signature, connect: connect || { mode: "direct", peer: handle, relay: null }, objects };
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
assert.equal(aziel.connect.socket, false);
assert.equal(aziel.connect.qnsd_public_proxy, false);
assert.equal(aziel.tab.kind, "mesh");
assert.match(aziel.display.summary, /library/);

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
assert.equal(decoy.plane, "dns");
assert.equal(decoy.allowlisted, false);

const allow = await dispatch("navigate", { url: "AZ.AzielEliab.AZ" }, aziel.session_id);
assert.equal(allow.plane, "mesh");
assert.equal(allow.code, "FG-GATE-REFUSE");
assert.equal(allow.reason, "name_not_in_ledger");
assert.equal(allow.allowlisted, true);
assert.equal(classifyDestination("azgrid.az").allowlisted, true);

const bad = structuredClone(record);
bad.objects[record.ref.object] = "<p>tampered</p>";
setMeshLedger([bad]);
const mismatch = await dispatch("navigate", { url: "library.aziel" }, "mismatch-sess");
assert.equal(mismatch.ok, false);
assert.equal(mismatch.code, "FG-GATE-REFUSE");
assert.equal(mismatch.reason, "hash_mismatch");
assert.equal(mismatch.html, "");
assert.match(mismatch.display.summary, /FG-GATE-REFUSE/);

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

console.log("worker mesh browser ok");
