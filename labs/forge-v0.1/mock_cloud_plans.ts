/**
 * Mock cloud blueprint source — 100 raw plans for Forge-v0.1 funnel testing.
 * Fetched in-memory (simulates GitHub API / Supabase Storage payload).
 *
 * Composition: 67 unique valid + 18 intentional dupes + 15 malformed = 100
 */

export interface RawPlan {
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

/** Canonical blueprint type alias for Forge-v0.1 engine */
export type Blueprint = RawPlan;

function basePlan(
  id: string,
  repo: string,
  inputs: Record<string, unknown>,
  outputs: Record<string, unknown>,
  extras: Partial<RawPlan> = {},
): RawPlan {
  return {
    id,
    schema_version: "forge-plan-v1",
    inputs,
    outputs,
    destination_repo: repo,
    validation_rule: "strict-json-v1",
    dependencies: extras.dependencies ?? [],
    ...extras,
  };
}

/** Build 67 unique valid plans + 18 near/exact duplicates + 15 malformed = 100 */
export function fetchMockCloudPlans(): RawPlan[] {
  const repos = [
    "sourcea/trustfield",
    "sourcea/noetfield",
    "sourcea/witnessbc",
    "sourcea/worker-hub",
    "sourcea/forge-bay",
  ];

  const valid: RawPlan[] = [];
  let seq = 1;

  const uid = () => {
    const n = seq;
    seq += 1;
    return n;
  };

  const fingerprint = (label: string) => `fp-${label}-seq${seq}-deterministic-unique-token`;

  // 12 high-score plans (core + client problem + low deps)
  for (let i = 0; i < 12; i += 1) {
    const n = uid();
    const repo = repos[i % repos.length];
    const fp = fingerprint(`high-${n}`);
    valid.push(
      basePlan(
        `PLAN-HIGH-${String(n).padStart(3, "0")}`,
        repo,
        {
          action: "dispatch_worker_job",
          capability: i % 2 === 0 ? "receipt_native_dispatch" : "cloud_worker_queue",
          client_problem_id: ["P0-trust-receipt-gap", "P1-run-visibility", "P2-onboard-friction"][i % 3],
          unique_signature: `high-plan-${n}-only-${repo.replace("/", "-")}`,
          plan_fingerprint: fp,
        },
        {
          artifact: "run_receipt_json",
          unique_output_key: `out-high-${n}`,
          plan_fingerprint: fp,
        },
        {
          core_capability: i % 2 === 0 ? "receipt_native_dispatch" : "cloud_worker_queue",
          client_problem: ["P0-trust-receipt-gap", "P1-run-visibility", "P2-onboard-friction"][i % 3],
          dependencies: i % 4 === 0 ? ["supabase-js"] : [],
        },
      ),
    );
  }

  // 20 medium-score (one positive modifier each, unique signatures)
  for (let i = 0; i < 20; i += 1) {
    const n = uid();
    const repo = repos[(i + 2) % repos.length];
    const fp = fingerprint(`med-${n}`);
    valid.push(
      basePlan(
        `PLAN-MED-${String(n).padStart(3, "0")}`,
        repo,
        {
          action: "build_summary",
          unique_signature: `med-plan-${n}-repo-${repo.replace("/", "-")}`,
          plan_fingerprint: fp,
          ...(i % 2 === 0 ? { capability: "gap_ranking_engine" } : {}),
          ...(i % 3 === 0 ? { client_problem_id: "P1-run-visibility" } : {}),
        },
        { artifact: "summary_json", unique_output_key: `out-med-${n}`, plan_fingerprint: fp },
        {
          core_capability: i % 2 === 0 ? "gap_ranking_engine" : undefined,
          client_problem: i % 3 === 0 ? "P1-run-visibility" : undefined,
          dependencies: i % 5 === 0 ? ["openrouter", "zod"] : ["zod"],
        },
      ),
    );
  }

  // 15 low-score (vague / already implemented / heavy deps)
  for (let i = 0; i < 15; i += 1) {
    const n = uid();
    const repo = repos[i % repos.length];
    const vague = i % 3 === 0 ? "optimize later" : i % 3 === 1 ? "tbd styling" : "fix style pass";
    const fp = fingerprint(`low-${n}`);
    valid.push(
      basePlan(
        `PLAN-LOW-${String(n).padStart(3, "0")}`,
        repo,
        {
          action: "misc_patch",
          note: vague,
          unique_signature: i < 5 ? "already-shipped-run-dashboard-v1" : `low-plan-${n}-only`,
          plan_fingerprint: fp,
        },
        { artifact: "markdown_note", unique_output_key: `out-low-${n}`, body: vague, plan_fingerprint: fp },
        {
          dependencies: ["react", "next", "supabase-js", "stripe"],
          notes: vague,
        },
      ),
    );
  }

  // 20 neutral baseline
  for (let i = 0; i < 20; i += 1) {
    const n = uid();
    const repo = repos[(i + 1) % repos.length];
    const fp = fingerprint(`base-${n}`);
    valid.push(
      basePlan(
        `PLAN-BASE-${String(n).padStart(3, "0")}`,
        repo,
        {
          action: "doc_sync",
          topic: `topic-${n}`,
          unique_signature: `base-plan-${n}-repo-${repo.replace("/", "-")}`,
          plan_fingerprint: fp,
        },
        { artifact: "doc_row", unique_output_key: `out-base-${n}`, plan_fingerprint: fp },
        { dependencies: ["none"] },
      ),
    );
  }

  if (valid.length !== 67) {
    throw new Error(`Expected 67 unique valid plans, got ${valid.length}`);
  }

  // 18 intentional duplicates (exact copy or near-copy of first 18 valid plans)
  const dupes: RawPlan[] = [];
  for (let i = 0; i < 16; i += 1) {
    const src = valid[i];
    dupes.push({
      ...src,
      id: `PLAN-DUP-${String(i + 1).padStart(3, "0")}`,
      notes: `duplicate-of-${src.id}`,
    });
  }
  // 2 near-duplicates (>=85% similar, same repo)
  const nearSrcA = valid[16];
  dupes.push({
    ...nearSrcA,
    id: "PLAN-NEAR-001",
    inputs: { ...(nearSrcA.inputs as Record<string, unknown>), _near_flag: true },
    notes: `near-duplicate-of-${nearSrcA.id}`,
  });
  const nearSrcB = valid[17];
  dupes.push({
    ...nearSrcB,
    id: "PLAN-NEAR-002",
    inputs: { ...(nearSrcB.inputs as Record<string, unknown>), _near_flag: true },
    notes: `near-duplicate-of-${nearSrcB.id}`,
  });

  if (dupes.length !== 18) {
    throw new Error(`Expected 18 duplicate plans, got ${dupes.length}`);
  }

  const malformed: unknown[] = [
    { id: "BAD-001", schema_version: "forge-plan-v1" },
    { id: "BAD-002", inputs: {}, outputs: {}, destination_repo: "x", validation_rule: "v" },
    { schema_version: "forge-plan-v1", inputs: {}, outputs: {}, destination_repo: "x", validation_rule: "v" },
    { id: "BAD-004", schema_version: "forge-plan-v1", outputs: {}, destination_repo: "x", validation_rule: "v" },
    { id: "BAD-005", schema_version: "forge-plan-v1", inputs: {}, destination_repo: "x", validation_rule: "v" },
    { id: "BAD-006", schema_version: "forge-plan-v1", inputs: {}, outputs: {}, validation_rule: "v" },
    { id: "BAD-007", schema_version: "forge-plan-v1", inputs: {}, outputs: {}, destination_repo: "x" },
    { id: "BAD-008", schema_version: "", inputs: {}, outputs: {}, destination_repo: "x", validation_rule: "v" },
    { id: "BAD-009", schema_version: "forge-plan-v1", inputs: null, outputs: {}, destination_repo: "x", validation_rule: "v" },
    { id: "BAD-010", schema_version: "forge-plan-v1", inputs: {}, outputs: null, destination_repo: "x", validation_rule: "v" },
    { id: "BAD-011", schema_version: "forge-plan-v1", inputs: {}, outputs: {}, destination_repo: "", validation_rule: "v" },
    { id: "BAD-012", schema_version: "forge-plan-v1", inputs: {}, outputs: {}, destination_repo: "x", validation_rule: "" },
    { id: 42, schema_version: "forge-plan-v1", inputs: {}, outputs: {}, destination_repo: "x", validation_rule: "v" },
    { id: "BAD-014", schema_version: "forge-plan-v1", inputs: "not-object", outputs: {}, destination_repo: "x", validation_rule: "v" },
    { id: "BAD-015", schema_version: "forge-plan-v1", inputs: {}, outputs: 99, destination_repo: "x", validation_rule: "v" },
  ];

  const payload: unknown[] = [...valid, ...dupes, ...malformed];

  if (payload.length !== 100) {
    throw new Error(`mock_cloud_plans: expected 100 plans, got ${payload.length}`);
  }

  return payload as RawPlan[];
}

/** Cloud stream alias — 100 blueprints for Forge-v0.1 */
export const fetchMockCloudBlueprints = fetchMockCloudPlans;
