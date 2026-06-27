# AgentGo / SA4 case study — 6000 plans (LOCKED v1)

**Saved at:** 2026-06-24T21:00:00Z · **v3 polished:** 2026-06-24T14:47:59Z  
**Machine:** `scripts/generate_agentgo_case_study_6000_plans_v1.py` · **Polish:** `scripts/polish_agentgo_case_study_v3.py`  
**Master:** `brain-os/plan-registry/AGENTGO_CASE_STUDY_6000_MASTER_v1.json`  
**Parent:** PureFlow case study #1 · SA4 desktop (`~/Desktop/SA4` → `~/Desktop/YA5/SA4`)

---

## One law

> **6000 case-study plans = 3 angles × 2000 plans each. Ship case study pages on sourcea.app before draining moonshot GEO polish.**

---

## Three angles (all implemented)

| Angle | ID | Prefix | Count | Story |
|-------|-----|--------|-------|-------|
| **A — Factory scale** | `cs-a-factory` | `ag-a-` | 2000 | 1,259-page GEO surface · trackers · research · compare |
| **B — Dual deploy** | `cs-b-dual` | `ag-b-` | 2000 | Agent Run :5180 + SA4 AgentGo :8080 · desktop landing parity |
| **C — Wil L3 demo** | `cs-c-wil` | `ag-c-` | 2000 | YA5 portfolio mirror · AgentGo ≠ SourceA separation law |

**Total:** 6000

---

## Grid (per angle)

| Dimension | Count |
|-----------|-------|
| Themes | 10 |
| Workstreams | 10 |
| Slices | 20 |
| **Per angle** | **2000** |

---

## Themes (all angles)

1. Case study narrative copy  
2. Landing ship (sourcea.app)  
3. Proof & receipts  
4. SA4 / AgentGo source tree  
5. GEO tracker surfaces  
6. Research / guides hub  
7. Compare /  pages  
8. Dual deploy wiring  
9. Wil ship gate & separation  
10. Revenue / CRM (SaaS buyer ICP)  

---

## Workstreams

Ship · Prove · Sell · Build · Operate · Govern · Document · Validate · Integrate · Scale

---

## Phase law (ranks 1–2000 per angle)

| Phase | Ranks | Focus |
|-------|-------|-------|
| **NOW** | 1–30 | Case study HTML · gates · first public proof |
| **NEXT** | 31–120 | Demo subset · CRM · outreach templates |
| **LATER** | 121–400 | Full SA4 subset ship · harden validators |
| **MOONSHOT** | 401–2000 | Scale · enterprise GEO · full 1259-page mirror |

---

## Pick law

1. Revenue Engine + T1 client (Planning Card A) still win over case-study drain  
2. Angle order default: **A → B → C** phase-first within each pack  
3. PureFlow remains case study #1 — AgentGo is **#2** (factory scale narrative)

```bash
bash scripts/plan-no-asf-run.sh pick-agentgo 3
python3 scripts/pick_agentgo_case_study_plan_v1.py --angle cs-a-factory --any-phase --limit 3 --prompt
```

---

## Generate

```bash
cd ~/Desktop/SourceA
python3 scripts/generate_agentgo_case_study_6000_plans_v1.py
bash scripts/validate-agentgo-case-study-6000-v1.sh
```

---

## Key disk paths

| Artifact | Path |
|----------|------|
| SA4 desktop | `~/Desktop/SA4` → `~/Desktop/YA5/SA4` |
| PureFlow case study | `SourceA-landing/green-unified/case-studies/pureflow.html` |
| AgentGo case study (shipped) | `SourceA-landing/green-unified/case-studies/agentgo.html` |
| Dual deploy script | `scripts/deploy_sourcea_desktop_landing_v1.py` |
| Wil terminology | `~/Desktop/YA5/.cursor/governance/TERMINOLOGY_2026.md` |
| Smart lexicon v2 | `scripts/lib/agentgo_smart_tasks_v2.py` |
| Polish wisdom v3 | `scripts/lib/agentgo_polish_wisdom_v3.py` |
| SA4 inventory receipt | `data/agentgo-sa4-inventory-receipt-v1.json` |
| Founder receipt | `~/.sina/agentgo-case-study-receipt-v1.json` |

---

## v2 smart upgrade

```bash
python3 scripts/upgrade_agentgo_case_study_6000_smart_v2.py
bash scripts/validate-agentgo-case-study-6000-v1.sh
```

**6000 unique titles** · pure law per angle · anti-drift guards · no generic slice filler.

---

## v3 polish (thoughtful details)

```bash
python3 scripts/polish_agentgo_case_study_v3.py
bash scripts/validate-agentgo-case-study-6000-v1.sh
```

- **schema_version 3** · `smart_tier: pure-unique-smart-polished`
- **Inventory receipt** — live SA4 counts (1,259 HTML · 592 research · 83 compare · 23 trackers)
- **Polish wisdom** — ranks 1–30 per angle appended to prompts
- **Bootstrap `done`** — shipped landing/copy/inventory rows (36 bootstrapped on first v3 run)
- **Case study page** — disk-accurate metrics · ICP section · build chain · PureFlow parity footer

---

*AgentGo SA4 case study 6000 v3 polished · June 2026*
