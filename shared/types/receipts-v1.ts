import { z } from "zod";

/** MCP chain receipt export — read-only verify layer */
export const McpReceiptV1 = z.object({
  schema: z.literal("mcp-receipt-v1"),
  receipt_id: z.string().uuid(),
  campus: z.enum(["sourcea", "virlux", "noetfield", "trustfield"]),
  tool: z.string(),
  verdict: z.enum(["PASS", "FAIL", "MOCK_ONLY"]),
  honest_label: z.string(),
  at: z.string().datetime(),
});
export type McpReceiptV1 = z.infer<typeof McpReceiptV1>;

export const GovernanceReceiptExportV1 = z.object({
  schema: z.literal("governance-receipt-export-v1"),
  queue_sa: z.string().optional(),
  factory_now_line: z.string().optional(),
  drift_score: z.number().min(0).max(100).optional(),
});
export type GovernanceReceiptExportV1 = z.infer<typeof GovernanceReceiptExportV1>;
