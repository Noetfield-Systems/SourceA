# ag-b-1893 — AgentGo SA4 case study plan (v3 polished)

**Version:** 3 · **Tier:** T3 · **Phase:** MOONSHOT · **Rank:** 1893
**Angle:** B · Angle B — Dual deploy
**Theme:** t10-revenue-crm · Revenue / CRM (SaaS ICP)
**Workstream:** w05-operate · Operate
**Slice:** 13/20 · **Receipt gate:** dual_deploy_pass
**SSOT:** `docs/AGENTGO_SA4_CASE_STUDY_6000_PLANS_LOCKED_v1.md`
**Inventory:** `data/agentgo-sa4-inventory-receipt-v1.json`

## Scope

Dual desktop deploy — agentrun-app :5180 + SA4 AgentGo :8080 · landing parity

## Task

**Document freeze window for** SaaS/marketing ICP CRM + outreach.

Factory FREEZE respect.

**Angle:** agency CTO who wants screen-share deploy proof on desktop
**Pure law:** Pure story: one green-unified spine · two desktop shells (cinematic + canonical).
**Anti-drift:** Never conflate localhost demo with production sourcea.app ship.
**Target path:** `scripts/sourcea_revenue_engine_crm_v1.py`
**Success metric:** outreach_sent logged
**Receipt:** note before `status: done`.
**Phase:** MOONSHOT · **Tier:** T3 · **Workstream:** Operate

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-sourcea-desktop-landing-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `ag-b-1893`
2. Evidence row in `brain-os/plan-registry/SOURCEA-PRIORITY.md` §AgentGo case study 6000
3. No cross-lane edits without EDIT ALLOWED
4. Keep AgentGo ≠ SourceA separation in all buyer-facing copy (angle C law)

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: polish_agentgo_case_study_v3.py v3
angle: cs-b-dual
smart: pure-unique-smart-polished
