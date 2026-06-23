/**
 * @deprecated Use forge_v01_engine.ts + runner.ts
 * Backward-compatible re-exports for existing imports.
 */

export {
  type Blueprint as RawPlan,
  type ValidBlueprint as ValidPlan,
  type ScoredBlueprint as ScoredPlan,
  type ForgeEngineResult as ForgePipelineResult,
  type ForgeFunnelMetrics,
  ioSimilarityPercent,
  isValidBlueprint as isValidPlan,
  stageValidate as validatePlans,
  stageDedup as dedupPlans,
  scoreBlueprint as scorePlan,
  stageScore as scorePlans,
  stageRank as rankPlans,
  stageRoute as routePlans,
  runForgeV01Engine as runForgePipeline,
  formatForgeRunSummary,
  buildForgeOutputJson,
  forgeEdgeHandler as forgeHandler,
} from "./forge_v01_engine.ts";

export { runWinTest, runForgeV01CloudSimulation as executeForgeV01 } from "./runner.ts";
