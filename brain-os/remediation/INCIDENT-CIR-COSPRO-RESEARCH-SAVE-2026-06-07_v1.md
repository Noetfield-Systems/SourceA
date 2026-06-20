# INCIDENT — CIR-COSPRO-RESEARCH-SAVE-2026-06-07

**Status:** **FINALIZED** — remediated 2026-06-09 · governance closure `~/.sina/governance/CIR-COSPRO-FINALIZED-v1.yaml`  
**Severity:** high  
**Recorded:** 2026-06-09

---

## Summary

`cursor_os_pro_research_lane_b_chat` (`execution_authority: false`) wrote **product SSOT / agent entry** files while doing voice research. Authorized vault YAML + `SourceA/RESEARCH` mirrors are valid; **cross-lane product docs are not**.

| Class | Detail |
|-------|--------|
| **Type** | cross_lane_unauthorized_edit + registry_duplication + worker_misattribution |
| **Agent** | `cursor_os_pro_research_lane_b_chat` |
| **execution_authority** | `false` |
| **Disk evidence** | Unauthorized paths mtime **2026-06-09 05:26** (all three) |

---

## Unauthorized paths (FORBIDDEN for research lane B)

| Path | Role |
|------|------|
| `~/Desktop/Cursor OS Pro/AGENTS.md` | Product agent entry |
| `~/Desktop/Cursor OS Pro/docs/SINGLE-SOURCE-OF-TRUTH.md` | Product blueprint SSOT |
| `~/Desktop/Cursor OS Pro/docs/VOICE_AGENT_ROADMAP_LOCKED_v1.md` | Product voice roadmap (LOCKED) |

**Law violated:** Research Chat B must stay in `docs/research/` vault + `research_save_enforcer.py` mirror — not promote findings into product SSOT.

---

## Authorized paths (KEEP — verify PASS)

| Path | Mirror |
|------|--------|
| `~/Desktop/Cursor OS Pro/docs/research/voice_composition_market_brain_v1.yaml` | `RESEARCH/.../RESEARCH-ACQUISITOR-REF-2026-06-07-CURSOR-OS-PRO-MARKET-BRAIN/` ✓ |
| `~/Desktop/Cursor OS Pro/docs/research/voice_dev_peer_comparison_v1.yaml` | `RESEARCH/.../RESEARCH-ACQUISITOR-REF-2026-06-07-CURSOR-OS-PRO-VOICE-DEV/` ✓ |
| `~/Desktop/Cursor OS Pro/scripts/investor-data-200.json` | Lane research ingest (authorized) |

```bash
python3 RESEARCH/_GOVERNANCE/research_save_enforcer.py verify \
  --trace-id RESEARCH-ACQUISITOR-REF-2026-06-07-CURSOR-OS-PRO-MARKET-BRAIN
python3 RESEARCH/_GOVERNANCE/research_save_enforcer.py verify \
  --trace-id RESEARCH-ACQUISITOR-REF-2026-06-07-CURSOR-OS-PRO-VOICE-DEV
# Both PASS as of 2026-06-09
```

---

## Remediation batch (execute only after founder confirm)

| Step | Action | Risk |
|------|--------|------|
| R1 | **Quarantine review** — founder diff of three unauthorized paths vs last known good (SSOT header `2026-06-03`, roadmap `2026-06-04`) | Low |
| R2 | **Revert spillover** — strip research-lane content from AGENTS.md / SSOT / VOICE_AGENT_ROADMAP; keep one-line pointers to `docs/research/README.md` only | Medium — no git repo; manual |
| R3 | **Register agent** — add `cursor_os_pro_research_lane_b` to `RESEARCH/_GOVERNANCE/WORKERS_REGISTRY.yaml` (`execution_authority: false`) | Low |
| R4 | **Lane rule** — `.cursor/rules/cursor-os-pro-research-lane-b.mdc` forbids edits outside `docs/research/` + `scripts/investor-data-200.json` + generators | Low |
| R5 | **Closeout** — research round YAML must cite `worker_id: research_acquisitor`, not product worker; `enforcer_verify: PASS` | Low |

**Explicitly out of scope until separate order:** editing `*_LOCKED_v*.md` law files in SourceA brain-os.

---

## Founder confirm phrase

```text
ASF: confirm CIR-COSPRO remediation
```

---

## Root cause

Research lane B treated /voice findings as **product SSOT updates** instead of **vault-only artifacts** + RESEARCH mirror. `research_save_enforcer.py` validates mirrors but does **not** block cross-path writes to product docs.

---

## Finalization checklist (all DONE)

| Step | Status |
|------|--------|
| R1–R2 Revert unauthorized AGENTS/SSOT/roadmap | DONE |
| R3 Worker registry + lane rule | DONE |
| R4 Registry INDEX dedup (131→73 canonical) | DONE |
| R5 `LANE_REGISTER=1` gate on refresh script | DONE |
| P0 `SINA_CROSS_LANE_EDIT_FORBIDDEN` + `AGENT_VERBS` law | DONE |
| P0 `000-cross-lane-edit-forbidden.mdc` (SourceA + COS Pro) | DONE |
| P0 `cross_lane_edit_guard_v1.py` + `governance-events.jsonl` | DONE |
| `validate-cross-lane-edit-v1.sh` PASS | DONE |
| MISS-007 + MISS-008 CLOSED | DONE |
| Compendium incident **010** | DONE |
| Closure receipt logged | DONE |
