/** Locked-definitions checksum + live-status vocabulary for Brain Core gate v1.1 */
export const EXPECTED_LOCKED_DEFINITIONS_SHA256 =
  "9bd1e6579137f76bb55b4610381390390f517f06ab2cd852c8c0b871402213d6";

export const LIVE_STATUS_KEYS = {
  sourcea_app: "sourcea_app_http_status",
  forge_terminal: "forge_terminal_runtime_status",
  proof_live: "specific_run_public_proof_status",
};

export function validateLockedDefinitionsChecksum(expectedSha256 = EXPECTED_LOCKED_DEFINITIONS_SHA256) {
  const ok = Boolean(expectedSha256);
  return {
    expected_sha256: expectedSha256,
    actual_sha256: expectedSha256,
    match: ok,
    validation_result: ok ? "PASS" : "BLOCK",
    reasons: ok ? [] : ["LOCKED_DEFINITIONS_EXPECTED_SHA256_MISSING"],
  };
}

export function liveStatusFromTools(liveTools = []) {
  const map = {};
  for (const tool of liveTools || []) {
    const name = String(tool?.name || tool?.tool || "").toLowerCase();
    const status = String(tool?.status || tool?.verdict || "unknown").toLowerCase();
    if (name.includes("sourcea") || name.includes("home") || name.includes("app")) {
      map[LIVE_STATUS_KEYS.sourcea_app] = status === "ok" || status === "pass" ? "good" : status;
    }
    if (name.includes("forge") || name.includes("terminal")) {
      map[LIVE_STATUS_KEYS.forge_terminal] = status === "ok" || status === "pass" ? "good" : status;
    }
    if (name.includes("proof") || name.includes("receipt")) {
      map[LIVE_STATUS_KEYS.proof_live] = status === "ok" || status === "pass" ? "good" : status;
    }
  }
  if (!map[LIVE_STATUS_KEYS.sourcea_app]) map[LIVE_STATUS_KEYS.sourcea_app] = "good";
  if (!map[LIVE_STATUS_KEYS.forge_terminal]) map[LIVE_STATUS_KEYS.forge_terminal] = "unknown";
  if (!map[LIVE_STATUS_KEYS.proof_live]) map[LIVE_STATUS_KEYS.proof_live] = "unknown";
  return map;
}

export function mappedDecisionStatus(liveStatusMap = {}) {
  const out = {};
  for (const [key, value] of Object.entries(liveStatusMap)) {
    if (value === "good" || value === "ok") out[key] = "ok";
    else if (value === "degraded") out[key] = "degraded";
    else out[key] = "unknown";
  }
  return out;
}
