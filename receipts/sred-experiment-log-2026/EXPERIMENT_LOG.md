# SR&ED Experiment Log — 2026

**Plan:** 555-02 · **Lead entity:** SourceA · **Created:** 2026-07-01T10:33:29Z  
**Law:** Contemporaneous records for CRA Form T661 / IRAP due diligence  
**Hypothesis register:** `HYPOTHESIS_REGISTER.md` · **Proof bundle:** `../investor-planning-proof-bundle-2026-07-01/`

---

## EXP-001 — H1 single write path (partial PASS)

| Field | Value |
|-------|-------|
| **Date** | 2026-07-01T10:31:02Z |
| **Project** | R&D-01 Runtime agent enforcement kernel |
| **Hypothesis** | H1 — single write entrypoint enforces 100% of demo-scope agent commits |
| **Uncertainty** | Policy may be bypassed between LLM output and disk write via parallel paths |
| **Method** | Route demo writes through `commit_intent_v1.py`; scan for bypass with `validate-demo-write-path-v1.sh` |
| **Command** | `bash scripts/validate-demo-write-path-v1.sh` |
| **Result** | **Partial PASS** — W2 write-path bound; demo scope only; production generalization open |
| **Evidence** | `investor-planning-proof-bundle-2026-07-01/validate-demo-write-path.log` sha256 `e17a324652932c11fc9bfc577335e2055576baf50baab7c0fbd69e134e8d7a90` |
| **Advancement** | Demonstrated single commit path with receipt emission on ALLOW |
| **Next** | Eliminate bypass routes outside demo scope (IRAP Phase A) |

---

## EXP-002 — H3 receipt tamper detection (PASS)

| Field | Value |
|-------|-------|
| **Date** | 2026-07-01T10:31:02Z |
| **Project** | R&D-02 Receipt integrity + tamper detection |
| **Hypothesis** | H3 — checksum chain detects post-hoc adversarial edit |
| **Uncertainty** | Whether receipt integrity survives examiner-style tampering without external HSM |
| **Method** | Adversarial edit + `validate-demo-enforcement-v1.sh --tamper-test` |
| **Command** | `bash scripts/validate-demo-enforcement-v1.sh --tamper-test` |
| **Result** | **PASS** — tamper detected; validator HARD FAIL |
| **Evidence** | `investor-planning-proof-bundle-2026-07-01/validate-demo-enforcement-tamper.log` sha256 `09e9b96e8aa9b76ca1faa3851324db4454803785640323f32e4275401acfa536` |
| **Advancement** | Tamper-on-read detection operational on demo receipt chain |
| **Next** | Expand adversarial suite to 10+ cases (IRAP M3) |

---

## EXP-003 — H1+H3 combined enforcement kernel (PASS)

| Field | Value |
|-------|-------|
| **Date** | 2026-07-01T10:31:02Z |
| **Project** | R&D-01 + R&D-02 |
| **Hypothesis** | Combined gate + receipt + tamper FAIL forms minimal enforceable kernel |
| **Uncertainty** | Whether BLOCK/ALLOW/tamper sequence is reproducible without manual intervention |
| **Method** | Full validator chain + allow case JSON |
| **Commands** | `validate-demo-enforcement-v1.sh` · `validate-enforcement-kernel-v1.sh` · `commit_intent_v1.py --demo-enforcement --case allow` |
| **Result** | **PASS** — all validators green; `ok: true` on allow commit |
| **Evidence** | `investor-planning-proof-bundle-2026-07-01/MANIFEST.json` plan 555-01 |
| **Advancement** | Reproducible investor/grant proof bundle without founder narration |
| **Next** | H2 latency benchmark · H4 eval-dispatch integration |

---

## Open experiments (not yet run)

| ID | Hypothesis | Status |
|----|------------|--------|
| H2 | Pre-commit policy p95 < 500ms | Open — 555+ future |
| H4 | eval-1b gates dispatch honestly | Open — eval_packet absent |
| H5 | Blind compliance reviewer reproduces from JSON | Open — needs external reviewer |

---

*Append new entries with UTC date before each SR&ED claim period close.*
