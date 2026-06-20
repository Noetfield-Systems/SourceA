
**Saved:** 2026-06-08T18:56:52Z · **Retrofit:** doc-datetime-law batch retrofit
[AUTO_AGENT_REF · Auto · AUTO-TRACE-DOC-FORMAT-v1.1]

**trace_tag:** `AUTO-TRACE-DOC-FORMAT-v1.1`
**agent:** `Auto`

| Field | Value |
|-------|-------|
| **trace_tag** | `AUTO-TRACE-DOC-FORMAT-v1.1` |
| **agent** | `Auto` |
| **repo_chat** | `SourceA` |
| **workspace** | `~/Desktop/SourceA` |
| **canonical** | `false` |
| **written** | `2026-06-08` |

# Auto doc tag standard — Cursor executor (SourceA)

**Canonical law:** `brain-os/contract/DOC_TRACE_TAG_FORMAT_LOCKED_v1.md`

## Law

Every doc **Auto** saves must carry **`AUTO-TRACE-*`** under agent name **`Auto`** — never `SINA-TRACE-*` or generic `EXEC-REF-*`.

## Format

```text
AUTO-TRACE-{DOMAIN}-{ARTIFACT}-v{MAJOR}.{MINOR}
```

## Markdown header (required)

```markdown
**trace_tag:** `AUTO-TRACE-WORKER-EXAMPLE-v1.0`
**agent:** `Auto`
```

## Scripts

```bash
# TRACE: AUTO-TRACE-WORKER-EXAMPLE-v1.0 · agent Auto · scripts/foo.sh
```

## Helper

```bash
python3 scripts/executor_doc_tag_v1.py --domain WORKER --artifact BATCH-GATE-10 --json
python3 scripts/executor_doc_tag_v1.py --domain RUNTIME --artifact UI-WIRING --script-comment scripts/foo.sh
```

## Search

```bash
rg 'AUTO-TRACE' ~/Desktop/SourceA/archive/attachments
rg 'agent Auto' ~/Desktop/SourceA/scripts
```
