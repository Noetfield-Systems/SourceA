# Portfolio — 6000 next plans (LOCKED v1)

**Saved at:** 2026-06-24T19:00:00Z  
**Machine:** `scripts/generate_portfolio_next_6000_plans_v1.py`  
**Master registry:** `brain-os/plan-registry/PORTFOLIO_NEXT_6000_MASTER_v1.json`  
**Manifest:** `data/portfolio-next-6000-manifest-v1.json`

---

## One law

> **6000 next plans = 6 portfolio repos × 1000 plans each. Revenue and proof NOW rows win over moonshot polish.**

---

## Grid

| Dimension | Count |
|-----------|-------|
| Repos | 6 |
| Plans per repo | 1000 |
| **Total** | **6000** |
| Per-repo grid | 10 themes × 10 workstreams × 10 slices |

---

## Repos

| # | Repo | Prefix | Pack path |
|---|------|--------|-----------|
| 1 | **SourceA** | `sa-next-` | `brain-os/plan-registry/portfolio-next-6000/sourcea/` |
| 2 | **WitnessBC** | `wb-next-` | `brain-os/plan-registry/portfolio-next-6000/witnessbc/` |
| 3 | **Noetfield** | `nf-next-` | `brain-os/plan-registry/portfolio-next-6000/noetfield/` |
| 4 | **TrustField** | `tf-next-` | `brain-os/plan-registry/portfolio-next-6000/trustfield/` |
| 5 | **VIRLUX** | `vx-next-` | `brain-os/plan-registry/portfolio-next-6000/virlux/` |
| 6 | **SinaaiMonoRepo** | `mx-next-` | `brain-os/plan-registry/portfolio-next-6000/mono/` |

Physical packs live under **SourceA `brain-os/`** (machine truth). External repo paths are recorded in each `REGISTRY.json` as `external_repo`.

---

## Themes (all repos)

1. Revenue & outreach  
2. Proof & receipts  
3. Landing & web  
4. Factory runtime  
5. Noetfield Intelligence 613  
6. MSB & compliance  
7. Civic proof lab  
8. Agentic SaaS  
9. Hub & control plane  
10. Cloud & integrate  

---

## Workstreams (all repos)

Ship · Prove · Sell · Build · Operate · Govern · Document · Validate · Integrate · Scale

---

## Phase law (per repo ranks 1–1000)

| Phase | Ranks | Focus |
|-------|-------|-------|
| **NOW** | 1–30 | Revenue Engine · T1 client · proof ship |
| **NEXT** | 31–120 | Landing · CRM · 613 diagnostics |
| **LATER** | 121–400 | Runtime hardening · vertical MVPs |
| **MOONSHOT** | 401–1000 | Scale · enterprise · moonshot |

---

## Anchors (NOW rows biased)

| Anchor | Repo | Theme |
|--------|------|-------|
| Revenue Engine v1 | SourceA | t01-revenue |
| PureFlow case study + offer | SourceA | t03-landing |
| Runtime hybrid spike | SourceA | t04-runtime |
| Noetfield 613 | Noetfield | t05-intelligence |
| Planning Authority Card A/B/C | SourceA | t02-proof |
| AgentGo SA4 case study (3 angles) | SourceA | sibling pack `agentgo-case-study-6000` |

**Sibling pack (not in 6000 grid):** `docs/AGENTGO_SA4_CASE_STUDY_6000_PLANS_LOCKED_v1.md` — 6000 plans for case study #2 (A factory · B dual · C Wil).

---

## Generate

```bash
cd ~/Desktop/SourceA
python3 scripts/generate_portfolio_next_6000_plans_v1.py
bash scripts/validate-portfolio-next-6000-v1.sh
```

---

## Pick law

**Dual-pick still wins:** `SOURCEA-PRIORITY.md` queue_sa · Revenue Engine open items · then `sa-next-0001`… head for SourceA Worker.

Do **not** run 6000 validators on Mac founder session.

---

## Supersession (UP-888 → 6000 canonical)

**Authority:** `docs/PORTFOLIO_UPGRADE_PLANS_CANONICAL_LOCKED_v1.md`  
**Mapping:** `data/upgrade-888-to-sa-next-mapping-v1.json` · merger `scripts/merge_upgrade_888_into_portfolio_next_v1.py`

| Legacy | Canonical field |
|--------|-----------------|
| `UP-0001`…`UP-0888` | `legacy_upgrade_id` on `sa-next-0001`…`0888` |

UP-888 registry is **superseded** — lineage at `brain-os/ssot/superseded/SOURCEA_UPGRADE_PLANS_888_REGISTRY_v1.json`.

**Validate canonical merge:** `bash scripts/validate-portfolio-upgrade-canonical-v1.sh`

---

*Portfolio next 6000 v1 · June 2026*
