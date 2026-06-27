# SourceA MCP Verify — install (STAB-052 · STAB-053)

**Saved at:** 2026-06-24T01:40:00Z

## From monorepo (dev)

```bash
cd ~/Desktop/SourceA/packages/mcp-verify   # when package present
npm install && npm link
```

## Cursor settings

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "sourcea-verify": {
      "command": "npx",
      "args": ["-y", "@sourcea/mcp-verify"],
      "env": {
        "SOURCEA_HOOK_URL": "https://hooks.sourcea.app/v1/relay"
      }
    }
  }
}
```

## Tools exposed

- `verify_claim` — run ORD truth gate on pasted agent output
- `seal_proof` — trigger Proof Pack seal path

## Public doc page

https://sourcea.app/sourcea/forge/cursor-bridge

## npm publish (STAB-052)

When ready: `npm publish --access public` from `packages/mcp-verify` with `@sourcea/mcp-verify` scope.

Until npm live: install from GitHub `sourcea-io/sourcea-boot` sibling repo or clone SourceA `packages/mcp-verify`.
