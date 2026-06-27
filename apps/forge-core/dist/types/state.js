import { z } from "zod";
export const ForgeRunStateSchema = z.object({
    schema: z.literal("forge-run-state-v1"),
    task_id: z.string().min(1),
    run_id: z.string().uuid(),
    created_at: z.string().datetime(),
    status: z.enum(["completed", "denied", "failed", "processing", "queued"]),
    result: z.string().optional(),
    kind: z.string().optional(),
    agent_id: z.string().optional(),
    governance: z.record(z.unknown()).optional(),
    execution: z
        .object({
        ok: z.boolean(),
        provider: z.string(),
        model: z.string().optional(),
        text: z.string().optional(),
        error: z.string().optional(),
        usage: z.record(z.unknown()).optional(),
    })
        .optional(),
    completed_at: z.string().datetime().optional(),
});
/** Minimal persisted state shape required by MVP spec */
export const PersistedStateSchema = z.object({
    task_id: z.string(),
    created_at: z.string(),
    status: z.string(),
    result: z.string().optional(),
});
