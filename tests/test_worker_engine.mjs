import assert from "node:assert/strict";
import { classifyQuery, dispatch, ethicalSearch, OPS, scrubHtml } from "../workers/download-tracker/src/engine.js";

assert.equal(classifyQuery("doxx their home address").refuse, true);
assert.equal(classifyQuery("FragGate kernel").refuse, false);
assert.ok(OPS.includes("ethical_search") && OPS.includes("navigate") && OPS.includes("airlock"));
assert.ok(OPS.includes("pair_status") && OPS.includes("sidenet_view"));

const searchFn = ethicalSearch("FragGate");
assert.equal(searchFn.ok, true);
assert.ok(searchFn.results.length >= 1);
assert.notEqual(searchFn.mode, "AZNet");

const scrub = scrubHtml("<script>x</script><p>ok</p>");
assert.ok(scrub.stripped_kinds.includes("script"));

const home = await dispatch("home", {});
assert.equal(home.ok, true);
assert.match(home.sigil, /sigil\.png/);
assert.ok(home.receipt.hash);

const locked = await dispatch("ethical_search", { q: "library", paired: false, session_id: home.session_id });
assert.equal(locked.code, "PAIR_REQUIRED");
assert.equal(locked.pair.protocol_embedded, false);
assert.ok(locked.pair.links.aznet_garden);

const paired = await dispatch("pair_status", { paired: true, session_id: home.session_id });
assert.equal(paired.paired, true);

const mcp = await dispatch("ethical_search", { q: "library", paired: true, session_id: home.session_id });
assert.equal(mcp.ok, true);
assert.ok(mcp.display.title);

const side = await dispatch("sidenet_view", { session_id: home.session_id });
assert.equal(side.viewer, true);
assert.equal(side.protocol_embedded, false);
assert.match(side.garden, /\/garden$/);

const airLocked = await dispatch("airlock", { content: "hi", filename: "a.txt", paired: false });
assert.equal(airLocked.code, "PAIR_REQUIRED");

const bad = await dispatch("not_real", {});
assert.equal(bad.code, "FG-HALLUC-TOOL");

console.log("worker engine smoke ok", OPS.length, "ops");
