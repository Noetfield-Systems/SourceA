# SourceA Forge Governance — Cursor Plugin (Card 1)

**Version:** 1.0.0 · **Categories:** Agent Orchestration · Infrastructure

> **We don't replace your MCP — we prove what your MCP did.**

Receipt-native proof layer for MCP hosts. After GitHub, Linear, or any action MCP runs, `sourcea-verify` returns `PASS` / `FAIL` / `MOCK_ONLY` with structured receipt JSON — read-only, chain-friendly.

## What's included

| Component | Purpose |
|-----------|---------|
| **MCP `sourcea-verify`** | `verify_run` · `factory_status` · `form_pick_parse` · `emit_receipt_readonly` |
| **Skill: verify-after-mcp** | Post-action verify workflow |
| **Skill: governance-receipt-recovery** | Recover audit context from receipts |
| **Rule: receipt-native-governance** | Honest proof boundary + MOCK_ONLY disclosure |

## Enterprise bootstrap (Corporate Promax)

**Pack:** `docs/CURSOR_CORPORATE_BOOTSTRAP_PACK_LOCKED_v1.md` · **Ledger:** `data/cursor-bootstrap-ledger-v1.json`  
**Validate:** `bash scripts/validate-all-e2e-v1.sh`

## Install (local / dev)

From monorepo root:

```bash
bash scripts/publish_sourcea_forge_governance_card_v1.py --json
```

Or point Cursor at this folder — it detects `.cursor-plugin/plugin.json`.

### MCP (stdio — free tier)

Already wired in `.mcp.json`:

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

Monorepo local dev:

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

## Honest disclosure

| Tier | Verdict | Meaning |
|------|---------|---------|
| **P1 stdio** | `MOCK_ONLY` common | Local verify; cloud receipt bucket federation is P2 |
| **P2 cloud SSE** | `PASS` / `FAIL` | Federated receipts at `mcp.sourcea.app` (when live) |

Do not claim enterprise-safe audit until cloud bucket + registry publish are live.

## Registry

- npm: `@sourcea/mcp-verify`
- Official MCP Registry: `io.github.sinakazemnezhad/sourcea-verify`
- Metadata: `packages/mcp-sourcea-verify/registry/server-v1.json`

## Chain position

```text
GitHub MCP / Linear MCP / Browser MCP  →  action
sourcea-verify MCP                     →  proof (read-only)
Founder / CI                           →  verdict
```

## License

MIT · Noetfield Systems / SourceA Forge
