import { z } from "zod";
import { ExecutorProviderSchema } from "../types/task.js";
/** @deprecated Use SubmitTaskSchema — kept for backward compatibility */
export const ForgeTaskPayloadSchema = z.object({
    prompt: z.string().min(1).optional(),
    goal: z.string().min(1).optional(),
    provider: ExecutorProviderSchema.optional(),
    model: z.string().optional(),
    work_order_id: z.string().optional(),
});
export const CreateTaskInputSchema = z
    .object({
    kind: z.enum(["llm_execute", "execute_stub", "compile_only"]).default("llm_execute"),
    agent_id: z.string().min(1).default("forge-worker-1"),
    role: z
        .enum([
        "planner",
        "builder",
        "critic",
        "repair",
        "optimizer",
        "deployer",
        "admin",
    ])
        .default("builder"),
    action_type: z.string().min(1).default("read_file"),
    payload: ForgeTaskPayloadSchema,
})
    .superRefine((value, ctx) => {
    const prompt = value.payload.prompt ?? value.payload.goal;
    if ((value.kind === "llm_execute" || value.kind === "compile_only") &&
        !prompt?.trim()) {
        ctx.addIssue({
            code: z.ZodIssueCode.custom,
            message: "payload.prompt or payload.goal is required",
            path: ["payload", "prompt"],
        });
    }
});
