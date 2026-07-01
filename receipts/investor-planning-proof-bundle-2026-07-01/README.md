# Investor planning proof bundle — 2026-07-01

**Plan:** 555-01 · **Status:** DONE  
**Use:** Attach to IRAP portal · SR&ED contemporaneous evidence · angel technical DD

## Reproduce

```bash
cd /workspace
bash scripts/validate-demo-enforcement-v1.sh
bash scripts/validate-demo-enforcement-v1.sh --tamper-test
bash scripts/validate-demo-write-path-v1.sh
bash scripts/validate-enforcement-kernel-v1.sh
```

## Contents

| File | Meaning |
|------|---------|
| `MANIFEST.json` | Machine index + sha256 |
| `validate-demo-enforcement.log` | BLOCK/ALLOW/receipt PASS |
| `validate-demo-enforcement-tamper.log` | Tamper FAIL detected |
| `validate-demo-write-path.log` | W2 single write path |
| `validate-enforcement-kernel.log` | K1 kernel PASS |
| `commit-intent-allow.json` | Allow case JSON output |
| `receipt-latest-demo.json` | Sample receipt for redaction (555-03) |
