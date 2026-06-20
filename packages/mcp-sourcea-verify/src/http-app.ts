import { randomUUID } from "node:crypto";
import express, { type Request, type Response } from "express";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { isInitializeRequest } from "@modelcontextprotocol/sdk/types.js";
import { createSourceaMcpServer } from "./create-server.js";

const transports: Record<string, StreamableHTTPServerTransport> = {};

function authOk(req: Request): boolean {
  const keys = (process.env.SOURCEA_MCP_API_KEYS ?? process.env.SOURCEA_MCP_TOKEN ?? "")
    .split(",")
    .map((k) => k.trim())
    .filter(Boolean);
  if (keys.length === 0) return true;
  const header = req.headers.authorization ?? "";
  const token = header.startsWith("Bearer ") ? header.slice(7) : "";
  return keys.includes(token);
}

function requireAuth(req: Request, res: Response): boolean {
  if (authOk(req)) return true;
  res.status(401).json({ ok: false, error: "unauthorized" });
  return false;
}

const app = express();
app.use(express.json({ limit: "1mb" }));

app.get("/health", (_req, res) => {
  res.json({
    ok: true,
    service: "sourcea-mcp-verify",
    transport: "streamable-http-sse",
    phase: "P2_sse",
  });
});

app.get("/mcp/health", (_req, res) => {
  res.json({ ok: true, service: "sourcea-mcp-verify", path: "/mcp" });
});

const mcpPost = async (req: Request, res: Response) => {
  if (!requireAuth(req, res)) return;
  const sessionId = req.headers["mcp-session-id"] as string | undefined;
  try {
    let transport: StreamableHTTPServerTransport;
    if (sessionId && transports[sessionId]) {
      transport = transports[sessionId];
    } else if (!sessionId && isInitializeRequest(req.body)) {
      transport = new StreamableHTTPServerTransport({
        sessionIdGenerator: () => randomUUID(),
        onsessioninitialized: (sid) => {
          transports[sid] = transport;
        },
      });
      transport.onclose = () => {
        const sid = transport.sessionId;
        if (sid && transports[sid]) delete transports[sid];
      };
      const server = createSourceaMcpServer();
      await server.connect(transport);
      await transport.handleRequest(req, res, req.body);
      return;
    } else {
      res.status(400).json({
        jsonrpc: "2.0",
        error: { code: -32000, message: "Bad Request: No valid session ID provided" },
        id: null,
      });
      return;
    }
    await transport.handleRequest(req, res, req.body);
  } catch (err) {
    console.error("sourcea-mcp error:", err);
    if (!res.headersSent) res.status(500).json({ ok: false, error: "internal_error" });
  }
};

const mcpGet = async (req: Request, res: Response) => {
  if (!requireAuth(req, res)) return;
  const sessionId = req.headers["mcp-session-id"] as string | undefined;
  if (!sessionId || !transports[sessionId]) {
    res.status(400).send("Invalid or missing session ID");
    return;
  }
  await transports[sessionId].handleRequest(req, res);
};

const mcpDelete = async (req: Request, res: Response) => {
  if (!requireAuth(req, res)) return;
  const sessionId = req.headers["mcp-session-id"] as string | undefined;
  if (!sessionId || !transports[sessionId]) {
    res.status(400).send("Invalid or missing session ID");
    return;
  }
  await transports[sessionId].handleRequest(req, res);
};

app.post("/mcp", mcpPost);
app.get("/mcp", mcpGet);
app.delete("/mcp", mcpDelete);

export default app;
