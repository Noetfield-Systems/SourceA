# ag-b-1203 — AgentGo SA4 case study plan (v3 polished)

**Version:** 3 · **Tier:** T1 · **Phase:** MOONSHOT · **Rank:** 1203
**Angle:** B · Angle B — Dual deploy
**Theme:** t07-compare-pages · Compare / competitor pages
**Workstream:** w01-ship · Ship
**Slice:** 3/20 · **Receipt gate:** landing_ship
**SSOT:** `docs/AGENTGO_SA4_CASE_STUDY_6000_PLANS_LOCKED_v1.md`
**Inventory:** `data/agentgo-sa4-inventory-receipt-v1.json`

## Scope

Dual desktop deploy — agentrun-app :5180 + SA4 AgentGo :8080 · landing parity

## Task

**Add page to commercial + depth gates for** GEO competitor compare matrix (Peec · Profound · Otterly adjacency).

Update landing-commercial-copy-audience + copy-depth JSON.

**Angle:** agency CTO who wants screen-share deploy proof on desktop
**Pure law:** Pure story: one green-unified spine · two desktop shells (cinematic + canonical).
**Anti-drift:** Never conflate localhost demo with production sourcea.app ship.
**Target path:** `~/Desktop/SA4/compare`
**Success metric:** compare URL completeness
**Receipt:** validate-landing-commercial-copy PASS before `status: done`.
**Phase:** MOONSHOT · **Tier:** T1 · **Workstream:** Ship

## Verify

```bash
bash ~/Desktop/SourceA/scripts/validate-sourcea-desktop-landing-v1.sh
```

## Closeout

1. `status: done` in REGISTRY.json for `ag-b-1203`
2. Evidence row in `brain-os/plan-registry/SOURCEA-PRIORITY.md` §AgentGo case study 6000
3. No cross-lane edits without EDIT ALLOWED
4. Keep AgentGo ≠ SourceA separation in all buyer-facing copy (angle C law)

---
agent_tag: AGENT-AUTO-SOURCEA
trigger: PLAN WITH NO ASF
generator: polish_agentgo_case_study_v3.py v3
angle: cs-b-dual
smart: pure-unique-smart-polished
