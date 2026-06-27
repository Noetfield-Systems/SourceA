# ag-b-0394 — AgentGo SA4 case study plan (v3 polished)

**Version:** 3 · **Tier:** T3 · **Phase:** LATER · **Rank:** 394
**Angle:** B · Angle B — Dual deploy
**Theme:** t02-landing-ship · Landing ship (sourcea.app)
**Workstream:** w10-scale · Scale
**Slice:** 14/20 · **Receipt gate:** dual_deploy_pass
**SSOT:** `docs/AGENTGO_SA4_CASE_STUDY_6000_PLANS_LOCKED_v1.md`
**Inventory:** `data/agentgo-sa4-inventory-receipt-v1.json`

## Scope

Dual desktop deploy — agentrun-app :5180 + SA4 AgentGo :8080 · landing parity

## Task

**Team handoff for** sourcea.app case study route + gates.

Worker INBOX.

**Angle:** agency CTO who wants screen-share deploy proof on desktop
**Pure law:** Pure story: one green-unified spine · two desktop shells (cinematic + canonical).
**Anti-drift:** Never conflate localhost demo with production sourcea.app ship.
**Target path:** `SourceA-landing/green-unified/case-studies/agentgo.html`
**Success metric:** commercial + depth gate PASS
**Receipt:** inbox before `status: done`.
**Phase:** LATER · **Tier:** T3 · **Workstream:** Scale

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-sourcea-desktop-landing-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `ag-b-0394`
2. Evidence row in `brain-os/plan-registry/SOURCEA-PRIORITY.md` §AgentGo case study 6000
3. No cross-lane edits without EDIT ALLOWED
4. Keep AgentGo ≠ SourceA separation in all buyer-facing copy (angle C law)

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: polish_agentgo_case_study_v3.py v3
angle: cs-b-dual
smart: pure-unique-smart-polished
