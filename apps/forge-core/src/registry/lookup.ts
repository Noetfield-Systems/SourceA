import { readFile } from "node:fs/promises";

import { loadRunState, loadTaskRecord } from "../state/store.js";
import { getRegistryPath } from "../paths.js";
import type { ForgeRunState } from "../types/state.js";
import type { ForgeTaskRecord } from "../types/task.js";

export async function getTaskById(taskId: string): Promise<ForgeTaskRecord | null> {
  return loadTaskRecord(taskId);
}

export async function getStateByTaskId(taskId: string): Promise<ForgeRunState | null> {
  return loadRunState(taskId);
}

export async function loadAgentRegistry(): Promise<Record<string, unknown>> {
  const raw = await readFile(getRegistryPath(), "utf8");
  return JSON.parse(raw) as Record<string, unknown>;
}
