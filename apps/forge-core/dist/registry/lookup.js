import { readFile } from "node:fs/promises";
import { loadRunState, loadTaskRecord } from "../state/store.js";
import { getRegistryPath } from "../paths.js";
export async function getTaskById(taskId) {
    return loadTaskRecord(taskId);
}
export async function getStateByTaskId(taskId) {
    return loadRunState(taskId);
}
export async function loadAgentRegistry() {
    const raw = await readFile(getRegistryPath(), "utf8");
    return JSON.parse(raw);
}
