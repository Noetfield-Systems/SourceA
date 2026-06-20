# ENFORCEMENT-1000 — Category index (audited)

**Audited:** 2026-06-11T23:25:25Z
**Unique titles:** 1000 / 1000
**Done:** 29 · **Backlog:** 971

## Win buckets

| Category | Count | Owner | Win | Months |
|----------|-------|-------|-----|--------|
| `CHAOS_HARDEN` | 100 | worker | CHAOS_HARDEN | 2026-08 |
| `CLOSEOUT` | 100 | brain | CLOSEOUT | 2026-12 |
| `NARRATIVE` | 100 | commercial | NARRATIVE | 2026-09 |
| `W1_DEMO` | 100 | worker | W1 | 2026-07 |
| `W2_KERNEL` | 400 | worker | W2 | 2026-06, 2026-07, 2026-10 |
| `W3_MONEY` | 200 | commercial | W3 | 2026-06, 2026-08 |

## Tier depth (all 1000)

| Tier | Count | Role |
|------|-------|------|
| `T0` | 250 | Ship — demo blocker |
| `T1` | 250 | CI + evidence |
| `T2` | 250 | Chaos / stress |
| `T3` | 250 | Polish or DELETE |

## Phase map

| Phase | IDs | Category |
|-------|-----|----------|
| `phase-e0-commit-gate` | enf-0001…enf-0100 | W2_KERNEL |
| `phase-e1-receipt-integrity` | enf-0101…enf-0200 | W2_KERNEL |
| `phase-e2-validator-tamper` | enf-0201…enf-0300 | W2_KERNEL |
| `phase-e3-demo-live` | enf-0301…enf-0400 | W1_DEMO |
| `phase-e4-commercial-w3` | enf-0401…enf-0500 | W3_MONEY |
| `phase-e5-bypass-chaos` | enf-0501…enf-0600 | CHAOS_HARDEN |
| `phase-e6-investor-pipeline` | enf-0601…enf-0700 | NARRATIVE |
| `phase-e7-regulated-wedge` | enf-0701…enf-0800 | W3_MONEY |
| `phase-e8-kernel-harden` | enf-0801…enf-0900 | W2_KERNEL |
| `phase-e9-dec-closeout` | enf-0901…enf-1000 | CLOSEOUT |

## Disk validators

- validate-demo-enforcement: **PASS**
- tamper test: **PASS**
- universe invariants: **PASS**

## Pick next

```bash
python3 scripts/pick-enforcement-no-asf-plan.py --any-tier --limit 3 --prompt
```

Regenerate: `python3 scripts/generate-enforcement-1000-prompts.py`
Re-audit: `python3 scripts/audit-enforcement-1000-v1.py`
