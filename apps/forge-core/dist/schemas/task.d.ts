import { z } from "zod";
/** @deprecated Use SubmitTaskSchema — kept for backward compatibility */
export declare const ForgeTaskPayloadSchema: z.ZodObject<{
    prompt: z.ZodOptional<z.ZodString>;
    goal: z.ZodOptional<z.ZodString>;
    provider: z.ZodOptional<z.ZodEnum<["openai", "gemini"]>>;
    model: z.ZodOptional<z.ZodString>;
    work_order_id: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    goal?: string | undefined;
    prompt?: string | undefined;
    provider?: "openai" | "gemini" | undefined;
    model?: string | undefined;
    work_order_id?: string | undefined;
}, {
    goal?: string | undefined;
    prompt?: string | undefined;
    provider?: "openai" | "gemini" | undefined;
    model?: string | undefined;
    work_order_id?: string | undefined;
}>;
export declare const CreateTaskInputSchema: z.ZodEffects<z.ZodObject<{
    kind: z.ZodDefault<z.ZodEnum<["llm_execute", "execute_stub", "compile_only"]>>;
    agent_id: z.ZodDefault<z.ZodString>;
    role: z.ZodDefault<z.ZodEnum<["planner", "builder", "critic", "repair", "optimizer", "deployer", "admin"]>>;
    action_type: z.ZodDefault<z.ZodString>;
    payload: z.ZodObject<{
        prompt: z.ZodOptional<z.ZodString>;
        goal: z.ZodOptional<z.ZodString>;
        provider: z.ZodOptional<z.ZodEnum<["openai", "gemini"]>>;
        model: z.ZodOptional<z.ZodString>;
        work_order_id: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        goal?: string | undefined;
        prompt?: string | undefined;
        provider?: "openai" | "gemini" | undefined;
        model?: string | undefined;
        work_order_id?: string | undefined;
    }, {
        goal?: string | undefined;
        prompt?: string | undefined;
        provider?: "openai" | "gemini" | undefined;
        model?: string | undefined;
        work_order_id?: string | undefined;
    }>;
}, "strip", z.ZodTypeAny, {
    kind: "llm_execute" | "execute_stub" | "compile_only";
    agent_id: string;
    role: "planner" | "builder" | "critic" | "repair" | "optimizer" | "deployer" | "admin";
    action_type: string;
    payload: {
        goal?: string | undefined;
        prompt?: string | undefined;
        provider?: "openai" | "gemini" | undefined;
        model?: string | undefined;
        work_order_id?: string | undefined;
    };
}, {
    payload: {
        goal?: string | undefined;
        prompt?: string | undefined;
        provider?: "openai" | "gemini" | undefined;
        model?: string | undefined;
        work_order_id?: string | undefined;
    };
    kind?: "llm_execute" | "execute_stub" | "compile_only" | undefined;
    agent_id?: string | undefined;
    role?: "planner" | "builder" | "critic" | "repair" | "optimizer" | "deployer" | "admin" | undefined;
    action_type?: string | undefined;
}>, {
    kind: "llm_execute" | "execute_stub" | "compile_only";
    agent_id: string;
    role: "planner" | "builder" | "critic" | "repair" | "optimizer" | "deployer" | "admin";
    action_type: string;
    payload: {
        goal?: string | undefined;
        prompt?: string | undefined;
        provider?: "openai" | "gemini" | undefined;
        model?: string | undefined;
        work_order_id?: string | undefined;
    };
}, {
    payload: {
        goal?: string | undefined;
        prompt?: string | undefined;
        provider?: "openai" | "gemini" | undefined;
        model?: string | undefined;
        work_order_id?: string | undefined;
    };
    kind?: "llm_execute" | "execute_stub" | "compile_only" | undefined;
    agent_id?: string | undefined;
    role?: "planner" | "builder" | "critic" | "repair" | "optimizer" | "deployer" | "admin" | undefined;
    action_type?: string | undefined;
}>;
export type CreateTaskInput = z.infer<typeof CreateTaskInputSchema>;
