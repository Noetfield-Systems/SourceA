/** Staging brain-core-v1 gate — deterministic draft → public reply filter. */
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
  const flag = String(env?.BRAIN_CORE_GATE_STAGING || "").trim();
  if (flag === "1" || flag.toLowerCase() === "true") return true;
  const header = String(request?.headers?.get("X-SourceA-Brain-Core-Gate") || "").toLowerCase();
  return header === "staging" || header === "1";
}

export function runBrainCoreGateStaging({
  userMessage = "",
  draftReply = "",
  confidence = null,
  citations = [],
  liveTools = [],
}) {
  const reasons = [];
  const passClaimed = PASS_RE.test(draftReply);
  const level = String(confidence?.level || "medium");
  const hits = Number(confidence?.hits || 0);
  const hasEvidence = hits > 0 || (citations || []).length > 0 || (liveTools || []).length > 0;

  if (passClaimed && level !== "high") {
    reasons.push("pass_claimed_without_high_confidence");
  }
  if (level === "low" && !hasEvidence) {
    reasons.push("low_confidence_no_evidence");
  }
  for (const bad of FORBIDDEN_PUBLIC) {
    if (draftReply.includes(bad)) {
      reasons.push(`forbidden_public_string:${bad}`);
    }
  }
  if (/\b(guarantee|certified|always works|100%)\b/i.test(draftReply) && level !== "high") {
    reasons.push("overclaim_without_high_confidence");
  }

  const gateResult = reasons.length ? "BLOCK" : "PASS";
  return {
    schema: "brain-core-gate-v1",
    schema_version: "1.0.0",
    receipt_type: "BRAIN_CORE_GATE_RESULT",
    gate_result: gateResult,
    status: gateResult === "PASS" ? "PASS" : "BLOCKED",
    pass_claimed: passClaimed,
    reasons,
    confidence_level: level,
    evidence_hits: hits,
    user_message_len: String(userMessage || "").length,
    staging: true,
  };
}
