# Batch 4 — critic packet (draft)

**Theme:** `SINA_COMMAND_*` legacy hub docs + remaining incident reports at root  
**Files:** 25 (8 command + 17 incident/index)  
**Expected root count after:** 252 − 25 = **227**

## Why this batch

- `ASF_RETIRE_SINA_COMMAND_FOREVER_LOCKED_v1.md` (batch 3 → `brain-os/law/`) retires Sina Command as live hub; root `SINA_COMMAND_*` files are legacy hub surface docs, not tier-0 law.
- Remaining `SINA_*_INCIDENT_*` at root are pointers/reports; canonical filing is `brain-os/incidents/` (batch 1–2 pattern).

## Destinations

| Class | Count | Target |
|-------|-------|--------|
| Legacy Sina Command hub | 7 | `archive/legacy/sina-command/` |
| Command stub | 1 | `archive/root-stubs/` |
| Incident reports + indexes | 14 | `brain-os/incidents/` |
| Incident stubs | 3 | `archive/root-stubs/` |

## Risk notes

1. **Hub READ_CHAIN** — `scripts/hub_essentials_index.py` still lists 3 root `SINA_COMMAND_*` paths; update after move (listed in manifest post-step).
2. **Maze mandatory reads** — `agent_three_pipelines_lib_v1.py` references `SINA_COMMAND_EDIT_LOCK`; update to archive path post-move.
3. **Dupes** — verify no filename collision in `brain-os/incidents/` before execute (executor should SKIP or fail loudly).

## Pre-flight

```bash
cd ~/Desktop/sourceA
bash infra/cleanup/scan-secrets-v1.sh
bash infra/cleanup/execute-batch-v1.sh --batch 4 --dry-run
python3 scripts/governance_paths_v1.py  # paths module smoke (import only)
bash scripts/validate-law-purity-ssot-v1.sh
```

## Approval

- [ ] ASF reviewed manifest rows in `cleanup-manifest.md` § Batch 4
- [ ] Set manifest status APPROVED for batch 4
