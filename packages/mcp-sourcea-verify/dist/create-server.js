import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { emitReceiptReadonly, factoryStatus, formPickParse, verifyRun, } from "./tools.js";
export function createSourceaMcpServer() {
    const server = new McpServer({
        name: "sourcea-verify",
        version: "1.0.0",
    });
    server.tool("verify_run", "Return PASS/FAIL/MOCK_ONLY + receipt JSON (read-only). Does not write Mac disk.", {
        receipt_id: z.string().optional(),
        receipt: z.record(z.unknown()).optional(),
        campus: z.enum(["sourcea", "virlux", "noetfield", "trustfield"]).optional(),
    }, async (args) => ({
        content: [{ type: "text", text: JSON.stringify(verifyRun(args), null, 2) }],
    }));
    server.tool("factory_status", "Read-only factory_now_line + queue head. Cloud SSE uses hub federation when configured.", { surface: z.enum(["hub", "brain", "inbox"]).optional() }, async (args) => ({
        content: [{ type: "text", text: JSON.stringify(await factoryStatus(args), null, 2) }],
    }));
    server.tool("form_pick_parse", "Parse ASF FIVE-STEP PICK block into structured decision JSON.", { raw_pick: z.string() }, async (args) => ({
        content: [{ type: "text", text: JSON.stringify(formPickParse(args), null, 2) }],
    }));
    server.tool("emit_receipt_readonly", "Validate receipt schema only — never writes ~/.sina.", { receipt: z.record(z.unknown()) }, async (args) => ({
        content: [{ type: "text", text: JSON.stringify(emitReceiptReadonly(args), null, 2) }],
    }));
    return server;
}
