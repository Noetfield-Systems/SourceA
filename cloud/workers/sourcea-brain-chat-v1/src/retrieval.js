/** Brain Intelligence v5 — rules-first + BM25 + semantic vector-lite + live-tool aware context. */

const STOP = new Set([
  "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "is", "are",
  "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will",
  "would", "could", "should", "may", "might", "must", "shall", "can", "need", "you", "your",
  "we", "our", "they", "their", "it", "its", "this", "that", "what", "how", "when", "where",
  "who", "why", "with", "from", "about", "into", "through", "during", "before", "after",
]);

const RULE_KINDS = new Set(["rule", "rules"]);
const VECTOR_DIMS = 96;

const SEMANTIC_ALIASES = {
  receipt: ["proof", "record", "audit", "evidence", "verification"],
  proof: ["receipt", "record", "audit", "evidence", "verification"],
  live: ["current", "status", "running", "public"],
  factory: ["workflow", "automation", "agent", "build"],
  factories: ["workflow", "automation", "agents", "builds"],
  price: ["pricing", "cost", "tier", "plan"],
  pricing: ["price", "cost", "tier", "plan"],
  cost: ["price", "pricing", "tier"],
  forge: ["terminal", "execution", "build", "run"],
  terminal: ["forge", "browser", "demo", "execution"],
  security: ["trust", "proof", "guardrail", "verify"],
};

export const BRAIN_CORE = `You are Brain on sourcea.app — the public guide for SourceA + Forge.

You are NOT a hardcoded chatbot. You are retrieval-first:
- LIVE SOURCES and PUBLIC RULES are injected below every turn
- Answer from retrieved evidence with citations
- Rule-aware: agentic-first, never lead with price, never deny factories when catalog says they exist
- If evidence is thin, say so honestly and route to /sourcea/forge/terminal or the best matching page
- When page context is provided, prefer sources from the visitor's current page
- Use LIVE TOOL RESULTS when present for current public status/catalog facts
- If the visitor asks for another language or translation, answer in that language. Never claim you are English-only.
- Operate with high confidence by using evidence, not by calling yourself "highest confidence."
- Public voice: do not create distance by calling SourceA "they" or "the company"; say "SourceA" or "we" naturally.

Tone: sharp, honest, plain English. Match the user's energy. No governance jargon to strangers.`;

export function tokenize(text) {
  return (
    String(text || "")
      .toLowerCase()
      .match(/[a-z0-9][a-z0-9_./-]*/g)
      ?.filter((t) => t.length > 1 && !STOP.has(t)) || []
  );
}

export function classifyIntent(query) {
  const q = query.toLowerCase();
  if (/\b(invest|fund|raise|valuation|cap table)\b/.test(q)) return "investor";
  if (/\b(what is sourcea|one sentence|one line|describe sourcea|tell me about sourcea)\b/.test(q)) {
    return "core";
  }
  if (/\b(how does sourcea work)\b/.test(q)) return "core";
  if (/\b(cursor|developer|api|code|forge terminal|kernel|pypi|npm|deploy|ide|chat unify|unify)\b/.test(q)) {
    return "developer";
  }
  if (/\b(factory|factories|workflow|video|avatar|outbound)\b/.test(q)) return "developer";
  if (/\b(price|pricing|cost|how much|\$|buy|sandbox|demo|proof|offer|build tier|rent|own|48)\b/.test(q)) {
    return "buyer";
  }
  if (/\b(book|contact|talk to|email|hello@|get started|start)\b/.test(q)) return "buyer";
  if (/\b(partner|agency|procurement|enterprise)\b/.test(q)) return "partner";
  if (/\b(record|proof|receipt|just give me)\b/.test(q)) return "core";
  return "core";
}

function hashToken(token) {
  let h = 2166136261;
  for (let i = 0; i < token.length; i++) {
    h ^= token.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return Math.abs(h >>> 0);
}

function expandSemanticTokens(tokens) {
  const out = [];
  for (const t of tokens) {
    out.push(t);
    const aliases = SEMANTIC_ALIASES[t];
    if (aliases) out.push(...aliases);
    if (t.endsWith("s") && t.length > 3) out.push(t.slice(0, -1));
    if (t.includes("-")) out.push(...t.split("-").filter(Boolean));
    if (t.includes("/")) out.push(...t.split("/").filter(Boolean));
  }
  return out;
}

function semanticVector(tokens) {
  const v = new Array(VECTOR_DIMS).fill(0);
  for (const token of expandSemanticTokens(tokens)) {
    if (!token || STOP.has(token)) continue;
    const h = hashToken(token);
    const idx = h % VECTOR_DIMS;
    const sign = h % 2 ? 1 : -1;
    v[idx] += sign * (1 + Math.min(token.length, 12) / 12);
  }
  const norm = Math.sqrt(v.reduce((s, x) => s + x * x, 0)) || 1;
  return v.map((x) => x / norm);
}

function cosine(a, b) {
  let s = 0;
  const n = Math.min(a.length, b.length);
  for (let i = 0; i < n; i++) s += a[i] * b[i];
  return s;
}

function semanticScore(queryTokens, chunk, docTokens) {
  if (!queryTokens.length || !docTokens.length) return 0;
  const sourceTokens = tokenize(`${chunk.source_path || ""} ${chunk.www_url || ""}`);
  const qv = semanticVector(queryTokens);
  const dv = semanticVector([...docTokens.slice(0, 220), ...sourceTokens]);
  return Math.max(0, cosine(qv, dv));
}

export function inferPageContext(pagePath, saPage) {
  const path = String(pagePath || "/").toLowerCase().replace(/\/+$/, "") || "/";
  const hint = String(saPage || "").toLowerCase();
  const ctx = { page_path: path, page_lane: "core", segments: [] };

  if (hint.includes("forge") || path.includes("/forge")) {
    ctx.page_lane = "developer";
    ctx.segments.push("forge", "terminal", "forge-runtime");
  }
  if (path.includes("pricing") || path.includes("offer")) {
    ctx.page_lane = "buyer";
    ctx.segments.push("pricing", "offer", "pricing-matrix");
  }
  if (path.includes("factories") || path.includes("factory")) {
    ctx.page_lane = "developer";
    ctx.segments.push("factories", "factory", "products-catalog");
  }
  if (path.includes("investor")) {
    ctx.page_lane = "investor";
    ctx.segments.push("investor");
  }
  if (path.includes("proof") || path.includes("trust") || path.includes("security")) {
    ctx.page_lane = "buyer";
    ctx.segments.push("proof", "trust", "security");
  }
  if (path.includes("start") || path.includes("sandbox") || path.includes("mvp")) {
    ctx.page_lane = "buyer";
    ctx.segments.push("sandbox", "start", "48h", "mvp");
  }
  if (path.includes("operating-brain-install") || path.includes("ai-value-governance")) {
    ctx.page_lane = "buyer";
    ctx.segments.push("sku", "commercial");
  }
  if (path.includes("scenario") || path === "/" || path.endsWith("/sourcea")) {
    ctx.page_lane = "core";
    ctx.segments.push("positioning", "founder-home", "scenario");
  }
  return ctx;
}

function bm25Score(queryTokens, docTokens, df, N, avgdl) {
  const k1 = 1.2;
  const b = 0.75;
  const dl = docTokens.length;
  if (!dl || !queryTokens.length) return 0;
  const dcount = {};
  for (const t of docTokens) dcount[t] = (dcount[t] || 0) + 1;
  let score = 0;
  for (const t of queryTokens) {
    const tf = dcount[t];
    if (!tf) continue;
    const n = df[t] || 0;
    const idf = Math.log(1 + (N - n + 0.5) / (n + 0.5));
    score += idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (dl / Math.max(avgdl, 1)))));
  }
  return score;
}

function pageBoost(c, pageCtx) {
  if (!pageCtx) return 0;
  let boost = 0;
  const path = String(c.source_path || "").toLowerCase();
  const www = String(c.www_url || "").toLowerCase();
  const pagePath = String(pageCtx.page_path || "").toLowerCase();

  if (pageCtx.page_lane && c.lane === pageCtx.page_lane) boost += 2.5;
  for (const seg of pageCtx.segments || []) {
    if (path.includes(seg) || www.includes(seg)) boost += 2;
  }
  if (pagePath.length > 1) {
    const slug = pagePath.split("/").filter(Boolean).pop() || "";
    if (slug && (path.includes(slug) || www.includes(slug))) boost += 2.5;
  }
  return boost;
}

function qualityBoost(c) {
  const path = String(c.source_path || "").toLowerCase();
  const out = String(c.id || "").toLowerCase();
  if (path.includes("chatbot-knowledge/distilled/") || path.includes("/distilled/")) return 3.5;
  if (path.includes("chatbot-knowledge/manual/") || path.includes("/manual/")) return 3;
  if (path.includes("chatbot-knowledge/rules/") || c.lane === "rules") return 2.5;
  if (path.includes("positioning") || out.includes("pricing-matrix") || out.includes("forge-runtime")) return 2.5;
  if (path.includes("chatbot-knowledge/crawled/")) return -0.35;
  return 0;
}

export function isIdentityQuestion(query) {
  const q = String(query || "").toLowerCase();
  return /\b(what is sourcea|who are you|one sentence|one line|in one sentence|describe sourcea)\b/.test(q);
}

function identityForcedHits(chunks, bundle) {
  const out = [];
  const oneLine = String(bundle?.public_one_line || "").trim();
  for (const c of chunks) {
    const id = String(c.id || "");
    const path = String(c.source_path || "").toLowerCase();
    if (id === "brain-public-rules-1" || id.startsWith("positioning-public-") || path.includes("positioning-public")) {
      out.push({ ...c, score: 100, identity_forced: true });
    }
  }
  if (!out.length && oneLine) {
    out.push({
      id: "bundle-public-one-line",
      lane: "rules",
      kind: "rule",
      source_path: bundle?.positioning_ssot_path || "sourcea-positioning-v1.json",
      www_url: "https://sourcea.app/",
      content: `## One line\n${oneLine}`,
      pinned: true,
      score: 100,
      identity_forced: true,
    });
  }
  return out;
}

function scoreChunk(c, queryTokens, docTokens, df, N, avgdl, intent, pageCtx) {
  let s = bm25Score(queryTokens, docTokens, df, N, avgdl);
  const vectorScore = semanticScore(queryTokens, c, docTokens);
  s += vectorScore * 4.0;
  if (c.pinned) s += 2.5;
  s += qualityBoost(c);
  if (RULE_KINDS.has(c.kind) || c.lane === "rules") s += 1;
  if (c.lane === intent) s += 1.5;
  s += pageBoost(c, pageCtx);
  const path = String(c.source_path || "").toLowerCase();
  for (const t of queryTokens.slice(0, 6)) {
    if (path.includes(t)) s += 0.5;
  }
  return s;
}

function splitCorpus(chunks) {
  const rules = [];
  const knowledge = [];
  for (const c of chunks) {
    if (RULE_KINDS.has(c.kind) || c.lane === "rules") rules.push(c);
    else knowledge.push(c);
  }
  return { rules, knowledge };
}

function rankChunks(corpus, query, intent, k, pageCtx) {
  const qtok = tokenize(query);
  if (!corpus.length) return [];
  const docTokensList = corpus.map((c) => tokenize(c.content || ""));
  const N = corpus.length;
  const df = {};
  for (const dt of docTokensList) {
    for (const t of new Set(dt)) df[t] = (df[t] || 0) + 1;
  }
  const avgdl = docTokensList.reduce((s, dt) => s + dt.length, 0) / N;
  const scored = [];
  for (let i = 0; i < corpus.length; i++) {
    const s = scoreChunk(corpus[i], qtok, docTokensList[i], df, N, avgdl, intent, pageCtx);
    if (s > 0) {
      scored.push({
        ...corpus[i],
        score: Math.round(s * 1000) / 1000,
        vector_score: Math.round(semanticScore(qtok, corpus[i], docTokensList[i]) * 1000) / 1000,
      });
    }
  }
  scored.sort((a, b) => b.score - a.score);
  return scored.slice(0, k);
}

function dedupeHits(hits) {
  const seen = new Set();
  const out = [];
  for (const h of hits) {
    const key = h.source_path || h.id || (h.content || "").slice(0, 80);
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(h);
  }
  return out;
}

function computeConfidence(hits) {
  if (!hits.length) return { score: 0, level: "low", hits: 0 };
  const scores = hits.map((h) => h.score || 0);
  const top = Math.max(...scores);
  const norm = Math.min(1, top / 10);
  const level = norm >= 0.55 ? "high" : norm >= 0.28 ? "medium" : "low";
  return { score: Math.round(norm * 1000) / 1000, level, hits: hits.length, top_score: top };
}

export function brainRetrieve(bundle, query, opts = {}) {
  const kRules = opts.kRules ?? 4;
  const kKnowledge = opts.kKnowledge ?? 8;
  const chunks = bundle?.chunks || [];
  const intent = opts.lane || classifyIntent(query);
  const pageCtx =
    opts.pageCtx ||
    inferPageContext(opts.pagePath || opts.page_path, opts.saPage || opts.sa_page);
  const { rules, knowledge } = splitCorpus(chunks);

  let ruleHits = rankChunks(rules, query, "rules", kRules, pageCtx);
  if (!ruleHits.length && rules.length) {
    ruleHits = rules.filter((r) => r.pinned).slice(0, kRules).map((r) => ({ ...r, score: 2 }));
  }

  let knowHits = rankChunks(knowledge, query, intent, kKnowledge, pageCtx);
  if (!knowHits.length && knowledge.length) {
    knowHits = knowledge.filter((c) => c.pinned).slice(0, 3).map((c) => ({ ...c, score: 1 }));
  }

  let hits = dedupeHits([...ruleHits, ...knowHits]);
  if (isIdentityQuestion(query)) {
    const forced = identityForcedHits(chunks, bundle);
    hits = dedupeHits([...forced, ...hits]);
  }
  const confidence = computeConfidence(hits);
  const sourcePaths = [...new Set(hits.map((h) => h.source_path).filter(Boolean))];

  return {
    intent,
    page_lane: pageCtx.page_lane,
    page_path: pageCtx.page_path,
    hits,
    rules_applied: ruleHits.length,
    knowledge_hits: knowHits.length,
    sources_consulted: sourcePaths.length,
    source_paths: sourcePaths.slice(0, 20),
    chunk_ids: hits.map((h) => h.id).filter(Boolean).slice(0, 20),
    confidence,
  };
}

export function knowledgeMeta(bundle) {
  const chunks = bundle?.chunks || [];
  const lanes = {};
  let ruleCount = 0;
  for (const c of chunks) {
    lanes[c.lane] = (lanes[c.lane] || 0) + 1;
    if (RULE_KINDS.has(c.kind) || c.lane === "rules") ruleCount += 1;
  }
  return {
    bundle_version: bundle?.bundle_version || "0.0.0",
    chunk_count: chunks.length,
    chars: bundle?.total_chars || 0,
    source_files: bundle?.source_files || 0,
    live_source_files: bundle?.live_source_files || bundle?.source_files || 0,
    rule_chunks: ruleCount,
    lanes,
    generated_at: bundle?.generated_at || null,
    mode: bundle?.retrieval || "brain_intelligence_v5",
    pipeline: "rules_first_bm25_vector_live_tools",
    vector: { provider: "semantic_hash_v1", dimensions: VECTOR_DIMS },
  };
}

export function assembleBrainPrompt(baseCore, retrieval, bundle = null) {
  const hits = retrieval?.hits || [];
  const publicOneLine = String(bundle?.public_one_line || "").trim();
  if (!hits.length) {
    const ssot = publicOneLine ? `\nCANONICAL ONE LINE (SSOT): ${publicOneLine}\n` : "";
    return { prompt: baseCore + ssot, citations: [], confidence: retrieval?.confidence || { level: "low" } };
  }

  const rulesBlock = [];
  const knowBlock = [];
  for (const [index, h] of hits.entries()) {
    const sourceNo = index + 1;
    const cite = h.www_url ? `\nPublic URL: ${h.www_url}` : "";
    const block = `### Source ${sourceNo}${cite}\n${h.content}`;
    if (RULE_KINDS.has(h.kind) || h.lane === "rules") rulesBlock.push(block);
    else knowBlock.push(block);
  }

  const citations = hits.map((h) => ({
    chunk_id: h.id || null,
    source_path: h.source_path,
    www_url: h.www_url || null,
    lane: h.lane,
    score: h.score || null,
    vector_score: h.vector_score || null,
    kind: h.kind || "doc",
  }));

  const conf = retrieval.confidence || {};
  const pageNote = retrieval.page_path
    ? `Visitor page: ${retrieval.page_path} (lane ${retrieval.page_lane || "core"}) — prefer matching sources.\n`
    : "";

  const ssotBlock = publicOneLine
    ? `CANONICAL PUBLIC ONE LINE (machine SSOT from ${bundle?.positioning_ssot_path || "sourcea-positioning-v1.json"}):\n${publicOneLine}\nFor identity questions, use this line verbatim unless the user asks for more detail.\n\n`
    : "";

  const prompt = `${baseCore}

${pageNote}${ssotBlock}BRAIN RETRIEVAL (${retrieval.sources_consulted || 0} live sources · confidence ${conf.level || "unknown"} · intent ${retrieval.intent} · vector semantic_hash_v1)
Answer ONLY from the blocks below. If blocks lack detail, say so and link a relevant sourcea.app page.
Never expose source_path, repo paths, file names, docs/*.md, JSON config names, model names, or internal implementation details to a visitor.
When you provide a link, use a full copyable URL like https://sourcea.app/sourcea/forge/terminal — not markdown-only relative links.
Do not write source markers like "(Source 5)" or "Source 2" in the answer. The widget renders citations separately.
Write clean public copy: answer directly, avoid hedges like "it looks like you might be asking", and keep the first sentence simple.
Prefer LIVE TOOL RESULTS over corpus text for current status, product lists, proof status, factories, and pricing routes.
If the user requests Farsi/Persian, Spanish, French, or another language, translate the grounded answer into that language and keep URLs unchanged.
Do not describe yourself as "highest confidence" or "highest-confidence"; confidence is an internal quality bar, not public copy.
Do not refer to SourceA as "they" or "the company" in visitor-facing answers; use "SourceA" or "we" where natural.

PUBLIC RULES (mandatory):
${rulesBlock.length ? rulesBlock.join("\n\n") : "- Follow agentic-first and grounded-only rules."}

LIVE KNOWLEDGE (cite URLs when used):
${knowBlock.length ? knowBlock.join("\n\n") : "- No specific page matched — suggest Forge Terminal demo."}`;

  return { prompt, citations, confidence: conf };
}

/** @deprecated use brainRetrieve */
export function retrieveChunks(bundle, query, k = 8) {
  return brainRetrieve(bundle, query, { kKnowledge: k }).hits;
}

/** @deprecated use assembleBrainPrompt */
export function buildGroundedPrompt(basePrompt, hits) {
  return assembleBrainPrompt(basePrompt, {
    hits,
    sources_consulted: hits.length,
    intent: "core",
    confidence: computeConfidence(hits),
  });
}
