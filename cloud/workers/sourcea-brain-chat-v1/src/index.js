/** Public Brain v4 — page-aware retrieval-first intelligence. */
import knowledgeBundle from "./knowledge-bundle.json";
import {
  isInternalMetaQuestion,
  isSensitiveInternalQuestion,
  lowConfidencePrefix,
  publicBoundaryReply,
  requestedLanguage,
  retrievalOnlyReply,
  sanitizeHistoryContent,
  sanitizePublicBody,
  sanitizeReply,
  strangerRecoveryReply,
  translationClarifierReply,
} from "./guardrails.js";
import {
  BRAIN_CORE,
  assembleBrainPrompt,
  brainRetrieve,
  inferPageContext,
  knowledgeMeta,
} from "./retrieval.js";
import { directLiveToolAnswer, gatherLiveTools, liveToolsMeta, liveToolsPrompt } from "./live-tools.js";

const CHAT_PATH = "/api/brain/chat/v1";
const STATUS_PATH = "/api/brain/status/v1";
const HEALTH_PATH = "/health";
const MAX_LEN = 2000;
const MAX_HISTORY = 12;
const WORKERS_AI_MODEL = "@cf/meta/llama-3.3-70b-instruct-fp8-fast";
const MODEL_TEMPERATURE = 0.2;
const TRACE_TTL_SECONDS = 60 * 60 * 24 * 365;
const TRACE_INDEX_LIMIT = 200;

const PUBLIC_MODELS = [
  { id: WORKERS_AI_MODEL, label: "Open-source Workers AI model", group: "Cloudflare Workers AI", cost: "$" },
];

const FORGE_TERMINAL_CORE = `${BRAIN_CORE}

Product mode: Forge Terminal public demo.
Reply in four labeled sections: 1) Bottom line 2) Business impact 3) Blockers 4) Next step. Under 400 words.`;

function cors(request) {
  const origin = request.headers.get("Origin") || "*";
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    Vary: "Origin",
    "Content-Type": "application/json",
    "Cache-Control": "no-store",
  };
}

function json(request, body, status = 200) {
  return new Response(JSON.stringify(sanitizePublicBody(body)), { status, headers: cors(request) });
}

function nowIso() {
  return new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
}

function safeId(raw, fallback = "") {
  const value = String(raw || "").trim().slice(0, 96);
  return value.replace(/[^a-zA-Z0-9_.:-]/g, "-") || fallback;
}

async function hash8(value) {
  const bytes = new TextEncoder().encode(String(value || ""));
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)]
    .slice(0, 8)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

function traceKv(env) {
  return env.BRAIN_CHAT_LOGS || env.CHAT_LOGS || env.BRAIN_CHAT_KV || null;
}

function publicTrace(trace) {
  return {
    trace_id: trace.trace_id,
    conversation_id: trace.conversation_id,
    turn_id: trace.turn_id,
    at: trace.at,
    decision_path: trace.decision_path,
    intent_alignment: trace.intent_alignment,
    logging: trace.logging,
  };
}

function intentAlignment({ message, retrieval, final, confidence, citations, liveTools }) {
  const q = String(message || "").toLowerCase();
  const intent = retrieval?.intent || "core";
  const routeByIntent = {
    buyer: "https://sourcea.app/sourcea/pricing",
    developer: "https://sourcea.app/sourcea/forge/terminal",
    investor: "https://sourcea.app/sourcea/investors",
    partner: "https://sourcea.app/start",
    core: "https://sourcea.app/sourcea/forge/terminal",
  };
  const reply = String(final?.reply || "");
  const issues = [];
  if (!reply.trim()) issues.push("empty_reply");
  const guardrail = String(final?.guardrail || "");
  if (guardrail && !/^(language_request|sensitive_internal_request|internal_meta_recovery)$/.test(guardrail)) {
    issues.push(`guardrail:${guardrail}`);
  }
  if ((confidence?.level || "") === "low" && !(citations || []).length && !(liveTools || []).length) {
    issues.push("low_confidence_no_evidence");
  }
  if (/\b(try|demo|browser|install|forge|ide|developer|api|code)\b/.test(q) && intent !== "developer") {
    issues.push("developer_intent_not_selected");
  }
  if (/\b(price|pricing|cost|buy|sandbox|offer)\b/.test(q) && intent !== "buyer") {
    issues.push("buyer_intent_not_selected");
  }
  const expected_route = routeByIntent[intent] || routeByIntent.core;
  return {
    intent,
    confidence_level: confidence?.level || "unknown",
    expected_route,
    outcome_oriented: reply.includes("https://sourcea.app") || reply.toLowerCase().includes("next step"),
    aligned: issues.length === 0,
    issues,
  };
}

async function buildTrace({
  request,
  body,
  message,
  history,
  product,
  requestedModel,
  pageCtx,
  retrieval,
  citations,
  confidence,
  liveTools,
  llmResult,
  final,
  provider,
  status = 200,
}) {
  const at = nowIso();
  const clientSession = safeId(body.session_id || body.sessionId || body.conversation_id || body.conversationId);
  const firstUser = history.find((item) => item.role === "user")?.content || message;
  const anonSeed = `${request.headers.get("User-Agent") || ""}|${pageCtx?.page_path || ""}|${firstUser}`;
  const conversation_id = clientSession || `anon-${await hash8(anonSeed)}`;
  const turnSeed = `${conversation_id}|${message}|${history.length}|${pageCtx?.page_path || ""}`;
  const turn_id = safeId(body.turn_id || body.turnId, `turn-${await hash8(turnSeed)}`);
  const trace_id = `trace-${await hash8(`${conversation_id}|${turn_id}|${final?.reply || ""}|${at}`)}`;
  const alignment = intentAlignment({ message, retrieval, final, confidence, citations, liveTools });
  const decision_path = [
    "request_validated",
    pageCtx?.page_path ? `page_context:${pageCtx.page_path}` : "page_context:none",
    `intent:${alignment.intent}`,
    `retrieval:${retrieval?.sources_consulted || 0}_sources`,
    `rules:${retrieval?.rules_applied || 0}`,
    `live_tools:${(liveTools || []).map((tool) => tool.id).join(",") || "none"}`,
    `provider:${provider || "unknown"}`,
    `reply_mode:${final?.mode || "unknown"}`,
    alignment.aligned ? "intent_aligned" : "intent_alignment_review",
  ];
  return {
    schema: "sourcea-brain-chat-turn-trace-v1",
    trace_id,
    conversation_id,
    turn_id,
    at,
    status,
    product: product || "brain",
    provider,
    model_requested: requestedModel || null,
    model_used: llmResult?.model_used || null,
    model_fallback: Boolean(llmResult?.fallback),
    request: {
      message,
      history,
      page_context: pageCtx || {},
    },
    decision_path,
    intent_alignment: alignment,
    retrieval: retrieval
      ? {
          intent: retrieval.intent,
          page_path: retrieval.page_path,
          page_lane: retrieval.page_lane,
          sources_consulted: retrieval.sources_consulted,
          rules_applied: retrieval.rules_applied,
          knowledge_hits: retrieval.knowledge_hits,
          source_paths: retrieval.source_paths,
          chunk_ids: retrieval.chunk_ids,
          confidence,
        }
      : null,
    live_tools: liveToolsMeta(liveTools || []),
    response: {
      ok: Boolean(final?.ok),
      reply_mode: final?.mode || null,
      guardrail: final?.guardrail || null,
      reply: final?.reply || "",
      citations: citations || [],
    },
    logging: {
      durable: false,
      binding: "pending",
    },
  };
}

async function persistTrace(env, trace) {
  const kv = traceKv(env);
  const loggable = { ...trace, logging: { durable: Boolean(kv), binding: kv ? "kv" : "console" } };
  if (!kv) {
    console.log(JSON.stringify({ type: "sourcea_brain_chat_trace", trace: loggable }));
    return;
  }
  await kv.put(`turn:${trace.trace_id}`, JSON.stringify(loggable), { expirationTtl: TRACE_TTL_SECONDS });
  const indexKey = `conversation:${trace.conversation_id}:turns`;
  let index = [];
  try {
    const raw = await kv.get(indexKey);
    if (raw) index = JSON.parse(raw);
  } catch {
    index = [];
  }
  index.unshift({
    trace_id: trace.trace_id,
    turn_id: trace.turn_id,
    at: trace.at,
    intent: trace.intent_alignment.intent,
    aligned: trace.intent_alignment.aligned,
  });
  await kv.put(indexKey, JSON.stringify(index.slice(0, TRACE_INDEX_LIMIT)), { expirationTtl: TRACE_TTL_SECONDS });
}

function recordTrace(ctx, env, trace) {
  trace.logging = { durable: Boolean(traceKv(env)), binding: traceKv(env) ? "kv" : "console" };
  if (ctx?.waitUntil) ctx.waitUntil(persistTrace(env, trace));
  else persistTrace(env, trace).catch((err) => console.log(`sourcea_brain_trace_failed:${String(err).slice(0, 160)}`));
}

function pageContextFromBody(body) {
  const pagePath = String(body.page_path || body.pagePath || "").trim();
  const saPage = String(body.sa_page || body.saPage || "").trim();
  const pageLane = String(body.page_lane || body.pageLane || "").trim();
  const ctx = inferPageContext(pagePath, saPage);
  if (pageLane) ctx.page_lane = pageLane;
  return ctx;
}

async function buildSystemPrompt(product, message, pageCtx, language = "") {
  const base = String(product || "").toLowerCase() === "forge_terminal" ? FORGE_TERMINAL_CORE : BRAIN_CORE;
  const retrieval = brainRetrieve(knowledgeBundle, message, {
    pageCtx,
    page_path: pageCtx.page_path,
    sa_page: pageCtx.sa_page,
  });
  const liveTools = await gatherLiveTools(message);
  const { prompt, citations, confidence } = assembleBrainPrompt(base, retrieval);
  const languageBlock =
    language && language !== "translate"
      ? `\n\nLANGUAGE REQUEST: Answer in ${language}. Do not say you are English-only. Keep SourceA facts grounded in the retrieved/live sources and keep URLs unchanged.`
      : "";
  return { prompt: prompt + liveToolsPrompt(liveTools) + languageBlock, citations, confidence, retrieval, liveTools };
}

function statusBody(env) {
  const ready = Boolean(env.AI);
  const current = WORKERS_AI_MODEL;
  const traceReady = Boolean(traceKv(env));
  return {
    schema: "sourcea-brain-chat-status-v1",
    ok: true,
    service: "sourcea-brain-chat-v1",
    ai_model_ready: ready,
    trace_storage_ready: traceReady,
    trace_storage: traceReady ? "kv" : "console",
    model: current,
    default_model: current,
    models: PUBLIC_MODELS,
    provider: "workers_ai",
    plane: "cloudflare_worker",
    max_message_len: MAX_LEN,
    hint: "Brain v5 — vector retrieval · read-only live tools · 112+ live sources",
    knowledge: knowledgeMeta(knowledgeBundle),
    live_tools: ["proof_status", "products_catalog", "factories_catalog", "pricing_route", "forge_terminal_route", "plan_registry"],
    endpoints: {
      chat: CHAT_PATH,
      status: STATUS_PATH,
      health: HEALTH_PATH,
    },
    at: nowIso(),
  };
}

function workersAIReplyText(result) {
  if (!result) return "";
  if (typeof result === "string") return result.trim();
  if (typeof result.response === "string") return result.response.trim();
  if (typeof result.result?.response === "string") return result.result.response.trim();
  const choice = result.choices?.[0]?.message?.content || result.result?.choices?.[0]?.message?.content;
  return String(choice || "").trim();
}

async function chatWorkersAI(env, messages, product, _requestedModel, systemPrompt) {
  if (!env.AI || typeof env.AI.run !== "function") {
    return { ok: false, reply: "", llm_error: "workers_ai_binding_missing" };
  }
  try {
    const result = await env.AI.run(WORKERS_AI_MODEL, {
      messages: [{ role: "system", content: systemPrompt }, ...messages.slice(-MAX_HISTORY)],
      temperature: MODEL_TEMPERATURE,
      max_tokens: product === "forge_terminal" ? 600 : 900,
    });
    const reply = workersAIReplyText(result);
    if (reply) return { ok: true, reply, model_used: WORKERS_AI_MODEL, fallback: false };
    return { ok: false, reply: "", llm_error: "empty_workers_ai_reply" };
  } catch (err) {
    return { ok: false, reply: "", llm_error: `workers_ai_error:${String(err?.message || err).slice(0, 180)}` };
  }
}

function finalizeReply(message, retrieval, citations, confidence, llmResult, liveTools = []) {
  let mode = "llm";
  let reply = "";
  let ok = true;
  let guardrail = null;
  const direct = directLiveToolAnswer(message, liveTools);

  if (direct) {
    const check = sanitizeReply(direct, { message, intent: retrieval.intent });
    return {
      ok: true,
      reply: check.text,
      mode: "live_tool_direct",
      guardrail: check.ok ? null : check.reason,
    };
  }

  if (llmResult.ok && llmResult.reply) {
    const check = sanitizeReply(llmResult.reply, { message, intent: retrieval.intent });
    if (check.ok) {
      reply = check.text;
      if (confidence?.level === "low") {
        reply = lowConfidencePrefix(confidence) + reply;
        mode = "llm_low_confidence";
      } else if (confidence?.level === "medium") {
        reply = lowConfidencePrefix(confidence) + reply;
      }
    } else {
      guardrail = check.reason;
      const fallback = retrievalOnlyReply(message, retrieval, citations);
      reply = fallback.reply;
      mode = "retrieval_guardrail";
    }
  } else {
    const fallback = retrievalOnlyReply(message, retrieval, citations);
    reply = fallback.reply;
    mode = "retrieval_only";
    ok = true;
  }

  return { ok, reply, mode, guardrail };
}

async function handlePost(request, env, ctx) {
  let body;
  try {
    body = await request.json();
  } catch {
    body = {};
  }
  const action = String(body.action || "chat").toLowerCase();
  if (action === "status" || action === "ping") {
    return json(request, statusBody(env));
  }
  const message = String(body.message || body.text || "").trim();
  if (!message) {
    return json(request, { ok: false, schema: "sourcea-brain-chat-receipt-v1", error: "message_required" }, 400);
  }
  if (message.length > MAX_LEN) {
    return json(
      request,
      { ok: false, schema: "sourcea-brain-chat-receipt-v1", error: "message_too_long", max: MAX_LEN },
      400,
    );
  }
  const history = [];
  if (Array.isArray(body.history)) {
    for (const item of body.history.slice(-MAX_HISTORY)) {
      if (!item || typeof item !== "object") continue;
      const role = String(item.role || "").toLowerCase();
      const content = String(item.content || "").trim();
      if ((role === "user" || role === "assistant") && content) {
        history.push({ role, content: sanitizeHistoryContent(content).slice(0, MAX_LEN) });
      }
    }
  }
  history.push({ role: "user", content: message });
  const product = String(body.product || "").toLowerCase();
  const requestedModel = String(body.model || "").trim();
  const pageCtx = pageContextFromBody(body);
  pageCtx.sa_page = pageCtx.sa_page || String(body.sa_page || body.saPage || "");
  const language = requestedLanguage(message);

  if (language === "translate") {
    const reply = translationClarifierReply();
    const trace = await buildTrace({
      request,
      body,
      message,
      history,
      product,
      requestedModel,
      pageCtx,
      retrieval: {
        intent: "core",
        page_path: pageCtx.page_path,
        page_lane: pageCtx.page_lane,
        sources_consulted: 0,
        rules_applied: 1,
        knowledge_hits: 0,
        source_paths: [],
        chunk_ids: [],
      },
      citations: [],
      confidence: { score: 1, level: "high", hits: 0 },
      liveTools: [],
      llmResult: {},
      final: { ok: true, reply, mode: "language_support", guardrail: "language_request" },
      provider: "guardrail",
    });
    recordTrace(ctx, env, trace);
    return json(request, {
      schema: "sourcea-brain-chat-receipt-v1",
      ok: true,
      reply,
      product: product || "brain",
      provider: "guardrail",
      model: null,
      model_requested: requestedModel || null,
      model_fallback: false,
      reply_mode: "language_support",
      guardrail: "language_request",
      citations: [],
      confidence: { score: 1, level: "high", hits: 0 },
      retrieval: {
        intent: "core",
        page_path: pageCtx.page_path,
        page_lane: pageCtx.page_lane,
        sources_consulted: 0,
        rules_applied: 1,
        chunk_ids: [],
        vector: "semantic_hash_v1",
      },
      live_tools: [],
      knowledge: knowledgeMeta(knowledgeBundle),
      at: nowIso(),
      message: "Brain handled language request",
      trace: publicTrace(trace),
      trace_id: trace.trace_id,
      conversation_id: trace.conversation_id,
      turn_id: trace.turn_id,
    });
  }

  if (isSensitiveInternalQuestion(message)) {
    const reply = publicBoundaryReply();
    const trace = await buildTrace({
      request,
      body,
      message,
      history,
      product,
      requestedModel,
      pageCtx,
      retrieval: {
        intent: "core",
        page_path: pageCtx.page_path,
        page_lane: pageCtx.page_lane,
        sources_consulted: 0,
        rules_applied: 1,
        knowledge_hits: 0,
        source_paths: [],
        chunk_ids: [],
      },
      citations: [],
      confidence: { score: 1, level: "high", hits: 0 },
      liveTools: [],
      llmResult: {},
      final: { ok: true, reply, mode: "public_boundary_refusal", guardrail: "sensitive_internal_request" },
      provider: "guardrail",
    });
    recordTrace(ctx, env, trace);
    return json(request, {
      schema: "sourcea-brain-chat-receipt-v1",
      ok: true,
      reply,
      product: product || "brain",
      provider: "guardrail",
      model: null,
      model_requested: requestedModel || null,
      model_fallback: false,
      reply_mode: "public_boundary_refusal",
      guardrail: "sensitive_internal_request",
      citations: [],
      confidence: { score: 1, level: "high", hits: 0 },
      retrieval: {
        intent: "core",
        page_path: pageCtx.page_path,
        page_lane: pageCtx.page_lane,
        sources_consulted: 0,
        rules_applied: 1,
        chunk_ids: [],
      },
      knowledge: knowledgeMeta(knowledgeBundle),
      at: nowIso(),
      message: "Brain protected public boundary",
      trace: publicTrace(trace),
      trace_id: trace.trace_id,
      conversation_id: trace.conversation_id,
      turn_id: trace.turn_id,
    });
  }

  if (isInternalMetaQuestion(message)) {
    const reply = strangerRecoveryReply();
    const trace = await buildTrace({
      request,
      body,
      message,
      history,
      product,
      requestedModel,
      pageCtx,
      retrieval: {
        intent: "core",
        page_path: pageCtx.page_path,
        page_lane: pageCtx.page_lane,
        sources_consulted: 0,
        rules_applied: 1,
        knowledge_hits: 0,
        source_paths: [],
        chunk_ids: [],
      },
      citations: [],
      confidence: { score: 1, level: "high", hits: 0 },
      liveTools: [],
      llmResult: {},
      final: { ok: true, reply, mode: "stranger_recovery", guardrail: "internal_meta_recovery" },
      provider: "guardrail",
    });
    recordTrace(ctx, env, trace);
    return json(request, {
      schema: "sourcea-brain-chat-receipt-v1",
      ok: true,
      reply,
      product: product || "brain",
      provider: "guardrail",
      model: null,
      model_requested: requestedModel || null,
      model_fallback: false,
      reply_mode: "stranger_recovery",
      guardrail: "internal_meta_recovery",
      citations: [],
      confidence: { score: 1, level: "high", hits: 0 },
      retrieval: {
        intent: "core",
        page_path: pageCtx.page_path,
        page_lane: pageCtx.page_lane,
        sources_consulted: 0,
        rules_applied: 1,
        chunk_ids: [],
      },
      knowledge: knowledgeMeta(knowledgeBundle),
      at: nowIso(),
      message: "Brain recovered public chat boundary",
      trace: publicTrace(trace),
      trace_id: trace.trace_id,
      conversation_id: trace.conversation_id,
      turn_id: trace.turn_id,
    });
  }

  const effectiveMessage =
    language && language !== "translate"
      ? `Explain SourceA briefly in ${language}. The visitor's message was: ${message}`
      : message;
  const { prompt, citations, confidence, retrieval, liveTools } = await buildSystemPrompt(
    product,
    effectiveMessage,
    pageCtx,
    language,
  );
  const llmResult = await chatWorkersAI(env, history, product, requestedModel, prompt);
  const final = finalizeReply(message, retrieval, citations, confidence, llmResult, liveTools);
  const provider =
    final.mode === "live_tool_direct" ? "live_tool" : final.mode.startsWith("retrieval") ? "retrieval" : "workers_ai";
  const trace = await buildTrace({
    request,
    body,
    message,
    history,
    product,
    requestedModel,
    pageCtx,
    retrieval,
    citations: final.ok ? citations : [],
    confidence: final.ok ? confidence : null,
    liveTools: final.ok ? liveTools : [],
    llmResult,
    final,
    provider,
  });
  recordTrace(ctx, env, trace);

  return json(request, {
    schema: "sourcea-brain-chat-receipt-v1",
    ok: final.ok,
    reply: final.reply,
    product: product || "brain",
    provider,
    model: llmResult.model_used || WORKERS_AI_MODEL,
    model_requested: requestedModel || null,
    model_fallback: !!llmResult.fallback,
    reply_mode: final.mode,
    guardrail: final.guardrail,
    citations: final.ok ? citations : [],
    confidence: final.ok ? confidence : null,
    retrieval: final.ok
      ? {
          intent: retrieval.intent,
          page_path: retrieval.page_path,
          page_lane: retrieval.page_lane,
          sources_consulted: retrieval.sources_consulted,
          rules_applied: retrieval.rules_applied,
          chunk_ids: retrieval.chunk_ids,
          vector: "semantic_hash_v1",
        }
      : null,
    live_tools: final.ok ? liveToolsMeta(liveTools) : [],
    knowledge: knowledgeMeta(knowledgeBundle),
    at: nowIso(),
    message: final.ok ? "Brain replied" : final.reply,
    trace: publicTrace(trace),
    trace_id: trace.trace_id,
    conversation_id: trace.conversation_id,
    turn_id: trace.turn_id,
  });
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors(request) });
    }
    if (url.pathname === HEALTH_PATH && request.method === "GET") {
      return json(request, {
        ok: true,
        schema: "sourcea-brain-chat-health-v1",
        service: "sourcea-brain-chat-v1",
        ai_model_ready: Boolean(env.AI),
        trace_storage_ready: Boolean(traceKv(env)),
        at: nowIso(),
      });
    }
    if (url.pathname === STATUS_PATH && request.method === "GET") {
      return json(request, statusBody(env));
    }
    if (url.pathname !== CHAT_PATH) {
      return json(request, { ok: false, error: "not_found" }, 404);
    }
    if (request.method === "GET") {
      return json(request, statusBody(env));
    }
    if (request.method === "POST") {
      return handlePost(request, env, ctx);
    }
    return json(request, { ok: false, error: "method_not_allowed" }, 405);
  },
};
