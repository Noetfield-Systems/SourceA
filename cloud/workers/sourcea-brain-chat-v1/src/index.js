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
const MAX_LEN = 2000;
const MAX_HISTORY = 12;
const DEFAULT_MODEL = "google/gemini-2.5-flash";

const PUBLIC_MODELS = [
  { id: "google/gemini-2.5-flash", label: "Gemini 2.5 Flash", group: "Google", cost: "$" },
  { id: "google/gemini-2.5-flash-lite-preview-06-17", label: "Gemini Flash-Lite", group: "Google", cost: "$" },
  { id: "anthropic/claude-3.5-haiku", label: "Claude 3.5 Haiku", group: "Anthropic", cost: "$" },
  { id: "anthropic/claude-3.5-sonnet", label: "Claude 3.5 Sonnet", group: "Anthropic", cost: "$$$" },
  { id: "openai/gpt-4o-mini", label: "GPT-4o mini", group: "OpenAI", cost: "$" },
  { id: "deepseek/deepseek-chat-v3-0324", label: "DeepSeek V4", group: "OpenRouter", cost: "$" },
];

const FALLBACK_MODELS = PUBLIC_MODELS.map((m) => m.id);

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
  };
}

function json(request, body, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: cors(request) });
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
  const ready = Boolean(env.OPENROUTER_API_KEY);
  const current = env.OPENROUTER_MODEL || DEFAULT_MODEL;
  return {
    schema: "sourcea-brain-chat-status-v1",
    ok: true,
    openrouter_ready: ready,
    model: current,
    default_model: current,
    models: PUBLIC_MODELS,
    provider: "openrouter",
    plane: "cloudflare_worker",
    max_message_len: MAX_LEN,
    hint: "Brain v5 — vector retrieval · read-only live tools · 112+ live sources",
    knowledge: knowledgeMeta(knowledgeBundle),
    live_tools: ["proof_status", "products_catalog", "factories_catalog", "pricing_route", "forge_terminal_route"],
  };
}

async function chatOpenRouter(env, messages, product, requestedModel, systemPrompt) {
  const key = env.OPENROUTER_API_KEY;
  if (!key) {
    return { ok: false, reply: "", llm_error: "no_api_key" };
  }
  const preferred = String(requestedModel || env.OPENROUTER_MODEL || DEFAULT_MODEL).trim();
  const chain = [preferred, ...FALLBACK_MODELS.filter((m) => m !== preferred)];
  let lastErr = "";
  for (const model of chain) {
    const resp = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${key}`,
        "Content-Type": "application/json",
        "HTTP-Referer": "https://sourcea.app",
        "X-Title": "SourceA Brain",
      },
      body: JSON.stringify({
        model,
        messages: [{ role: "system", content: systemPrompt }, ...messages.slice(-MAX_HISTORY)],
        temperature: 0.38,
        max_tokens: product === "forge_terminal" ? 600 : 900,
      }),
    });
    if (resp.ok) {
      const data = await resp.json();
      const reply = (data.choices?.[0]?.message?.content || "").trim();
      return { ok: true, reply, model_used: model, fallback: model !== preferred };
    }
    const status = resp.status;
    let detail = "";
    try {
      detail = JSON.stringify(await resp.json());
    } catch {
      detail = await resp.text();
    }
    lastErr = `Brain offline (${status}) — ${detail.slice(0, 200)}`;
    if (status !== 429 && status !== 503 && status !== 502 && status !== 504) break;
  }
  return { ok: false, reply: lastErr || "Brain offline", llm_error: lastErr };
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
      reply: check.ok ? check.text : direct,
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

async function handlePost(request, env) {
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
    return json(request, {
      schema: "sourcea-brain-chat-receipt-v1",
      ok: true,
      reply: translationClarifierReply(),
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
      at: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
      message: "Brain handled language request",
    });
  }

  if (isSensitiveInternalQuestion(message)) {
    return json(request, {
      schema: "sourcea-brain-chat-receipt-v1",
      ok: true,
      reply: publicBoundaryReply(),
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
      at: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
      message: "Brain protected public boundary",
    });
  }

  if (isInternalMetaQuestion(message)) {
    return json(request, {
      schema: "sourcea-brain-chat-receipt-v1",
      ok: true,
      reply: strangerRecoveryReply(),
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
      at: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
      message: "Brain recovered public chat boundary",
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
  const llmResult = await chatOpenRouter(env, history, product, requestedModel, prompt);
  const final = finalizeReply(message, retrieval, citations, confidence, llmResult, liveTools);

  return json(request, {
    schema: "sourcea-brain-chat-receipt-v1",
    ok: final.ok,
    reply: final.reply,
    product: product || "brain",
    provider: final.mode.startsWith("retrieval") ? "retrieval" : "openrouter",
    model: llmResult.model_used || env.OPENROUTER_MODEL || DEFAULT_MODEL,
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
    at: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
    message: final.ok ? "Brain replied" : final.reply,
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors(request) });
    }
    if (url.pathname !== CHAT_PATH) {
      return json(request, { ok: false, error: "not_found" }, 404);
    }
    if (request.method === "GET") {
      return json(request, statusBody(env));
    }
    if (request.method === "POST") {
      return handlePost(request, env);
    }
    return json(request, { ok: false, error: "method_not_allowed" }, 405);
  },
};
