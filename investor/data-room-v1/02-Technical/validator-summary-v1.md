# Validator summary — 2026-07-01

Captured during 555-01 proof bundle. Associate can re-run commands in `PROOF_COMMANDS.md`.

| Validator | Result | Key line |
|-----------|--------|----------|
| `validate-demo-enforcement-v1.sh` | PASS | Copilot BLOCK/ALLOW · receipt · spine |
| `validate-demo-enforcement-v1.sh --tamper-test` | PASS | tamper detected |
| `validate-demo-write-path-v1.sh` | PASS | W2 write-path · commit_intent → receipt · spine bound |
| `validate-enforcement-kernel-v1.sh` | PASS | K1 tamper-on-read |
| `commit_intent_v1.py --demo-enforcement --case allow` | PASS | `"ok": true` · outcome COMMITTED |

**Manifest with sha256:** `receipts/investor-planning-proof-bundle-2026-07-01/MANIFEST.json`
