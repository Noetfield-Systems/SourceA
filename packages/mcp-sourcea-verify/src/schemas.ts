import { z } from "zod";

export const RECEIPT_SCHEMA = z.object({
  schema: z.string().optional(),
  receipt_id: z.string().optional(),
  id: z.string().optional(),
  verdict: z.enum(["PASS", "FAIL", "MOCK_ONLY", "GO", "NO_GO"]).optional(),
  status: z.string().optional(),
  at: z.string().optional(),
  saved_at: z.string().optional(),
});

export type ReceiptInput = z.infer<typeof RECEIPT_SCHEMA>;

export function receiptId(receipt: ReceiptInput): string {
  return receipt.receipt_id ?? receipt.id ?? "unknown";
}

export function verdictFromReceipt(receipt: ReceiptInput): "PASS" | "FAIL" | "MOCK_ONLY" {
  if (receipt.verdict === "PASS" || receipt.verdict === "GO") return "PASS";
  if (receipt.verdict === "FAIL" || receipt.verdict === "NO_GO") return "FAIL";
  if (receipt.verdict === "MOCK_ONLY") return "MOCK_ONLY";
  if (receipt.status?.toUpperCase() === "PASS") return "PASS";
  if (receipt.status?.toUpperCase() === "FAIL") return "FAIL";
  return "MOCK_ONLY";
}
