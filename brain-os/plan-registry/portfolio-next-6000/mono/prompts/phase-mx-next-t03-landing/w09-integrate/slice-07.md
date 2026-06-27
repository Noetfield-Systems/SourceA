# mx-next-0287 — SinaaiMonoRepo next plan

**Version:** 1 · **Tier:** T2 · **Phase:** LATER
**Theme:** t03-landing · Landing & web
**Workstream:** w09-integrate · Integrate
**Slice:** 7/10 · **Receipt gate:** none
**SSOT:** `docs/PORTFOLIO_NEXT_6000_PLANS_LOCKED_v1.md`

## Scope

Mono portfolio spine — cross-lane receipts only

## Task

SinaaiMonoRepo · Landing & web · Integrate · slice 7/10 — P2 — harden · validate · document. Bounded path only. Receipt on disk before done. Parent: Mono portfolio spine — cross-lane receipts only. Priority doc: `os/plan-library/mono-1000/REGISTRY.json`.

## Verify

```bash
test -f ~/Desktop/Noetfield/SinaaiMonoRepo/os/plan-library/mono-1000/REGISTRY.json
```

## Closeout

1. `status: done` in REGISTRY.json for `mx-next-0287`
2. Evidence row in `os/plan-library/mono-1000/REGISTRY.json`
3. No cross-lane edits without EDIT ALLOWED

---
agent_tag: AGENT-AUTO-MONO
trigger: PLAN WITH NO ASF
generator: generate_portfolio_next_6000_plans_v1.py v1
