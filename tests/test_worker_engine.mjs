import assert from "node:assert/strict";
import { classifyQuery, dispatch, ethicalSearch, OPS, scrubHtml } from "../workers/download-tracker/src/engine.js";

assert.equal(classifyQuery("doxx their home address").refuse, true);
assert.equal(classifyQuery("FragGate kernel").refuse, false);
assert.ok(OPS.includes("ethical_search") && OPS.includes("navigate") && OPS.includes("airlock"));

const search = ethicalSearch("FragGate");
assert.equal(search.ok, true);
assert.ok(search.results.length >= 1);

const scrub = scrubHtml("<script>x</script><p>ok</p>");
assert.ok(scrub.stripped_kinds.includes("script"));

const home = await dispatch("home", {});
assert.equal(home.ok, true);
assert.match(home.sigil, /sigil\.png/);
assert.ok(home.receipt.hash);

const mcp = await dispatch("ethical_search", { q: "library", session_id: home.session_id });
assert.equal(mcp.ok, true);
assert.ok(mcp.display.title);

const bad = await dispatch("not_real", {});
assert.equal(bad.code, "FG-HALLUC-TOOL");

console.log("worker engine smoke ok", OPS.length, "ops");
