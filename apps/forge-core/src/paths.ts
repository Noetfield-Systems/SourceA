import { homedir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const packageRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const repoRoot = resolve(packageRoot, "..", "..");

export const FORGE_QUEUE_NAME = "forge-tasks";
export const FORGE_JOB_NAME = "forge.task.execute";

export function getRepoRoot(): string {
  return process.env.SOURCEA_ROOT?.trim() || repoRoot;
}

export function getStateRoot(): string {
  const custom = process.env.FORGE_STATE_DIR?.trim();
  if (custom) return custom;
  return join(homedir(), ".sina", "forge-core");
}

export function getTasksDir(): string {
  return join(getStateRoot(), "tasks");
}

export function getRunsDir(): string {
  return join(getStateRoot(), "state");
}

export function getReceiptsDir(): string {
  return join(getStateRoot(), "receipts");
}

export function getRegistryPath(): string {
  return join(getRepoRoot(), "apps", "forge-core", "registry", "agents.json");
}

export function getGovernanceCliPath(): string {
  return join(
    getRepoRoot(),
    "apps",
    "forge-governance",
    "service",
    "govern_cli.py",
  );
}

export function getScriptsDir(): string {
  return join(getRepoRoot(), "scripts");
}

export function getRedisUrl(): string {
  return process.env.REDIS_URL?.trim() || "redis://127.0.0.1:6379";
}

export function getApiPort(): number {
  const raw = process.env.FORGE_CORE_API_PORT?.trim() || "13040";
  return Number.parseInt(raw, 10);
}
