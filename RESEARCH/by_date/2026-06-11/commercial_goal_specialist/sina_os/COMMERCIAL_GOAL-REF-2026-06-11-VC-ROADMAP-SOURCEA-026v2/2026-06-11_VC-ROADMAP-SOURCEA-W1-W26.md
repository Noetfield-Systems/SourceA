# SourceA Engine Roadmap — Weeks 1–26 (W1/W2 only)

**Saved:** 2026-06-11T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**trace_id:** `COMMERCIAL_GOAL-REF-2026-06-11-VC-ROADMAP-SOURCEA-026v2`  
**scope:** **Layer 1 SourceA only** — no Noetfield/TrustField GTM in this table  
**portfolio_money:** see `NOETFIELD-LANE-6MO-029` · `TRUSTFIELD-LANE-6MO-030`  
**parent:** `THREE-LAYER-028` · `100M-SIGNAL-6MO-v2`  
**date:** 2026-06-11

---

## Weekly table — SourceA engine + enforcement demo

| Week | Engineering Deliverable | Demo Capability | Risk | Exit Criteria |
|------|-------------------------|-----------------|------|---------------|
| **1** | FR-003 start · projection bypass audit (report) | RT LIVE tamper-FAIL (`validate-universe-invariants-v1.sh`) | FR-003 slip | FR-003 in progress · tamper-FAIL on RT receipt |
| **2** | FR-003 complete · Phase 1.10 seal start | BLOCK/ALLOW storyboard doc | 1.10 delay | FR-003 PASS |
| **3** | **D1** demo policy P-001 + intent fixtures | Policy loads · no execute yet | Scope creep to NF product | D1 merged logged |
| **4** | Phase **1.10 seal** · append-only receipt log spec | Overwrite → FAIL spec | Demo scope creep | 1.10 sealed · D4 spec approved |
| **5** | **D2** `governance_demo_gate_v1` in gatekeeper | **BLOCK** exits ≠0 · P-001 | Gate bypass | BLOCK reproducible |
| **6** | **D3** ALLOW stub + receipt writer | **ALLOW** → receipt JSON | No spine yet | ALLOW receipt logged |
| **7** | D3 **spine_event_id** bind | ALLOW → receipt + spine row | Missing spine row | Full ALLOW chain |
| **8** | **`sourcea_execute_v1 --demo-enforcement`** wired | One-command BLOCK+ALLOW | Multi write paths | Internal one-command demo |
| **9** | **D4** append-only `receipt-log.jsonl` | Overwrite → validator FAIL | Log not enforced | Overwrite FAIL |
| **10** | **D5** `validate-demo-enforcement-v1.sh` | **TAMPER** edit → exit 1 | False PASS | Tamper FAIL live |
| **11** | D6 runbook · Hub demo button spec → Maintainer | 5-min dry-run ≤5 min | Cascade slow | Dry-run timed PASS |
| **12** | Close demo-path bypass #1 | Rehearsal cannot lie | Bypass found | Rehearsal PASS |
| **13** | Hub **"Run governance demo"** button (Maintainer) | Founder one-tap demo | Hub breaks chain | One-tap works |
| **14** | Investor video backup + JSONL export bundle | DD export pack | Fake tamper in video | Video + JSONL logged |
| **15** | Hub projection bypass #1 (if safe post-1.10) | Demo + 1 hardening proof | Breaks demo | Bypass closed or documented |
| **16** | Optional **generic policy scenario #2** (not TF product) | Two intents same engine | Scope doubles | 2 intents · same gate |
| **17** | Demo validator in CI (demo scope) | Tamper regression always FAIL | CI noise | CI fails tampered fixture |
| **18** | Commit gate bypass audit doc (max 5 paths) | Audit "demo vs rest" | — | Audit doc logged |
| **19** | Demo regression fix only | External observer dry-run | — | **W1 candidate PASS** |
| **20** | Second bypass close OR log generalization | Witnessed demo | — | **W1 PASS** external |
| **21** | DD export bundle polish | Pack: policy·receipt·spine·validator | — | DD pack complete |
| **22** | Demo stability — 10 consecutive PASS | 10/10 runs | Demo flake | 10/10 PASS |
| **23** | `validate-demo-enforcement` in Maintainer scan | Demo = narrative ship gate | — | Maintainer scan includes demo |
| **24** | Commit gate slice #2 if investor feedback | Enforcement metric on screen | — | Gate slice or defer doc |
| **25** | **Freeze** demo scope — docs only | Final rehearsal | Feature creep | Scope frozen |
| **26** | **W2 sign-off** — demo write path audit | **W1+W2** investor demo day | Bypass found late | **Binary W1+W2 PASS** |

---

## SourceA win conditions (this roadmap)

| ID | PASS |
|----|------|
| **W1** | Live BLOCK · ALLOW · tamper-FAIL · 5 min |
| **W2** | Single demo write path · receipt · spine · validator HARD FAIL |

**W3 (revenue)** is **not** in this table — portfolio lanes only.

---

## Critical path

> Tamper-proof demo on single commit path — **SourceA Layer 1**.

---

## Portfolio sync (weekly — no money in SourceA row)

| Week | Noetfield lane | TrustField lane |
|------|----------------|-----------------|
| Every Friday | NF worker posts pipeline status | TF worker posts if T5 active |
| W19+ | May use SourceA JSONL export in NF pitch | May use export in TF pitch if ASF enables T5 |

**execution_authority:** false
