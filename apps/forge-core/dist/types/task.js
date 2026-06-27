import { randomUUID } from "node:crypto";
import { z } from "zod";
export const ForgeTaskKindSchema = z.enum([
    "llm_execute",
    "execute_stub",
    "compile_only",
]);
export const ExecutorProviderSchema = z.enum(["openai", "gemini"]);
export const ForgeTaskPayloadSchema = z.object({
    goal: z.string().min(1),
    prompt: z.string().min(1).optional(),
    provider: ExecutorProviderSchema.optional(),
    model: z.string().optional(),
    work_order_id: z.string().optional(),
});
export const ForgeTaskSchema = z.object({
    schema: z.literal("forge-task-v1"),
    id: z.string().min(1),
    run_id: z.string().uuid(),
    kind: ForgeTaskKindSchema,
    agent_id: z.string().min(1),
    role: z.enum([
        "planner",
        "builder",
        "critic",
        "repair",
        "optimizer",
        "deployer",
        "admin",
    ]),
    action_type: z.string().min(1).default("read_file"),
    payload: ForgeTaskPayloadSchema,
    created_at: z.string().datetime(),
});
export const ForgeTaskStatusSchema = z.enum([
    "queued",
    "processing",
    "completed",
    "denied",
    "failed",
]);
export const ForgeTaskRecordSchema = ForgeTaskSchema.extend({
    status: ForgeTaskStatusSchema,
    updated_at: z.string().datetime(),
    governance: z.record(z.unknown()).optional(),
    error: z.string().optional(),
    state_path: z.string().optional(),
    receipt_path: z.string().optional(),
    result: z.string().optional(),
});
/** Public API — POST /tasks */
export const SubmitTaskSchema = z.object({
    goal: z.string().min(1),
    provider: ExecutorProviderSchema.optional(),
});
export function newTaskId() {
    return `tsk_${randomUUID().replace(/-/g, "")}`;
}
export function newRunId() {
    return randomUUID();
}
