/** BM25 + intent hybrid retrieval for Brain knowledge bundle (v2). */

const STOP = new Set([
  "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "is", "are",
  "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will",
  "would", "could", "should", "may", "might", "must", "shall", "can", "need", "you", "your",
  "we", "our", "they", "their", "it", "its", "this", "that", "what", "how", "when", "where",
  "who", "why", "with", "from", "about", "into", "through", "during", "before", "after",
]);

export function tokenize(text) {
  return String(text || "")
    .toLowerCase()
    .match(/[a-z0-9][a-z0-9_./-]*/g)?.filter((t) => t.length > 1 && !STOP.has(t)) || [];
}

export function classifyIntent(query) {
  const q = query.toLowerCase();
  if (/\b(invest|fund|raise|valuation)\b/.test(q)) return "investor";
  if (/\b(cursor|developer|api|code|forge terminal|kernel|pypi|npm|deploy|ide)\b/.test(q)) return "developer";
  if (/\b(price|pricing|cost|how much|\$|buy|sandbox|demo|proof|offer)\b/.test(q)) return "buyer";
  if (/\b(partner|agency|procurement|enterprise)\b/.test(q)) return "partner";
  return "core";
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

export function retrieveChunks(bundle, query, k = 8) {
  const chunks = bundle?.chunks || [];
  if (!chunks.length) return [];
  const qtok = tokenize(query);
  if (!qtok.length) return chunks.filter((c) => c.pinned).slice(0, k);

  const docTokensList = chunks.map((c) => tokenize(c.content || ""));
  const N = chunks.length;
  const df = {};
  for (const dt of docTokensList) {
    for (const t of new Set(dt)) df[t] = (df[t] || 0) + 1;
  }
  const avgdl = docTokensList.reduce((s, dt) => s + dt.length, 0) / N;
  const intent = classifyIntent(query);

  const scored = [];
  for (let i = 0; i < chunks.length; i++) {
    const c = chunks[i];
    let s = bm25Score(qtok, docTokensList[i], df, N, avgdl);
    if (c.pinned) s += 2;
    if (c.lane === intent) s += 1.5;
    // boost title/path token matches
    const path = String(c.source_path || "").toLowerCase();
    for (const t of qtok.slice(0, 6)) {
      if (path.includes(t)) s += 0.5;
    }
    if (s > 0) scored.push({ ...c, score: Math.round(s * 1000) / 1000 });
  }
  scored.sort((a, b) => b.score - a.score);
  return scored.slice(0, k);
}

export function knowledgeMeta(bundle) {
  const chunks = bundle?.chunks || [];
  const lanes = {};
  for (const c of chunks) lanes[c.lane] = (lanes[c.lane] || 0) + 1;
  return {
    bundle_version: bundle?.bundle_version || "0.0.0",
    chunk_count: chunks.length,
    chars: bundle?.total_chars || 0,
    source_files: bundle?.source_files || 0,
    lanes,
    generated_at: bundle?.generated_at || null,
    mode: bundle?.retrieval || "bm25_hybrid_v1",
  };
}

export function buildGroundedPrompt(basePrompt, hits) {
  if (!hits?.length) return { prompt: basePrompt, citations: [] };
  const block = hits
    .map((h) => {
      const cite = h.www_url ? ` (${h.www_url})` : "";
      return `### ${h.source_path}${cite}\n${h.content}`;
    })
    .join("\n\n");
  const citations = hits.map((h) => ({
    source_path: h.source_path,
    www_url: h.www_url || null,
    lane: h.lane,
    score: h.score || null,
  }));
  const prompt = `${basePrompt}

GROUNDED KNOWLEDGE (${hits.length} retrieved chunks — cite URLs when relevant; do not invent facts beyond this):
${block}

CITATION RULE: Mention page paths or URLs when helpful. Never reveal internal paths or secrets.`;
  return { prompt, citations };
}
