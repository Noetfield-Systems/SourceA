# INCIDENT-026 — Brain chat validator recursion (report pointer)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Status:** remediated · **Subject:** SUBJ-AGENT  
**Canonical body:** `brain-os/incidents/SINA_BRAIN_CHAT_VALIDATOR_RECURSION_INCIDENT_026_LOCKED_v1.md`  
**Law:** `brain-os/enforcement/BRAIN_NO_FULL_E2E_SHELL_LOCKED_v1.md` · `BRAIN_UNIFIED_RULES_LOCKED_v1.md`

## One-screen summary

Brain agent blocked chat 15–25+ minutes by chaining validators and re-running live-prompt E2E after receipts existed. **Agent conduct failure** — not system failure.

## One-line law

Brain: implement → receipt → reply **<30s** → STOP. No validator chains. No `Await` **>90s**. Closeout reads receipts only.

## Verify

```bash
python3 scripts/brain_session_guard_v1.py --write --json
bash scripts/validate-closeout-receipt-only-v1.sh
```
