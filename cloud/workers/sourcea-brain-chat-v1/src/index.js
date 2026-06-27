/** Public Brain chat — OpenRouter proxy for sourcea.app (key never in browser). */
import knowledgeBundle from "./knowledge-bundle.json";
import { buildGroundedPrompt, knowledgeMeta, retrieveChunks } from "./retrieval.js";

const CHAT_PATH = "/api/brain/chat/v1";
const MAX_LEN = 2000;
const MAX_HISTORY = 12;
const DEFAULT_MODEL = "google/gemini-2.5-flash";

/** Public demo models (OpenRouter) — shown in UI; server tries fallbacks on 503. */
const PUBLIC_MODELS = [
  { id: "google/gemini-2.5-flash", label: "Gemini 2.5 Flash", group: "Google", cost: "$" },
  { id: "google/gemini-2.5-flash-lite-preview-06-17", label: "Gemini Flash-Lite", group: "Google", cost: "$" },
  { id: "anthropic/claude-3.5-haiku", label: "Claude 3.5 Haiku", group: "Anthropic", cost: "$" },
  { id: "anthropic/claude-3.5-sonnet", label: "Claude 3.5 Sonnet", group: "Anthropic", cost: "$$$" },
  { id: "openai/gpt-4o-mini", label: "GPT-4o mini", group: "OpenAI", cost: "$" },
  { id: "deepseek/deepseek-chat-v3-0324", label: "DeepSeek V4", group: "OpenRouter", cost: "$" },
];

const FALLBACK_MODELS = PUBLIC_MODELS.map((m) => m.id);

const FORGE_TERMINAL_DEMO_SYSTEM = `You are Forge Terminal on sourcea.app — a founder-friendly advisor for strangers trying the public living-chat demo.

Reply in plain English with four short labeled sections:
1) Bottom line
2) What this means for their business
3) Blockers or risks
4) Suggested next step

Rules:
- Helpful operator tone — not a sales bot
- Never mention OpenRouter, models, API keys, receipts, PASS/BLOCK, or internal governance
- This public page has no workspace — mention Mac Forge IDE adds workspace, quality gate, and cloud dispatch when relevant
- Keep under 400 words`;

const BRAIN_SYSTEM = `You are Brain on sourcea.app — a sharp, honest guide for strangers. Not a pushy sales bot.

ONE-LINE (when asked "what is SourceA?"):
SourceA is an AI execution platform powered by Forge — it runs real builds, automations, agent workflows, and governed development pipelines for founders and agencies. Proof and receipts are built in; they are not the whole product.

WHAT SOURCEA IS NOT:
- Not "just records" or "just verification software"
- Not a generic ChatGPT wrapper

WHAT FORGE IS:
- Forge Terminal: the execution desk — living chat, workspace, agents, quality gate, cloud dispatch
- Public try (no install): /sourcea/forge/terminal
- Flow: idea → prompt forge → agents → quality gate → execute (Cursor / cloud)

CONVERSATION ORDER:
1) Their problem / what they want to accomplish
2) One concrete sentence on what SourceA + Forge does for that
3) ONE matched example (specific, not abstract)
4) Why this beats chat-only AI
5) Price or booking ONLY if they ask or value is clear

PRICING:
- NEVER open with dollar amounts
- If they ask: scope-dependent; typical governed deploy setup is often in the $1,500–$5,000 range — say "depends on scope" first
- /sourcea/offer · /sourcea/pricing

IDE / CLOUD QUESTIONS:
- Lead with YES partially: Forge Terminal is the execution desk — try in browser at /sourcea/forge/terminal; full Mac IDE for founders
- Never open with "We don't offer" — reframe to what Forge IS
- Not a generic hosted IDE clone — governed AI execution with workspace and agents
- Ask what they need: app generation, coding agents, deployment, team workflows?

"YOU JUST GIVE ME RECORDS?" (recover honestly):
- Acknowledge: fair pushback — records alone are not the product
- Reframe: Forge runs the work; proof shows clients what ran, what changed, and that it passed quality

EXACT HELP EXAMPLES (use when they ask for lists — 3 bullets, concrete):
- Agency QBR prep: scope "audit client AI deliverables" → agents review outputs → quality gate → client-ready summary + audit trail
- Content engine: weekly B2B posts → prompt forge → batch runs → founder approves → per-client tracked delivery
- Dev/automation: "add Stripe webhook" → advisor plans → patch proposal → verify → route to Cursor or cloud execute

TONE:
- Plain English, short paragraphs, bullets for lists
- Max one cal.com/sourcea/proof-demo link per reply unless they want to book
- Never mention OpenRouter, models, API keys, PASS/BLOCK, factories, or governance jargon
- Be interesting — match their energy, answer the actual question first`;

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

function buildSystemPrompt(product, message) {
  const base = systemForProduct(product);
  const hits = retrieveChunks(knowledgeBundle, message, 8);
  return buildGroundedPrompt(base, hits);
}

function statusBody(env) {
  const ready = Boolean(env.OPENROUTER_API_KEY);
  const current = env.OPENROUTER_MODEL || DEFAULT_MODEL;
  const knowledge = knowledgeMeta(knowledgeBundle);
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
    hint: "Brain — execution platform guide for Forge, examples, and booking",
    knowledge,
  };
}

function systemForProduct(product) {
  return String(product || "").toLowerCase() === "forge_terminal" ? FORGE_TERMINAL_DEMO_SYSTEM : BRAIN_SYSTEM;
}

async function chatOpenRouter(env, messages, product, requestedModel, systemPrompt) {
  const key = env.OPENROUTER_API_KEY;
  if (!key) {
    return {
      ok: false,
      reply: "Brain is not available right now — book a demo at cal.com/sourcea/proof-demo",
    };
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
    if (status !== 429 && status !== 503 && status !== 502 && status !== 504) {
      break;
    }
  }
  return { ok: false, reply: lastErr || "Brain offline — try proof chips or book a demo" };
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
        history.push({ role, content: content.slice(0, MAX_LEN) });
      }
    }
  }
  history.push({ role: "user", content: message });
  const product = String(body.product || "").toLowerCase();
  const requestedModel = String(body.model || "").trim();
  const { prompt, citations } = buildSystemPrompt(product, message);
  const result = await chatOpenRouter(env, history, product, requestedModel, prompt);
  const { ok, reply, model_used, fallback } = result;
  return json(request, {
    schema: "sourcea-brain-chat-receipt-v1",
    ok,
    reply,
    product: product || "brain",
    provider: "openrouter",
    model: model_used || env.OPENROUTER_MODEL || DEFAULT_MODEL,
    model_requested: requestedModel || null,
    model_fallback: !!fallback,
    citations: ok ? citations : [],
    knowledge: knowledgeMeta(knowledgeBundle),
    at: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
    message: ok ? "Brain replied" : reply,
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
