import { mkdir, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { ForgeRunStateSchema, } from "../types/state.js";
import { ForgeTaskRecordSchema, } from "../types/task.js";
import { getReceiptsDir, getRunsDir, getTasksDir } from "../paths.js";
async function ensureDir(path) {
    await mkdir(path, { recursive: true });
}
export async function saveTaskRecord(record) {
    await ensureDir(getTasksDir());
    const path = join(getTasksDir(), `${record.id}.json`);
    await writeFile(path, `${JSON.stringify(record, null, 2)}\n`, "utf8");
    return path;
}
export async function loadTaskRecord(taskId) {
    const path = join(getTasksDir(), `${taskId}.json`);
    try {
        const raw = await readFile(path, "utf8");
        return ForgeTaskRecordSchema.parse(JSON.parse(raw));
    }
    catch {
        return null;
    }
}
export async function saveRunState(state) {
    await ensureDir(getRunsDir());
    const path = join(getRunsDir(), `${state.task_id}.json`);
    await writeFile(path, `${JSON.stringify(state, null, 2)}\n`, "utf8");
    return path;
}
export async function loadRunState(taskId) {
    const path = join(getRunsDir(), `${taskId}.json`);
    try {
        const raw = await readFile(path, "utf8");
        return ForgeRunStateSchema.parse(JSON.parse(raw));
    }
    catch {
        return null;
    }
}
export function toPersistedState(state) {
    return {
        task_id: state.task_id,
        created_at: state.created_at,
        status: state.status,
        result: state.result,
    };
}
export async function saveReceipt(taskId, receipt) {
    await ensureDir(getReceiptsDir());
    const path = join(getReceiptsDir(), `${taskId}.json`);
    await writeFile(path, `${JSON.stringify(receipt, null, 2)}\n`, "utf8");
    return path;
}
