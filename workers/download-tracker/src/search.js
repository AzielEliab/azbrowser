/**
 * AZ Search — AZ Browser's primary search.
 * A hit is a record this shell holds, or a corpus row whose returned
 * fields contain the query. Empty is an honest miss. Nothing is invented.
 * Not a Softwares card. Agents use FragGate slug=azbrowser op=ethical_search.
 * Sidenet is AZNet. Cap-7 is not an ICANN name.
 * Author: Aziel Eliab only.
 */

import { LOCK, ORDER } from "./lens.js";
import {
  AZ_DOMAIN_REACH,
  CAP7_FACTORY_LABELS,
  CAP7_FALSE_SITES,
  RESERVED_SLOTS,
} from "./mesh-browser.js";

export const ENGINE = "AZ Search";
export const PRODUCT = "AZ Browser";
export const SIDENET = "AZNet";
export const FRAGGATE_CORPUS = "https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call";

const CATALOG = [
  { title: "Aziel Digital Library", url: "https://www.azielcorpuslibrary.net/", source: "cite", blurb: "Public library site. A live corpus row is listed only when FragGate returns one whose fields contain the query.", tags: "library corpus aziel research" },
  { title: "FragGate kernel", url: "https://github.com/AzielEliab/fraggate", source: "cite", blurb: "One door — discover, route, refuse. FG-0.1.", tags: "fraggate mcp door kernel" },
  { title: "aziel-runtime", url: "https://github.com/AzielEliab/aziel-runtime", source: "cite", blurb: "Catalog and FragGate door.", tags: "runtime mcp openapi catalog" },
  { title: "AZMail (sibling, not this product)", url: "https://github.com/AzielEliab/azmail", source: "cite", blurb: "Mail airlock. Separate program. Not rebuilt in AZ Browser.", tags: "azmail mail airlock sibling" },
  { title: "GodLock", url: "https://godlock.uk/", source: "cite", blurb: "Offline hardening score. Not a VPN.", tags: "godlock abad hardening" },
  { title: "Aziel Eliab", url: "https://www.azieleliab.com/", source: "cite", blurb: "Public identity: Aziel Eliab only.", tags: "author identity aziel eliab" },
  { title: "Wikipedia", url: "https://en.wikipedia.org/wiki/Main_Page", source: "cite", blurb: "Encyclopedia main page. Cite the article you open.", tags: "encyclopedia wiki wikipedia" },
  { title: "MDN Web Docs", url: "https://developer.mozilla.org/", source: "cite", blurb: "Public web-platform documentation.", tags: "html css javascript http browser mdn" },
];

const STOP = new Set(["a", "an", "the", "of", "or", "and", "to", "for", "in", "on"]);
const SKIP_RECEIPT = new Set(["ethics_refuse"]);
const SOURCE_RANK = { mesh: 0, slot: 1, airlock: 2, receipt: 3, cap7: 4, "hub-cite": 5, "aziel-corpus": 6, cite: 7 };
const SECRET = new Set(["private_key", "secret", "seed", "sk", "pair_token"]);
const FALSE_LABELS = new Set(CAP7_FALSE_SITES.map((host) => host.replace(/\.az$/, "")));

function tokensOf(query) {
  return String(query || "")
    .toLowerCase()
    .match(/[a-z0-9][a-z0-9._-]*/g)
    ?.filter((word) => word.length >= 2 && !STOP.has(word)) || [];
}

function contains(token, blob) {
  if (token.length >= 4) return blob.includes(token);
  const re = new RegExp("(?:^|[^a-z0-9])" + token.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "(?:$|[^a-z0-9])");
  return re.test(blob);
}

function score(tokens, blob) {
  const low = String(blob || "").toLowerCase();
  return tokens.reduce((n, token) => n + (contains(token, low) ? 1 : 0), 0);
}

function httpUrl(value) {
  const text = String(value || "").trim();
  if (text.startsWith("https://") || text.startsWith("http://")) return text;
  return "";
}

function clip(text, limit) {
  return String(text || "").replace(/\s+/g, " ").trim().slice(0, limit || 240);
}

function candidate(row) {
  const out = {
    title: row.title,
    url: row.url || "",
    source: row.source,
    blurb: clip(row.blurb),
    tags: row.tags || "",
    plane: row.plane || row.source,
  };
  if (row.icann != null) {
    out.icann = row.icann;
    out.public_icann = ["cap7", "hub-cite", "mesh", "slot"].includes(row.source) ? false : row.icann;
  }
  if (row.false_site != null) out.false_site = row.false_site;
  if (row.receipt) out.receipt = row.receipt;
  if (row.record_id) out.record_id = row.record_id;
  return out;
}

function meshCandidates(records) {
  const found = [];
  for (const record of records || []) {
    if (!record || typeof record !== "object") continue;
    if (Object.keys(record).some((key) => SECRET.has(key))) continue;
    const name = String(record.name || "").trim();
    const handle = String(record.handle || "").trim();
    if (!name && !handle) continue;
    const bits = [name, handle, String(record.status || "")];
    const objects = record.objects && typeof record.objects === "object" ? record.objects : null;
    if (objects) {
      for (const [key, value] of Object.entries(objects).slice(0, 4)) {
        bits.push(String(key).slice(0, 80));
        if (typeof value === "string") bits.push(value.slice(0, 240));
      }
    }
    const title = name || handle + ".aziel";
    found.push(candidate({
      title,
      url: title,
      source: "mesh",
      plane: "mesh",
      icann: false,
      blurb: "Local mesh name " + title + ". Handle " + (handle || "unset") + ". Not an ICANN name.",
      tags: bits.join(" "),
    }));
  }
  return found;
}

function slotText(slot) {
  if (typeof slot === "boolean") return "";
  if (Number.isInteger(slot)) return String(slot);
  return String(slot || "").trim();
}

function slotCandidates(records, handle) {
  const found = [];
  for (const row of RESERVED_SLOTS) {
    found.push(candidate({
      title: row.label,
      url: row.host,
      source: "slot",
      plane: "cite",
      icann: false,
      blurb: "Reserved hub mirror " + row.label + ". Not user-nameable. AZ Browser did not register .az.",
      tags: [row.label, row.host, row.id, "reserved hub mirror slot"].join(" "),
    }));
  }
  const who = String(handle || "").trim().toLowerCase();
  const seen = new Set();
  for (const record of records || []) {
    if (!record) continue;
    const owner = String(record.handle || "").trim().toLowerCase();
    if (!owner || (who && owner !== who)) continue;
    seen.add(owner);
    const slot = slotText(record.slot);
    const name = String(record.name || "").trim();
    if (name && ["1", "2", "3"].includes(slot)) {
      found.push(candidate({
        title: name,
        url: name,
        source: "slot",
        plane: "mesh",
        icann: false,
        blurb: "User slot " + slot + " for " + owner + ". Status " + (record.status || "PENDING") + ".",
        tags: [name, owner, "user slot", slot].join(" "),
      }));
    }
  }
  for (const owner of [...seen].sort()) {
    const automatic = owner + ".aziel";
    found.push(candidate({
      title: automatic,
      url: automatic,
      source: "slot",
      plane: "mesh",
      icann: false,
      blurb: "Automatic mesh name for handle " + owner + ".",
      tags: [automatic, owner, "automatic"].join(" "),
    }));
  }
  return found;
}

function cap7Candidates() {
  return CAP7_FACTORY_LABELS.map((label) => {
    const host = label + ".az";
    const falseSite = FALSE_LABELS.has(label);
    return candidate({
      title: host,
      url: host,
      source: "cap7",
      plane: "cap7",
      icann: false,
      false_site: falseSite,
      blurb: falseSite
        ? "Cap-7 false site " + host + ". Not public DNS. Not an ICANN name. Not a hub."
        : "Cap-7 name " + host + " on the AZNet sidenet. Mesh pairing only. Not an ICANN name. Not a hub.",
      tags: ["cap7", label, host, "sidenet aznet mesh"].join(" "),
    });
  });
}

function hubCandidates() {
  return AZ_DOMAIN_REACH.map((row) => candidate({
    title: row.display_name,
    url: row.hub,
    source: "hub-cite",
    plane: "cite",
    icann: false,
    blurb: "Hub cite " + row.hub + ". Mirror " + row.mirrors + ". Cap-7 label " + row.cap7_label + " is a separate mesh name. AZ Browser did not register .az.",
    tags: [row.display_name, row.mesh_key, row.hub, row.mirrors, "hub mirror"].join(" "),
  }));
}

function historyCandidates(receipts, airlocks) {
  const found = [];
  const airHashes = new Set((airlocks || []).map((row) => String((row && (row.hash || row.content_hash)) || "")));
  for (const row of airlocks || []) {
    if (!row) continue;
    const url = String(row.url || "");
    const filename = String(row.filename || "");
    const verdict = String(row.verdict || "");
    const digest = String(row.hash || row.content_hash || "");
    found.push(candidate({
      title: "Airlock · " + (filename || url || "Airlock"),
      url,
      source: "airlock",
      plane: "airlock",
      blurb: "Airlock history. Verdict " + (verdict || "unset") + ".",
      tags: ["airlock", url, filename, verdict, digest].join(" "),
      receipt: digest,
    }));
  }
  for (const row of receipts || []) {
    if (!row) continue;
    const action = String(row.action || "");
    if (SKIP_RECEIPT.has(action)) continue;
    const payload = row.payload && typeof row.payload === "object" ? row.payload : {};
    if (action === "airlock" && airHashes.has(String(payload.hash || ""))) continue;
    const bits = [action, String(row.hash || "")];
    for (const key of ["url", "q", "query", "filename", "verdict", "note", "name", "handle"]) {
      if (typeof payload[key] === "string" && payload[key]) bits.push(payload[key].slice(0, 180));
    }
    if (bits.length < 3) continue;
    const digest = String(row.hash || "");
    const source = action === "airlock" ? "airlock" : "receipt";
    found.push(candidate({
      title: "Receipt · " + action,
      url: typeof payload.url === "string" ? payload.url : "",
      source,
      plane: source,
      blurb: "Receipt " + digest.slice(0, 16) + " for " + action + ".",
      tags: bits.join(" "),
      receipt: digest,
    }));
  }
  return found;
}

function citeCandidates() {
  return CATALOG.map((item) => candidate({
    title: item.title,
    url: item.url,
    source: item.source,
    plane: "cite",
    blurb: item.blurb,
    tags: item.tags,
  }));
}

function corpusCandidates(rows, queryTokens) {
  const matched = [];
  let returned = 0;
  for (const row of rows || []) {
    if (!row || typeof row !== "object") continue;
    if (Object.keys(row).some((key) => SECRET.has(key))) continue;
    returned += 1;
    const title = String(row.title || row.name || "").trim();
    const recordId = String(row.record_id || row.id || "").trim();
    if (!title && !recordId) continue;
    const keywords = Array.isArray(row.keywords) ? row.keywords.join(" ") : String(row.keywords || row.subjects || "");
    const identity = [title, recordId, keywords, String(row.subjects || "")].join(" ");
    if (score(queryTokens, identity) <= 0) continue;
    const url = httpUrl(row.url || row.href || row.link);
    matched.push(candidate({
      title: title || recordId,
      url,
      source: "aziel-corpus",
      plane: "corpus",
      blurb: String(row.snippet || row.blurb || ("Corpus record " + recordId)),
      tags: identity,
      record_id: recordId,
    }));
  }
  return { matched, returned };
}

function dedupe(scored, limit) {
  scored.sort((a, b) => b[0] - a[0] || a[1] - b[1]);
  const seen = new Set();
  const hits = [];
  for (const [, , row] of scored) {
    const key = row.url || [row.source, row.title, row.record_id || "", row.receipt || ""].join("|");
    if (!key || seen.has(key)) continue;
    seen.add(key);
    const clean = { ...row };
    delete clean.tags;
    hits.push(clean);
    if (hits.length >= limit) break;
  }
  return hits;
}

export function collectHits(query, sources) {
  const bag = sources || {};
  const queryTokens = tokensOf(query);
  const cap = Math.max(1, Math.min(Number(bag.limit) || 8, 16));
  const corpus = corpusCandidates(bag.corpus || [], queryTokens);
  const pool = [
    ...meshCandidates(bag.records || []),
    ...slotCandidates(bag.records || [], bag.handle || ""),
    ...cap7Candidates(),
    ...hubCandidates(),
    ...historyCandidates(bag.receipts || [], bag.airlocks || []),
    ...citeCandidates(),
    ...corpus.matched,
  ];
  const scored = [];
  for (const row of pool) {
    const blob = [row.title, row.blurb, row.tags, row.url].join(" ");
    const rank = score(queryTokens, blob);
    if (rank <= 0) continue;
    scored.push([rank, SOURCE_RANK[row.source] ?? 9, row]);
  }
  return {
    results: queryTokens.length ? dedupe(scored, cap) : [],
    corpus_returned: corpus.returned,
    corpus_matched: corpus.matched.length,
  };
}

export function extractCorpusRecords(body) {
  const found = [];
  const walk = (node, depth) => {
    if (depth > 6 || !node || typeof node !== "object" || Array.isArray(node)) return;
    for (const key of ["records", "results", "hits"]) {
      if (Array.isArray(node[key])) found.push(...node[key].filter((row) => row && typeof row === "object"));
    }
    for (const key of ["result", "data", "payload"]) {
      if (node[key] && typeof node[key] === "object") walk(node[key], depth + 1);
    }
  };
  walk(body, 0);
  return found;
}

export async function fetchCorpus(query) {
  try {
    const response = await fetch(FRAGGATE_CORPUS, {
      method: "POST",
      headers: { "content-type": "application/json", "user-agent": "Mozilla/5.0" },
      body: JSON.stringify({ slug: "aziel-corpus", op: "search", payload: { q: query } }),
    });
    const body = await response.json();
    return { asked: true, ok: true, records: extractCorpusRecords(body), error: "" };
  } catch {
    return { asked: true, ok: false, records: [], error: "corpus_unreachable" };
  }
}

export function assembleSearch(query, ethics, sources) {
  if (ethics && ethics.refuse) {
    return {
      ok: false,
      code: "ETHICS_REFUSE",
      action: "ethical_search",
      engine: ENGINE,
      product: PRODUCT,
      sidenet: SIDENET,
      alias: "lamb_lens",
      query,
      ethics,
      results: [],
      citations: [],
      invented: false,
      advisory: true,
      softwares_card: false,
      label: "AZ Search refused. Lamb Lens advisory gate.",
      note: "Cite sources. Refuse doxxing, credential harvest, and malware lure.",
    };
  }
  const gathered = collectHits(query, sources);
  const hits = gathered.results;
  const status = { ...(sources && sources.corpus_status ? sources.corpus_status : {}) };
  if (sources && sources.corpus && status.asked == null) {
    status.asked = true;
    status.ok = true;
  }
  if (status.asked == null) status.asked = false;
  status.returned = gathered.corpus_returned;
  status.matched = gathered.corpus_matched;
  const count = hits.length;
  let plain = count
    ? "AZ Search listed " + count + " record" + (count === 1 ? "" : "s") + " this shell holds or that a corpus response contained."
    : "AZ Search found no matching name, slot, receipt, airlock row, or cite.";
  const next = count
    ? "Open a result, or search again. A .aziel name or a web address goes straight to navigation."
    : "Try another word, or open a .aziel name or a web address. Nothing was invented.";
  if (status.asked) {
    plain += status.ok === false
      ? " The corpus door was not reached, so no corpus row was added."
      : " The corpus returned " + gathered.corpus_returned + " rows; " + gathered.corpus_matched + " contained the query in the fields AZ Search read.";
  }
  return {
    ok: true,
    action: "ethical_search",
    engine: ENGINE,
    product: PRODUCT,
    sidenet: SIDENET,
    alias: "lamb_lens",
    mode: "az_search",
    query,
    ethics,
    lens: {
      order: ORDER.slice(),
      lock: LOCK,
      service: "The query was searched once, across names, slots, Cap-7, hub cites, receipts, and corpus rows already in hand.",
      clarity: plain,
      peace: "No ads, no tracking, and no invented hits.",
    },
    clarity: { order: ORDER.slice(), lock: LOCK, plain, next },
    results: hits,
    citations: hits.map((hit) => ({
      title: hit.title || "",
      url: hit.url || "",
      source: hit.source || "",
      record_id: hit.record_id || "",
      receipt: hit.receipt || "",
    })),
    corpus: status,
    invented: false,
    advisory: true,
    softwares_card: false,
    cap7_public_icann: false,
    label: "AZ Search. Lamb Lens — Service, then Clarity, then Peace. Cite sources.",
    note: plain,
  };
}
