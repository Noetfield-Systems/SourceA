import { z } from "zod";
export declare const ForgeRunStateSchema: z.ZodObject<{
    schema: z.ZodLiteral<"forge-run-state-v1">;
    task_id: z.ZodString;
    run_id: z.ZodString;
    created_at: z.ZodString;
    status: z.ZodEnum<["completed", "denied", "failed", "processing", "queued"]>;
    result: z.ZodOptional<z.ZodString>;
    kind: z.ZodOptional<z.ZodString>;
    agent_id: z.ZodOptional<z.ZodString>;
    governance: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
    execution: z.ZodOptional<z.ZodObject<{
        ok: z.ZodBoolean;
        provider: z.ZodString;
        model: z.ZodOptional<z.ZodString>;
        text: z.ZodOptional<z.ZodString>;
        error: z.ZodOptional<z.ZodString>;
        usage: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
    }, "strip", z.ZodTypeAny, {
        provider: string;
        ok: boolean;
        error?: string | undefined;
        model?: string | undefined;
        text?: string | undefined;
        usage?: Record<string, unknown> | undefined;
    }, {
        provider: string;
        ok: boolean;
        error?: string | undefined;
        model?: string | undefined;
        text?: string | undefined;
        usage?: Record<string, unknown> | undefined;
    }>>;
    completed_at: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    status: "queued" | "processing" | "completed" | "denied" | "failed";
    schema: "forge-run-state-v1";
    run_id: string;
    created_at: string;
    task_id: string;
    kind?: string | undefined;
    agent_id?: string | undefined;
    governance?: Record<string, unknown> | undefined;
    result?: string | undefined;
    execution?: {
        provider: string;
        ok: boolean;
        error?: string | undefined;
        model?: string | undefined;
        text?: string | undefined;
        usage?: Record<string, unknown> | undefined;
    } | undefined;
    completed_at?: string | undefined;
}, {
    status: "queued" | "processing" | "completed" | "denied" | "failed";
    schema: "forge-run-state-v1";
    run_id: string;
    created_at: string;
    task_id: string;
    kind?: string | undefined;
    agent_id?: string | undefined;
    governance?: Record<string, unknown> | undefined;
    result?: string | undefined;
    execution?: {
        provider: string;
        ok: boolean;
        error?: string | undefined;
        model?: string | undefined;
        text?: string | undefined;
        usage?: Record<string, unknown> | undefined;
    } | undefined;
    completed_at?: string | undefined;
}>;
export type ForgeRunState = z.infer<typeof ForgeRunStateSchema>;
/** Minimal persisted state shape required by MVP spec */
export declare const PersistedStateSchema: z.ZodObject<{
    task_id: z.ZodString;
    created_at: z.ZodString;
    status: z.ZodString;
    result: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    status: string;
    created_at: string;
    task_id: string;
    result?: string | undefined;
}, {
    status: string;
    created_at: string;
    task_id: string;
    result?: string | undefined;
}>;
export type PersistedState = z.infer<typeof PersistedStateSchema>;
