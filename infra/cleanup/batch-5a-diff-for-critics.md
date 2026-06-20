# Batch 5a — critic packet

**Saved:** 2026-06-20T17:25:00Z  
**Theme:** `SOURCEA_*` product/commercial/governance law → `brain-os/law/`  
**Files:** 69  
**Expected root after:** 227 − 69 = **158**  
**Machine audit:** `infra/cleanup/batch-5a-grep-audit.json`  
**Receipt:** `data/cleanup-track-progress-v1.json`

## Rationale

Batch 5a relocates remaining root `SOURCEA_*` LOCKED docs under **Option A** taxonomy (`brain-os/law/`). **Path 2** lineage — SINA OS stays live; no platform rename.

Pointer work **completed before execute** (Batch 3 lesson):

- `scripts/governance_paths_v1.py` — `law_doc()` + named constants
- ~20 Python/shell consumers patched to import canonical paths
- `scripts/hub_essentials_index.py` — 16 READ_CHAIN rows → `brain-os/law/SOURCEA_*`

## Pre-flight (2026-06-20)

| Check | Result |
|-------|--------|
| Source files on disk | **PASS** (69/69) |
| Dest filename collision at `brain-os/law/` | **PASS** (0) |
| Script `ROOT / "SOURCEA_*"` hardcodes | **PASS** (0 remaining in scripts/) |
| Secret scan | Run before execute |
| Wildcards in manifest | **PASS** (exact filenames only) |

## HIGH-risk files (grep + patched)

| File | Consumers (sample) | Patch |
|------|-------------------|-------|
| `SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md` | form scripts, validators | `LIVE_FOUNDER_FORM` |
| `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md` | brain wire, validators | `SUPER_FAST_HUB` |
| `SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md` | brain wire | `AGENTIC_LAYER_STACK` |
| `SOURCEA_FOUNDER_MESSAGE_NORMALIZATION_LOCKED_v1.md` | form, voice sources | `FOUNDER_MESSAGE_NORM` |
| `SOURCEA_INCIDENT_FIX_OWNERSHIP_GOVERNANCE_HARDENING_LOCKED_v1.md` | stairlift, cascade | `INCIDENT_FIX_OWNERSHIP` |

## Risk notes

1. **Hub JSON** (`agent-control-panel/command-data*.json`) may still embed root paths — hub rebuild on next refresh; not blocking file move.
2. **`.cursor/rules`** may cite root `SOURCEA_*` — update on next rule touch or bulk replace if drift reported.
3. **Dupes:** if any dest exists post-move, root copy → `archive/root-stubs/` (none expected today).

## NOT in 5a (158 files remain)

`SINA_*` (48) · `OTHER` (77) · `WORLD_*` (10) · `FOUNDER_*` (7) · `CURSOR_*` (5) · `ASF_*` (3) · prompts (3) · `keep-root` (2) · `ENFORCEMENT-*` (2) · `INCIDENT_*` (1)

→ Sub-batches **5b–5f** per `infra/cleanup/batch-5-triage-draft.md`

## Approval

- [x] Agent pre-flight + pointer patch complete
- [x] ASF implement-plan approval (Batch 5a)
- [ ] Operator executes batch 5a (after pointer commit in same batch)

## Execute

```bash
cd ~/Desktop/SourceA
bash infra/cleanup/scan-secrets-v1.sh
bash infra/cleanup/execute-batch-v1.sh --batch 5a --dry-run
bash infra/cleanup/execute-batch-v1.sh --batch 5a
bash infra/cleanup/generate-inventory-v1.sh
python3 scripts/governance_paths_v1.py
bash scripts/validate-law-purity-ssot-v1.sh
```
