/** Lamb Lens lock. Service, then Clarity, then Peace. */

export const ORDER = ["Service", "Clarity", "Peace"];
export const LOCK = "A feature that sacrifices Service, Clarity, or Peace fails review.";

const REASONS = {
  name_not_in_ledger: [
    "This name is not in the local ledger, so there is nothing to open.",
    "Check the spelling, or open a name this node already has. An allowlisted hub name still needs a ledger record.",
  ],
  name_not_final: [
    "This name is not final. It has not aged, or it does not have enough witnesses.",
    "Wait until it is final, or open a different name. A pending name is not a verified site.",
  ],
  name_pending: [
    "This name is pending. It is not a verified site.",
    "Wait for age and witnesses, or open a final name. No page bytes were loaded.",
  ],
  equivocating_handle: [
    "This handle has two conflicting records for the same sequence. Neither page is shown.",
    "Open a different handle. This node will not pick a side.",
  ],
  rollback: [
    "This record is older than the latest sequence for that handle.",
    "Open the current name for this handle.",
  ],
  bad_prev: [
    "This record does not link to the previous one in its chain.",
    "Open a record whose chain is intact.",
  ],
  handle_isolated: [
    "This handle is isolated from the mesh. Its pages are not shown.",
    "Go back, or open a different site. If this is your handle, you can file a signed appeal to ask for a re-check. This browser does not decide that appeal, and it does not delete local data.",
  ],
  design_mode_local_only: [
    "Design mode opens only on the machine that holds the handle key.",
    "Open AZBrowser on that machine. Nothing was published.",
  ],
  peer_blocked: [
    "This handle is blocked on this node.",
    "Unblock it here if you want it back. Other handles still open. No other node was cut off.",
  ],
  island_mode: [
    "This node is in island mode, so mesh names stay closed.",
    "Turn island mode off to rejoin, or keep using local apps and ordinary web addresses.",
  ],
  keys_must_stay_on_node: [
    "A private key was in this record. It was refused and not shown.",
    "Keep the handle key on the local node and send only the public record.",
  ],
  bad_handle: [
    "That handle is not a valid name.",
    "Use letters, numbers, and . _ - , then try again.",
  ],
  bad_grant: [
    "This capability request needs an origin, a kind, and a resource.",
    "Name all three. Kinds are network, fetch, storage, and file.",
  ],
  bad_island: [
    "Island mode needs true or false.",
    "Send enabled true to leave the mesh, or false to rejoin. Local apps and the ordinary web stay available either way.",
  ],
  airlock_quarantine: [
    "These bytes look executable or use a blocked type. They stay in quarantine.",
    "Do not run them. Promote does not release this kind of file.",
  ],
  scanner_absent: [
    "The handle key matched, and the page is held because this shell has no malware scanner.",
    "Choose Promote on this node to view the scrubbed page. Scripts still do not run.",
  ],
  object_missing: [
    "The signed page is not on this node.",
    "Pull that object on the local node, then try the name again.",
  ],
  hash_mismatch: [
    "The page bytes do not match the signed hash.",
    "Do not trust this copy. Open a record whose hash matches.",
  ],
  unsigned_module: [
    "A module on this page is not signed, so the page is not shown.",
    "Use a record whose modules are signed.",
  ],
  engine_digest_mismatch: [
    "The record digest does not match its contents.",
    "Do not open this copy. Use a record whose digest matches.",
  ],
  bad_handle_signature: [
    "The handle signature does not match this record.",
    "Do not open it. Use a record signed by that handle key.",
  ],
  network_not_granted: [
    "This app asked for the network, and no grant allows that resource.",
    "Leave it blocked, or grant that exact resource if you mean to allow it. Grants are receipted and rare.",
  ],
  file_not_granted: [
    "This app asked for a local file, and no grant allows that path.",
    "Leave it blocked, or grant that exact path if you mean to allow it.",
  ],
  cross_origin_not_granted: [
    "This app asked for another origin, and no grant allows it.",
    "Leave it blocked, or grant that exact origin if you mean to allow it.",
  ],
  storage_outside_origin: [
    "This app asked to store data outside its own origin.",
    "That stays denied. Storage inside its own origin does not ask.",
  ],
  bad_record: [
    "This ledger row has no name or handle.",
    "Skip it. A usable record names both.",
  ],
};

export function clarify(reason, code = "FG-GATE-REFUSE") {
  const row = REASONS[reason] || [
    "This was refused (" + (reason || "unspecified") + ").",
    "Try another address, or read the receipt for this action.",
  ];
  return {
    order: ORDER.slice(),
    lock: LOCK,
    code,
    reason: reason || "",
    plain: row[0],
    next: row[1],
  };
}

export function ethicsClarity(reasons) {
  const named = (reasons || []).join(", ") || "the ethical gate";
  return {
    order: ORDER.slice(),
    lock: LOCK,
    code: "ETHICS_REFUSE",
    reason: "ethics_refuse",
    plain: "This was refused before anything was fetched. The advisory gate matched " + named + ".",
    next: "Try a different query. This gate does not claim to catch every harmful request.",
  };
}

export function lensStatus() {
  return {
    order: ORDER.slice(),
    lock: LOCK,
    service: "One request opens a local app, a mesh name, or an ordinary web address.",
    clarity: "Verified handles, pending names, and isolated handles stay distinct. Every refusal says what happened and what to do next.",
    peace: "No ads, no tracking, no telemetry, and no notification spam. Capability grants are receipted and rare.",
    ads: false,
    tracking: false,
    telemetry: "off",
    notifications: false,
    miragegrid_decoys: "separate",
  };
}

export function stampRefusal(out) {
  if (!out || typeof out !== "object") return out;
  if (out.code === "ETHICS_REFUSE") {
    const reasons = out.ethics && out.ethics.reasons ? out.ethics.reasons : [];
    out.clarity = ethicsClarity(reasons);
    return out;
  }
  if (out.code === "FG-GATE-REFUSE") {
    out.clarity = clarify(out.reason || "");
  }
  return out;
}
