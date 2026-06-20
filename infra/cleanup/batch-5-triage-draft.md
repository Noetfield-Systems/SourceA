# Batch 5 — remainder triage (draft)

**Saved:** 2026-06-20T17:15:13Z  
**Status:** DRAFT — 5a executed · root **158** files  
**Inventory:** 158 root files (post–Batch 5a)

---

## Bucket summary (post–Batch 4 projection)

| Bucket | Count | Proposed default dest | Notes |
|--------|------:|----------------------|-------|
| `SOURCEA_*` | 69 | `brain-os/law/` or `docs/locked/` | Product/commercial LOCKED |
| `SINA_*` (non-command) | ~40 | `brain-os/law/` or `archive/legacy/sina/` | Depends on lineage Path 1 vs 2 |
| `OTHER` | 77 | row-by-row | Mixed prompts, indexes, stubs |
| `WORLD_*` | 10 | `brain-os/wtm/` or `docs/locked/` | WTM / world model |
| `FOUNDER_*` | 7 | `brain-os/law/enforcement/` | Founder-facing ops law |
| `CURSOR_*` | 5 | `docs/archive/` or `brain-os/law/` | Tooling notices |
| `ASF_*` | 3 | `brain-os/system/` | Program trackers |
| `ENFORCEMENT-*` | 2 | `brain-os/law/` | 6MO plans — lineage doc already moved |
| `prompt-txt` | 3 | `archive/root-sprawl/` or delete-after-grep | Chat extract prompts |
| `keep-root` | 2 | **keep-root** | `START_HERE.md`, `ACTIVE_NOW.md` |
| `INCIDENT_*` | 1 | `brain-os/incidents/` | Stragglers after batch 4 |

---

## Suggested sub-batches (after taxonomy pick)

| Sub-batch | Theme | ~files |
|-----------|-------|-------:|
| **5a** | `SOURCEA_*` product/commercial LOCKED | 69 |
| **5b** | `WORLD_*` + WTM pointers | 10 |
| **5c** | `FOUNDER_*` + founder ops | 7 |
| **5d** | `CURSOR_*` + tooling notices | 5 |
| **5e** | Remaining `SINA_*` (lineage-dependent) | ~40 |
| **5f** | `OTHER` triage — one row per file | 77 |

---

## Rules (unchanged)

1. **No wildcards** in manifest rows — exact filename per row.
2. **grep consumers** before each sub-batch (same as Batch 3 lesson).
3. **Dupes:** if dest exists, root copy → `archive/root-stubs/` (see Batch 4 INCIDENT-023 fix).
4. **Operator executes** — agent writes manifest rows only.

---

## Generate next inventory

```bash
cd ~/Desktop/SourceA
bash infra/cleanup/generate-inventory-v1.sh
```

After Batch 4 execute, re-run bucket script and replace counts in this doc.
