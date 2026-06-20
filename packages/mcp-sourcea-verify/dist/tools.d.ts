export declare function verifyRun(input: {
    receipt_id?: string;
    receipt?: unknown;
    campus?: string;
}): {
    verdict: "FAIL";
    receipt: null;
    export_url: string;
    violations: import("zod").typeToFlattenedError<{
        schema?: string | undefined;
        receipt_id?: string | undefined;
        id?: string | undefined;
        verdict?: "PASS" | "FAIL" | "MOCK_ONLY" | "GO" | "NO_GO" | undefined;
        status?: string | undefined;
        at?: string | undefined;
        saved_at?: string | undefined;
    }, string>;
    campus?: undefined;
} | {
    verdict: "PASS" | "FAIL" | "MOCK_ONLY";
    receipt: {
        schema?: string | undefined;
        receipt_id?: string | undefined;
        id?: string | undefined;
        verdict?: "PASS" | "FAIL" | "MOCK_ONLY" | "GO" | "NO_GO" | undefined;
        status?: string | undefined;
        at?: string | undefined;
        saved_at?: string | undefined;
    };
    export_url: string;
    campus: string;
    violations?: undefined;
} | {
    verdict: "MOCK_ONLY";
    receipt: {
        schema: string;
        receipt_id: string;
        verdict: string;
        at: string;
        honest_label: string;
    };
    export_url: string;
    campus: string;
    violations?: undefined;
};
export declare function factoryStatus(input: {
    surface?: string;
}): Promise<{
    surface: string;
    factory_now_line: string;
    queue_sa: string;
    as_of: string;
    transport: string;
    source_url: string;
} | {
    surface: string;
    factory_now_line: string;
    queue_sa: string;
    as_of: string;
    transport: string;
}>;
export declare function formPickParse(input: {
    raw_pick: string;
}): {
    subject: string;
    pick: "A" | "B" | "C" | "D";
    effect: string;
    raw_length: number;
};
export declare function emitReceiptReadonly(input: {
    receipt: unknown;
}): {
    schema_ok: boolean;
    violations: import("zod").typeToFlattenedError<{
        schema?: string | undefined;
        receipt_id?: string | undefined;
        id?: string | undefined;
        verdict?: "PASS" | "FAIL" | "MOCK_ONLY" | "GO" | "NO_GO" | undefined;
        status?: string | undefined;
        at?: string | undefined;
        saved_at?: string | undefined;
    }, string>;
    receipt_id?: undefined;
    note?: undefined;
} | {
    schema_ok: boolean;
    violations: string[];
    receipt_id: string;
    note: string;
};
