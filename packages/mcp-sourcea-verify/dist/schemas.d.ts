import { z } from "zod";
export declare const RECEIPT_SCHEMA: z.ZodObject<{
    schema: z.ZodOptional<z.ZodString>;
    receipt_id: z.ZodOptional<z.ZodString>;
    id: z.ZodOptional<z.ZodString>;
    verdict: z.ZodOptional<z.ZodEnum<["PASS", "FAIL", "MOCK_ONLY", "GO", "NO_GO"]>>;
    status: z.ZodOptional<z.ZodString>;
    at: z.ZodOptional<z.ZodString>;
    saved_at: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    schema?: string | undefined;
    receipt_id?: string | undefined;
    id?: string | undefined;
    verdict?: "PASS" | "FAIL" | "MOCK_ONLY" | "GO" | "NO_GO" | undefined;
    status?: string | undefined;
    at?: string | undefined;
    saved_at?: string | undefined;
}, {
    schema?: string | undefined;
    receipt_id?: string | undefined;
    id?: string | undefined;
    verdict?: "PASS" | "FAIL" | "MOCK_ONLY" | "GO" | "NO_GO" | undefined;
    status?: string | undefined;
    at?: string | undefined;
    saved_at?: string | undefined;
}>;
export type ReceiptInput = z.infer<typeof RECEIPT_SCHEMA>;
export declare function receiptId(receipt: ReceiptInput): string;
export declare function verdictFromReceipt(receipt: ReceiptInput): "PASS" | "FAIL" | "MOCK_ONLY";
