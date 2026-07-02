/** Brain Core v1 gate — locked-definitions checksum + live-status aware filter. */
import {
  validateLockedDefinitionsChecksum,
  liveStatusFromTools,
  mappedDecisionStatus,
  LIVE_STATUS_KEYS,
} from "./locked-definitions-gate-v1.js";

const PASS_RE = /\bPASS\b/i;
const FORBIDDEN_PUBLIC = [
  "92/100",
  "5/5 audited",
  "200 live route",
  "Entity proof placeholder",
  "SOC2 certified",
  "ISO 42001 certified",
];

export function brainCoreGateStagingEnabled(env, request) {
  const prodFlag = String(env?.BRAIN_CORE_GATE_V1_ENABLED || "").trim();
  if (prodFlag === "1" || prodFlag.toLowerCase() === "true") return true;
  const flag = String(env?.BRAIN_CORE_GATE_STAGING || "").trim();
  if (flag === "1" || flag.toLowerCase() === "true") return true;
  const header = String(request?.headers?.get("X-SourceA-Brain-Core-Gate") || "").toLowerCase();
  return header === "staging" || header === "1";
}

function _intentClaim(userMessage = "") {
  const text = String(userMessage || "").toLowerCase();
  if (text.includes("forge") || text.includes("terminal")) return "forge_terminal_guaranteed_live_runtime";
  if (text.includes("proof") || text.includes("receipt") || text.includes("every possible run")) {
    return "every_possible_run_has_public_proof";
  }
  return "sourcea_is_live";
}

function _statusKeyForClaim(claimId) {
  if (claimId === "forge_terminal_guaranteed_live_runtime") return LIVE_STATUS_KEYS.forge_terminal;
  if (claimId === "every_possible_run_has_public_proof") return LIVE_STATUS_KEYS.proof_live;
  return LIVE_STATUS_KEYS.sourcea_app;
}

export function runBrainCoreGateStaging({
  userMessage = "",
  draftReply = "",
  confidence = null,
  citations = [],
  liveTools = [],
}) {
  const reasons = [];
  const defsValidation = validateLockedDefinitionsChecksum();
  if (defsValidation.validation_result !== "PASS") {
    reasons.push("locked_definitions_checksum_block");
  }

  const liveStatus = liveStatusFromTools(liveTools);
  const mapped = mappedDecisionStatus(liveStatus);
  const claimId = _intentClaim(userMessage);
  const statusKey = _statusKeyForClaim(claimId);
  const mappedStatus = mapped[statusKey] || "unknown";

  const passClaimed = PASS_RE.test(draftReply);
  const level = String(confidence?.level || "medium");
  const hits = Number(confidence?.hits || 0);
  const hasEvidence = hits > 0 || (citations || []).length > 0 || (liveTools || []).length > 0;

  if (passClaimed && level !== "high") {
    reasons.push("pass_claimed_without_high_confidence");
  }
  if (passClaimed && mappedStatus === "unknown") {
    reasons.push("pass_claimed_without_live_status");
  }
  if (mappedStatus === "degraded") {
    reasons.push(`live_status_degraded:${statusKey}`);
  }
  if (level === "low" && !hasEvidence) {
    reasons.push("low_confidence_no_evidence");
  }
  for (const bad of FORBIDDEN_PUBLIC) {
    if (draftReply.includes(bad) || String(userMessage || "").includes(bad)) {
      reasons.push(`forbidden_public_string:${bad}`);
    }
  }
  const overclaimText = `${userMessage}\n${draftReply}`;
  if (/\b(guarantee|certified|always works|100%)\b/i.test(overclaimText) && level !== "high") {
    reasons.push("overclaim_without_high_confidence");
  }

  const gateResult = reasons.length ? "BLOCK" : "PASS";
  let publicLanguage = String(draftReply || "");
  for (const bad of FORBIDDEN_PUBLIC) {
    publicLanguage = publicLanguage.split(bad).join("[redacted]");
  }
  publicLanguage = publicLanguage.replace(PASS_RE, "verified");

  const safePublic =
    mappedStatus === "degraded"
      ? "That public route may be degraded right now. Start from the SourceA product or proof route first."
      : "I can share what SourceA documents publicly. For specifics, use the cited pages or book a scoped audit.";

  return {
    schema: "brain-core-gate-v1",
    schema_version: "1.1.0",
    receipt_type: "BRAIN_CORE_GATE_RESULT",
    gate_result: gateResult,
    status: gateResult === "PASS" ? "PASS" : "BLOCKED",
    pass_claimed: passClaimed,
    reasons,
    confidence_level: level,
    evidence_hits: hits,
    user_message_len: String(userMessage || "").length,
    claim_id: claimId,
    live_status: liveStatus,
    mapped_status: mapped,
    locked_definitions_validation: defsValidation,
    sanitized_output: {
      ok: gateResult === "PASS",
      public_language: publicLanguage,
      safe_public_language: safePublic,
    },
  };
}
