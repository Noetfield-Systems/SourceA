import { z } from "zod";
export declare const GovernanceCheckNameSchema: z.ZodEnum<["rate_limit", "cost_limit", "allowed_action"]>;
export declare const GovernRequestSchema: z.ZodObject<{
    agent_id: z.ZodString;
    agent_role: z.ZodString;
    action_type: z.ZodString;
    task_id: z.ZodOptional<z.ZodString>;
    payload: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
    dry_run: z.ZodOptional<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    agent_id: string;
    action_type: string;
    agent_role: string;
    payload?: Record<string, unknown> | undefined;
    task_id?: string | undefined;
    dry_run?: boolean | undefined;
}, {
    agent_id: string;
    action_type: string;
    agent_role: string;
    payload?: Record<string, unknown> | undefined;
    task_id?: string | undefined;
    dry_run?: boolean | undefined;
}>;
export declare const GovernDecisionSchema: z.ZodObject<{
    status: z.ZodEnum<["ALLOW", "DENY"]>;
    reason: z.ZodOptional<z.ZodString>;
    checks: z.ZodOptional<z.ZodArray<z.ZodObject<{
        name: z.ZodEnum<["rate_limit", "cost_limit", "allowed_action"]>;
        status: z.ZodEnum<["ALLOW", "DENY"]>;
        reason: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        name: "rate_limit" | "cost_limit" | "allowed_action";
        status: "ALLOW" | "DENY";
        reason?: string | undefined;
    }, {
        name: "rate_limit" | "cost_limit" | "allowed_action";
        status: "ALLOW" | "DENY";
        reason?: string | undefined;
    }>, "many">>;
    kernel: z.ZodOptional<z.ZodRecord<z.ZodString, z.ZodUnknown>>;
}, "strip", z.ZodTypeAny, {
    status: "ALLOW" | "DENY";
    reason?: string | undefined;
    checks?: {
        name: "rate_limit" | "cost_limit" | "allowed_action";
        status: "ALLOW" | "DENY";
        reason?: string | undefined;
    }[] | undefined;
    kernel?: Record<string, unknown> | undefined;
}, {
    status: "ALLOW" | "DENY";
    reason?: string | undefined;
    checks?: {
        name: "rate_limit" | "cost_limit" | "allowed_action";
        status: "ALLOW" | "DENY";
        reason?: string | undefined;
    }[] | undefined;
    kernel?: Record<string, unknown> | undefined;
}>;
export type GovernRequest = z.infer<typeof GovernRequestSchema>;
export type GovernDecision = z.infer<typeof GovernDecisionSchema>;
