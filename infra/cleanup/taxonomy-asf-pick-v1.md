# Cleanup — ASF taxonomy & lineage pick (tracking)

**Status:** LOCKED — ASF picks recorded · Batch 4 executed 2026-06-20  
**Saved:** 2026-06-20T17:20:00Z  
**Receipt:** `data/cleanup-track-progress-v1.json`

---

## Why this blocks Batch 4

Batch 4 moves legacy Sina Command hub docs and incident indexes. Critics flagged that `brain-os/system/`, `brain-os/incidents/`, and nested `law/entry/` / `law/enforcement/` entered the tree without a single ratified map. **Pick once → batches 4–5 follow the same buckets.**

---

## Taxonomy — pick ONE

### Option A — Minimal (recommended · matches disk after 3.5)

```text
brain-os/
  law/              # binding LOCKED governance
    entry/          # routers (START_HERE, GOVERNANCE_ENTRY, MANDATORY_READ)
    enforcement/    # agent conduct / verbs / loops
  system/           # indexes, registries, program trackers
  incidents/        # incident reports (from batches 1–2)
archive/
  legacy/sina-command/   # retired hub surface (Batch 4)
  root-stubs/            # root pointers only
```

**Cost:** Low — ratify what exists. Batch 4 destinations already match.

### Option B — Collapse to law + ssot only

```text
brain-os/law/ + brain-os/ssot/ only
```

**Cost:** High — another consolidation pass + mass pointer update. **Defer** unless ASF explicitly wants this refactor now.

| Pick | Action after ASF word |
|------|------------------------|
| **A** | Mark `[x] Taxonomy Option A` in manifest · proceed to Batch 4 approve |
| **B** | New batch **3.6** manifest before any Batch 4 execute |

---

## Lineage — pick ONE

### Path 1 — SourceA-only apex · archive SINA law

- Move remaining live `SINA_*` law to `archive/legacy/sina/` over time
- Apex SSOT becomes `SOURCEA_*` only
- **Not a cleanup batch** — implies `~/.sina` → `~/.sourcea` migration (~586 script touchpoints + live JSON state)

### Path 2 — SINA OS stays load-bearing (recommended · matches disk)

- Keep `SINA_OS_SSOT`, governance entry, authority index in live `brain-os/`
- Retire only **Sina Command surface** docs → `archive/legacy/sina-command/` (Batch 4)
- Keep `~/.sina` runtime path

| Pick | Batch 4 impact |
|------|----------------|
| **Path 1** | Freeze Batch 4 until platform-rename project is scoped |
| **Path 2** | Batch 4 rows valid as written |

---

## ASF checklist (copy to form or manifest)

- [x] Taxonomy: **Option A**
- [x] Lineage: **Path 2**
- [x] Batch 4 executed — 2026-06-20

**When all three checked:** run commands in `cleanup-manifest.md` § Execute batch 4.
