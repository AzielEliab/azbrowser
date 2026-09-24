/**
 * Hosted shell chrome: plain tools, mesh words, counters, themes.
 * Machine JSON routes are not involved.
 */
import assert from "node:assert/strict";
import { homeHtml } from "../workers/download-tracker/src/ui.js";

const html = homeHtml({ views: 3, downloads: 4 });

assert.match(html, /id="sidePanel" hidden/);
assert.match(html, /Check this address/);
assert.match(html, /Show held page/);
assert.match(html, /This machine only/);
assert.match(html, /Turn presence on/);
assert.match(html, /Turn presence off/);
assert.match(html, /Join this browser/);
assert.match(html, /id="views">3</);
assert.match(html, /id="downloads">4</);
assert.match(html, /Live Nodes/);
assert.match(html, /id="meshNodeCount"/);
assert.match(html, />Mesh off</);
assert.match(html, /id="qnmLive"/);
assert.match(html, /id="qnmLocked"/);
assert.match(html, /id="qnmIsolated"/);
assert.match(html, /id="meshPlain"/);
assert.match(html, /data-theme-choice="night"/);
assert.match(html, /data-theme-choice="day"/);
assert.match(html, /data-theme-choice="aziel"/);
assert.match(html, /id="themeToggle"/);
assert.match(html, /id="azielMode"/);
assert.match(html, /--focus:#f0d060/);
assert.match(html, /--focus:#7a5c00/);
assert.match(html, /id="btnGo"/);
assert.match(html, /id="designBtn"/);
assert.match(html, /overflow-x:clip/);
assert.match(html, /Search or enter a \.aziel name or web address/);
assert.doesNotMatch(html, /QNM-BUILD-1\.0/);
assert.doesNotMatch(html, /QNS-CD-1\.0/);
assert.doesNotMatch(html, /THIS IS NOT/);
assert.doesNotMatch(html, /No receipt = no action/);
assert.doesNotMatch(html, /Mesh connected/);

console.log("worker chrome ok");
