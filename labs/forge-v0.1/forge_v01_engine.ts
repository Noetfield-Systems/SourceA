/**
 * Forge-v0.1 Engine — deterministic 5-stage blueprint pipeline.
 *
 * CLOUD-PLANE ONLY: in-memory processing. No local fs. Edge/container safe.
 * Stages: Validate → Dedup → Score → Rank → Route
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface Blueprint {
  id: string;
  schema_version: string;
  inputs: Record<string, unknown> | unknown[];
  outputs: Record<string, unknown> | unknown[];
  destination_repo: string;
  validation_rule: string;
  dependencies?: string[];
  client_problem?: string;
  core_capability?: string;
  notes?: string;
}

export interface ValidBlueprint extends Blueprint {
  id: string;
  schema_version: string;
  inputs: Record<string, unknown> | unknown[];
  outputs: Record<string, unknown> | unknown[];
  destination_repo: string;
  validation_rule: string;
}

export interface ScorePatternRule {
  pattern: string;
  points: number;
}

export interface ScoredBlueprint extends ValidBlueprint {
  score: number;
  score_breakdown: {
    core_capability: boolean;
    client_problem: boolean;
    minimal_dependencies: boolean;
    vague_keywords: boolean;
    already_implemented: boolean;
    pattern_adjustment?: number;
    tier_adjustment?: number;
  };
}

export interface ForgeFunnelMetrics {
  totalIn: number;
  dupesDropped: number;
  malformedDropped: number;
  alreadyHaveDropped: number;
  validRemaining: number;
}

export interface ForgeScoringConfig {
  target_repo?: string;
  core_capabilities: string[];
  client_problems: string[];
  already_implemented_plan_ids: string[];
  already_implemented_signatures: string[];
  vague_keyword_patterns: string[];
  dedup_similarity_threshold?: number;
  score_boost_patterns?: ScorePatternRule[];
  score_penalty_patterns?: ScorePatternRule[];
  tier_score?: Record<string, number>;
}

export interface ForgeEngineResult {
  schema: "forge-v0.1-output";
  at: string;
  architecture: "A";
  target_repo?: string;
  funnel: ForgeFunnelMetrics;
  summary_line: string;
  win_test_question: string;
  win_test_card: string[];
  top_10: ScoredBlueprint[];
  routed: Record<string, ScoredBlueprint[]>;
  all_ranked: ScoredBlueprint[];
  dropped_malformed_ids: string[];
  dropped_duplicate_ids: string[];
  dropped_already_have_ids: string[];
}

export type ForgeStage =
  | "validate"
  | "dedup"
  | "score"
  | "rank"
  | "route";

// ---------------------------------------------------------------------------
// Scoring SSOT (overridden by data/forge-scoring-ssot-v01.json in runner)
// ---------------------------------------------------------------------------

export const DEFAULT_SCORING: ForgeScoringConfig = {
  core_capabilities: [
    "cloud_worker_dispatch_api",
    "receipt_native_store",
    "_evidence_pipeline",
    "gap_ranking_engine",
    "worker_hub_projection",
    "worker_run_dashboard",
    "mac_control_cockpit_observe",
    "forge_deterministic_router",
  ],
  client_problems: [
    "P0-trust-receipt-gap",
    "P1-run-visibility",
    "P2-onboard-friction",
    "P3-pricing-clarity",
    "P4-mac-cockpit-only",
  ],
  already_implemented_plan_ids: [],
  already_implemented_signatures: [],
  vague_keyword_patterns: ["optimize later", "tbd", "fix style", "mock_only", "glance only"],
  dedup_similarity_threshold: 85,
};

function scoringSets(cfg: ForgeScoringConfig) {
  return {
    caps: new Set(cfg.core_capabilities),
    probs: new Set(cfg.client_problems),
    alreadyIds: new Set(cfg.already_implemented_plan_ids),
    alreadySigs: new Set(cfg.already_implemented_signatures),
    vague: cfg.vague_keyword_patterns.map((p) => p.toLowerCase()),
    threshold: cfg.dedup_similarity_threshold ?? 85,
  };
}

function hasMinimalDependencies(blueprint: ValidBlueprint): boolean {
  return (blueprint.dependencies ?? []).length <= 1;
}

function matchesAlreadyImplemented(blueprint: ValidBlueprint, cfg: ForgeScoringConfig): boolean {
  const { alreadyIds, alreadySigs } = scoringSets(cfg);
  if (alreadyIds.has(blueprint.id)) return true;
  const blob = blueprintBlob(blueprint);
  for (const sig of alreadySigs) {
    if (blob.includes(sig)) return true;
  }
  const implSig = (blueprint.inputs as Record<string, unknown>)?.implementation_signature;
  if (typeof implSig === "string" && alreadySigs.has(implSig)) return true;
  return false;
}

function touchesCoreCapability(blueprint: ValidBlueprint, cfg: ForgeScoringConfig): boolean {
  const { caps } = scoringSets(cfg);
  if (blueprint.core_capability && caps.has(blueprint.core_capability)) return true;
  const blob = blueprintBlob(blueprint);
  for (const cap of caps) {
    if (blob.includes(cap)) return true;
  }
  return false;
}

function addressesClientProblem(blueprint: ValidBlueprint, cfg: ForgeScoringConfig): boolean {
  const { probs } = scoringSets(cfg);
  if (blueprint.client_problem && probs.has(blueprint.client_problem)) return true;
  const blob = blueprintBlob(blueprint);
  for (const prob of probs) {
    if (blob.includes(prob)) return true;
  }
  return false;
}

function hasVagueKeywords(blueprint: ValidBlueprint, cfg: ForgeScoringConfig): boolean {
  const blob = blueprintBlob(blueprint).toLowerCase();
  return scoringSets(cfg).vague.some((p) => blob.includes(p));
}

function blueprintActionText(blueprint: ValidBlueprint): string {
  const inputs = blueprint.inputs as Record<string, unknown>;
  const action = inputs.action ?? blueprint.notes ?? "";
  return String(action);
}

function patternAdjustment(text: string, cfg: ForgeScoringConfig): number {
  const t = text.toLowerCase();
  let adj = 0;
  for (const row of cfg.score_boost_patterns ?? []) {
    if (t.includes(row.pattern.toLowerCase())) {
      adj += row.points;
    }
  }
  for (const row of cfg.score_penalty_patterns ?? []) {
    if (t.includes(row.pattern.toLowerCase())) {
      adj -= row.points;
    }
  }
  return adj;
}

function tierAdjustment(blueprint: ValidBlueprint, cfg: ForgeScoringConfig): number {
  const inputs = blueprint.inputs as Record<string, unknown>;
  const tier = String(inputs.tier ?? "");
  return cfg.tier_score?.[tier] ?? 0;
}

function humanLine(row: ScoredBlueprint): string {
  const inputs = row.inputs as Record<string, unknown>;
  const action = inputs.action ?? row.notes ?? "";
  return (
    `${row.id} score=${row.score} ` +
    `[${inputs.workstream}|${inputs. ?? "mac"}] ${String(action).slice(0, 100)}`
  );
}

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------

function stableStringify(value: unknown): string {
  if (value === null || typeof value !== "object") {
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return `[${value.map(stableStringify).join(",")}]`;
  }
  const obj = value as Record<string, unknown>;
  const keys = Object.keys(obj).sort();
  return `{${keys.map((k) => `${JSON.stringify(k)}:${stableStringify(obj[k])}`).join(",")}}`;
}

function signatureHash(blueprint: ValidBlueprint): string {
  return stableStringify({ inputs: blueprint.inputs, outputs: blueprint.outputs });
}

function tokenSet(text: string): Set<string> {
  return new Set(
    text
      .toLowerCase()
      .split(/\W+/)
      .filter((t) => t.length > 1),
  );
}

export function ioSimilarityPercent(a: ValidBlueprint, b: ValidBlueprint): number {
  const ha = signatureHash(a);
  const hb = signatureHash(b);
  if (ha === hb) return 100;

  const ta = tokenSet(ha);
  const tb = tokenSet(hb);
  if (ta.size === 0 && tb.size === 0) return 100;

  let intersection = 0;
  for (const t of ta) {
    if (tb.has(t)) intersection += 1;
  }
  const union = new Set([...ta, ...tb]).size;
  return union === 0 ? 0 : (intersection / union) * 100;
}

function blueprintBlob(blueprint: ValidBlueprint): string {
  return stableStringify({
    id: blueprint.id,
    inputs: blueprint.inputs,
    outputs: blueprint.outputs,
    destination_repo: blueprint.destination_repo,
    validation_rule: blueprint.validation_rule,
    dependencies: blueprint.dependencies,
    client_problem: blueprint.client_problem,
    core_capability: blueprint.core_capability,
    notes: blueprint.notes,
  });
}

function extractSignatures(blueprint: ValidBlueprint): string[] {
  const sigs: string[] = [];
  const walk = (v: unknown): void => {
    if (typeof v === "string") sigs.push(v);
    else if (Array.isArray(v)) v.forEach(walk);
    else if (v && typeof v === "object") Object.values(v).forEach(walk);
  };
  walk(blueprint.inputs);
  walk(blueprint.outputs);
  if (blueprint.core_capability) sigs.push(blueprint.core_capability);
  return sigs;
}

// ---------------------------------------------------------------------------
// Stage 1 — Validate
// ---------------------------------------------------------------------------

export function isValidBlueprint(raw: unknown): raw is ValidBlueprint {
  if (!raw || typeof raw !== "object") return false;
  const p = raw as Record<string, unknown>;
  if (typeof p.id !== "string" || !p.id.trim()) return false;
  if (typeof p.schema_version !== "string" || !p.schema_version.trim()) return false;
  if (typeof p.destination_repo !== "string" || !p.destination_repo.trim()) return false;
  if (typeof p.validation_rule !== "string" || !p.validation_rule.trim()) return false;
  if (p.inputs === null || p.inputs === undefined) return false;
  if (p.outputs === null || p.outputs === undefined) return false;
  const inOk =
    typeof p.inputs === "object" && (Array.isArray(p.inputs) || !Array.isArray(p.inputs));
  const outOk =
    typeof p.outputs === "object" && (Array.isArray(p.outputs) || !Array.isArray(p.outputs));
  return inOk && outOk;
}

export function stageValidate(rawBlueprints: unknown[]): {
  valid: ValidBlueprint[];
  malformedDropped: number;
  malformedIds: string[];
} {
  const valid: ValidBlueprint[] = [];
  const malformedIds: string[] = [];

  for (const raw of rawBlueprints) {
    if (isValidBlueprint(raw)) {
      valid.push(raw);
    } else {
      const id =
        raw && typeof raw === "object" && typeof (raw as { id?: unknown }).id === "string"
          ? (raw as { id: string }).id
          : "(unknown)";
      malformedIds.push(id);
    }
  }

  return { valid, malformedDropped: malformedIds.length, malformedIds };
}

// ---------------------------------------------------------------------------
// Stage 2 — Dedup
// ---------------------------------------------------------------------------

export function stageDedup(
  valid: ValidBlueprint[],
  cfg: ForgeScoringConfig = DEFAULT_SCORING,
): {
  unique: ValidBlueprint[];
  dupesDropped: number;
  duplicateIds: string[];
  alreadyHaveDropped: number;
  alreadyHaveIds: string[];
} {
  const { threshold, alreadyIds, alreadySigs } = scoringSets(cfg);
  const unique: ValidBlueprint[] = [];
  const duplicateIds: string[] = [];
  const alreadyHaveIds: string[] = [];

  for (const blueprint of valid) {
    if (matchesAlreadyImplemented(blueprint, cfg)) {
      alreadyHaveIds.push(blueprint.id);
      continue;
    }
    let isDupe = false;
    for (const kept of unique) {
      if (kept.destination_repo !== blueprint.destination_repo) continue;
      const sim = ioSimilarityPercent(kept, blueprint);
      const hashMatch = signatureHash(kept) === signatureHash(blueprint);
      if (hashMatch || sim >= threshold) {
        isDupe = true;
        break;
      }
    }
    if (isDupe) duplicateIds.push(blueprint.id);
    else unique.push(blueprint);
  }

  return {
    unique,
    dupesDropped: duplicateIds.length,
    duplicateIds,
    alreadyHaveDropped: alreadyHaveIds.length,
    alreadyHaveIds,
  };
}

// ---------------------------------------------------------------------------
// Stage 3 — Score
// ---------------------------------------------------------------------------

export function scoreBlueprint(
  blueprint: ValidBlueprint,
  cfg: ForgeScoringConfig = DEFAULT_SCORING,
): ScoredBlueprint {
  let score = 0;
  const core_capability = touchesCoreCapability(blueprint, cfg);
  const client_problem = addressesClientProblem(blueprint, cfg);
  const minimal_dependencies = hasMinimalDependencies(blueprint);
  const vague_keywords = hasVagueKeywords(blueprint, cfg);
  const already_implemented = matchesAlreadyImplemented(blueprint, cfg);
  const pattern_adj = patternAdjustment(blueprintActionText(blueprint), cfg);
  const tier_adj = tierAdjustment(blueprint, cfg);

  if (core_capability) score += 10;
  if (client_problem) score += 10;
  if (minimal_dependencies) score += 10;
  if (vague_keywords) score -= 15;
  if (already_implemented) score -= 15;
  score += pattern_adj + tier_adj;

  return {
    ...blueprint,
    score,
    score_breakdown: {
      core_capability,
      client_problem,
      minimal_dependencies,
      vague_keywords,
      already_implemented,
      pattern_adjustment: pattern_adj,
      tier_adjustment: tier_adj,
    },
  };
}

export function stageScore(
  blueprints: ValidBlueprint[],
  cfg: ForgeScoringConfig = DEFAULT_SCORING,
): ScoredBlueprint[] {
  return blueprints.map((b) => scoreBlueprint(b, cfg));
}

// ---------------------------------------------------------------------------
// Stage 4 — Rank
// ---------------------------------------------------------------------------

export function stageRank(scored: ScoredBlueprint[]): ScoredBlueprint[] {
  return [...scored].sort((a, b) => {
    if (b.score !== a.score) return b.score - a.score;
    return a.id.localeCompare(b.id);
  });
}

// ---------------------------------------------------------------------------
// Stage 5 — Route
// ---------------------------------------------------------------------------

export function stageRoute(ranked: ScoredBlueprint[]): Record<string, ScoredBlueprint[]> {
  const routed: Record<string, ScoredBlueprint[]> = {};
  for (const blueprint of ranked) {
    const repo = blueprint.destination_repo;
    if (!routed[repo]) routed[repo] = [];
    routed[repo].push(blueprint);
  }
  return routed;
}

// ---------------------------------------------------------------------------
// Engine orchestrator (uninterrupted 5-stage pipeline)
// ---------------------------------------------------------------------------

export function runForgeV01Engine(
  rawBlueprints: unknown[],
  cfg: ForgeScoringConfig = DEFAULT_SCORING,
): ForgeEngineResult {
  if (rawBlueprints.length !== 100) {
    throw new Error(`Forge-v0.1 requires exactly 100 blueprints, received ${rawBlueprints.length}`);
  }

  const { valid, malformedDropped, malformedIds } = stageValidate(rawBlueprints);
  const { unique, dupesDropped, duplicateIds, alreadyHaveDropped, alreadyHaveIds } = stageDedup(
    valid,
    cfg,
  );
  const scored = stageScore(unique, cfg);
  const ranked = stageRank(scored);
  const routed = stageRoute(ranked);
  const top_10 = ranked.slice(0, 10);

  const funnel: ForgeFunnelMetrics = {
    totalIn: rawBlueprints.length,
    dupesDropped,
    malformedDropped,
    alreadyHaveDropped,
    validRemaining: unique.length,
  };

  return {
    schema: "forge-v0.1-output",
    at: new Date().toISOString(),
    architecture: "A",
    target_repo: cfg.target_repo,
    funnel,
    summary_line: formatForgeRunSummary(funnel),
    win_test_question: "Are these the 10 you would have picked by hand, or better?",
    win_test_card: top_10.map(humanLine),
    top_10,
    routed,
    all_ranked: ranked,
    dropped_malformed_ids: malformedIds,
    dropped_duplicate_ids: duplicateIds,
    dropped_already_have_ids: alreadyHaveIds,
  };
}

export function formatForgeRunSummary(funnel: ForgeFunnelMetrics): string {
  return (
    `Forge Run Summary: ${funnel.totalIn} in -> ${funnel.dupesDropped} dupes dropped -> ` +
    `${funnel.malformedDropped} malformed dropped -> ${funnel.alreadyHaveDropped} already-have dropped -> ` +
    `${funnel.validRemaining} valid remaining -> Top 10 ranked & routed.`
  );
}

/** In-memory cloud artifact (JSON string — never written to host disk) */
export function buildForgeOutputJson(result: ForgeEngineResult): string {
  return JSON.stringify(
    {
      schema: result.schema,
      at: result.at,
      architecture: result.architecture,
      target_repo: result.target_repo,
      funnel: result.funnel,
      summary_line: result.summary_line,
      win_test_question: result.win_test_question,
      win_test_card: result.win_test_card,
      top_10: result.top_10,
      routed: result.routed,
    },
    null,
    2,
  );
}

/** Supabase Edge / Vercel serverless handler */
export function forgeEdgeHandler(
  requestBlueprints: unknown[],
  cfg: ForgeScoringConfig = DEFAULT_SCORING,
): Response {
  try {
    const result = runForgeV01Engine(requestBlueprints, cfg);
    const body = buildForgeOutputJson(result);
    return new Response(body, {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "X-Forge-Summary": result.summary_line,
      },
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return new Response(JSON.stringify({ ok: false, error: message }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }
}
