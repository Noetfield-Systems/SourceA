# Batch 4 — critic packet

**Saved:** 2026-06-20T17:15:13Z  
**Theme:** `SINA_COMMAND_*` legacy hub docs + remaining incident reports at root  
**Files:** 25 (8 command + 17 incident/index)  
**Expected root count after:** 252 − 25 = **227**  
**Machine receipt:** `data/cleanup-track-progress-v1.json`

## Why this batch

- `ASF_RETIRE_SINA_COMMAND_FOREVER_LOCKED_v1.md` (batch 3 → `brain-os/law/`) retires Sina Command as live hub; root `SINA_COMMAND_*` files are legacy hub surface docs, not tier-0 law.
- Remaining `SINA_*_INCIDENT_*` at root are pointers/reports; canonical filing is `brain-os/incidents/` (batch 1–2 pattern).

## Destinations

| Class | Count | Target |
|-------|-------|--------|
| Legacy Sina Command hub | 7 | `archive/legacy/sina-command/` |
| Command stub | 1 | `archive/root-stubs/` |
| Incident reports + indexes | 13 | `brain-os/incidents/` |
| Incident stubs | 4 | `archive/root-stubs/` |

## Pre-flight (2026-06-20)

| Check | Result |
|-------|--------|
| All 25 source files logged | **PASS** (25/25) |
| Secret scan | **PASS** (`scan-secrets-v1.sh` — no key hits) |
| Dest filename collision | **FIXED** — INCIDENT-023 root file is pointer stub; row changed to `archive/root-stubs/` |
| Dupes vs `brain-os/incidents/` | **1 reconciled** — canonical body already under `brain-os/incidents/` |
| Manifest status | **FROZEN** — execute blocked until ASF APPROVED |

## Risk notes

1. **Hub READ_CHAIN** — `scripts/hub_essentials_index.py` lists 3 root `SINA_COMMAND_*` paths; update after move (listed in manifest post-step).
2. **Maze mandatory reads** — `agent_three_pipelines_lib_v1.py` references `SINA_COMMAND_EDIT_LOCK`; update to `archive/legacy/sina-command/…` post-move.
3. **Taxonomy / lineage** — Batch 4 assumes **Option A + Path 2** (`infra/cleanup/taxonomy-asf-pick-v1.md`). Other picks may change Batch 5, not Batch 4 rows.

## Pre-flight commands (operator)

```bash
cd ~/Desktop/SourceA
bash infra/cleanup/scan-secrets-v1.sh
# After manifest APPROVED:
bash infra/cleanup/execute-batch-v1.sh --batch 4 --dry-run
bash infra/cleanup/execute-batch-v1.sh --batch 4
python3 scripts/governance_paths_v1.py
bash scripts/validate-law-purity-ssot-v1.sh
bash infra/cleanup/generate-inventory-v1.sh
```

## Approval

- [x] Agent pre-flight complete (sources, scan, dupe reconcile)
- [ ] ASF reviewed manifest rows in `cleanup-manifest.md` § Batch 4
- [ ] ASF taxonomy + lineage pick (`taxonomy-asf-pick-v1.md`)
- [ ] Set manifest status **APPROVED** for batch 4
- [ ] **Operator** executes batch 4 (not agent)
