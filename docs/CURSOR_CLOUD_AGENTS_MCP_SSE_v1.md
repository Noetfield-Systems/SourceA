# Cursor Cloud Agents — MCP SSE integration

**Saved:** 2026-06-19T16:00:00Z · **Phase:** P2_sse

## Team Integrations (Cursor Settings)

| Server | URL | Auth |
|--------|-----|------|
| sourcea-verify | `https://sourcea-mcp-verify.vercel.app/mcp` | `Bearer ${SOURCEA_MCP_TOKEN}` |
| virlux-verify | `https://virlux-api.vercel.app/mcp` | `Bearer ${VIRLUX_MCP_TOKEN}` |

## Per-agent scope

- **Review agent:** `sourcea-verify` only
- **Verify agent:** `virlux-verify` + Playwright MCP
- **Planning agent:** Linear MCP only

## Local stdio fallback

See `mcp.fragment.json` in each `cursor-plugin/` folder.

## Law

- Read-only verify — never writes `~/.sina`
- Mac = control plane · SSE = cloud execution plane
