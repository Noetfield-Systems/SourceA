# SourceA MCP Verify — install (STAB-052 · STAB-053)

**Saved at:** 2026-06-24T01:40:00Z

## From monorepo (dev)

```bash
cd ~/Desktop/SourceA/packages/mcp-sourcea-verify
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

- `verify_run` — return PASS/FAIL/MOCK_ONLY + receipt JSON
- `factory_status` — read-only `factory_now_line` glance
- `form_pick_parse` — parse ASF `PICK:` into structured decision JSON
- `emit_receipt_readonly` — validate receipt schema without writing `~/.sina`

## Public doc page

https://sourcea.app/sourcea/forge/cursor-bridge

## npm publish (STAB-052)

When ready: `npm publish --access public` from `packages/mcp-sourcea-verify` with `@sourcea/mcp-verify` scope.

Until npm live: install from GitHub `kazemnezhadsina144-dot/sourcea-boot` sibling repo or clone SourceA `packages/mcp-sourcea-verify`.
