# Governance Meta-Audit — LOCKED v1

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Authority:** ASF order — Governance must be audited by machine, not self-grade  
**PICK:** `Q-GOV-META-AUDIT-v1` **YES**  
**Extends:** `SOURCEA_GOVERNANCE_CENTER_SELF_GOVERN_LOCKED_v1.md` · `SOURCEA_THREE_ZONE_HUB_SPINE_LOCKED_v1.md` · INCIDENT-033 · INCIDENT-034  
**Machine:** `scripts/governance_meta_audit_v1.py` · `~/.sina/governance-meta-audit-receipt-v1.json`

---

## Law (one sentence)

**Governance Specialist cannot claim fixed, PASS, or “not present locally” until governance meta-audit PASS — disk grep beats chat.**

---

## What meta-audit checks (daily spine)

| # | Check | FAIL class |
|---|--------|------------|
| 1 | `agent_truth_bundle_v1.py` — factory-now line present | SSOT |
| 2 | `validate-brain-not-command-data-ssot-v1.sh` | QUEUE |
| 3 | `validate-super-fast-hub-v1.sh` | H1 |
| 4 | `validate-museum-stale-copy-v1.sh` — no daily-steer poison in museum founder hero | MUSEUM-033 |
| 5 | `validate-prompt-feed-no-autosend-copy-v1.sh` | INCIDENT-028 |
| 6 | `agent_memory_mirror_v1.py --validate` | MIRROR |
| 7 | Judge temporal — 0 ACTIVE_STALE / REVERT on Gov · Worker · Brain chats | CHAT |

---

## Governance Center veto

`governance_center_run_v1.py` **step 0** = meta-audit.  
If meta-audit **FAIL** → `governance-center-receipt-v1.json` **`ok: false`** even when self-heal steps pass.

---

## Forbidden (Governance Specialist)

- “Fixed” / “not present locally” without `governance-meta-audit-receipt-v1.json` **`ok: true`** attached
- PASS cart or E2E while museum founder-hero still steers Prompt feed / auto-send
- Daily investigation of `/legacy/` or full `command-data.json` (Zone C — `SOURCEA_THREE_ZONE_HUB_SPINE_LOCKED_v1.md`)

---

## Cadence

| Tier | When |
|------|------|
| **fast** | Every Governance session start · Governance Center run · **15m** schedule |
| **full** | Daily + Judge batch on `e54ddfa8,fd67502f,58148ac9` |

---

## Verify

```bash
python3 scripts/governance_meta_audit_v1.py --tier fast --json
bash scripts/validate-governance-meta-audit-v1.sh
```

**END**
