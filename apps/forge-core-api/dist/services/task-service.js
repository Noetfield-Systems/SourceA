import { createQueuedTask, getStateByTaskId, getTaskById, SubmitTaskSchema, toPersistedState, } from "@sourcea/forge-core";
export async function submitTask(body) {
    const parsed = SubmitTaskSchema.safeParse(body);
    if (!parsed.success) {
        return { ok: false, error: parsed.error.flatten() };
    }
    const { record } = await createQueuedTask(parsed.data);
    return {
        ok: true,
        task_id: record.id,
        status: record.status,
    };
}
export async function fetchTask(taskId) {
    const task = await getTaskById(taskId);
    if (!task) {
        return { ok: false, error: "task_not_found" };
    }
    return {
        ok: true,
        task_id: task.id,
        status: task.status,
        created_at: task.created_at,
        result: task.result,
        error: task.error,
    };
}
export async function fetchState(taskId) {
    const state = await getStateByTaskId(taskId);
    if (!state) {
        return { ok: false, error: "state_not_found" };
    }
    return { ok: true, state: toPersistedState(state) };
}
