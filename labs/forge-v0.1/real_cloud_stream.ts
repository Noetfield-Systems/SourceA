/**
 * Real cloud blueprint stream — 100 plans from secondary-cloud-drain SSOT.
 * Architecture A: payload lives in repo/cloud; Mac runner imports in-memory only.
 */

import realPayload from "../../data/forge-real-blueprints-v01.json" with { type: "json" };
import scoringSsot from "../../data/forge-scoring-ssot-v01.json" with { type: "json" };
import type { Blueprint } from "./forge_v01_engine.ts";

export interface ForgeScoringConfig {
  schema: string;
  target_repo: string;
  core_capabilities: string[];
  client_problems: string[];
  already_implemented_plan_ids: string[];
  already_implemented_signatures: string[];
  vague_keyword_patterns: string[];
  dedup_similarity_threshold: number;
  score_boost_patterns?: { pattern: string; points: number }[];
  score_penalty_patterns?: { pattern: string; points: number }[];
  tier_score?: Record<string, number>;
}

export const FORGE_SCORING_SSOT = scoringSsot as ForgeScoringConfig;

export function fetchRealCloudBlueprints(): Blueprint[] {
  const rows = (realPayload as { blueprints?: Blueprint[] }).blueprints ?? [];
  if (rows.length !== 100) {
    throw new Error(`forge-real-blueprints-v01: expected 100, got ${rows.length}`);
  }
  return rows;
}

/** Simulates GET https://railway.../forge/blueprints/v01.json */
export async function fetchRealCloudBlueprintsRemote(
  baseUrl = "https://sourcea-fbe-runner-production.up.railway.app",
): Promise<Blueprint[]> {
  const res = await fetch(`${baseUrl.replace(/\/$/, "")}/forge/blueprints/v01.json`);
  if (!res.ok) throw new Error(`cloud blueprints fetch failed: ${res.status}`);
  const doc = (await res.json()) as { blueprints?: Blueprint[] };
  const rows = doc.blueprints ?? [];
  if (rows.length !== 100) throw new Error(`remote blueprints count ${rows.length} != 100`);
  return rows;
}
