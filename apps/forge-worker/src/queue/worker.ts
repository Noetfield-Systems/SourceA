import {
  createTaskWorker,
  saveReceipt,
  saveRunState,
  updateTaskStatus,
  type ForgeRunState,
  type ForgeTask,
} from "@sourcea/forge-core";

import { checkGovernance } from "../governance/client.js";
import { executePrompt } from "../executor/index.js";

async function persistFailure(
  task: ForgeTask,
  error: string,
  governance?: ForgeRunState["governance"],
): Promise<void> {
  const now = new Date().toISOString();
  const runState: ForgeRunState = {
    schema: "forge-run-state-v1",
    task_id: task.id,
    run_id: task.run_id,
    status: "failed",
    created_at: task.created_at,
    completed_at: now,
    governance,
    result: error,
  };
  const statePath = await saveRunState(runState);
  await saveReceipt(task.id, {
    schema: "forge-receipt-v1",
    task_id: task.id,
    status: "failed",
    error,
    state_path: statePath,
    at: now,
  });
  await updateTaskStatus(task.id, {
    status: "failed",
    error,
    state_path: statePath,
    result: error,
  });
}

export async function processTask(task: ForgeTask): Promise<void> {
  const now = new Date().toISOString();
  await updateTaskStatus(task.id, { status: "processing" });

  try {
    const governance = await checkGovernance(task);

    if (governance.status !== "ALLOW") {
      const deniedState: ForgeRunState = {
        schema: "forge-run-state-v1",
        task_id: task.id,
        run_id: task.run_id,
        status: "denied",
        created_at: task.created_at,
        completed_at: now,
        governance,
        result: governance.reason,
      };
      const statePath = await saveRunState(deniedState);
      await saveReceipt(task.id, {
        schema: "forge-receipt-v1",
        task_id: task.id,
        status: "denied",
        governance,
        state_path: statePath,
        at: now,
      });
      await updateTaskStatus(task.id, {
        status: "denied",
        governance,
        state_path: statePath,
        error: governance.reason,
        result: governance.reason,
      });
      return;
    }

    const prompt = task.payload.goal || task.payload.prompt || "";
    const execution = await executePrompt(prompt, task.payload.provider);

    const completedAt = new Date().toISOString();
    const finalStatus = execution.ok ? "completed" : "failed";

    const runState: ForgeRunState = {
      schema: "forge-run-state-v1",
      task_id: task.id,
      run_id: task.run_id,
      status: finalStatus,
      kind: task.kind,
      agent_id: task.agent_id,
      governance,
      execution,
      result: execution.text,
      created_at: task.created_at,
      completed_at: completedAt,
    };

    const statePath = await saveRunState(runState);
    await saveReceipt(task.id, {
      schema: "forge-receipt-v1",
      task_id: task.id,
      status: finalStatus,
      governance,
      execution,
      state_path: statePath,
      at: completedAt,
    });

    await updateTaskStatus(task.id, {
      status: finalStatus,
      governance,
      state_path: statePath,
      result: execution.text,
      error: execution.ok ? undefined : execution.error,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    await persistFailure(task, message);
    throw error;
  }
}

export function startQueueWorker(): ReturnType<typeof createTaskWorker> {
  const worker = createTaskWorker(processTask);

  worker.on("completed", (job) => {
    console.log(`[forge-worker] completed task=${job.data.id}`);
  });

  worker.on("failed", async (job, error) => {
    const task = job?.data;
    console.error(
      `[forge-worker] failed task=${task?.id ?? "unknown"} error=${error.message}`,
    );
    if (task?.id) {
      try {
        await persistFailure(task, error.message);
      } catch {
        // already logged
      }
    }
  });

  return worker;
}
