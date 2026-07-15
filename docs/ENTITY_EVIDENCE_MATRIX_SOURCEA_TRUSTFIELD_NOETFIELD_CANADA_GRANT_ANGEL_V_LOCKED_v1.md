# Canada Entity Evidence Matrix — SourceA · TrustField · Noetfield · FORGE

**Saved:** 2026-07-01T10:33:29Z  
**Version:** 1.2 — LOCKED  
**route_id:** `locked_product_spec_doc`  
**sequence_id:** SA-2026-07-01-CANADA-ENTITY-EVIDENCE-MATRIX  
**Parent:** `docs/CANADA_ICP_GRANT_VC_EVIDENCE_Q3_2026_INVESTOR_PLANNING_DATABASE_LOCKED_v1.md`  
**Usage:** Fill-in-the-blank ops checklist — update status weekly; cite disk paths in DD

**Status legend:** `[ ]` Not started · `[~]` In progress · `[x]` Done · `[—]` N/A for entity · `[!]` Blocker

**Last reviewed:** 2026-07-01T10:33:29Z  
**Reviewer:** cursor-agent (555-02 execution)

---

## Readiness rollup (updated after 555-02)

| Tier | Done | In progress | Not started | Score |
|------|------|-------------|-------------|-------|
| T0 Legal | 1 | 2 | 7 | **10%** |
| SRED | 4 | 3 | 5 | **33%** |
| IRAP | 2 | 0 | 8 | **20%** |
| ANG | 4 | 2 | 17 | **17%** |
| SEED | 0 | 0 | 8 | **0%** |
| **555 inbox** | 2 | 0 | 3 | **40%** |

**Critical path (blocks all funding):** T0-01..04 (entity + IP) · ANG-05 (film W1) · ANG-11 (W3 pilot)

**Disk-verified PASS (2026-07-01):** SRED-02..05 · ANG-06..09 · 555-01 bundle · 555-02 experiment log

---

## 0. Entity roles (do not blur in funding applications)

| Entity | Canada funding role | R&D claimant? | Commercial raise entity? | Customer-facing? |
|--------|---------------------|---------------|--------------------------|------------------|
| **SourceA** | Engine / control plane / validators | **Primary candidate** (spine R&D) | No (DD appendix only) | Dev/design partners only |
| **TrustField** | Regulated wedge · MSB/RWA evidence | Secondary (if commercial R&D there) | **Yes — angel/seed front door** | Yes — fintech/crypto pilots |
| **Noetfield** | FI Copilot governance wedge | Secondary (govern-before-execution) | Later — after TF signal | Yes — bank pilot lane |
| **FORGE** | Primary sellable SKU (T2) | Product R&D under SourceA license | Via holding later | Yes — founders/small teams |
| **WitnessBC** | GRC product proof (tertiary Canada) | No for Canada cold outreach | No | CISO/GRC buyers — not Canada lead |

**Intercompany firewall SSOT:** `investor/TRUSTFIELD_VC_TRUST_LEGAL_ANTI_MORTEM_v1.md` · entity correction docs in `os/commercial/`

---

## 1. Tier 0 — Table stakes (all entities)

| ID | Evidence item | SourceA | TrustField | Noetfield | FORGE | Disk path / artifact | Owner | Status |
|----|---------------|---------|------------|-----------|-------|----------------------|-------|--------|
| T0-01 | CCPC incorporation certificate | [ ] | [ ] | [ ] | [—] | Minute book / corp registry extract | COUNSEL | |
| T0-02 | Minute book + founder resolutions | [ ] | [ ] | [ ] | [—] | COUNSEL-held | COUNSEL | |
| T0-03 | Business bank (legal name only) | [ ] | [ ] | [ ] | [—] | Bank letter / void cheque redacted | Founder | |
| T0-04 | Founder → company IP assignment | [ ] | [ ] | [ ] | [—] | COUNSEL — day zero | COUNSEL | |
| T0-05 | Intercompany firewall doc | [x] | [~] | [~] | [—] | `investor/TRUSTFIELD_VC_TRUST_LEGAL_ANTI_MORTEM_v1.md` §3 | Founder | |
| T0-06 | NUANS / trademark search clear | [ ] | [ ] | [ ] | [—] | COUNSEL filing | COUNSEL | |
| T0-07 | Entity email domain live | [—] | [ ] | [ ] | [—] | @trustfield.ca · @noetfield.* | Ops | |
| T0-08 | GST/HST registration when threshold | [ ] | [ ] | [ ] | [—] | CRA account | COUNSEL | |
| T0-09 | Cap table clean (no entity blur) | [ ] | [ ] | [ ] | [—] | Cap table spreadsheet v___ | COUNSEL | |
| T0-10 | SourceA field-of-use license to TF/NF | [ ] | [ ] | [ ] | [—] | COUNSEL — limited delivery license | COUNSEL | |

**Fill-in:** TrustField incorporation verify live per `TRUSTFIELD_VC_TRUST_LEGAL_ANTI_MORTEM_v1.md` governance mission YAML — status: _______________

---

## 2. Tier 1 — SR&ED / grant records

### 2A. R&D project definitions

| Project ID | Project name | Lead entity | Technological uncertainty (one line) | Status |
|------------|--------------|-------------|--------------------------------------|--------|
| R&D-01 | Runtime agent enforcement kernel | SourceA | Policy cannot be bypassed between LLM output and disk write | [~] |
| R&D-02 | Receipt integrity + tamper detection | SourceA | Cryptographic/checksum chain survives adversarial edit | [~] |
| R&D-03 | Pre-run dispatch gate (eval-1b) | SourceA | Live model eval gates factory dispatch without false green | [ ] |
| R&D-04 | Regulated evidence export (Trust Brief) | TrustField | Examiner-replayable chain for FINTRAC-adjacent ops | [ ] |
| R&D-05 | Govern-before-execution (Copilot) | Noetfield | Block agent commit before policy check in FI workflow | [ ] |

### 2B. SR&ED contemporaneous evidence

| ID | Evidence type | Entity | Disk path / how to produce | Status |
|----|---------------|--------|----------------------------|--------|
| SRED-01 | Architecture diagram (enforcement loop) | SourceA | `brain-os/system/SOURCEA_FULL_LAYERED_CONTROL_PLAN_LOCKED_v1.md` + export diagram | [ ] |
| SRED-02 | Source code — commit gate | SourceA | `scripts/commit_intent_v1.py` | [x] |
| SRED-03 | Source code — demo enforcement | SourceA | `scripts/validate-demo-enforcement-v1.sh` · `scripts/demo-enforcement-5min-v1.sh` · `scripts/validate-enforcement-kernel-v1.sh` | [x] |
| SRED-04 | Experiment log (dated) | SourceA | `receipts/sred-experiment-log-2026/` — **555-02 DONE** | [x] |
| SRED-05 | Hypothesis register | SourceA | `receipts/sred-experiment-log-2026/HYPOTHESIS_REGISTER.md` | [x] |
| SRED-06 | Git commit history mapped to project IDs | SourceA | `git log --oneline scripts/commit_intent_v1.py scripts/validate-demo-enforcement-v1.sh` | [~] |
| SRED-07 | Eval-1b reports | SourceA | `eval_packet_v1b_report.json` — **absent logged 2026-07-01**; use structural mode + honest counter | [!] |
| SRED-08 | Timesheets (% R&D allocation) | All R&D entities | Payroll / timesheet export — _____% SourceA R&D | [ ] |
| SRED-09 | Meeting minutes (R&D decisions) | SourceA | Dated LOCKED docs in `brain-os/law/` | [~] |
| SRED-10 | Form T661 technical narrative draft | SourceA | Derive from `docs/IRAP_TECHNICAL_NARRATIVE_ENFORCEMENT_KERNEL_UNCERTAINTY_DRAFT_LOCKED_v1.md` | [~] |
| SRED-11 | Financial statements (2 years) | TrustField or R&D entity | Accountant export | [ ] |
| SRED-12 | T2 + T661 filed | R&D entity | Fiscal year end: _______________ | [ ] |

**SR&ED qualifying uncertainty (copy to T661):** See IRAP narrative doc §2 — same uncertainty spine.

---

## 3. Tier 1 — IRAP package

| ID | IRAP deliverable | Entity (apply via) | Disk path / action | Status |
|----|------------------|-------------------|-------------------|--------|
| IRAP-01 | CRA business number | _____________ | Corp records | [ ] |
| IRAP-02 | Business plan (10–15 pp) | _____________ | Draft from `investor/ONE_PAGER.md` + commercial SSOT | [ ] |
| IRAP-03 | ITA one-pager | _____________ | `docs/IRAP_TECHNICAL_NARRATIVE_ENFORCEMENT_KERNEL_UNCERTAINTY_DRAFT_LOCKED_v1.md` (exec summary) | [x] |
| IRAP-04 | Technical work plan + Gantt | SourceA | IRAP doc §5 milestones — not started pre-approval | [ ] |
| IRAP-05 | Budget line-by-line | _____________ | Roles: founder eng ___% · contractor ___% | [ ] |
| IRAP-06 | Team CVs | _____________ | Founder CV + technical profiles | [ ] |
| IRAP-07 | Co-funding proof | _____________ | Bank balance / runway statement | [ ] |
| IRAP-08 | Commercialization plan | TrustField | `os/commercial/CANADA_RWA_STRATEGY_DEEP_RESEARCH_UPGRADE_LOCKED_v2.md` | [x] |
| IRAP-09 | ITA intake call logged | _____________ | Date: _______________ ITA name: _______________ | [ ] |
| IRAP-10 | Portal submission | _____________ | iip-pip.nrc-cnrc.gc.ca — after ITA invite | [ ] |

**Counsel decision — IRAP applicant entity:** [ ] SourceA  [ ] TrustField  [ ] Other: _______________

**Rule:** No R&D work on IRAP-funded scope until written approval.

---

## 4. Tier 2 — Angel evidence

### 4A. Founder / institutional layer (Canada ICP)

| ID | Item | Entity | Disk path / action | Status |
|----|------|--------|-------------------|--------|
| ANG-01 | LinkedIn anchor video (20–40s) | Founder (institutional) | `~/.sina/avatar-pipeline-v1/master-image.jpg` · script: `data/avatar-scripts-v1.json` → linkedin_anchor_v1 | [ ] |
| ANG-02 | Master headshot | Founder | `skill-founder-identity-layers` — real preferred | [ ] |
| ANG-03 | Founder CV (2 pp) | Founder | PDF in data room `01 Entity/` | [ ] |
| ANG-04 | Category sentence frozen | All | *We make AI execution impossible to bypass governance.* | [x] |

### 4B. Technical proof (W1 / W2)

| ID | Item | Entity | Disk path / command | Status |
|----|------|--------|---------------------|--------|
| ANG-05 | W1 — 5-min demo filmed | SourceA | `scripts/demo-enforcement-5min-v1.sh` · `investor/ENFORCEMENT_DEMO_5MIN.md` | [ ] |
| ANG-06 | W2 — single write path | SourceA | `scripts/commit_intent_v1.py --demo-enforcement` | [x] |
| ANG-07 | Validator PASS artifact | SourceA | `receipts/investor-planning-proof-bundle-2026-07-01/` — **555-01 DONE** | [x] |
| ANG-08 | Tamper-FAIL on camera | SourceA | `bash scripts/validate-demo-enforcement-v1.sh --tamper-test` — **PASS verified** | [x] |
| ANG-09 | Latest receipt JSON (redacted) | SourceA | `~/.sina/demo-enforcement/receipts/latest-demo-receipt.json` — **555-03 packages for DD** | [~] |
| ANG-10 | 90s demo cut for email | SourceA | Film from W1 — path: _______________ | [ ] |

### 4C. Commercial proof (W3)

| ID | Item | Entity | Disk path / action | Status |
|----|------|--------|-------------------|--------|
| ANG-11 | W3 paid pilot or LOI | TrustField | Target: CAD $3–7.5K discovery · `os/commercial/CANADA_PRIORITY_A_SEND_READY_EMAILS_LOCKED_v1.md` | [ ] |
| ANG-12 | Signed NDA | TrustField | COUNSEL template — party: TrustField only | [ ] |
| ANG-13 | Signed MSA | TrustField | COUNSEL | [ ] |
| ANG-14 | Signed DPA (before data) | TrustField | COUNSEL — before client data | [ ] |
| ANG-15 | Signed SOW + invoice | TrustField | Invoice from TrustField bank only | [ ] |
| ANG-16 | Bank deposit proof | TrustField | Redacted statement in data room | [ ] |
| ANG-17 | CRM log (pipeline truth) | TrustField | No verbal "great meetings" — export dated | [ ] |
| ANG-18 | Priority A send log | TrustField | Ocree **APPROVED** · Fundmore **APPROVED** (NF-RD) — champion pending per `SOURCEA_ECOSYSTEM_FAST_BUSINESS_MODEL_LOCKED_v2.md` | [~] |

### 4D. Angel deck + data room

| ID | Item | Path | Status |
|----|------|------|--------|
| ANG-19 | 3-slide deck | `investor/ENFORCEMENT_3SLIDE_DECK_v1.md` | [x] |
| ANG-20 | Honest counter appendix | eval_1b_gate_ok false when 402 · dispatch_ready | [~] |
| ANG-21 | VC Trust Center v1 | `TRUSTFIELD_VC_TRUST_LEGAL_ANTI_MORTEM_v1.md` Part 5 | [ ] |
| ANG-22 | Use of funds (12–18 mo) | Spreadsheet v___ | [ ] |
| ANG-23 | BC EBC pre-approval (if BC angels) | eTCA authorization letter | [ ] |

---

## 5. Tier 3 — Seed VC evidence (Q4 2026+ target)

| ID | Item | Entity | Threshold | Status |
|----|------|--------|-----------|--------|
| SEED-01 | MRR or equivalent | TrustField | $25K–$50K MRR or 2+ paid pilots ≥$3K | [ ] |
| SEED-02 | Second design partner | TrustField or Noetfield | Named champion + LOI/SOW | [ ] |
| SEED-03 | 8–10 slide seed deck | TrustField | Extend `ENFORCEMENT_3SLIDE_DECK_v1.md` | [ ] |
| SEED-04 | Full data room (7 folders) | TrustField | Anti-mortem Part 5 structure | [ ] |
| SEED-05 | Reference customer (permission) | TrustField | Redacted case study | [ ] |
| SEED-06 | Security one-pager | SourceA + TF | E&O/cyber COI path | [ ] |
| SEED-07 | SR&ED/IRAP in flight | R&D entity | Receipt / claim confirmation | [ ] |
| SEED-08 | Lead VC in diligence | TrustField | Fund name: _______________ | [ ] |

---

## 6. Per-entity artifact map (disk SSOT)

### SourceA — engine / R&D spine

| Purpose | Path |
|---------|------|
| Investor win condition | `brain-os/law/enforcement/ENFORCEMENT_6MO_INVESTOR_WIN_LOCKED_v1.md` |
| Commit gate | `scripts/commit_intent_v1.py` |
| Demo validator | `scripts/validate-demo-enforcement-v1.sh` |
| W2 write-path validator | `scripts/validate-demo-write-path-v1.sh` |
| Kernel validator | `scripts/validate-enforcement-kernel-v1.sh` |
| 5-min demo script | `investor/ENFORCEMENT_DEMO_5MIN.md` · `scripts/demo-enforcement-5min-v1.sh` |
| Receipts (runtime) | `~/.sina/demo-enforcement/receipts/` |
| Fundraise strategy | `investor/AGENTIC_INFRA_FUNDRAISE_PORTFOLIO_STRATEGY_v1.md` |
| Positioning | `docs/research-vault/GOLDEN_REPORT_SOURCEA_SITE_POSITIONING_v1.md` |
| Eval gate | `eval_packet_v1b_report.json` (when live) |

**Do not on SourceA invoice:** TrustField commercial SOW · MSB claims

### TrustField — Canada commercial / raise entity

| Purpose | Path |
|---------|------|
| VC trust framework | `investor/TRUSTFIELD_VC_TRUST_LEGAL_ANTI_MORTEM_v1.md` |
| Canada strategy | `os/commercial/CANADA_RWA_STRATEGY_DEEP_RESEARCH_UPGRADE_LOCKED_v2.md` |
| Send-ready emails | `os/commercial/CANADA_PRIORITY_A_SEND_READY_EMAILS_LOCKED_v1.md` |
| Outreach motion | `investor/ENFORCEMENT_OUTREACH_v1.md` |
| 3-slide deck | `investor/ENFORCEMENT_3SLIDE_DECK_v1.md` |
| Business model | `os/commercial/SOURCEA_ECOSYSTEM_FAST_BUSINESS_MODEL_LOCKED_v2.md` |

**TrustField external sentence:**

> TrustField is the regulated commercial face of a provable governance engine — contracts, receipts, and relationships VCs can verify without founder storytelling.

### Noetfield — FI Copilot wedge (parallel, not Canada lead)

| Purpose | Path |
|---------|------|
| Canada NF block | `os/commercial/PORTFOLIO_SOURCEA_WITNESSBC_777_INSIGHT_PLAN_LOCKED_v1.md` |
| Bank pilot lane | Site: bank-pilot · copilot pages (verify live) |
| Separate invoice rule | Never single-brand invoice with TrustField |

### FORGE — primary SKU (post W1+W3)

| Purpose | Path |
|---------|------|
| Tier T2 sell | `docs/research-vault/GOLDEN_REPORT_SOURCEA_SITE_POSITIONING_v1.md` § FORGE |
| Fundraise timing | After enforcement proof — not lead for Canada grant |

---

## 7. Weekly ops template (copy each Monday)

```markdown
## Week of _____________

### Wins
- 

### Evidence status delta
- T0: ___/10 · SRED: ___/12 · IRAP: ___/10 · ANG: ___/23 · SEED: ___/8

### Blockers [!]
- 

### Next 3 moves (founder)
1. 
2. 
3. 

### Entity blur check
- [ ] No mixed invoice
- [ ] No MSB license claim
- [ ] No revenue without deposit
```

---

## 8. Hostile DD associate test

> For each Tier 2 item marked [x], can an associate open **one file or run one command** without calling you?

If no → item is not done.

**Commands that must PASS before angel meeting:**

```bash
bash scripts/validate-demo-enforcement-v1.sh
bash scripts/validate-demo-enforcement-v1.sh --tamper-test
bash scripts/validate-demo-write-path-v1.sh
bash scripts/validate-enforcement-kernel-v1.sh
python3 scripts/commit_intent_v1.py --demo-enforcement --case allow --json
```

---

## 9. Trading lane evidence rows (from alignment analysis)

| ID | Item | Entity | Status | Notes |
|----|------|--------|--------|-------|
| TRD-01 | TrustField = evidence layer positioning frozen | TrustField | [x] | Not trading bot |
| TRD-02 | Noetfield split from crypto outbound | Noetfield | [x] | Routing law logged |
| TRD-03 | Priority A Ocree send | TrustField | [~] | Approved · champion pending |
| TRD-04 | FINTRAC demo script filmed | TrustField | [ ] | 15-min live demo |
| TRD-05 | Prop trader lane explicitly declined | All | [x] | AKIVA owns open-source |

---

## 10. Cross-reference index (full database — 5 docs)

| Doc | Path |
|-----|------|
| Parent database | `docs/CANADA_ICP_GRANT_VC_EVIDENCE_Q3_2026_INVESTOR_PLANNING_DATABASE_LOCKED_v1.md` |
| Real market analysis | `docs/REAL_MARKET_ANALYSIS_JULY_2026_ENGLISH_INVESTOR_PLANNING_LOCKED_v1.md` |
| Trading lane analysis | `docs/TRADING_LANE_TRUSTFIELD_NOETFIELD_BOUNDED_AUTONOMY_MARKET_ALIGNMENT_ANAL_LOCKED_v1.md` |
| IRAP narrative | `docs/IRAP_TECHNICAL_NARRATIVE_ENFORCEMENT_KERNEL_UNCERTAINTY_DRAFT_LOCKED_v1.md` |
| Enforcement 6MO | `brain-os/law/enforcement/ENFORCEMENT_6MO_INVESTOR_WIN_LOCKED_v1.md` |
| VC anti-mortem | `investor/TRUSTFIELD_VC_TRUST_LEGAL_ANTI_MORTEM_v1.md` |
| 555 plans inbox | `docs/555_PLANS_NEXT_UPGRADES_INVESTOR_PLANNING_INBOX_LOCKED_v1.md` |
| SR&ED experiment log | `receipts/sred-experiment-log-2026/` |

---

*Locked fill-in-the-blank matrix v1.2. Update status columns weekly; bump `Saved:` UTC on structural edits.*

**Upgrade v1.2:** 555-02 SR&ED log done · readiness rollup refresh · queue_head 555-03.
