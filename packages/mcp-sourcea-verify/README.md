# @sourcea/mcp-verify

**P1 publish** — read-only governance receipt MCP for Cursor · Claude · Codex.

> We don't replace your MCP — we prove what your MCP did.

## Tools

| Tool | Purpose |
|------|---------|
| `verify_run` | PASS/FAIL/MOCK_ONLY + receipt JSON |
| `factory_status` | Read-only `factory_now_line` glance |
| `form_pick_parse` | ASF `PICK:` → structured decision |
| `emit_receipt_readonly` | Schema validate only — **never writes `~/.sina`** |

## Install (Cursor)

Add to `.cursor/mcp.json` or `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "sourcea-verify": {
      "command": "npx",
      "args": ["-y", "@sourcea/mcp-verify"]
    }
  }
}
```

Local dev from monorepo:

```json
{
  "mcpServers": {
    "sourcea-verify": {
      "command": "node",
      "args": ["packages/mcp-sourcea-verify/dist/index.js"]
    }
  }
}
```

## Registry

Official MCP Registry name: `io.github.sinakazemnezhad/sourcea-verify`  
Metadata: `registry/server-v1.json`

### Cloud SSE (P2)

```bash
npm run build && npm run start:http   # local :8787
# Vercel: bash ../../scripts/deploy_mcp_sse_vercel_v1.sh
```

URL: `https://sourcea-mcp-verify.vercel.app/mcp` · health: `/health`

## Law

- Read-only verify — no `~/.sina` writes via MCP
- Mac = control plane · cloud SSE in P2
- Disclosure ladder T1+ for public badges
