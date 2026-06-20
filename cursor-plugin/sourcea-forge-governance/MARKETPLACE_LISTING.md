# SourceA Forge Governance — Cursor Marketplace Listing (Card 1)

**Saved:** 2026-06-19T06:35:30Z · **Version:** 1.0.0 · **Category:** Agent Orchestration

---

## Title

**SourceA Forge Governance — Proof Layer for AI Agents**

## Subtitle (one line)

Receipt-native verification after GitHub, Linear, and any action MCP — read-only PASS / FAIL / MOCK_ONLY.

## Short description (card blurb)

We don't replace your MCP — we prove what your MCP did. After agents execute via GitHub, Linear, browser, or deploy tools, `sourcea-verify` returns structured receipt JSON with an honest verdict. Chain-friendly, read-only, enterprise-audit ready.

## What's included

| Component | Count | Purpose |
|-----------|-------|---------|
| **MCP server** | 1 | `@sourcea/mcp-verify` — stdio via npx |
| **Skills** | 2 | verify-after-mcp · governance-receipt-recovery |
| **Rules** | 1 | receipt-native-governance |
| **Canvas** | 0 | Phase 1.5 — Founder Form Canvas separate listing |

## MCP tools

| Tool | Description |
|------|-------------|
| `verify_run` | PASS / FAIL / MOCK_ONLY + receipt JSON (read-only) |
| `factory_status` | factory_now_line + queue head (read-only) |
| `emit_receipt_readonly` | Schema validate receipt without disk write |
| `form_pick_parse` | Parse structured founder PICK blocks |

## Chain position

```text
GitHub MCP / Linear MCP / Vercel skill  →  execute
sourcea-verify MCP                      →  proof (read-only)
Founder / CI                            →  verdict
```

## Partner line (marketplace)

> We make every other plugin enterprise-safe — they act, we prove.

## Categories

- **Primary:** Agent Orchestration
- **Secondary:** Infrastructure

## Keywords

proof, receipt, mcp, verify, audit, agent-orchestration, governance, enterprise

## Honest tier disclosure (required in listing)

| Tier | Verdict | Meaning |
|------|---------|---------|
| **Free stdio** | Often `MOCK_ONLY` | Local schema verify; no cloud federation |
| **Cloud SSE** (P2) | `PASS` / `FAIL` | Federated receipts when token + SSE live |

Do not claim SOC2 / board export until TrustField Phase 2.

## Install snippet (auto from `.mcp.json`)

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

## Founder submit checklist

1. **npm** — `cd packages/mcp-sourcea-verify && npm login && npm publish --access public`
2. **MCP registry** — submit `packages/mcp-sourcea-verify/registry/server-v1.json` at registry.modelcontextprotocol.io
3. **Cursor marketplace** — upload bundle `data/publish-artifacts/sourcea-forge-governance-card1-*.tar.gz` or point at `cursor-plugin/sourcea-forge-governance/`
4. **Cloud SSE (optional P2)** — deploy `packages/mcp-sourcea-verify` to Vercel · set `SOURCEA_MCP_TOKEN` in Cursor Team Integrations

## Artifacts logged

| Artifact | Path |
|----------|------|
| Plugin bundle tar | `data/publish-artifacts/sourcea-forge-governance-card1-20260619T063529Z.tar.gz` |
| npm pack | `data/publish-artifacts/sourcea-mcp-verify-1.0.0.tgz` |
| Publish receipt | `receipts/card-1-sourcea-forge-governance-publish-v1.json` |

## License

MIT · Noetfield Systems / SourceA Forge
