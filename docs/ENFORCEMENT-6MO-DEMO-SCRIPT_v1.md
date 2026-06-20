# ENFORCEMENT-6MO — demo script (short)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Law:** `brain-os/law/enforcement/ENFORCEMENT_6MO_INVESTOR_WIN_LOCKED_v1.md`  
**Full notes:** `investor/ENFORCEMENT_DEMO_5MIN.md`  
**Run:** `bash scripts/demo-enforcement-5min-v1.sh`  
**CI:** `bash scripts/validate-demo-enforcement-v1.sh`

---

## One-liner

> We make AI execution impossible to bypass governance.

---

## Copilot beats (P-001)

| Time | Beat | Command |
|------|------|---------|
| 0:30 | **BLOCK** | `sourcea_execute_v1.py --demo-enforcement --case block` |
| 1:30 | **ALLOW** | `--case allow` → receipt + spine |
| 2:30 | **TAMPER** | `validate-demo-enforcement-v1.sh --tamper-test` |
| 4:00 | **KILL** | `~/.sina/auto-run-disabled-v1.flag` (optional) |
| 5:00 | **ASK** | NF/TF pilot · LOI · deposit |

---

## Files

| Path | Role |
|------|------|
| `brain-os/demo/governance_demo_policy_v1.json` | Rule P-001 |
| `scripts/commit_intent_v1.py --demo-enforcement` | Commit gate |
| `~/.sina/demo-enforcement/receipts/latest-demo-receipt.json` | Tamper target |

**Full artifact index:** `brain-os/demo/ENFORCEMENT_ARTIFACTS_INDEX_v1.md`
