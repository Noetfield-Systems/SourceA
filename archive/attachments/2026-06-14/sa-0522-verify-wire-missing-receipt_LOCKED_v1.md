# sa-0522 — verify:wire missing-receipt hardening

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14T13:30Z · **Phase:** s5-P3 commercial · **Tier:** T0

## Problem

`validate-verify-wire-v1.sh` called `build_pack()` before asserting artifacts — verify:wire always passed even when `runreceipt/out/` was empty.

## Fix

| Piece | Role |
|-------|------|
| `scripts/runreceipt/pack_v1.py` → `assert_runreceipt_artifacts()` | verify:wire gate — requires `run.jsonl` · `summary.json` · `receipt.html` with PASS/FAIL status |
| `scripts/validate-verify-wire-v1.sh` | Assert-only — **no auto-build**; exits non-zero when artifacts missing |
| `scripts/validate-verify-wire-missing-receipt-v1.sh` | Negative probe — removes artifacts, proves gate fails |
| `scripts/validate-verify-wire-runreceipt-schema-v1.sh` | Positive path — `build_pack()` then assert (sa-0502 compat) |

## Machine proof

```bash
cd scripts && bash validate-verify-wire-missing-receipt-v1.sh
cd scripts && bash validate-verify-wire-runreceipt-schema-v1.sh
```

## PROGRAM_PROGRESS hook

`signals_auto.verify_wire_missing_receipt` → this attachment + `assert_runreceipt_artifacts` in `pack_v1.py`.

*End sa-0522*
