import {
  createQueuedTask,
  getStateByTaskId,
  getTaskById,
  SubmitTaskSchema,
  toPersistedState,
} from "@sourcea/forge-core";

export async function submitTask(body: unknown) {
  const parsed = SubmitTaskSchema.safeParse(body);
  if (!parsed.success) {
    return { ok: false as const, error: parsed.error.flatten() };
  }

  const { record } = await createQueuedTask(parsed.data);
  return {
    ok: true as const,
    task_id: record.id,
    status: record.status,
  };
}

export async function fetchTask(taskId: string) {
  const task = await getTaskById(taskId);
  if (!task) {
    return { ok: false as const, error: "task_not_found" };
  }
  return {
    ok: true as const,
    task_id: task.id,
    status: task.status,
    created_at: task.created_at,
    result: task.result,
    error: task.error,
  };
}

export async function fetchState(taskId: string) {
  const state = await getStateByTaskId(taskId);
  if (!state) {
    return { ok: false as const, error: "state_not_found" };
  }
  return { ok: true as const, state: toPersistedState(state) };
}
