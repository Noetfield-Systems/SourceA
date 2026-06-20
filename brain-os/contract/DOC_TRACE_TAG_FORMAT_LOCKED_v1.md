# Doc trace tag format (LOCKED v1.1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**trace_tag:** `AUTO-TRACE-DOC-FORMAT-v1.1`  
**agent:** `Auto` (Cursor executor)  
**Locked:** 2026-06-07 · **Amended:** 2026-06-08 (ASF) — tags under agent name, not SINA

---

## Format

```text
AUTO-TRACE-{DOMAIN}-{ARTIFACT}-v{MAJOR}.{MINOR}
```

| Part | Rule | Example |
|------|------|---------|
| Prefix | **Always `AUTO-TRACE`** — Cursor executor agent | `AUTO-TRACE-...` |
| `DOMAIN` | Uppercase lane | `WORKER`, `RAIL`, `RUNTIME`, `RULE` |
| `ARTIFACT` | Short slug | `PACK-FORMAT`, `W1-QUEUE`, `W1-REGISTRY` |
| `vMAJOR.MINOR` | Bumps on shape change | `v1.2` |

**Forbidden:** `SINA-TRACE-*` on agent-saved docs (founder/SINA product tags stay separate).

**Required on every agent-saved doc:**

1. **Markdown / law:** `trace_tag:` + optional `agent: Auto` in first 6 lines
2. **JSON:** `"trace_tag"` + `"agent": "Auto"` at top level
3. **Generator output:** writes both into REGISTRY + paste queue header

## Grep

```bash
rg 'AUTO-TRACE-WORKER' /Users/sinakazemnezhad/Desktop/SourceA
rg 'AUTO-TRACE' ~/.sina
```

## Line test

No new agent-saved doc without `AUTO-TRACE-*` tag — reject regen.
