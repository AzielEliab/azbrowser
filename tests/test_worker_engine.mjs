import assert from "node:assert/strict";
import { readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { classifyQuery, dispatch, ethicalSearch, LIMITATION, OPS, SIGIL, SKILL_MD, scrubHtml } from "../workers/download-tracker/src/engine.js";
import { homeHtml } from "../workers/download-tracker/src/ui.js";
import { handleRuntimeApi } from "../workers/download-tracker/src/runtime.js";

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
assert.equal(SIGIL, "/sigil.png");
assert.match(html, /<title>[^<]*Aziel Eliab[^<]*<\/title>/);
assert.match(html, /Search or enter a \.aziel name or web address/);
assert.match(html, /id="btnGo"/);
assert.match(html, /id="downloadBtn"/);
assert.match(html, /class="btn block primary"/);
assert.match(html, /href="\/download\?asset=azbrowser-0\.1\.0\.tar\.gz"/);
assert.match(html, />Download</);
assert.match(html, /<footer class="quiet">/);
assert.match(html, /title="Go \/ ethical search"/);
assert.match(html, /callOp\(looksUrl \? "navigate" : "ethical_search"/);
assert.match(html, /\/v1\/fraggate\/call/);
assert.match(html, /class="brandmark" alt="" src="\/sigil\.png"/);
assert.match(html, /title="Home"/);
assert.doesNotMatch(html, /everblooming/i);
assert.doesNotMatch(html, /azielcorpuslibrary\.net\/sigil/);
assert.doesNotMatch(html, /AZNet ethical search/);
assert.doesNotMatch(html, /Search AZNet/);
assert.doesNotMatch(html, /class="aznet"/);
assert.doesNotMatch(html, />AZNet<\/span>/);
assert.match(html, /id="meshStrip"/);
assert.match(html, /id="meshLine"/);
assert.match(html, /Live Nodes/);
assert.match(html, /id="sidePanel" hidden/);
assert.match(html, /\/v1\/mesh/);
assert.match(html, /\/v1\/fraggate\/call/);
assert.doesNotMatch(html, /THIS IS NOT/);
assert.doesNotMatch(html, /QNM-BUILD-1\.0/);
assert.doesNotMatch(html, /No receipt = no action/);
assert.doesNotMatch(html, /id="node-gate"/);

const sigilPath = join(dirname(fileURLToPath(import.meta.url)), "../workers/download-tracker/public/sigil.png");
assert.equal(statSync(sigilPath).size, 75035);
assert.equal(readFileSync(sigilPath).subarray(0, 8).toString("hex"), "89504e470d0a1a0a");

const scrub = scrubHtml("<script>x</script><p>ok</p>");
assert.ok(scrub.stripped_kinds.includes("script"));

const home = await dispatch("home", {});
assert.equal(home.ok, true);
assert.equal(home.sigil, "/sigil.png");
assert.match(home.sigil, /sigil\.png/);
assert.ok(home.receipt.hash);
assert.doesNotMatch(home.display.summary, /everblooming/i);
assert.doesNotMatch(SKILL_MD, /everblooming/i);

const skillReq = new Request("https://azbrowser-download-tracker.vibelock.workers.dev/v1/skill", { method: "GET" });
const skillRes = await handleRuntimeApi(skillReq, new URL(skillReq.url), {});
assert.equal(skillRes.status, 200);
assert.doesNotMatch(await skillRes.text(), /everblooming/i);

const mcp = await dispatch("ethical_search", { q: "library", session_id: home.session_id });
assert.equal(mcp.ok, true);
assert.ok(mcp.display.title);

const bad = await dispatch("not_real", {});
assert.equal(bad.code, "FG-HALLUC-TOOL");

console.log("worker engine smoke ok", OPS.length, "ops");
