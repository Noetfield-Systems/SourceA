import { z } from "zod";
export declare const ForgeTaskKindSchema: z.ZodEnum<["llm_execute", "execute_stub", "compile_only"]>;
export declare const ExecutorProviderSchema: z.ZodEnum<["openai", "gemini"]>;
export declare const ForgeTaskPayloadSchema: z.ZodObject<{
    goal: z.ZodString;
    prompt: z.ZodOptional<z.ZodString>;
    provider: z.ZodOptional<z.ZodEnum<["openai", "gemini"]>>;
    model: z.ZodOptional<z.ZodString>;
    work_order_id: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    goal: string;
    prompt?: string | undefined;
    provider?: "openai" | "gemini" | undefined;
    model?: string | undefined;
    work_order_id?: string | undefined;
}, {
    goal: string;
    prompt?: string | undefined;
    provider?: "openai" | "gemini" | undefined;
    model?: string | undefined;
    work_order_id?: string | undefined;
}>;
export declare const ForgeTaskSchema: z.ZodObject<{
    schema: z.ZodLiteral<"forge-task-v1">;
    id: z.ZodString;
    run_id: z.ZodString;
    kind: z.ZodEnum<["llm_execute", "execute_stub", "compile_only"]>;
    agent_id: z.ZodString;
    role: z.ZodEnum<["planner", "builder", "critic", "repair", "optimizer", "deployer", "admin"]>;
    action_type: z.ZodDefault<z.ZodString>;
    payload: z.ZodObject<{
        goal: z.ZodString;
        prompt: z.ZodOptional<z.ZodString>;
        provider: z.ZodOptional<z.ZodEnum<["openai", "gemini"]>>;
        model: z.ZodOptional<z.ZodString>;
        work_order_id: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        goal: string;
        prompt?: string | undefined;
        provider?: "openai" | "gemini" | undefined;
        model?: string | undefined;
        work_order_id?: string | undefined;
    }, {
        goal: string;
        prompt?: string | undefined;
        provider?: "openai" | "gemini" | undefined;
        model?: string | undefined;
        work_order_id?: string | undefined;
    }>;
    created_at: z.ZodString;
}, "strip", z.ZodTypeAny, {
    schema: "forge-task-v1";
    id: string;
    run_id: string;
    kind: "llm_execute" | "execute_stub" | "compile_only";
    agent_id: string;
    role: "planner" | "builder" | "critic" | "repair" | "optimizer" | "deployer" | "admin";
    action_type: string;
    payload: {
        goal: string;
        prompt?: string | undefined;
        provider?: "openai" | "gemini" | undefined;
        model?: string | undefined;
        work_order_id?: string | undefined;
    };
    created_at: string;
}, {
    schema: "forge-task-v1";
    id: string;
    run_id: string;
    kind: "llm_execute" | "execute_stub" | "compile_only";
    agent_id: string;
    role: "planner" | "builder" | "critic" | "repair" | "optimizer" | "deployer" | "admin";
    payload: {
        goal: string;
        prompt?: string | undefined;
        provider?: "openai" | "gemini" | undefined;
        model?: string | undefined;
        work_order_id?: string | undefined;
    };
    created_at: string;
    action_type?: string | undefined;
}>;
export declare const ForgeTaskStatusSchema: z.ZodEnum<["queued", "processing", "completed", "denied", "failed"]>;
export declare const ForgeTaskRecordSchema: z.ZodObject<{
    schema: z.ZodLiteral<"forge-task-v1">;
    id: z.ZodString;
    run_id: z.ZodString;
    kind: z.ZodEnum<["llm_execute", "execute_stub", "compile_only"]>;
    agent_id: z.ZodString;
    role: z.ZodEnum<["planner", "builder", "critic", "repair", "optimizer", "deployer", "admin"]>;
    action_type: z.ZodDefault<z.ZodString>;
    payload: z.ZodObject<{
        goal: z.ZodString;
        prompt: z.ZodOptional<z.ZodString>;
        provider: z.ZodOptional<z.ZodEnum<["openai", "gemini"]>>;
        model: z.ZodOptional<z.ZodString>;
        work_order_id: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        goal: string;
        prompt?: string | undefined;
        provider?: "openai" | "gemini" | undefined;
        model?: string | undefined;
        work_order_id?: string | undefined;
    }, {
        goal: string;
        prompt?: string | undefined;
        provider?: "openai" | "gemini" | undefined;
        model?: string | undefined;
        work_order_id?: string | undefined;
    }>;
    created_at: z.ZodString;
} & {
    status: z.ZodEnum<["queued", "processing", "completed", "denied", "failed"]>;
    updated_at: z.ZodString;
    governance: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
    error: z.ZodOptional<z.ZodString>;
    state_path: z.ZodOptional<z.ZodString>;
    receipt_path: z.ZodOptional<z.ZodString>;
    result: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    status: "queued" | "processing" | "completed" | "denied" | "failed";
    schema: "forge-task-v1";
    id: string;
    run_id: string;
    kind: "llm_execute" | "execute_stub" | "compile_only";
    agent_id: string;
    role: "planner" | "builder" | "critic" | "repair" | "optimizer" | "deployer" | "admin";
    action_type: string;
    payload: {
        goal: string;
        prompt?: string | undefined;
        provider?: "openai" | "gemini" | undefined;
        model?: string | undefined;
        work_order_id?: string | undefined;
    };
    created_at: string;
    updated_at: string;
    error?: string | undefined;
    governance?: Record<string, unknown> | undefined;
    state_path?: string | undefined;
    receipt_path?: string | undefined;
    result?: string | undefined;
}, {
    status: "queued" | "processing" | "completed" | "denied" | "failed";
    schema: "forge-task-v1";
    id: string;
    run_id: string;
    kind: "llm_execute" | "execute_stub" | "compile_only";
    agent_id: string;
    role: "planner" | "builder" | "critic" | "repair" | "optimizer" | "deployer" | "admin";
    payload: {
        goal: string;
        prompt?: string | undefined;
        provider?: "openai" | "gemini" | undefined;
        model?: string | undefined;
        work_order_id?: string | undefined;
    };
    created_at: string;
    updated_at: string;
    error?: string | undefined;
    action_type?: string | undefined;
    governance?: Record<string, unknown> | undefined;
    state_path?: string | undefined;
    receipt_path?: string | undefined;
    result?: string | undefined;
}>;
/** Public API — POST /tasks */
export declare const SubmitTaskSchema: z.ZodObject<{
    goal: z.ZodString;
    provider: z.ZodOptional<z.ZodEnum<["openai", "gemini"]>>;
}, "strip", z.ZodTypeAny, {
    goal: string;
    provider?: "openai" | "gemini" | undefined;
}, {
    goal: string;
    provider?: "openai" | "gemini" | undefined;
}>;
export type ForgeTask = z.infer<typeof ForgeTaskSchema>;
export type ForgeTaskRecord = z.infer<typeof ForgeTaskRecordSchema>;
export type SubmitTaskInput = z.infer<typeof SubmitTaskSchema>;
export type ExecutorProvider = z.infer<typeof ExecutorProviderSchema>;
export declare function newTaskId(): string;
export declare function newRunId(): string;
