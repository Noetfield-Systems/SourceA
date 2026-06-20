# ASF governance PICK batch — Q-GOV-FAST-WIRE + Q-CHANGE-QUORUM (LOCKED v1)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Authority:** ASF FIVE-STEP PICK (chat paste)  
**Receipt:** `founder_pick_apply_v1.py` · `~/.sina/founder-picks-applied-v1.jsonl`

---

## PICKs locked

| ID | Pick | Effect |
|----|------|--------|
| **Q-GOV-FAST-WIRE-v1** | **A** | SHIP full fast governance pack — `wf-governance-fast-15m` daily · Judge + Thread n8n weekly · H1 alarm strip only |
| **Q-CHANGE-QUORUM-v1** | **A** | SHIP Change Quorum weekly — SSOT fingerprint + owner class + ≤20 delta rows · `judge_center_audit_v1.py --ssot-delta` |

---

## Machine after apply

| Signal | Value |
|--------|-------|
| `open_questions_count` | **0** |
| `awaiting_founder_picks` | **false** |
| Applied picks total | **52** |

---

## Maintainer 2 SHIP (now unblocked)

1. H2 `/machines/` route + pending registry UI
2. n8n: `wf-governance-fast-15m` · `wf-judge-audit-batch` · `wf-thread-scout-weekly`
3. `judge_center_audit_v1.py --ssot-delta` + `validate-change-quorum-v1.sh`
4. Thread Room panel on **H2 second hop** (not H1 daily)
5. H1 alarm strip fields: `change_quorum_summary` one line

---

*End ASF_FORM_GOV_PICK_BATCH_2026-06-14_LOCKED_v1*
