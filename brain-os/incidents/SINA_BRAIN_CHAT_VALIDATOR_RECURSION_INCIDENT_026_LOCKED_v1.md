# INCIDENT-026 — Brain chat validator recursion & blocking (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-10  
**sequence_id:** SA-2026-06-10-INCIDENT-026  
**Subject:** SUBJ-AGENT · Brain conduct  
**Classification:** **P0** — Brain chat blocking  
**Canonical pointer:** `SINA_BRAIN_CHAT_VALIDATOR_RECURSION_INCIDENT_026_REPORT_LOCKED_v1.md`  
**Related:** INCIDENT-008 (stall/timing) · `BRAIN_NO_FULL_E2E_SHELL_LOCKED_v1.md` · `BRAIN_UNIFIED_RULES_LOCKED_v1.md` §1

---

## 1. Executive summary

A **Brain** Cursor session blocked founder chat **15–25+ minutes** by:

1. Chaining slow validators in one shell (`cross-plan && closeout && hub_refresh`)
2. Re-running the same **~138s** live-prompt E2E pipeline **6+ times** after receipts were already present
3. Using long `Await` on subprocess trees instead of replying **<30s** then STOP

**Root cause:** **Agent conduct failure** — not Cursor, hub, or brain_sync infrastructure.

**One-line law:**

> Brain chat: implement → write receipt → reply in **<30s** → STOP. **Never** chain validators, **never** `Await` on shells **>90s**, closeout **reads receipts only**.

---

## 2. Timeline (2026-06-10 UTC) — terminal evidence

| Time (UTC) | Event | Duration | Terminal |
|------------|-------|----------|----------|
| 13:15:44 | `live_prompt_lane_audit_v1.py` (includes E2E) | **152s** | 169944 |
| 13:18:10 | `validate-live-prompt-feed-e2e-v1.sh` standalone | **138s** | 799108 |
| 13:20:31 | `live-prompt-lane-score-v1.py --strict` (E2E + smokes) | **219s** | 161015 |
| 13:24:15 | `cross-plan && closeout && hub_refresh` chained | **25+ min** | 394084 |
| 13:32:47 | cross-plan JSON printed; closeout still re-running validators | — | 394084 |
| 13:44:08 | Receipt-based closeout fix (post-incident) | **15s** | 201236 |
| 13:49:22 | Original chained command finally exit 0 | **1507s** | 394084 |

---

## 3. What broke (conduct)

| Failure | Evidence |
|---------|----------|
| Chat silence >15 min | No founder reply while shells ran |
| Validator recursion | closeout called audit + lane-score + E2E + cross-plan again |
| Law violation | `BRAIN_UNIFIED_RULES` reply **<30s** · `BRAIN_NO_FULL_E2E` max **90s** shell |
| Blame deflection | Agent initially cited “system/infrastructure” — founder corrected: **personal conduct** |

---

## 4. Remediation (shipped)

| Item | Path |
|------|------|
| Receipt-only closeout | `scripts/live-prompt-worker-closeout-v1.py` |
| cross-plan `--fast` | `scripts/cross-plan-readiness-v1.py` |
| Brain guard extension | `scripts/brain_session_guard_v1.py` · `BRAIN_NO_FULL_E2E_SHELL_LOCKED_v1.md` v1.1 |
| Closeout grep gate | `scripts/validate-closeout-receipt-only-v1.sh` |
| Lane-score `--use-receipt` | `scripts/live-prompt-lane-score-v1.py` |
| Cursor rule | `.cursor/rules/000-brain-unified.mdc` |

---

## 5. Verify (Brain-safe only)

```bash
python3 scripts/brain_session_guard_v1.py --write --json
bash scripts/validate-closeout-receipt-only-v1.sh
python3 scripts/live-prompt-worker-closeout-v1.py --json
```

**Forbidden in Brain chat for verify:** full E2E, lane-score `--strict`, chained `&&` validators.

---

**Status:** REMEDIATED 2026-06-10 — INCIDENT-026 + Brain guard hardened
