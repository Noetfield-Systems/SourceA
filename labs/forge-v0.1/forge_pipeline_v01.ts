/**
 * Forge-v0.1 — deterministic 100-plan processing pipeline.
 * Cloud-native: in-memory only (no local fs). Supabase Edge / Node compatible.
 */

import { fetchMockCloudPlans, type RawPlan } from "./mock_cloud_plans.ts";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ValidPlan extends RawPlan {
  id: string;
  schema_version: string;
  inputs: Record<string, unknown> | unknown[];
  outputs: Record<string, unknown> | unknown[];
  destination_repo: string;
  validation_rule: string;
}

export interface ScoredPlan extends ValidPlan {
  score: number;
  score_breakdown: {
    core_capability: boolean;
    client_problem: boolean;
    minimal_dependencies: boolean;
    vague_keywords: boolean;
    already_implemented: boolean;
  };
}

export interface RoutedGroup {
  destination_repo: string;
  plans: ScoredPlan[];
}

export interface ForgeFunnelMetrics {
  totalIn: number;
  dupesDropped: number;
  malformedDropped: number;
  validRemaining: number;
}

export interface ForgePipelineResult {
  schema: "forge-v0.1-output";
  at: string;
  funnel: ForgeFunnelMetrics;
  top_10: ScoredPlan[];
  routed: Record<string, ScoredPlan[]>;
  all_ranked: ScoredPlan[];
  dropped_malformed_ids: string[];
  dropped_duplicate_ids: string[];
}

// ---------------------------------------------------------------------------
// Hardcoded scoring rules (deterministic — zero LLM)
// ---------------------------------------------------------------------------

const CORE_CAPABILITIES = new Set([
  "receipt_native_dispatch",
  "cloud_worker_queue",
  "gap_ranking_engine",
  "trust_receipt_store",
  "worker_run_dashboard",
]);

const CLIENT_PROBLEMS = new Set([
  "P0-trust-receipt-gap",
  "P1-run-visibility",
  "P2-onboard-friction",
  "P3-pricing-clarity",
]);

const VAGUE_KEYWORD_RE =
  /\b(optimize\s+later|tbd|fix\s+style|styling\s+tbd|maybe\s+later|todo\s+later)\b/i;

/** Signatures already shipped — negative modifier if matched */
const ALREADY_IMPLEMENTED = new Set([
  "already-shipped-run-dashboard-v1",
  "legacy-hub-batch-loop-v0",
  "mac-local-validator-marathon",
]);

const DEDUP_SIMILARITY_THRESHOLD = 85;

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

function signatureHash(plan: ValidPlan): string {
  return stableStringify({ inputs: plan.inputs, outputs: plan.outputs });
}

function tokenSet(text: string): Set<string> {
  return new Set(
    text
      .toLowerCase()
      .split(/\W+/)
      .filter((t) => t.length > 1),
  );
}

/** Jaccard similarity 0–100 between two plan IO signatures */
export function ioSimilarityPercent(a: ValidPlan, b: ValidPlan): number {
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

function planBlob(plan: ValidPlan): string {
  return stableStringify({
    id: plan.id,
    inputs: plan.inputs,
    outputs: plan.outputs,
    destination_repo: plan.destination_repo,
    validation_rule: plan.validation_rule,
    dependencies: plan.dependencies,
    client_problem: plan.client_problem,
    core_capability: plan.core_capability,
    notes: plan.notes,
  });
}

function extractSignatures(plan: ValidPlan): string[] {
  const sigs: string[] = [];
  const walk = (v: unknown): void => {
    if (typeof v === "string") sigs.push(v);
    else if (Array.isArray(v)) v.forEach(walk);
    else if (v && typeof v === "object") Object.values(v).forEach(walk);
  };
  walk(plan.inputs);
  walk(plan.outputs);
  if (plan.core_capability) sigs.push(plan.core_capability);
  return sigs;
}

// ---------------------------------------------------------------------------
// Step 1 — Validate
// ---------------------------------------------------------------------------

export function isValidPlan(raw: unknown): raw is ValidPlan {
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

export function validatePlans(rawPlans: unknown[]): {
  valid: ValidPlan[];
  malformedDropped: number;
  malformedIds: string[];
} {
  const valid: ValidPlan[] = [];
  const malformedIds: string[] = [];

  for (const raw of rawPlans) {
    if (isValidPlan(raw)) {
      valid.push(raw);
    } else {
      const id =
        raw && typeof raw === "object" && typeof (raw as { id?: unknown }).id === "string"
          ? (raw as { id: string }).id
          : "(unknown)";
      malformedIds.push(id);
    }
  }

  return {
    valid,
    malformedDropped: malformedIds.length,
    malformedIds,
  };
}

// ---------------------------------------------------------------------------
// Step 2 — Dedup
// ---------------------------------------------------------------------------

export function dedupPlans(valid: ValidPlan[]): {
  unique: ValidPlan[];
  dupesDropped: number;
  duplicateIds: string[];
} {
  const unique: ValidPlan[] = [];
  const duplicateIds: string[] = [];

  for (const plan of valid) {
    let isDupe = false;
    for (const kept of unique) {
      if (kept.destination_repo !== plan.destination_repo) continue;

      const sim = ioSimilarityPercent(kept, plan);
      const hashMatch = signatureHash(kept) === signatureHash(plan);
      if (hashMatch || sim >= DEDUP_SIMILARITY_THRESHOLD) {
        isDupe = true;
        break;
      }
    }
    if (isDupe) {
      duplicateIds.push(plan.id);
    } else {
      unique.push(plan);
    }
  }

  return {
    unique,
    dupesDropped: duplicateIds.length,
    duplicateIds,
  };
}

// ---------------------------------------------------------------------------
// Step 3 — Score
// ---------------------------------------------------------------------------

function touchesCoreCapability(plan: ValidPlan): boolean {
  if (plan.core_capability && CORE_CAPABILITIES.has(plan.core_capability)) return true;
  const blob = planBlob(plan);
  for (const cap of CORE_CAPABILITIES) {
    if (blob.includes(cap)) return true;
  }
  return false;
}

function addressesClientProblem(plan: ValidPlan): boolean {
  if (plan.client_problem && CLIENT_PROBLEMS.has(plan.client_problem)) return true;
  const blob = planBlob(plan);
  for (const prob of CLIENT_PROBLEMS) {
    if (blob.includes(prob)) return true;
  }
  return false;
}

function hasMinimalDependencies(plan: ValidPlan): boolean {
  const deps = plan.dependencies ?? [];
  return deps.length <= 1;
}

function hasVagueKeywords(plan: ValidPlan): boolean {
  return VAGUE_KEYWORD_RE.test(planBlob(plan));
}

function matchesAlreadyImplemented(plan: ValidPlan): boolean {
  for (const sig of extractSignatures(plan)) {
    if (ALREADY_IMPLEMENTED.has(sig)) return true;
  }
  const blob = planBlob(plan);
  for (const sig of ALREADY_IMPLEMENTED) {
    if (blob.includes(sig)) return true;
  }
  return false;
}

export function scorePlan(plan: ValidPlan): ScoredPlan {
  let score = 0;
  const core_capability = touchesCoreCapability(plan);
  const client_problem = addressesClientProblem(plan);
  const minimal_dependencies = hasMinimalDependencies(plan);
  const vague_keywords = hasVagueKeywords(plan);
  const already_implemented = matchesAlreadyImplemented(plan);

  if (core_capability) score += 10;
  if (client_problem) score += 10;
  if (minimal_dependencies) score += 10;
  if (vague_keywords) score -= 15;
  if (already_implemented) score -= 15;

  return {
    ...plan,
    score,
    score_breakdown: {
      core_capability,
      client_problem,
      minimal_dependencies,
      vague_keywords,
      already_implemented,
    },
  };
}

export function scorePlans(plans: ValidPlan[]): ScoredPlan[] {
  return plans.map(scorePlan);
}

// ---------------------------------------------------------------------------
// Step 4 — Rank
// ---------------------------------------------------------------------------

export function rankPlans(scored: ScoredPlan[]): ScoredPlan[] {
  return [...scored].sort((a, b) => {
    if (b.score !== a.score) return b.score - a.score;
    return a.id.localeCompare(b.id);
  });
}

// ---------------------------------------------------------------------------
// Step 5 — Route
// ---------------------------------------------------------------------------

export function routePlans(ranked: ScoredPlan[]): Record<string, ScoredPlan[]> {
  const routed: Record<string, ScoredPlan[]> = {};
  for (const plan of ranked) {
    const repo = plan.destination_repo;
    if (!routed[repo]) routed[repo] = [];
    routed[repo].push(plan);
  }
  return routed;
}

// ---------------------------------------------------------------------------
// Pipeline orchestrator
// ---------------------------------------------------------------------------

export function runForgePipeline(rawPlans: unknown[]): ForgePipelineResult {
  const totalIn = rawPlans.length;

  const { valid, malformedDropped, malformedIds } = validatePlans(rawPlans);
  const { unique, dupesDropped, duplicateIds } = dedupPlans(valid);
  const scored = scorePlans(unique);
  const ranked = rankPlans(scored);
  const routed = routePlans(ranked);

  const funnel: ForgeFunnelMetrics = {
    totalIn,
    dupesDropped,
    malformedDropped,
    validRemaining: unique.length,
  };

  return {
    schema: "forge-v0.1-output",
    at: new Date().toISOString(),
    funnel,
    top_10: ranked.slice(0, 10),
    routed,
    all_ranked: ranked,
    dropped_malformed_ids: malformedIds,
    dropped_duplicate_ids: duplicateIds,
  };
}

export function formatForgeRunSummary(funnel: ForgeFunnelMetrics): string {
  return (
    `Forge Run Summary: ${funnel.totalIn} in -> ${funnel.dupesDropped} dupes dropped -> ` +
    `${funnel.malformedDropped} malformed dropped -> ${funnel.validRemaining} valid remaining -> ` +
    `Top 10 ranked & routed.`
  );
}

/** Cloud artifact — JSON string (no local fs write) */
export function buildForgeOutputJson(result: ForgePipelineResult): string {
  const payload = {
    schema: result.schema,
    at: result.at,
    funnel: result.funnel,
    top_10: result.top_10,
    routed: result.routed,
  };
  return JSON.stringify(payload, null, 2);
}

// ---------------------------------------------------------------------------
// Win Test — automated assertions
// ---------------------------------------------------------------------------

export function runWinTest(result: ForgePipelineResult): { ok: boolean; errors: string[] } {
  const errors: string[] = [];
  const { funnel, top_10, all_ranked, dropped_malformed_ids, dropped_duplicate_ids } = result;

  // Funnel arithmetic
  const accounted =
    funnel.validRemaining + funnel.malformedDropped + funnel.dupesDropped;
  if (accounted !== funnel.totalIn) {
    errors.push(
      `Funnel mismatch: ${funnel.validRemaining}+${funnel.malformedDropped}+${funnel.dupesDropped}=${accounted} != ${funnel.totalIn}`,
    );
  }

  // Summary line
  const summary = formatForgeRunSummary(funnel);
  const expectedSummary =
    `Forge Run Summary: ${funnel.totalIn} in -> ${funnel.dupesDropped} dupes dropped -> ${funnel.malformedDropped} malformed dropped -> ${funnel.validRemaining} valid remaining -> Top 10 ranked & routed.`;
  if (summary !== expectedSummary) {
    errors.push("Summary string does not match funnel metrics");
  }

  // Top 10 scores beat lower-ranked
  if (top_10.length > 0 && all_ranked.length > 10) {
    const minTop = Math.min(...top_10.map((p) => p.score));
    const rest = all_ranked.slice(10);
    const maxRest = Math.max(...rest.map((p) => p.score));
    if (minTop < maxRest) {
      errors.push(`Win test fail: min top-10 score ${minTop} < max lower-ranked ${maxRest}`);
    }
  }

  // Top 10 strictly descending-ish (sorted)
  for (let i = 1; i < top_10.length; i += 1) {
    if (top_10[i].score > top_10[i - 1].score) {
      errors.push(`Top 10 not sorted at index ${i}`);
      break;
    }
  }

  // No malformed/dupe ids in survivors
  const survivorIds = new Set(all_ranked.map((p) => p.id));
  for (const id of dropped_malformed_ids) {
    if (survivorIds.has(id)) errors.push(`Malformed id survived: ${id}`);
  }
  for (const id of dropped_duplicate_ids) {
    if (survivorIds.has(id)) errors.push(`Duplicate id survived: ${id}`);
  }

  // Routed groups cover all ranked
  const routedCount = Object.values(result.routed).reduce((n, arr) => n + arr.length, 0);
  if (routedCount !== all_ranked.length) {
    errors.push(`Routed count ${routedCount} != ranked ${all_ranked.length}`);
  }

  return { ok: errors.length === 0, errors };
}

// ---------------------------------------------------------------------------
// Entry (simulates cloud handler + local verification run)
// ---------------------------------------------------------------------------

export function executeForgeV01(rawPlans?: unknown[]): {
  result: ForgePipelineResult;
  outputJson: string;
  summaryLine: string;
  winTest: { ok: boolean; errors: string[] };
} {
  const plans = rawPlans ?? fetchMockCloudPlans();
  const result = runForgePipeline(plans);
  const outputJson = buildForgeOutputJson(result);
  const summaryLine = formatForgeRunSummary(result.funnel);
  const winTest = runWinTest(result);
  return { result, outputJson, summaryLine, winTest };
}

/** Deno / Supabase Edge export */
export function forgeHandler(requestPlans: unknown[]): Response {
  const { outputJson, summaryLine, winTest } = executeForgeV01(requestPlans);
  if (!winTest.ok) {
    return new Response(
      JSON.stringify({ ok: false, errors: winTest.errors, summary: summaryLine }),
      { status: 500, headers: { "Content-Type": "application/json" } },
    );
  }
  return new Response(outputJson, {
    status: 200,
    headers: {
      "Content-Type": "application/json",
      "X-Forge-Summary": summaryLine,
    },
  });
}

// Node / tsx direct run
const isMain =
  typeof process !== "undefined" &&
  !!process.argv[1] &&
  (process.argv[1].endsWith("forge_pipeline_v01.ts") ||
    process.argv[1].endsWith("forge_pipeline_v01.js"));

if (isMain) {
  const { outputJson, summaryLine, winTest, result } = executeForgeV01();
  console.log(summaryLine);
  console.log("--- forge_v0.1_output.json (in-memory artifact) ---");
  console.log(outputJson);
  if (winTest.ok) {
    console.log("WIN TEST: PASS");
  } else {
    console.error("WIN TEST: FAIL");
    for (const e of winTest.errors) console.error(`  - ${e}`);
    process.exitCode = 1;
  }
  // Expose metrics for quick inspection without fs
  void result;
}
