# ENFORCEMENT-6MO — Weekly Operating Plan (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.1 — LOCKED  
**sequence_id:** SA-2026-06-11-ENFORCEMENT-6MO-WEEKLY  
**Horizon:** 2026-06-11 → 2026-12-31 (26 weeks)  
**Synthesized from:** Commercial Goal Specialist · Governance Goal Specialist · Brief/Demo Worker · Brain fleet · disk audit 2026-06-11  
**Supersedes v1.0:** §3 ASF role · §5 commercial columns · §6 rhythm · §10 metrics — manual founder ops **void** per `SINA_ENFORCEMENT_6MO_LAW_SUPERSESSION_LOCKED_v1.md`  
**Parent law:** `SINA_P0_PORTFOLIO_AUTOMATION_AND_EVIDENCE_LAW_LOCKED_v1.md` Pillar A  
**Accepted regime:** 5–10% · high risk · proof over completeness  

---

## 0. Big picture (one page)

You are not building an OS company in 6 months. You are building **the smallest system that cannot lie on camera**, plus **one paid signal**, to maximize **$100M narrative credibility** (not guaranteed close).

| Layer | What it is |
|-------|------------|
| **Category (external only)** | *We make AI execution impossible to bypass governance.* |
| **Product label** | AI Governance Execution Layer |
| **Demo wedge** | Copilot policy change — BLOCK / ALLOW / tamper FAIL |
| **Money wedge** | NF-001 (Noetfield Copilot) or TF-001 (TrustField RPAA) design partner |
| **Raise target (honest)** | Seed **$3M–$10M** @ **$15M–$40M pre** if W1+W2+W3 land |
| **North star (24mo)** | $100M outcome signal — budget as upside, not plan |

**Final rule:** If it can bypass, it doesn’t exist.

---

## 1. Win conditions (binary — Dec 31)

| ID | PASS when | Owner |
|----|-----------|-------|
| **W1** | 5-min live demo: BLOCK → ALLOW → tamper **FAIL** on camera (backup video OK for cascade only; tamper must be live) | ASF + Worker |
| **W2** | Demo-scoped single write path · receipt per ALLOW · `validate-demo-enforcement-v1.sh` + tamper PASS | Worker |
| **W3** | NF-001 or TF-001 **deposit ≥CAD 2K** or **signed LOI/SOW** | ASF + Commercial |

**Program FAIL if:** demo bypass in rehearsal OR no W3 by Week 22 review.

---

## 2. Disk baseline (Week 0 — 2026-06-11)

### Shipped (do not rebuild)

| Slice | Status | Proof |
|-------|--------|-------|
| DEMO-ENF-S1 policy + intents | **done** | `governance_demo_policy_v1.json` |
| DEMO-ENF-S2 BLOCK gate | **done** | `--case block` exits ≠ 0 |
| DEMO-ENF-S3 ALLOW + spine | **done** | `spine_event_id` on receipt |
| DEMO-ENF-S4 append-only log | **done** | `receipt-log.jsonl` |
| DEMO-ENF-S5 tamper validator | **done** | `validate-demo-enforcement-v1.sh --tamper-test` |
| DEMO-ENF-S6 runbook | **done** | `INVESTOR_DEMO_RUNBOOK_v1.md` |
| RT LIVE gate + universe validator | **done** | INCIDENT-027 latch |
| Investor materials stub | **done** | `ENFORCEMENT_DEMO_5MIN.md` · `ENFORCEMENT_3SLIDE_DECK_v1.md` · `ENFORCEMENT_OUTREACH_v1.md` |
| enforcement-1000 pack | **done** | 1000 categorized plans · 29 disk-proven T0 |

### Open (critical path)

| Slice | Owner | Week target |
|-------|-------|-------------|
| DEMO-ENF-S7 film W1 | ASF | Week 2–3 |
| DEMO-ENF-S8 Hub one-tap demo | Maintainer 2 | Week 4 |
| DEMO-ENF-S9 bypass inventory validator | Worker | Week 3–4 |
| DEMO-ENF-W3 money signal | ASF | Week 1–22 parallel |
| FR-003 + Phase 1.10 seal | Maintainer 2 | Week 1–4 parallel |
| `validate-demo-write-path-v1.sh` | Worker | Week 1 |

**Validators today:** demo PASS · tamper PASS · universe PASS · factory FREEZE ON (background only).

---

## 3. Operating model

### Roles (no lane crossing)

| Role | Owns | Never |
|------|------|-------|
| **ASF (you)** | Hub tap · wedge PICK · **final contact** on hot leads · film demo presence | Manual post/email/call · Terminal · factory drain hero |
| **Worker** | enf-* T0 ship · S7/S9 · validators · n8n outreach glue · recording artifacts | Hub rewrite · naming sprint |
| **Maintainer 2** | FR-003 · 1.10 · S8 Hub Action · hero scrub | Demo implementation |
| **Commercial agents** | Outreach queue · CRM · LOI/SOW drafts · deck polish via agents | SourceA code · manual founder send |
| **Brain** | Route · audit · weekly gate review | Implementation |

### Gate test (every task)

Increases **(a)** enforcement strength **(b)** demo credibility **(c)** willingness to pay — else **DELETE**.

### Falsifiers (stop the line)

| Signal | Action |
|--------|--------|
| Validator PASS after hand-edit receipt | Stop all outreach until fixed |
| Demo uses fake BLOCK output | Kill video; re-film |
| No LOI conversation by Week 8 | Double outreach; zero new features |
| No W3 signal by Week 22 | Reframe to honest seed band; no $100M close talk |
| Projection cited as law in any deck | Rewrite materials |

### Pick order (engineering)

```bash
python3 scripts/pick-enforcement-no-asf-plan.py --any-tier --limit 1 --prompt
```

Factory `sa-1000` = **background only** until W1 filmed.

---

## 4. Funding tiers (plan finances here)

| Tier | Dec 2026 target | Probability |
|------|-----------------|-------------|
| **A** | W1 filmed + W2 green + 3 discovery calls | 60–70% |
| **B** | A + W3 deposit/LOI + 10 investor meetings | 30–40% |
| **C** | B + tier-1 intro + $100M **narrative** credible | 15–25% |
| **D** | $100M round closed | <10% |

**Budget A–B. Pitch C as upside.**

---

## 5. Twenty-six week plan

**Week 1 anchor:** 2026-06-11 (Thu). Adjust dates if start shifts; keep sequence.

### PHASE I — PROVE (Weeks 1–4) · Jun

**Theme:** Kernel honest · film demo · start money lane · close Maintainer parallel

| Week | Dates | Engineering (Worker) | Maintainer 2 | Commercial / ASF | Exit gate |
|------|-------|----------------------|--------------|------------------|-----------|
| **W1** | Jun 11–17 | Verify S1–S6 closeout receipts; ship `validate-demo-write-path-v1.sh` (enf-0002); internal dry-run `demo-enforcement-5min-v1.sh` 3× | FR-003 EXTERNAL_CRITIC wiring start | **Pick wedge:** NF primary / TF backup; agentic outreach spec wired; **approve batch 1** (5 targets) — agents queue · founder hub tap only | Dry-run ≤5:00 · validators green |
| **W2** | Jun 18–24 | S7 **film take 1**; archive logs `archive/attachments/2026-06-*/`; enf-0007/0008 if flaky | FR-003 → 1.10 seal push | Outreach batch 1 (5 targets from `ENFORCEMENT_OUTREACH_v1.md`); send 3-slide deck link | Recording logged OR 3 clean live runs |
| **W3** | Jun 25–Jul 1 | S7 **film take 2** (backup); S9 bypass inventory validator stub; polish runbook | Phase **1.10 seal** target | Follow-up batch 1; log CRM pipeline stages | Best video selected; bypass doc updated |
| **W4** | Jul 2–8 | S9 CI: spawn-without-gate FAIL; chaos dry-run kill terminal mid-demo | **S8 Hub Action** one-tap `demo-enforcement-5min-v1.sh` | LOI draft v1 sent to warmest lead | Founder one-tap demo works |

**Month 1 gate (Jul 8):** W2 demo path green · W1 rehearsal credible · ≥3 conversations logged · FR-003/1.10 status documented.

---

### PHASE II — PACKAGE (Weeks 5–8) · Jul–Aug

**Theme:** Demo cannot lie · pilot SKU · outreach scale

| Week | Dates | Engineering | Maintainer | Commercial / ASF | Exit gate |
|------|-------|-------------|------------|------------------|-----------|
| **W5** | Jul 9–15 | Receipt hardening: spine_event_id on all demo receipts; enf-0101 tier CI | Hub hero scrub (tertiary copy only) | NF-001 one-pager finalize; 10-target list named | Pilot doc ready |
| **W6** | Jul 16–22 | TF wedge stub: RPAA-flavored second intent (optional second beat) | Monitor hub P0 stays enforcement not drain | Agentic follow-up batch 2; demo link in every sequence; **6 conversations logged** | 6 conversations cumulative |
| **W7** | Jul 23–29 | Export **diligence bundle**: video + validator logs + sample receipt JSON | — | Pilot proposal template (90-day · CAD 2K–10K) | Data room folder v1 |
| **W8** | Aug 1–7 | Monthly chaos drill #1: hand-edit receipt → FAIL on camera | — | **Gate:** ≥1 LOI conversation active OR program outreach 2× | Month 2 gate PASS |

**Month 2 gate (Aug 7):** Internal + external demo without fakes · LOI path alive.

---

### PHASE III — SIGNAL (Weeks 9–14) · Aug–Sep

**Theme:** Close design partner · widen one bypass · investor-ready materials

| Week | Dates | Engineering | Maintainer | Commercial / ASF | Exit gate |
|------|-------|-------------|------------|------------------|-----------|
| **W9** | Aug 8–14 | Close top bypass from `DEMO_BYPASS_AUDIT_v1.md` (demo scope) | align_command_data gate-aware scrub | Pilot SOW sent to #1 lead | SOW out |
| **W10** | Aug 15–21 | `validate-enforcement-demo-v1.sh` wired to anti-staleness bundle | — | TF-001 RPAA brief if NF stalls | Validator in CI habit |
| **W11** | Aug 22–28 | Kill/replay 60s clip for deck (optional) | — | Negotiate deposit terms | Verbal commit or pass |
| **W12** | Aug 29–Sep 4 | Freeze demo features — bugfix only | — | **Target: W3 deposit invoice or LOI signature** | W3 attempt logged |
| **W13** | Sep 5–11 | Second scenario polish (if pilot needs) | — | Customer reference prep | — |
| **W14** | Sep 12–18 | Month 3 hardening only | — | Case study template draft | Month 3 gate |

**Month 3 gate (Sep 18):** W3 deposit/LOI **signed** OR honest miss declared + pivot list.

---

### PHASE IV — NARRATIVE (Weeks 15–20) · Sep–Nov

**Theme:** Seed conversations · pipeline heat · no new scope

| Week | Dates | Engineering | Commercial / ASF | Exit gate |
|------|-------|-------------|------------------|-----------|
| **W15** | Sep 19–25 | Bugfix only | 3-slide deck final (`ENFORCEMENT_3SLIDE_DECK_v1.md`) | Deck ready |
| **W16** | Sep 26–Oct 2 | — | Investor target list 25 funds | List complete |
| **W17** | Oct 3–9 | Chaos drill #2 | Investor meetings 1–3 | 3 meetings |
| **W18** | Oct 10–16 | — | Meetings 4–7 · warm intros | 7 cumulative |
| **W19** | Oct 17–23 | — | Meetings 8–10 | 10 cumulative |
| **W20** | Oct 24–30 | — | Pipeline review: verbal commits | Month 5 gate |

**Month 5 gate (Oct 30):** 10+ investor meetings OR W3 already closed + expansion conversations.

---

### PHASE V — CLOSE (Weeks 21–26) · Nov–Dec

**Theme:** Freeze · honest tier · raise or reset

| Week | Dates | All lanes | Exit gate |
|------|-------|-----------|-----------|
| **W21** | Nov 1–7 | Seed data room zip; cap table snapshot | Data room ready |
| **W22** | Nov 8–14 | **W3 binary review** — deposit/LOI or declared miss | W3 status locked |
| **W23** | Nov 15–21 | Investor meetings 11–15 (if raising) | Term sheet talk or pass |
| **W24** | Nov 22–28 | Honest tier A/B/C/D scoring doc | Tier declared |
| **W25** | Dec 1–7 | **FREEZE** — no new features | Scope locked |
| **W26** | Dec 8–31 | Closeout report · thank partners · Jan plan pointer only | ENFORCEMENT-6MO closeout PASS or honest FAIL |

**Month 6 gate (Dec 31):** W1 + W2 + W3 evidence logged · tier logged · 2027 pointer filed.

---

## 6. Weekly ASF rhythm (founder — hub only · agentic commercial)

| Day | Action |
|-----|--------|
| **Mon** | Hub: Review gate · **Approve outbound batch** (one tap) |
| **Tue** | Hub: **Final contact** card only if agent flagged hot lead |
| **Wed** | Hub: Approve agent-drafted proof post (LinkedIn queue) |
| **Thu** | Sina Command: Refresh · Safety if needed · Hub demo tap when S8 ships |
| **Fri** | Hub: Pipeline snapshot · forward Worker slice if blocked |

**Minimum commercial:** 3 **agent-logged conversations**/week Weeks 1–8; investor meetings Weeks 15–20 via agent booking · founder final contact only.

**Law:** `SINA_P0_PORTFOLIO_AUTOMATION_AND_EVIDENCE_LAW_LOCKED_v1.md` · `AGENTIC_W3_OUTREACH_WORKFLOW_SPEC_v1.md`

---

## 7. Weekly engineering rhythm (Worker)

| Week type | Actions |
|-----------|---------|
| **Ship week** | 1× `enf-*` T0 from pick script · validator PASS · receipt YAML |
| **Film week** | S7 only — no new features |
| **Harden week** | T1 CI + chaos from enforcement-1000 |
| **Freeze week** | Bugfix only — reject new enf scope |

---

## 8. Artifact map (single index)

| Need | Path |
|------|------|
| Law | `brain-os/law/enforcement/ENFORCEMENT_6MO_INVESTOR_WIN_LOCKED_v1.md` |
| This plan | `brain-os/law/enforcement/ENFORCEMENT_6MO_WEEKLY_OPERATING_PLAN_LOCKED_v1.md` |
| 30-day slices | `brain-os/demo/ENFORCEMENT_30DAY_BACKLOG_v1.md` |
| 1000 plans | `brain-os/plan-registry/enforcement-1000/REGISTRY.json` |
| Category index | `brain-os/plan-registry/ENFORCEMENT-1000-CATEGORY-INDEX.md` |
| Demo run | `scripts/demo-enforcement-5min-v1.sh` |
| Speaker notes | `investor/ENFORCEMENT_DEMO_5MIN.md` |
| Outreach | `investor/ENFORCEMENT_OUTREACH_v1.md` |
| 3 slides | `investor/ENFORCEMENT_3SLIDE_DECK_v1.md` |
| Commercial plan | `~/.sina/agent-workspaces/trustfield/commercial-goal/2026-06-11_100M-SIGNAL-6MO-EXECUTION-PLAN.md` |
| Bypass honesty | `brain-os/demo/DEMO_BYPASS_AUDIT_v1.md` |

---

## 9. DELETE list (6 months — frozen)

Trust OS / Decision Cloud naming · whitepaper-first · digital twin · causal graph · learning loop · full OS · REGISTRY drain as investor metric · hub hero sprints · factory velocity headline · GPT paradigm sprints without ASF adopt · Mono mx unless demo-blocked.

---

## 10. Success metrics dashboard (update weekly)

| Metric | W1 target | W8 | W14 | W26 |
|--------|-----------|-----|-----|-----|
| Demo dry-run clean | 3× | 10× | — | — |
| Video logged | — | 1 | 2 | best cut |
| Validators PASS | daily | daily | daily | daily |
| Agent-logged conversations | 3 | 10 | 15 | — |
| LOI/deposit | 0 | draft | **signed** | closed |
| Investor meetings | 0 | 0 | — | 10–15 |
| enf T0 done count | 35+ | 80+ | 120+ | freeze |
| Revenue CAD | 0 | 0 | ≥2K | ≥2K |

---

## 11. One-line operating constraint

> **Speed > completeness · Proof > narrative · One deposit proves market · Then raise.**

---

## Annex A — Preserved spirit (from superseded docs — not lost)

**Canonical:** `SINA_ENFORCEMENT_6MO_PRESERVED_SPIRIT_AND_LINEAGE_LOCKED_v1.md`  
**Rule:** MASTER-PLAN · VC-ROADMAP engineering weeks 1–6 are **void** (S1–S6 shipped). **All rows below remain active.**

### A.1 Gate test (every task)

Increases **(a)** enforcement **(b)** demo credibility **(c)** willingness to pay — else **DELETE**.

### A.2 W3 bottleneck (preserved)

Outreach **Week 1** · demo follows conversation · 13–16 week sales cycle if delayed.

### A.3 Failure modes

| FM | Prevention |
|----|------------|
| FM1 Delayed outreach | Agentic batch Week 1 |
| FM2 Q&A bypass | Adversarial week 10 · S9 inventory |
| FM3 Scope creep | DELETE list · EXTERNAL_CRITIC report-only |

### A.4 Weeks 7–26 engineering (still on roadmap)

Hub S8 · film W1 week 9 · adversarial 8–10 · receipt export 13–14 · RPAA stub 15–16 · scope freeze 17–18 · pilot 19–20 · deck week 21 · investor meetings 22–26.

### A.5 Commercial preserved

- 10-target personas (`ENFORCEMENT_OUTREACH`)  
- CAD $2K min · 90-day pilot · FINTRAC wedge for TF fallback  
- Terminal demo OK for proposal · film for investors  
- Investor one-liner in PRESERVED_SPIRIT §2  

### A.6 Layered advisory preserved

Serialization truth · honest counter · one thread · evidence flywheel · β+ hybrid with **agentic PM** (not manual call).

---

*End ENFORCEMENT-6MO weekly operating plan — synthesized Commercial + Governance + Brief specialists · Brain route only.*
