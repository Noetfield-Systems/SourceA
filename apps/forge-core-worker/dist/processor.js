import { createTaskWorker, loadTaskRecord, saveReceipt, saveRunState, saveTaskRecord, } from "@sourcea/forge-core";
import { checkGovernance } from "./governance.js";
import { executeLlm } from "./llm.js";
async function updateTask(taskId, patch) {
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
export async function processTask(task) {
    const now = new Date().toISOString();
    await updateTask(task.id, { status: "processing" });
    const governance = await checkGovernance(task);
    if (governance.status !== "ALLOW") {
        const deniedState = {
            schema: "forge-run-state-v1",
            run_id: task.run_id,
            task_id: task.id,
            status: "denied",
            kind: task.kind,
            agent_id: task.agent_id,
            governance,
            created_at: task.created_at,
            completed_at: now,
        };
        const statePath = await saveRunState(deniedState);
        const receiptPath = await saveReceipt(task.run_id, {
            schema: "forge-receipt-v1",
            run_id: task.run_id,
            task_id: task.id,
            status: "denied",
            governance,
            state_path: statePath,
            at: now,
        });
        await updateTask(task.id, {
            status: "denied",
            governance,
            state_path: statePath,
            receipt_path: receiptPath,
            error: governance.reason,
        });
        return;
    }
    let llmResult;
    if (task.kind === "execute_stub") {
        llmResult = {
            ok: true,
            provider: "forge-stub",
            stub: true,
            text: `stub-ok:${task.payload.prompt ?? "no-prompt"}`,
        };
    }
    else if (task.kind === "llm_execute" || task.kind === "compile_only") {
        const prompt = task.payload.prompt ??
            `Forge task ${task.id} — respond with one concise sentence.`;
        llmResult = await executeLlm(prompt, task.payload.model);
    }
    else {
        llmResult = {
            ok: false,
            provider: "forge",
            error: `unsupported_kind:${task.kind}`,
        };
    }
    const completedAt = new Date().toISOString();
    const finalStatus = llmResult.ok ? "completed" : "failed";
    const runState = {
        schema: "forge-run-state-v1",
        run_id: task.run_id,
        task_id: task.id,
        status: finalStatus === "completed" ? "completed" : "failed",
        kind: task.kind,
        agent_id: task.agent_id,
        governance,
        llm: llmResult,
        result: {
            text: llmResult.text,
            stub: llmResult.stub ?? false,
        },
        created_at: task.created_at,
        completed_at: completedAt,
    };
    const statePath = await saveRunState(runState);
    const receiptPath = await saveReceipt(task.run_id, {
        schema: "forge-receipt-v1",
        run_id: task.run_id,
        task_id: task.id,
        status: finalStatus,
        governance,
        llm: llmResult,
        state_path: statePath,
        at: completedAt,
    });
    await updateTask(task.id, {
        status: finalStatus,
        governance,
        state_path: statePath,
        receipt_path: receiptPath,
        error: llmResult.ok ? undefined : llmResult.error,
    });
}
export function startWorker() {
    const worker = createTaskWorker(processTask);
    worker.on("completed", (job) => {
        console.log(`[forge-worker] completed task=${job.data.id}`);
    });
    worker.on("failed", (job, error) => {
        console.error(`[forge-worker] failed task=${job?.data?.id ?? "unknown"} error=${error.message}`);
    });
    return worker;
}
