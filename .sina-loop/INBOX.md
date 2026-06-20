<!-- WORKER_INBOX pending=1 source=sourcea_worker_professional_assignment queue=1/3 role=check sa=B0101 -->
# SourceA Worker — prompt ready (INBOX delivery)

**Do not expect clipboard paste.** Hub/autoloop wrote this file so Brain chat is not hijacked.

**Lane:** SourceA Worker only — if you are Brain, ignore this file.

**Updated:** 2026-06-20T17:38:36Z

---

# SourceA Worker — W-CLOUD-001 · CHECK

**Phase:** Cloud plans — Brain cloud 1000 + FORGE + FBE Railway · **Execution plane:** cloud_forge
**Assignment SSOT:** `data/sourcea-worker-professional-assignment-v1.json`
**Mac Law:** `~/Desktop/MacLaw/MAC_CONTROL_PLANE_LOCKED.md`

## Task

Mac control plane + cloud FORGE dry-run envelope (observe only)

**Mac Law:** Mac observes only — Hub :13020 · Mac Health · Routing · Mac Law cockpit. No factory motors · no Mac build when `mac_build_forbidden: true`. Cloud FORGE / Railway FBE executes.

## This turn (CHECK only)

1. `python3 scripts/prompt_feasibility_gate.py --role worker --strict`
2. `bash scripts/worker_turn_entry_v1.sh`
3. Execute role — **one turn · one item · STOP**

## Verify (executor runs — founder never Terminal)

- `bash scripts/validate-mac-control-plane-v1.sh`
- `python3 scripts/forge_cloud_env_load_v1.py --json`
- `python3 scripts/forge__run_v1.py --stack sourcea --dry-run --json`
- `bash scripts/validate-forge-mvp-baseline-v1.sh`

## Forbidden

- Mac factory body · local motor drain · building app code on Mac when cloud_forge
- Batch multiple queue items · skip WORKER_ROUND_REPORT

## Close

```yaml
status: WORKER_ROUND_REPORT
round_type: check | act | verify
sa_focus: B0101
assignment_id: W-CLOUD-001
phase_id: phase-cloud
execution_plane: cloud
validate:
  spine: PASS|FAIL
summary: one line Mac Law + cloud receipt path
```

Then: `python3 scripts/goal1_lane_broker.py worker-submit --stdin`


---

**Worker:** execute fully · `WORKER_ROUND_REPORT` · STOP  
**Founder:** stay in Brain or Hub — open Worker chat when ready; no Terminal
