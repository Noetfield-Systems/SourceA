# Proof commands — angel / grant DD

**Plan:** 555-03 · **Data room:** `investor/data-room-v1/02-Technical/`  
**Reproduce without founder:** run from SourceA repo root

```bash
bash scripts/validate-demo-enforcement-v1.sh
bash scripts/validate-demo-enforcement-v1.sh --tamper-test
bash scripts/validate-demo-write-path-v1.sh
bash scripts/validate-enforcement-kernel-v1.sh
python3 scripts/commit_intent_v1.py --demo-enforcement --case allow --json
```

**Expected:** BLOCK case fails closed · ALLOW emits receipt · tamper test detects edit · write-path bound.

**Full artifact bundle:** `receipts/investor-planning-proof-bundle-2026-07-01/MANIFEST.json` (555-01)

**SR&ED experiment log:** `receipts/sred-experiment-log-2026/EXPERIMENT_LOG.md` (555-02)
