# Batch 5b — critic packet

**Saved:** 2026-06-20T18:00:00Z  
**Theme:** `WORLD_*` root stub retirement (canonical at `brain-os/wtm/`)  
**Files:** 10  
**Expected root after:** 158 − 10 = **148**  
**Machine audit:** `infra/cleanup/batch-5b-grep-audit.json`  
**Receipt:** `data/cleanup-track-progress-v1.json`

## Rationale

Batch 5b removes root **MOVED** pointer stubs for World Target Model docs. Full SSOT bodies already live under **`brain-os/wtm/`** (same filenames). This is **not** a content migration — execute uses action **`archive`** → `archive/root-stubs/`.

Using **`move`** → `brain-os/wtm/` would skip all 10 rows (`execute-batch-v1.sh` exits when dest exists).

## Pre-flight (2026-06-20)

| Check | Result |
|-------|--------|
| Source stubs logged | **PASS** (10/10) |
| Canonical at `brain-os/wtm/` | **PASS** (10/10) |
| Dest collision at `archive/root-stubs/` | **PASS** (0 existing WORLD_* there) |
| Pointer patch before archive | **PASS** (6 scripts + governance_paths_v1) |
| Secret scan | Run before execute |
| Wildcards in manifest | **PASS** (exact filenames only) |

## HIGH-risk files (grep + patched)

| File | Consumers (sample) | Patch |
|------|-------------------|-------|
| `WORLD_TARGET_MODEL_MAP_LOCKED_v5.md` | agent_system_unified, agent_rules_in_charge | `brain-os/wtm/...` path |
| `WORLD_TARGET_MODEL_AUTHORITY_LAW_LOCKED_v1.md` | important_docs_index | `brain-os/wtm/...` prefix |
| `WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v2.md` | important_docs_index, roadmaps_goals | `brain-os/wtm/...` |
| `WORLD_TARGET_MODEL_STEP_ID_MIGRATION_LOCKED_v1.md` | important_docs_index | `brain-os/wtm/...` |
| `WORLD_TARGET_MODEL_UI_INCIDENT_REPORT_LOCKED_v1.md` | ecosystem_incidents_index | `brain-os/wtm/...` |
| `WORLD_TARGET_MODEL_PHASE_NAMING_INCIDENT_REPORT_LOCKED_v1.md` | ecosystem_incidents_index | `brain-os/wtm/...` |

## Risk notes

1. **Hub JSON** may embed root paths — refreshes on next hub rebuild; non-blocking.
2. **meta_reasoning_policy** display strings still bare filenames — hub labels only; no file resolve.
3. Stub text references `archive/superseded/pointers/` — informational; canonical remains `brain-os/wtm/`.

## NOT in 5b (148 files remain after)

`FOUNDER_*` (7) · `SINA_*` (48) · `OTHER` (77) · `CURSOR_*` (5) · etc. → sub-batches **5c–5f**

## Approval

- [x] Agent pre-flight + pointer patch complete
- [x] ASF implement-plan approval (Batch 5b)
- [x] Operator executes batch 5b — done 2026-06-20 (python executor · 10 archived)

## Execute

```bash
cd ~/Desktop/SourceA
bash infra/cleanup/scan-secrets-v1.sh
bash infra/cleanup/execute-batch-v1.sh --batch 5b --dry-run
bash infra/cleanup/execute-batch-v1.sh --batch 5b
bash infra/cleanup/generate-inventory-v1.sh
python3 scripts/cleanup_track_sync_v1.py --json
python3 scripts/world_model_plan_check_v1.py --json
bash scripts/validate-map-pointer-docs-v1.sh
bash scripts/validate-law-purity-ssot-v1.sh
```
