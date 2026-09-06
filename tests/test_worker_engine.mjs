import assert from "node:assert/strict";
import { classifyQuery, dispatch, ethicalSearch, LIMITATION, OPS, scrubHtml } from "../workers/download-tracker/src/engine.js";
import { homeHtml } from "../workers/download-tracker/src/ui.js";

assert.equal(classifyQuery("doxx their home address").refuse, true);
assert.equal(classifyQuery("FragGate kernel").refuse, false);
assert.ok(OPS.includes("ethical_search") && OPS.includes("navigate") && OPS.includes("airlock"));

assert.match(LIMITATION, /Lamb Lens ethical search/);
assert.match(LIMITATION, /separate product\/engine/);
assert.match(LIMITATION, /pairing is order\/token only/);
assert.doesNotMatch(LIMITATION, /AZNet ethical search/);
assert.equal(classifyQuery("FragGate").label.includes("AZNet"), false);
assert.match(classifyQuery("FragGate").label, /Lamb Lens/);

const search = ethicalSearch("FragGate");
assert.equal(search.ok, true);
assert.ok(search.results.length >= 1);
assert.equal(search.mode, "lamb_lens");
assert.doesNotMatch(search.label, /AZNet/);
assert.match(search.label, /Lamb Lens/);

const html = homeHtml({ views: 0, downloads: 0 });
assert.match(html, /Lamb Lens ethical search/);
assert.match(html, /id="btnGo"/);
assert.match(html, /title="Go \/ ethical search"/);
assert.match(html, /callOp\(looksUrl \? "navigate" : "ethical_search"/);
assert.match(html, /\/v1\/fraggate\/call/);
assert.doesNotMatch(html, /AZNet ethical search/);
assert.doesNotMatch(html, /Search AZNet/);
assert.doesNotMatch(html, /class="aznet"/);
assert.doesNotMatch(html, />AZNet<\/span>/);
assert.match(html, /pairing order\/token only/);

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
