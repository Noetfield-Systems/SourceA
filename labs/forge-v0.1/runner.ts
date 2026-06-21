/**
 * Forge-v0.1 Runner — cloud cockpit (Architecture A).
 *
 * Default: real 100 blueprints from secondary-cloud-drain SSOT.
 * Mock:   npx tsx runner.ts --mock
 * Remote: npx tsx runner.ts --remote
 */

import { fetchMockCloudBlueprints } from "./mock_cloud_plans.ts";
import {
  buildForgeOutputJson,
  runForgeV01Engine,
  type ForgeEngineResult,
  type ForgeScoringConfig,
} from "./forge_v01_engine.ts";
import {
  fetchRealCloudBlueprints,
  fetchRealCloudBlueprintsRemote,
  FORGE_SCORING_SSOT,
} from "./real_cloud_stream.ts";

export interface CloudBlueprintStream {
  source: string;
  fetch(): Promise<unknown[]>;
}

export class RealCloudStream implements CloudBlueprintStream {
  readonly source = "forge-real-blueprints-v01";

  async fetch(): Promise<unknown[]> {
    return fetchRealCloudBlueprints();
  }
}

export class RemoteCloudStream implements CloudBlueprintStream {
  readonly source = "railway-forge-blueprints";

  constructor(private readonly baseUrl: string) {}

  async fetch(): Promise<unknown[]> {
    return fetchRealCloudBlueprintsRemote(this.baseUrl);
  }
}

export class MockCloudStream implements CloudBlueprintStream {
  readonly source = "mock-cloud-plans";

  async fetch(): Promise<unknown[]> {
    return fetchMockCloudBlueprints();
  }
}

function scoringConfig(): ForgeScoringConfig {
  return {
    target_repo: FORGE_SCORING_SSOT.target_repo,
    core_capabilities: FORGE_SCORING_SSOT.core_capabilities,
    client_problems: FORGE_SCORING_SSOT.client_problems,
    already_implemented_plan_ids: FORGE_SCORING_SSOT.already_implemented_plan_ids,
    already_implemented_signatures: FORGE_SCORING_SSOT.already_implemented_signatures,
    vague_keyword_patterns: FORGE_SCORING_SSOT.vague_keyword_patterns,
    dedup_similarity_threshold: FORGE_SCORING_SSOT.dedup_similarity_threshold,
    score_boost_patterns: FORGE_SCORING_SSOT.score_boost_patterns,
    score_penalty_patterns: FORGE_SCORING_SSOT.score_penalty_patterns,
    tier_score: FORGE_SCORING_SSOT.tier_score,
  };
}

export function runWinTest(result: ForgeEngineResult): { ok: boolean; errors: string[] } {
  const errors: string[] = [];
  const { funnel, top_10, all_ranked } = result;

  const accounted =
    funnel.validRemaining +
    funnel.malformedDropped +
    funnel.dupesDropped +
    funnel.alreadyHaveDropped;
  if (accounted !== funnel.totalIn) {
    errors.push(`Funnel mismatch: ${accounted} != ${funnel.totalIn}`);
  }

  if (result.summary_line !== result.funnel && result.summary_line.length < 20) {
    errors.push("summary_line missing");
  }

  if (top_10.length !== 10) {
    errors.push(`Expected top_10 length 10, got ${top_10.length}`);
  }

  if (top_10.length > 0 && all_ranked.length > 10) {
    const minTop = Math.min(...top_10.map((p) => p.score));
    const maxRest = Math.max(...all_ranked.slice(10).map((p) => p.score));
    if (minTop < maxRest) {
      errors.push(`min top-10 score ${minTop} < max lower-ranked ${maxRest}`);
    }
  }

  return { ok: errors.length === 0, errors };
}

export async function runForgeV01CloudSimulation(
  stream: CloudBlueprintStream = new RealCloudStream(),
): Promise<{
  result: ForgeEngineResult;
  outputJson: string;
  summaryLine: string;
  winTest: { ok: boolean; errors: string[] };
}> {
  const blueprints = await stream.fetch();
  const cfg = stream.source === "mock-cloud-plans" ? undefined : scoringConfig();
  const result = runForgeV01Engine(blueprints, cfg);
  const outputJson = buildForgeOutputJson(result);
  const winTest = runWinTest(result);
  return { result, outputJson, summaryLine: result.summary_line, winTest };
}

async function main(): Promise<void> {
  const args = new Set(process.argv.slice(2));
  const stream = args.has("--mock")
    ? new MockCloudStream()
    : args.has("--remote")
      ? new RemoteCloudStream(
          process.env.FORGE_CLOUD_URL ??
            "https://sourcea-fbe-runner-production.up.railway.app",
        )
      : new RealCloudStream();

  console.log(`Forge-v0.1 · stream=${stream.source} · architecture=A (cloud code, Mac read-only)`);
  const { outputJson, summaryLine, winTest, result } = await runForgeV01CloudSimulation(stream);

  console.log(summaryLine);
  console.log("");
  console.log(`WIN TEST QUESTION: ${result.win_test_question}`);
  console.log("--- top 10 (your yes/no) ---");
  for (const line of result.win_test_card) console.log(`  ${line}`);
  console.log("");
  console.log("--- forge_v0.1_output.json (in-memory · cloud artifact) ---");
  console.log(outputJson);

  if (winTest.ok) console.log("WIN TEST: PASS");
  else {
    console.error("WIN TEST: FAIL");
    for (const e of winTest.errors) console.error(`  - ${e}`);
    process.exitCode = 1;
  }
}

const isMain =
  typeof process !== "undefined" &&
  !!process.argv[1] &&
  (process.argv[1].endsWith("runner.ts") || process.argv[1].endsWith("runner.js"));

if (isMain) {
  main().catch((err) => {
    console.error(err instanceof Error ? err.message : String(err));
    process.exitCode = 1;
  });
}
