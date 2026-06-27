import { enqueueTask } from "../queue.js";
import { saveTaskRecord, loadTaskRecord } from "../state/store.js";
import {
  type ForgeTask,
  type ForgeTaskRecord,
  newRunId,
  newTaskId,
  type SubmitTaskInput,
} from "../types/task.js";

export async function createQueuedTask(
  input: SubmitTaskInput,
): Promise<{ task: ForgeTask; record: ForgeTaskRecord }> {
  const now = new Date().toISOString();
  const id = newTaskId();
  const runId = newRunId();

  const task: ForgeTask = {
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

  const record: ForgeTaskRecord = {
    ...task,
    status: "queued",
    updated_at: now,
  };

  await saveTaskRecord(record);
  await enqueueTask(task);

  return { task, record };
}

export async function updateTaskStatus(
  taskId: string,
  patch: Partial<ForgeTaskRecord>,
): Promise<ForgeTaskRecord> {
  const existing = await loadTaskRecord(taskId);
  if (!existing) {
    throw new Error(`task_not_found:${taskId}`);
  }
  const updated: ForgeTaskRecord = {
    ...existing,
    ...patch,
    updated_at: new Date().toISOString(),
  };
  await saveTaskRecord(updated);
  return updated;
}
