import { z } from "zod";
export const GovernanceCheckNameSchema = z.enum([
    "rate_limit",
    "cost_limit",
    "allowed_action",
]);
export const GovernRequestSchema = z.object({
    agent_id: z.string().min(1),
    agent_role: z.string().min(1),
    action_type: z.string().min(1),
    task_id: z.string().optional(),
    payload: z.record(z.unknown()).optional(),
    dry_run: z.boolean().optional(),
});
export const GovernDecisionSchema = z.object({
    status: z.enum(["ALLOW", "DENY"]),
    reason: z.string().optional(),
    checks: z
        .array(z.object({
        name: GovernanceCheckNameSchema,
        status: z.enum(["ALLOW", "DENY"]),
        reason: z.string().optional(),
    }))
        .optional(),
    kernel: z.record(z.unknown()).optional(),
});
