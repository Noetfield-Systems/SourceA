import { enqueueTask } from "../queue.js";
import { saveTaskRecord, loadTaskRecord } from "../state/store.js";
import { newRunId, newTaskId, } from "../types/task.js";
export async function createQueuedTask(input) {
    const now = new Date().toISOString();
    const id = newTaskId();
    const runId = newRunId();
    const task = {
        schema: "forge-task-v1",
        id,
        run_id: runId,
        kind: "llm_execute",
        agent_id: "forge-worker-1",
        role: "builder",
        action_type: "read_file",
        payload: {
            goal: input.goal,
            prompt: input.goal,
            provider: input.provider,
        },
        created_at: now,
    };
    const record = {
        ...task,
        status: "queued",
        updated_at: now,
    };
    await saveTaskRecord(record);
    await enqueueTask(task);
    return { task, record };
}
export async function updateTaskStatus(taskId, patch) {
    const existing = await loadTaskRecord(taskId);
    if (!existing) {
        throw new Error(`task_not_found:${taskId}`);
    }
    const updated = {
        ...existing,
        ...patch,
        updated_at: new Date().toISOString(),
    };
    await saveTaskRecord(updated);
    return updated;
}
