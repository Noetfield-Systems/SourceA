import { z } from "zod";

/** FBE execution contract spec — mirrors data/fbe_execution_contract_v1.json */
export const FbeExecutionContractSpecV1 = z.object({
  schema: z.literal("fbe-execution-contract-v1"),
  version: z.string(),
  saved_at: z.string().optional(),
  kernel_version: z.string(),
  kernel_hash_source: z.string().optional(),
  default_execution_mode: z.enum(["CLOUD_ONLY", "LOCAL_ALLOWED"]),
  allowed_execution_modes: z.array(z.enum(["CLOUD_ONLY", "LOCAL_ALLOWED"])),
  required_fields: z.array(z.string()),
  policy_gate: z.object({
    deny_local_when_freeze: z.boolean().optional(),
    require_kernel_version_match: z.boolean().optional(),
    require_policy_hash_when_tenant_set: z.boolean().optional(),
  }),
  receipt_schema: z.string().optional(),
  receipt_fields: z.array(z.string()).optional(),
  route_map: z.record(z.string(), z.record(z.string(), z.string())).optional(),
});
export type FbeExecutionContractSpecV1 = z.infer<typeof FbeExecutionContractSpecV1>;

/** Runtime contract envelope — mirrors scripts/fbe/lib/execution_contract_v1.py build_contract() */
export const FbeExecutionContractV1 = z.object({
  schema: z.literal("fbe-execution-contract-v1"),
  job_id: z.string().min(1),
  factory_id: z.string().min(1),
  kernel_version: z.string().min(1),
  kernel_hash: z.string().optional(),
  tenant_id: z.string().min(1),
  bay_slug: z.string().optional(),
  work_order_id: z.string().optional(),
  input: z.record(z.string(), z.unknown()).optional(),
  policy_pack: z.string().optional(),
  policy_hash: z.string().optional(),
  execution_mode: z.enum(["CLOUD_ONLY", "LOCAL_ALLOWED"]),
  at: z.string(),
});
export type FbeExecutionContractV1 = z.infer<typeof FbeExecutionContractV1>;

export const FbeContractValidationV1 = z.object({
  ok: z.boolean(),
  errors: z.array(z.string()),
  contract: FbeExecutionContractV1.optional(),
});
export type FbeContractValidationV1 = z.infer<typeof FbeContractValidationV1>;

export const FbePolicyGateV1 = z.object({
  ok: z.boolean(),
  decision: z.enum(["ALLOW", "DENY"]),
  reasons: z.array(z.string()),
  policy_passed: z.boolean(),
  at: z.string(),
});
export type FbePolicyGateV1 = z.infer<typeof FbePolicyGateV1>;

/** Validate required fields + execution_mode against spec (TS mirror of validate_contract). */
export function validateExecutionContract(
  contract: FbeExecutionContractV1,
  spec: FbeExecutionContractSpecV1,
): FbeContractValidationV1 {
  const errors: string[] = [];
  for (const key of spec.required_fields) {
    const val = (contract as Record<string, unknown>)[key];
    if (val === undefined || val === null || String(val).trim() === "") {
      errors.push(`missing:${key}`);
    }
  }
  if (contract.execution_mode && !spec.allowed_execution_modes.includes(contract.execution_mode)) {
    errors.push(`invalid_execution_mode:${contract.execution_mode}`);
  }
  if (spec.policy_gate.require_kernel_version_match) {
    const kv = contract.kernel_version || "";
    if (kv && !kv.startsWith("fbe-v") && !kv.includes("+")) {
      errors.push("kernel_version_malformed");
    }
  }
  return { ok: errors.length === 0, errors, contract };
}

/** Policy gate mirror — freeze + cloud URL checks before SHIP. */
export function policyGateExecutionContract(
  contract: FbeExecutionContractV1,
  opts: { freezeActive: boolean; cloudUrlConfigured: boolean },
): FbePolicyGateV1 {
  const reasons: string[] = [];
  if (opts.freezeActive && contract.execution_mode === "LOCAL_ALLOWED") {
    reasons.push("freeze_blocks_local_execution");
  }
  if (opts.freezeActive && !opts.cloudUrlConfigured) {
    reasons.push("freeze_requires_cloud_worker_url");
  }
  const decision = reasons.length === 0 ? "ALLOW" : "DENY";
  return {
    ok: decision === "ALLOW",
    decision,
    reasons,
    policy_passed: decision === "ALLOW",
    at: new Date().toISOString(),
  };
}
