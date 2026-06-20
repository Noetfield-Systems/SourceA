import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { RECEIPT_SCHEMA, receiptId, verdictFromReceipt } from "./schemas.js";
export function verifyRun(input) {
    if (input.receipt) {
        const parsed = RECEIPT_SCHEMA.safeParse(input.receipt);
        if (!parsed.success) {
            return {
                verdict: "FAIL",
                receipt: null,
                export_url: "",
                violations: parsed.error.flatten(),
            };
        }
        const receipt = parsed.data;
        return {
            verdict: verdictFromReceipt(receipt),
            receipt,
            export_url: `https://mcp.sourcea.app/export/${receiptId(receipt)}`,
            campus: input.campus ?? "sourcea",
        };
    }
    const id = input.receipt_id ?? "demo-receipt";
    return {
        verdict: "MOCK_ONLY",
        receipt: {
            schema: "sourcea-mcp-receipt-v1",
            receipt_id: id,
            verdict: "MOCK_ONLY",
            at: new Date().toISOString(),
            honest_label: "P2 cloud SSE — receipt bucket federation",
        },
        export_url: `https://sourcea-mcp-verify.vercel.app/mcp/export/${id}`,
        campus: input.campus ?? "sourcea",
    };
}
async function factoryStatusCloud(hubUrl, surface) {
    const base = hubUrl.replace(/\/$/, "");
    const urls = [`${base}/api/fbe/cloud-proxy/v1`, `${base}/api/agent-live-surfaces/v1`];
    for (const url of urls) {
        try {
            const res = await fetch(url, { signal: AbortSignal.timeout(4000) });
            if (!res.ok)
                continue;
            const raw = (await res.json());
            return {
                surface,
                factory_now_line: raw.factory_now_line ??
                    raw.cloud_practical_300_line ??
                    "cloud proxy ok — factory line pending sync",
                queue_sa: raw.queue_sa ?? "SINGLE_SA",
                as_of: raw.updated_at ?? new Date().toISOString(),
                transport: "cloud_sse_federation",
                source_url: url,
            };
        }
        catch {
            /* try next */
        }
    }
    return null;
}
export async function factoryStatus(input) {
    const surface = input.surface ?? "hub";
    const cloud = process.env.SOURCEA_MCP_CLOUD === "1" ||
        process.env.VERCEL === "1" ||
        Boolean(process.env.SOURCEA_HUB_URL);
    if (cloud && process.env.SOURCEA_HUB_URL) {
        const fed = await factoryStatusCloud(process.env.SOURCEA_HUB_URL, surface);
        if (fed)
            return fed;
    }
    const surfacesPath = join(homedir(), ".sina", "agent-live-surfaces-v1.json");
    try {
        const raw = JSON.parse(readFileSync(surfacesPath, "utf8"));
        return {
            surface,
            factory_now_line: raw.factory_now_line ?? "factory-now unavailable — run session gate on Mac control plane",
            queue_sa: raw.queue_sa ?? "unknown",
            as_of: raw.updated_at ?? new Date().toISOString(),
            transport: "read_only_local_stdio",
        };
    }
    catch {
        return {
            surface,
            factory_now_line: "0 sent · 0 active · 0 close — cloud federation pending",
            queue_sa: "SINGLE_SA",
            as_of: new Date().toISOString(),
            transport: cloud ? "cloud_sse_fallback" : "fallback_p1",
        };
    }
}
export function formPickParse(input) {
    const raw = input.raw_pick.trim();
    const pickMatch = raw.match(/\bPICK:\s*([A-D])\b/i) ?? raw.match(/\b([A-D])\b/);
    const subjectMatch = raw.match(/Subject:\s*(.+?)(?:\n|Question:|$)/is);
    const questionMatch = raw.match(/Question:\s*(.+?)(?:\n|Effect:|$)/is);
    const effectMatch = raw.match(/Effect:\s*(.+)$/is);
    return {
        subject: subjectMatch?.[1]?.trim() ?? "unspecified",
        pick: (pickMatch?.[1]?.toUpperCase() ?? "A"),
        effect: effectMatch?.[1]?.trim() ?? questionMatch?.[1]?.trim() ?? "see raw_pick",
        raw_length: raw.length,
    };
}
export function emitReceiptReadonly(input) {
    const parsed = RECEIPT_SCHEMA.safeParse(input.receipt);
    if (!parsed.success) {
        return { schema_ok: false, violations: parsed.error.flatten() };
    }
    const receipt = parsed.data;
    const violations = [];
    if (!receipt.receipt_id && !receipt.id)
        violations.push("missing receipt_id or id");
    if (!receipt.verdict && !receipt.status)
        violations.push("missing verdict or status");
    return {
        schema_ok: violations.length === 0,
        violations,
        receipt_id: receiptId(receipt),
        note: "read-only validate — does not write ~/.sina",
    };
}
