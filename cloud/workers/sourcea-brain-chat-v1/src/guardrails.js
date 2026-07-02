/** Post-generation guardrails + retrieval-only fallback (Brain v4). */

const SOURCEA_ORIGIN = "https://sourcea.app";

const FORBIDDEN_PATTERNS = [
  /\bopenrouter\b/i,
  /@cf\/[a-z0-9._:/-]+/i,
  /\b(?:google|anthropic|openai|deepseek)\/[a-z0-9._:/-]+/i,
  /\b(?:Gemini|Claude|GPT-?4o|DeepSeek|Llama|Qwen)(?:\s+[A-Za-z0-9.:-]+){0,5}\b/i,
  /\bsk-[a-z0-9_-]{8,}/i,
  /\bapi[_-]?key\s*[:=]/i,
  /:?13020|:?13027|:?8780|:?8781/,
  /\bcom\.sourcea\./i,
  /\bPASS\/BLOCK\b/,
  /\b(?:PASS|BLOCK|ALLOW)\b/,
  /\bINCIDENT-\d+\b/i,
  /\bbrain-os\b/i,
  /\bhighest[- ]confidence\b/i,
  /\b(?:docs|scripts|brain-os|cloud\/workers|SourceA-landing|sites\/SourceA-landing)\//i,
  /\bsourcea-brain-chat-config-v1\.json\b/i,
];

const PRICE_IN_LEAD = /\$\d{2,}|(?:^|\s)(?:1500|5000|6000|8000)(?:\s|$)/;

export function isPricingQuestion(message) {
  return /\b(price|pricing|cost|how much|tier|build|rent|own|\$)\b/i.test(String(message || ""));
}

export function isInternalMetaQuestion(message) {
  return /\b(internal|docx|source paths?|repo paths?|private config|config json|what are you talking about)\b/i.test(
    String(message || ""),
  ) || /\bwhy (?:did|do|are) you (?:mention|talking about|calling).*\b(?:stranger|client|source|repo|doc|json|config)\b/i.test(
    String(message || ""),
  );
}

export function isSensitiveInternalQuestion(message) {
  return /\b(openrouter|api key|secret|token|password|brain-os|incident files?|internal files?|repo files?|local ports?|localhost|127\.0\.0\.1|mac (?:path|port|config|secret|key|local|file|repo))\b/i.test(
    String(message || ""),
  );
}

export function requestedLanguage(message) {
  const q = String(message || "")
    .trim()
    .toLowerCase()
    .replace(/[.!?؟،,;:]+$/g, "");
  const words = q.split(/\s+/).filter(Boolean);
  const aliases = {
    farsi: "Farsi/Persian",
    persian: "Farsi/Persian",
    فارسی: "Farsi/Persian",
    فارسي: "Farsi/Persian",
    spanish: "Spanish",
    español: "Spanish",
    espanol: "Spanish",
    french: "French",
    français: "French",
    francais: "French",
    german: "German",
    deutsch: "German",
    arabic: "Arabic",
    عربي: "Arabic",
    hindi: "Hindi",
    urdu: "Urdu",
    chinese: "Chinese",
    mandarin: "Chinese",
    japanese: "Japanese",
    korean: "Korean",
    portuguese: "Portuguese",
    italian: "Italian",
    russian: "Russian",
    turkish: "Turkish",
  };
  if (aliases[q]) return aliases[q];
  for (const w of words) {
    if (aliases[w]) return aliases[w];
  }
  const target = q.match(/\b(?:in|to|translate to|به)\s+([a-z\u0600-\u06ffçñéèêáíóúü-]{3,})\b/i);
  if (target?.[1]) return aliases[target[1]] || target[1];
  if (
    /\b(can|could|please)?\s*(you\s+)?translate\b/.test(q) ||
    /\byou are ai you can translate\b/.test(q)
  ) {
    return "translate";
  }
  return "";
}

export function translationClarifierReply() {
  return "You’re right. I can translate. Tell me the target language, or send the sentence you want translated.";
}

export function publicBoundaryReply() {
  return [
    "I can't share internal keys, local ports, repo paths, or private configuration.",
    "",
    "For a public visitor, the useful answer is: SourceA is an AI execution platform powered by Forge. It runs real builds, automations, and agent workflows with proof of what ran.",
    "",
    `Try the public Forge Terminal here: ${SOURCEA_ORIGIN}/sourcea/forge/terminal`,
  ].join("\n");
}

export function canonicalPublicUrl(url) {
  const raw = String(url || "").trim();
  if (!raw) return "";
  if (/^https:\/\/sourcea\.app\/proof\/live\/?$/i.test(raw)) return `${SOURCEA_ORIGIN}/sourcea/proof/live`;
  if (/^https:\/\/sourcea\.app\/forge\/terminal\/?$/i.test(raw)) return `${SOURCEA_ORIGIN}/sourcea/forge/terminal`;
  if (/^https:\/\/sourcea\.app\/pricing\/?$/i.test(raw)) return `${SOURCEA_ORIGIN}/sourcea/pricing`;
  if (raw.startsWith("/sourcea/")) return `${SOURCEA_ORIGIN}${raw}`;
  if (raw === "/start") return `${SOURCEA_ORIGIN}/start`;
  if (raw.startsWith("/")) return `${SOURCEA_ORIGIN}${raw}`;
  return raw;
}

export function normalizePublicLinks(reply) {
  return String(reply || "")
    .replace(/\[([^\]]+)\]\((https:\/\/sourcea\.app[^)]+)\)/g, (_m, label, url) => `${label}: ${canonicalPublicUrl(url)}`)
    .replace(/\[([^\]]+)\]\((\/[^)]+)\)/g, (_m, label, url) => `${label}: ${canonicalPublicUrl(url)}`)
    .replace(/\bhttps:\/\/sourcea\.app\/proof\/live\/?\b/gi, `${SOURCEA_ORIGIN}/sourcea/proof/live`)
    .replace(/\bhttps:\/\/sourcea\.app\/forge\/terminal\/?\b/gi, `${SOURCEA_ORIGIN}/sourcea/forge/terminal`)
    .replace(/(^|[\s(])\/sourcea\/([a-z0-9/_-]+)/gi, (_m, pre, path) => `${pre}${SOURCEA_ORIGIN}/sourcea/${path}`)
    .replace(/(^|[\s(])\/start\b/g, `$1${SOURCEA_ORIGIN}/start`)
    .replace(/\s*\((?:Source|Sources)\s+\d+(?:\s*(?:,|and)\s*\d+)*\)\.?/gi, "")
    .replace(/\s*\bSource\s+\d+(?:\s*(?:,|and)\s*\d+)*\.?/gi, "")
    .replace(/\s*\(,\s*[a-z0-9_-]+\)\.?/gi, "")
    .replace(/\s*\((?:\s*,\s*)+\)\.?/g, "")
    .replace(/[ \t]{2,}/g, " ")
    .replace(/\s+\n/g, "\n");
}

export function sanitizePublicText(value) {
  return String(value || "")
    .replace(/\bPASS\/BLOCK\b/g, "allowed-or-stopped result")
    .replace(/\bPASS or BLOCK\b/g, "allowed or stopped")
    .replace(/\bALLOW\/BLOCK\b/g, "allowed-or-stopped result")
    .replace(/\bALLOW or BLOCK\b/g, "allowed or stopped")
    .replace(/\bPASS\b/g, "passed")
    .replace(/\bALLOW\b/g, "allowed")
    .replace(/\bAPPROVED\b/g, "available")
    .replace(/\bBLOCK\b/g, "stopped")
    .replace(/\bOpenRouter routing\b/gi, "AI model routing")
    .replace(/\bOpenRouter\b/gi, "AI model layer")
    .replace(/@cf\/[a-z0-9._:/-]+/gi, "AI model")
    .replace(/\b(?:google|anthropic|openai|deepseek)\/[a-z0-9._:/-]+/gi, "AI model")
    .replace(/\bGemini(?:\s+[A-Za-z0-9.:-]+){0,4}\b/g, "AI model")
    .replace(/\bClaude(?:\s+[A-Za-z0-9.:-]+){0,4}\b/g, "AI model")
    .replace(/\bGPT-?4o(?:\s+[A-Za-z0-9.:-]+){0,3}\b/gi, "AI model")
    .replace(/\bDeepSeek(?:\s+[A-Za-z0-9.:-]+){0,4}\b/g, "AI model")
    .replace(/\bLlama(?:\s+[A-Za-z0-9.:-]+){0,5}\b/g, "AI model")
    .replace(/\bQwen(?:\s+[A-Za-z0-9.:-]+){0,5}\b/g, "AI model")
    .replace(/\b(?:localhost|127\.0\.0\.1):\d+\b/gi, "local service")
    .replace(/:?\b(?:13020|13027|8780|8781)\b/g, "local service")
    .replace(/\bcom\.sourcea\.[a-z0-9_.-]+\b/gi, "internal app")
    .replace(/\bsourcea-brain-chat-config-v1\.json\b/gi, "public chat config")
    .replace(/\b(?:docs|scripts|brain-os|cloud\/workers|SourceA-landing|sites\/SourceA-landing)\/[^\s),]+/gi, "internal source")
    .replace(/\bbrain-os\b/gi, "internal knowledge base")
    .replace(/\bINCIDENT-\d+\b/gi, "internal issue")
    .replace(/\bFactory proceed\b/gi, "Cloud execution")
    .replace(/\bfactory-live\.json\b/gi, "live proof data")
    .replace(/\bfactory disk\b/gi, "proof record")
    .replace(/\binternal factory jargon\b/gi, "internal wording")
    .replace(/\bhighest[- ]confidence public guide\b/gi, "public guide")
    .replace(/\bhighest[- ]confidence public intelligence\b/gi, "public guide")
    .replace(/\bhighest[- ]confidence\b/gi, "evidence-backed")
    .replace(/\s+\)/g, ")")
    .replace(/\(\s*\)/g, "")
    .replace(/[ \t]{2,}/g, " ")
    .trim();
}

function sanitizePublicKey(key) {
  return String(key || "")
    .replace(/openrouter/gi, "ai_model")
    .replace(/model_used/gi, "ai_model")
    .replace(/model_requested/gi, "ai_model_requested")
    .replace(/model_fallback/gi, "ai_model_fallback");
}

function isInternalMetadataKey(key) {
  return /^(chunk_id|chunk_ids|source_path|source_paths)$/i.test(String(key || ""));
}

function isMachineReceiptKey(key) {
  return /^brain_core_gate$/i.test(String(key || ""));
}

export function sanitizePublicBody(value, key = "") {
  if (isMachineReceiptKey(key)) {
    return value;
  }
  if (isInternalMetadataKey(key)) {
    if (Array.isArray(value)) return value.map(() => "public source");
    if (value) return "public source";
    return value;
  }
  if (typeof value === "string") return sanitizePublicText(value);
  if (Array.isArray(value)) return value.map((item) => sanitizePublicBody(item, key));
  if (!value || typeof value !== "object") return value;
  return Object.fromEntries(
    Object.entries(value).map(([childKey, row]) => [sanitizePublicKey(childKey), sanitizePublicBody(row, childKey)]),
  );
}

function normalizeSourceAVoice(reply) {
  return String(reply || "")
    .replace(/\bThey promise\b/g, "SourceA aims")
    .replace(/\bThey offer\b/g, "SourceA offers")
    .replace(/\bThey provide\b/g, "SourceA provides")
    .replace(/\bThey call\b/g, "SourceA calls")
    .replace(/\btheir (MVP|service|services|platform|pricing|offer|offers|product|products)\b/gi, (_m, noun) => `SourceA's ${noun}`)
    .replace(/\bthe company\b/gi, "SourceA");
}

export function sanitizeHistoryContent(content) {
  return normalizeSourceAVoice(
    sanitizePublicText(normalizePublicLinks(content))
      .replace(/\bhighest[- ]confidence\b/gi, "evidence-backed")
      .replace(/\bhighest[- ]confidence public guide\b/gi, "public guide")
      .replace(/\bhighest[- ]confidence public intelligence\b/gi, "public guide")
      .replace(/\bpublic intelligence\b/gi, "public guide"),
  ).slice(0, 2000);
}

function cleanOpeningHedge(reply) {
  return String(reply || "")
    .replace(/^it looks like you (?:might be|are) asking about (?:a |an )?["“]?([^"”]+)["”]?\.\s*/i, "")
    .replace(/^you might be asking about (?:a |an )?["“]?([^"”]+)["”]?\.\s*/i, "")
    .replace(/^sourcea provides verifiable delivery receipts, which they call /i, "A live receipt is ");
}

function addRequiredPublicLinks(message, reply) {
  const q = String(message || "").toLowerCase();
  let out = String(reply || "").trim();
  if (/\b(live receipt|live proof|proof live|receipt)\b/.test(q) && !out.includes(`${SOURCEA_ORIGIN}/sourcea/proof/live`)) {
    out += `\n\nLive proof page: ${SOURCEA_ORIGIN}/sourcea/proof/live`;
  }
  if (/\b(forge terminal|try forge|browser demo|ide cloud)\b/.test(q) && !out.includes(`${SOURCEA_ORIGIN}/sourcea/forge/terminal`)) {
    out += `\n\nTry Forge Terminal: ${SOURCEA_ORIGIN}/sourcea/forge/terminal`;
  }
  return out;
}

function cleanKnownPublicAnswer(message, reply) {
  const q = String(message || "").toLowerCase();
  if (/\b(is .* live|running|status|up)\b/.test(q)) return reply;
  if (/\bhighest[- ]confidence\b/.test(q)) {
    return [
      "For Brain, confidence is not a title.",
      "",
      "It means Brain should use public evidence, live tools, clean links, and clear uncertainty handling before answering. If the evidence is thin, Brain should say so instead of sounding certain.",
    ].join("\n");
  }
  if (/\b(live receipt|live proof|proof live)\b/.test(q)) {
    return [
      "A live receipt is proof that a SourceA run actually happened: what ran, what was checked, and what result it produced.",
      "",
      `Live proof: ${SOURCEA_ORIGIN}/sourcea/proof/live`,
    ].join("\n");
  }
  return reply;
}

export function strangerRecoveryReply() {
  return [
    "You're right. That was a bad public-chat answer.",
    "",
    "You should never see internal source names or repo paths in this chat. Brain should answer like a public website guide: plain explanation, direct copyable links, and no internal file references.",
    "",
    `SourceA is an AI execution platform powered by Forge. It helps founders and agencies run real builds, automations, and agent workflows with proof of what ran. Try Forge Terminal here: ${SOURCEA_ORIGIN}/sourcea/forge/terminal`,
  ].join("\n");
}

export function sanitizeReply(reply, { message = "", intent = "core" } = {}) {
  const text = cleanKnownPublicAnswer(
    message,
    sanitizePublicText(addRequiredPublicLinks(message, normalizeSourceAVoice(cleanOpeningHedge(normalizePublicLinks(reply))))),
  ).trim();
  if (!text) return { ok: false, reason: "empty", text: "" };

  for (const pat of FORBIDDEN_PATTERNS) {
    if (pat.test(text)) {
      return { ok: false, reason: "forbidden_phrase", text };
    }
  }

  const lower = text.toLowerCase();
  if (!isPricingQuestion(message) && intent !== "buyer") {
    const lead = lower.slice(0, 100);
    if (PRICE_IN_LEAD.test(lead) && !lead.includes("forge terminal")) {
      return { ok: false, reason: "lead_price", text };
    }
  }

  return { ok: true, text };
}

function excerpt(content, max = 280) {
  const flat = String(content || "")
    .replace(/^#+\s+/gm, "")
    .replace(/\s+/g, " ")
    .trim();
  if (flat.length <= max) return flat;
  return flat.slice(0, max).trim() + "…";
}

function bestLink(hit) {
  if (hit?.www_url) return hit.www_url;
  const sp = String(hit?.source_path || "");
  if (sp.includes("forge/terminal") || sp.includes("forge-runtime")) return "/sourcea/forge/terminal";
  if (sp.includes("pricing")) return "/sourcea/pricing";
  if (sp.includes("factories")) return "/sourcea/factories/";
  if (sp.includes("offer") || sp.includes("48h")) return "/sourcea/offer";
  if (sp.includes("start") || sp.includes("sandbox")) return "/start";
  return "/sourcea/forge/terminal";
}

export function retrievalOnlyReply(message, retrieval, citations) {
  const hits = (retrieval?.hits || []).filter((h) => h.lane !== "rules" && h.kind !== "rule" && h.kind !== "rules");
  const top = hits.slice(0, 3);
  if (!top.length) {
    return {
      ok: true,
      reply:
        "I'm drawing from our public docs but need a sharper match. Try **Forge Terminal** in your browser: /sourcea/forge/terminal — or tell me what you're trying to build or automate.",
      mode: "retrieval_only",
      citations: citations || [],
    };
  }

  const lead = excerpt(top[0].content, 320);
  const link = canonicalPublicUrl(bestLink(top[0]));
  const intent = retrieval?.intent || "core";
  let route = link;
  if (intent === "developer") route = `${SOURCEA_ORIGIN}/sourcea/forge/terminal`;
  else if (intent === "buyer" && !String(message).toLowerCase().includes("forge")) route = `${SOURCEA_ORIGIN}/sourcea/pricing`;

  const reply = `${lead}\n\nBased on our live docs (${retrieval?.sources_consulted || top.length} sources matched). Next step: ${route}`;
  return { ok: true, reply, mode: "retrieval_only", citations: citations || [] };
}

export function lowConfidencePrefix(confidence) {
  const level = confidence?.level || "low";
  if (level === "high") return "";
  if (level === "medium") {
    return "I'm moderately confident on this — ";
  }
  return "I don't have a strong match in our public docs — ";
}
