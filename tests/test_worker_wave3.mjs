import assert from "node:assert/strict";
import { generateKeyPairSync, sign, createHash } from "node:crypto";
import { dispatch, setMeshLedger } from "../workers/download-tracker/src/engine.js";
import { canonical, engineDigestFor, sha256Hex, witnessMessage } from "../workers/download-tracker/src/mesh-browser.js";
import { homeHtml } from "../workers/download-tracker/src/ui.js";

async function signedRecord(page, name, handle) {
  const { publicKey, privateKey } = generateKeyPairSync("ed25519");
  const spki = publicKey.export({ format: "der", type: "spki" });
  const raw = spki.subarray(spki.length - 32).toString("hex");
  const pageHash = await sha256Hex(page);
  const ref = {
    name,
    handle,
    public_key: raw,
    object: pageHash,
    seq: 1,
    prev: "0".repeat(64),
    modules: [],
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
    connect: { mode: "direct", peer: handle, relay: null },
    objects: { [pageHash]: page },
    witnesses: [],
  };
  for (const witnessHandle of ["relay-a", "relay-b"]) {
    const keys = generateKeyPairSync("ed25519");
    const wspki = keys.publicKey.export({ format: "der", type: "spki" });
    const message = canonical(witnessMessage(record, witnessHandle));
    record.witnesses.push({
      handle: witnessHandle,
      public_key: wspki.subarray(wspki.length - 32).toString("hex"),
      signature: sign(null, Buffer.from(message), keys.privateKey).toString("hex"),
      receipt: createHash("sha256").update(Buffer.from(message)).digest("hex"),
    });
  }
  return record;
}

const isolated = await signedRecord("<h1>Library</h1>", "library.aziel", "library");
isolated.isolation = { state: "ISOLATED", reason: "policy_hate", check: "text_classifier", evidence_hash: "ab".repeat(32) };
const shelf = await signedRecord("<p>shelf</p>", "shelf.aziel", "shelf");
shelf.slot = 2;
setMeshLedger([isolated, shelf]);

const refused = await dispatch("navigate", { url: "library.aziel", operator_override: true }, "iso");
assert.equal(refused.code, "FG-GATE-REFUSE");
assert.equal(refused.reason, "handle_isolated");
assert.equal(refused.policy_page, true);
assert.match(refused.html, /This handle is isolated/);
assert.match(refused.html, /appeal/i);
assert.match(refused.html, /NCMEC/);
assert.doesNotMatch(refused.html, /Library/);
assert.equal(refused.isolation.content_stored, false);
assert.equal(refused.scripts_executed, false);

const other = await dispatch("navigate", { url: "shelf.aziel" }, "shelf");
assert.equal(other.ok, true);
assert.notEqual(other.reason, "handle_isolated");

const slots = await dispatch("slots", { handle: "shelf" }, "slots");
assert.equal(slots.reserved_count, 4);
assert.equal(slots.user_count, 3);
assert.equal(slots.user[1].name, "shelf.aziel");
assert.equal(slots.user[0].status, "empty");
assert.equal(slots.miragegrid.changed, false);
assert.equal(slots.miragegrid.separate_layer, true);
assert.equal(slots.reserved.every((row) => row.user_nameable === false), true);

const design = await dispatch("design_mode", { handle: "shelf" }, "design");
assert.equal(design.code, "FG-GATE-REFUSE");
assert.equal(design.reason, "design_mode_local_only");
assert.match(design.html, /hosting node/);
assert.equal(design.publish, false);

const html = homeHtml({ views: 0, downloads: 0 });
assert.match(html, /id="themeToggle"/);
assert.match(html, /id="azielMode"/);
assert.match(html, /id="bookmarks"/);
assert.match(html, /data-theme/);
assert.match(html, /id="btnGo"/);

console.log("worker wave 3 ok");
