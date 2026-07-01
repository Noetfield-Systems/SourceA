# IRAP Technical Narrative — Runtime Agent Enforcement Kernel

**Saved:** 2026-07-01T10:33:29Z  
**Version:** 1.2 — LOCKED (draft for ITA intake — customize applicant entity with counsel)  
**route_id:** `locked_product_spec_doc`  
**sequence_id:** SA-2026-07-01-IRAP-ENFORCEMENT-KERNEL-NARRATIVE  
**Parent:** `docs/CANADA_ICP_GRANT_VC_EVIDENCE_Q3_2026_INVESTOR_PLANNING_DATABASE_LOCKED_v1.md`  
**Usage:** ITA one-pager (first call) · IRAP portal technical section skeleton · SR&ED T661 uncertainty spine

**Applicant entity (fill before submit):** _______________________ (CCPC · BC/Ontario · CRA BN: _____________)

**ITA intake:** 1-877-994-4727 · https://nrc.canada.ca/en/support-technology-innovation

---

## 1. Executive summary (ITA one-pager — paste or read aloud)

**Company:** [Legal name] — Canadian incorporated SME building **agentic trust infrastructure** for regulated and high-stakes software workflows.

**Problem:** Enterprises are deploying AI agents that read, write, and execute actions autonomously. Existing tools (LLM observability, chat interfaces, post-hoc logging) **record** what happened but do not **prevent** policy violations at execution time. In regulated sectors (financial services, compliance, audit), this gap blocks production deployment — industry data in 2026 shows ~89% of agent projects fail to reach production, primarily due to governance and audit gaps.

**Technical uncertainty:** There is no known, production-grade method to enforce organizational policy on autonomous agent actions **before** state-changing commits occur, while maintaining cryptographically verifiable audit trails that survive adversarial tampering — without adding unacceptable latency to developer workflows.

**Proposed R&D:** Develop and validate a **runtime enforcement kernel** that: (1) gates every agent write through a single commit path; (2) emits signed receipts per action; (3) hard-fails on policy violation or receipt tampering; (4) integrates with existing agent development environments (e.g. Cursor-class IDEs) without replacing the LLM.

**Commercialization:** License enforcement proof to regulated commercial pilots (Canadian fintech/crypto evidence chain) and developer SKU (governed app factory). First revenue target: paid shadow pilots CAD $3–7.5K.

**Canada benefit:** Jobs in technical R&D in [province]; exportable governance IP; supports Canadian regulated financial sector readiness (CSA tokenization, FINTRAC evidence expectations, Bill C-15 stablecoin readiness).

**Ask:** IRAP support for ___ FTE-months of experimental development over ___ months. Co-funding capacity demonstrated (see financials).

---

## 2. Technological uncertainty (IRAP + SR&ED core)

### 2.1 Why routine engineering is insufficient

| Approach | Limitation |
|----------|------------|
| LLM observability (Langfuse, LangSmith) | Traces actions **after** execution; cannot block |
| Enterprise AI GRC (Credo AI, OneTrust) | Policy registry and documentation; **no runtime enforcement** on API/write path |
| Prompt guardrails | Bypassable; not auditable; no receipt chain |
| Chat-as-memory agent loops | Non-deterministic; fails compliance record-keeping |
| Standard CI validators | Run outside live agent session; do not gate each commit |

**Uncertainty statement (CRA/IRAP language):**

> It is not known whether a single deterministic commit gate can enforce heterogeneous organizational policies across multi-agent workflows in real time, while producing tamper-evident receipts suitable for regulatory examination, at latency acceptable for interactive developer agent sessions (<500ms gate overhead target — hypothesis to be validated).

### 2.2 Due diligence performed (line 043 equivalent)

- Reviewed enterprise agent adoption reports (Gartner 40% agent embed by end-2026; production gap 14–31%)
- Reviewed academic multi-agent trading/governance architectures (bounded autonomy models; arxiv agentic finance 2026)
- Reviewed commercial governance platforms — documentation layer without execution-path enforcement
- Internal prototype demonstrates BLOCK/ALLOW/tamper-FAIL on demo scope — **production generalization is uncertain**

---

## 3. Hypotheses to test (experimental development)

| ID | Hypothesis | Test method | Success criterion | Status (2026-07-01) |
|----|------------|-------------|-------------------|---------------------|
| H1 | A single write entrypoint can enforce 100% of demo-scope agent commits | Route all demo writes through `commit_intent_v1.py` | Zero bypass paths in validator scan | **Partial PASS** — `validate-demo-write-path-v1.sh` |
| H2 | Policy evaluation can run pre-commit without >500ms p95 overhead | Benchmark gate latency under load | p95 < 500ms on reference hardware | **Open** — not benchmarked |
| H3 | Receipt checksum chain detects tampering post-hoc | Adversarial edit + `validate-demo-enforcement-v1.sh --tamper-test` | HARD FAIL on tamper | **PASS** — tamper detected on disk |
| H4 | Eval gate can block factory dispatch when live model eval fails | Integrate eval-1b packet with dispatch gate | `dispatch_ready: false` when eval fails honestly | **Open** — `eval_packet_v1b_report.json` absent |
| H5 | Evidence export format is usable by compliance reviewer without founder narration | Blind review by external reviewer | Reviewer reproduces BLOCK/ALLOW from JSON alone | **Open** — needs external reviewer |

**Note:** H1 and H3 have **verified positive results** on demo scope (disk audit 2026-07-01). H2, H4, H5 remain **uncertain** — qualifying ongoing experimental development for IRAP/SR&ED.

---

## 4. Systematic investigation plan

### 4.1 Architecture under test

```text
Agent intent (JSON)
       │
       ▼
┌──────────────────┐
│  commit_intent   │  ← single write path (R&D focus)
│  gate + policy   │
└────────┬─────────┘
         │ ALLOW                    │ BLOCK
         ▼                          ▼
   Receipt emit               Deny receipt + exit
   ~/.sina/.../receipts/
         │
         ▼
   Validator CI (tamper-FAIL)
```

**Existing code paths (evidence of work in progress — verified 2026-07-01):**
- `scripts/commit_intent_v1.py` — commit gate
- `scripts/validate-demo-enforcement-v1.sh` — BLOCK/ALLOW/tamper CI ✅ PASS
- `scripts/validate-demo-write-path-v1.sh` — W2 single write path ✅ PASS
- `scripts/validate-enforcement-kernel-v1.sh` — K1 tamper-on-read ✅ PASS
- `scripts/demo-enforcement-5min-v1.sh` — investor/demo runner
- `~/.sina/demo-enforcement/receipts/` — sample receipts on disk
- `brain-os/law/enforcement/ENFORCEMENT_6MO_INVESTOR_WIN_LOCKED_v1.md` — project scope law

### 4.2 Experiments (phased)

**Phase A — Kernel hardening (months 1–2)**  
- Eliminate bypass routes in demo scope  
- Formalize receipt schema v1 · checksum algorithm  
- Document failure modes · adversarial test suite  

**Phase B — Latency + scale (months 2–4)**  
- Benchmark policy engine under concurrent agent sessions  
- Experiment with caching vs strict re-eval tradeoffs  
- **Uncertainty:** whether strict mode meets latency budget  

**Phase C — Eval integration (months 3–5)**  
- Wire live eval-1b gate to dispatch without false green  
- **Uncertainty:** model credit outage vs structural eval mode honesty  

**Phase D — External validity (months 4–6)**  
- Shadow pilot with Canadian fintech design partner (staging only)  
- Export Trust Brief JSON — blind compliance reviewer test (H5)  

---

## 5. Milestones and deliverables (Gantt skeleton)

| Month | Milestone | Deliverable | Evidence artifact |
|-------|-----------|-------------|-------------------|
| M1 | Single write path proven | Validator green · bypass scan report | `validate-demo-write-path-v1.sh` output — **PASS 2026-07-01** |
| M2 | Receipt schema frozen v1 | JSON schema + sample receipts | `~/.sina/demo-enforcement/receipts/` — **samples exist** |
| M3 | Tamper suite complete | 10+ adversarial cases | `--tamper-test` PASS · expand adversarial register |
| M4 | Latency benchmark report | p50/p95 gate timing | `receipts/sred-experiment-log-2026/latency/` |
| M5 | Eval-dispatch integration | Honest gate receipt | eval packet + dispatch receipt JSON |
| M6 | Shadow pilot evidence export | Redacted Trust Brief | TrustField SOW deliverable |

**IRAP rule:** Do not mark M4–M6 as started in IRAP proposal if work begins before approval — list as planned scope only.

---

## 6. Budget skeleton (customize with ITA)

| Role | FTE % | Months | IRAP-eligible? | Notes |
|------|-------|--------|----------------|-------|
| Founder / lead engineer | ___% | ___ | Yes — if payroll | Primary investigator |
| Senior developer (if hired) | ___% | ___ | Yes | Kernel + validators |
| Subcontractor (specialist) | — | ___ | Up to 50% co-pay | Security audit · counsel excluded |
| Equipment / cloud | — | — | Limited | LLM API for eval experiments |

**Co-funding:** Company demonstrates ability to pay salaries during reimbursement lag (bank statements on file).

**Typical IRAP request band:** $75K–$200K · 60–80% of eligible technical labour.

---

## 7. Team qualifications

| Name | Role | Relevant experience |
|------|------|---------------------|
| _______________ | Founder / PI | Multi-year agentic systems · governance architecture · [years] software delivery |
| _______________ | Technical advisor (if any) | _______________ |

**Attach:** CVs · GitHub/contributions summary · list of shipped validators and governance docs (SourceA tree).

**Internal technical capacity:** IRAP requires in-house technical execution — not 100% outsourced build.

---

## 8. Commercialization plan (IRAP section)

### 8.1 Market

- **Primary (2026–2027):** Canadian regulated fintech/crypto — evidence chain for FINTRAC-adjacent and CSA tokenization scrutiny  
- **Secondary:** Developer teams running Cursor-class agents in production — governed execution SKU (FORGE)

### 8.2 Go-to-market

| Quarter | Action | Revenue signal |
|---------|--------|----------------|
| Q3 2026 | Priority A outreach (12 accounts) | 3 emails/week · log human reactions |
| Q3–Q4 2026 | TrustField discovery pilot | CAD $3–7.5K SOW |
| Q4 2026 | Second pilot · angel data room | LOI or repeat purchase |
| 2027 | Seed raise · expand SKU | $3–10M seed target post-pilot |

**Commercial SSOT:** `os/commercial/CANADA_RWA_STRATEGY_DEEP_RESEARCH_UPGRADE_LOCKED_v2.md` · `os/commercial/CANADA_PRIORITY_A_SEND_READY_EMAILS_LOCKED_v1.md`

### 8.3 Competitors (honest)

| Vendor | Gap we test |
|--------|-------------|
| Credo AI / OneTrust | Policy registry — no execution-path enforcement |
| Langfuse / LangSmith | Observability — post-hoc |
| Microsoft Copilot Studio | Enterprise agent platform — generic governance |

**Differentiation under test:** Pre-run gate + tamper-evident receipt + validator hard-FAIL — provable on camera.

---

## 9. Benefits to Canada

| Benefit | Mechanism |
|---------|-----------|
| Technical jobs | ___ FTE R&D in [province] during project |
| Innovation capacity | Open validator patterns · Canadian CCPC IP |
| Regulated sector readiness | Evidence tooling for CSA/FINTRAC/Bill C-15 convergence |
| Export potential | Agentic trust infrastructure — global market $10B+ agents TAM 2026 |

---

## 10. Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Latency budget not met (H2 fails) | Architectural fallback: async commit queue with optimistic UI |
| LLM API costs block live eval (H4) | Structural eval mode — honest false, no fake green |
| Commercial pilot delayed | Parallel grant work on kernel — pilot not gating R&D eligibility |
| SR&ED / IRAP overlap | Counsel allocates hours per project · no double-count |
| Scope creep | ENFORCEMENT-6MO law — delete features that don't strengthen gate |

---

## 11. Supporting documentation checklist (upload to portal)

```
□ Incorporation certificate
□ CRA business number
□ Financial statements (2 years)
□ Ownership structure
□ CVs — technical team
□ This narrative (signed/dated)
□ Architecture diagram (export from §4.1)
□ Git commit summary — enforcement scripts
□ Experiment log register (create on project start)
□ Commercialization one-pager — TrustField pilot SKU
□ Letters of interest (optional — accelerates ITA)
```

---

## 12. SR&ED crossover paragraph (for Form T661)

*Copy into T661 project description if same R&D scope claimed:*

> The project addresses experimental development in computer programming to resolve technological uncertainty regarding real-time enforcement of policy on autonomous AI agent write operations. Work includes systematic investigation through prototype commit gates, receipt integrity testing, adversarial tamper experiments, and integration testing with live model evaluation gates. Advancement sought: a verifiable method to make agent execution governance unavoidable without replacing underlying language models. Contemporaneous records include source code (`scripts/commit_intent_v1.py`, validation scripts), dated experiment logs, architecture documentation, and validator outputs stored in project receipts.

---

## 13. ITA first-call script (60 seconds)

> We're a Canadian CCPC building runtime enforcement for AI agents — not another chat wrapper. The uncertainty is whether you can gate every agent write before it hits disk, with tamper-proof receipts fast enough for developer workflows. We have a working demo that BLOCKs bad commits, ALLOWs good ones, and FAILs on tamper — but generalizing to production policy sets and regulated export formats is unsolved. We're commercializing through Canadian fintech evidence pilots while the R&D core stays in the enforcement kernel. We're looking for IRAP support for [X] months of experimental development and have co-funding capacity. Can we walk through the technical uncertainty and our milestone plan?

---

## 14. Related disk SSOT

| Path | Role |
|------|------|
| `docs/ENTITY_EVIDENCE_MATRIX_SOURCEA_TRUSTFIELD_NOETFIELD_CANADA_GRANT_ANGEL_V_LOCKED_v1.md` | Fill-in status tracker |
| `receipts/sred-experiment-log-2026/EXPERIMENT_LOG.md` | Contemporaneous SR&ED entries (555-02) |
| `receipts/sred-experiment-log-2026/HYPOTHESIS_REGISTER.md` | H1–H5 status register |
| `docs/CANADA_ICP_GRANT_VC_EVIDENCE_Q3_2026_INVESTOR_PLANNING_DATABASE_LOCKED_v1.md` | Full funding lane analysis |
| `brain-os/law/enforcement/ENFORCEMENT_6MO_INVESTOR_WIN_LOCKED_v1.md` | Scope boundary |
| `investor/ENFORCEMENT_DEMO_5MIN.md` | Demo script |
| `scripts/validate-demo-enforcement-v1.sh` | Reproducible proof command |

---

**Before submission:** Counsel confirms applicant entity · no pre-approval work on funded scope · financials current · sign and date PDF export.

---

## 15. Disk verification appendix (v1.1 upgrade)

Run and attach stdout to IRAP / SR&ED evidence bundle:

```bash
cd /workspace  # or ~/Desktop/SourceA
bash scripts/validate-demo-enforcement-v1.sh 2>&1 | tee receipts/irap-proof-validate-demo-$(date -u +%Y%m%d).log
bash scripts/validate-demo-enforcement-v1.sh --tamper-test 2>&1 | tee -a receipts/irap-proof-validate-demo-$(date -u +%Y%m%d).log
bash scripts/validate-demo-write-path-v1.sh 2>&1 | tee receipts/irap-proof-write-path-$(date -u +%Y%m%d).log
bash scripts/validate-enforcement-kernel-v1.sh 2>&1 | tee receipts/irap-proof-kernel-$(date -u +%Y%m%d).log
```

**Upgrade v1.1:** Hypothesis status column · disk-verified code paths · M1–M3 progress · proof capture commands.

*Locked draft — bump `Saved:` UTC on material edits.*
