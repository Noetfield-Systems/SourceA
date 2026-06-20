---
name: verify-after-mcp
description: >-
  After any GitHub, Linear, or action MCP call, invoke sourcea-verify verify_run
  and emit_receipt_readonly. Use on PR workflows, issue sync, or when the user
  asks for proof, audit, or controlled agent runs.
---

# Verify after MCP action

**Chain pattern:** action MCP executes → `sourcea-verify` proves → founder reads verdict.

## When to run

| Trigger | Action |
|---------|--------|
| After GitHub MCP (PR, issue, comment) | Call `verify_run` with receipt id or inline receipt |
| After Linear MCP (issue create/update) | Same |
| User asks "prove it" / "receipt" / "audit" | Run full verify chain |
| Before claiming ship complete | `emit_receipt_readonly` on draft receipt |

## Tools (sourcea-verify MCP)

1. **`verify_run`** — Returns `PASS` | `FAIL` | `MOCK_ONLY` + receipt JSON. Read-only.
2. **`emit_receipt_readonly`** — Schema validate only. **Never writes local disk.**
3. **`factory_status`** — Optional glance at queue head (read-only).
4. **`form_pick_parse`** — Parse structured founder PICK blocks when present.

## Workflow

```
1. Action MCP completes (e.g. github.create_pull_request)
2. Build witness object: { tool, args_summary, at }
3. verify_run({ receipt: witness }) OR verify_run({ receipt_id })
4. If verdict MOCK_ONLY — say so honestly; do not claim cloud federation
5. Reply with verdict + one-line proof summary
```

## Honest labels

- **MOCK_ONLY** — Local stdio tier; cloud receipt bucket not federated yet.
- **PASS** — Receipt schema valid and witness matches policy.
- **FAIL** — Schema or policy violation; fix before ship.

## Law

- Do not replace GitHub/Linear/browser MCP — prove what they did.
- No writes to `~/.sina` or founder secrets via MCP tools.
- Chat is not SSOT — receipt JSON is.
