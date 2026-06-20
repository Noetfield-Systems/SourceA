# SourceA Engine Roadmap — Weeks 1–26 (W1/W2 only · disk-aligned v3)

**Saved:** 2026-06-11T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**trace_id:** `COMMERCIAL_GOAL-REF-2026-06-11-VC-ROADMAP-SOURCEA-026v3`  
**supersedes:** `VC-ROADMAP-SOURCEA-026v2` (scheduled D1–D5 as future — **already on disk**)  
**scope:** **Layer 1 SourceA only** — no Noetfield/TrustField GTM in this table  
**portfolio_money:** `NOETFIELD-LANE-029` · `TRUSTFIELD-LANE-030`  
**parent:** `THREE-LAYER-028` · `BIG-PICTURE-031` · `100M-SIGNAL-6MO-v2`  
**date:** 2026-06-11

---

## Week 0 baseline (shipped — do not rebuild)

| Slice | Status | Proof |
|-------|--------|-------|
| DEMO-ENF-S1 policy + intents | **done** | `governance_demo_policy_v1.json` |
| DEMO-ENF-S2 BLOCK gate | **done** | `--case block` exits ≠ 0 |
| DEMO-ENF-S3 ALLOW + spine | **done** | `spine_event_id` on receipt |
| DEMO-ENF-S4 append-only log | **done** | `receipt-log.jsonl` |
| DEMO-ENF-S5 tamper validator | **done** | `validate-demo-enforcement-v1.sh --tamper-test` PASS |
| DEMO-ENF-S6 runbook | **done** | `INVESTOR_DEMO_RUNBOOK_v1.md` |

---

## Weekly table — from current disk forward

| Week | Engineering Deliverable | Demo Capability | Risk | Exit Criteria |
|------|-------------------------|-----------------|------|---------------|
| **1** | `validate-demo-write-path-v1.sh` · verify S1–S6 closeout receipts | Internal dry-run 3× | Rebuild D1–D5 by mistake | Write-path validator on disk · dry-run log |
| **2** | **S7** film take 1 · archive logs | **W1** recording or 3 clean live runs | Demo flake | Recording on disk OR 3× PASS |
| **3** | **S9** bypass inventory validator · enf-0007/0008 if flaky | Rehearsal cannot lie | Bypass found | Bypass inventory validator PASS |
| **4** | **S8** Hub one-tap demo (Maintainer) · FR-003 → 1.10 seal push | Founder one-tap BLOCK/ALLOW/tamper | Hub breaks chain | One-tap works · 1.10 progress |
| **5** | Receipt hardening: spine_event_id on all demo receipts | DD export bundle start | False PASS | All demo receipts bound |
| **6** | Close demo-path bypass #1 | 5-min dry-run ≤5 min | Multi write paths | Rehearsal timed PASS |
| **7** | Investor video backup + JSONL export bundle | External observer dry-run | Fake tamper in video | Video + JSONL on disk |
| **8** | Demo validator in CI (demo scope) | Tamper regression always FAIL | CI noise | CI fails tampered fixture |
| **9** | Commit gate bypass audit doc (max 5 paths) | Audit "demo vs rest" | Scope creep | Audit doc on disk |
| **10** | **W1 candidate PASS** — witnessed external dry-run | Live tamper on camera | Demo flake | **W1 PASS** (external witness) |
| **11–12** | Demo stability — 10 consecutive PASS | 10/10 runs | Bypass late find | 10/10 PASS |
| **13–14** | Hub projection bypass #1 (if safe post-1.10) | Demo + 1 hardening proof | Breaks demo | Bypass closed or documented |
| **15–16** | Optional generic policy scenario #2 (not TF/NF product) | Two intents same engine | Scope doubles | 2 intents · same gate |
| **17–18** | DD export bundle polish | Pack: policy·receipt·spine·validator | — | DD pack complete |
| **19–20** | Commit gate slice #2 if investor feedback | Enforcement metric on screen | — | Gate slice or defer doc |
| **21–22** | Demo regression fix only | Second external observer | — | **W1 reconfirm PASS** |
| **23** | `validate-demo-enforcement` in Maintainer scan | Demo = narrative ship gate | — | Maintainer scan includes demo |
| **24–25** | **Freeze** demo scope — docs only | Final rehearsal | Feature creep | Scope frozen |
| **26** | **W2 sign-off** — demo write path audit | **W1+W2** investor demo day | Bypass found late | **Binary W1+W2 PASS** |

---

## SourceA win conditions (this roadmap)

| ID | PASS |
|----|------|
| **W1** | Live BLOCK · ALLOW · tamper-FAIL · 5 min |
| **W2** | Single demo write path · receipt · spine · validator HARD FAIL |

**W3 (revenue)** is **not** in this table — portfolio lanes only.

---

## Portfolio sync (weekly — no money in SourceA row)

| Week | Noetfield lane | TrustField lane |
|------|----------------|-----------------|
| Every Friday | NF worker posts pipeline status | TF worker posts if T5 active |
| W7+ | May attach SourceA demo clip / JSONL in NF pitch | May use export in TF pitch if ASF enables T5 |

**execution_authority:** false
