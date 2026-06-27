# sa-score2-0239 — Automate downloadable security one-pager PDF from /trust

**Saved at:** 2026-06-25T09:28:52Z
**Batch:** 2 · **Grade:** A · **Tier:** T3 · **Phase:** LATER
**Score dimension:** Enterprise buyer readiness (48→93)
**Market analog:** Vanta / SafeBase
**Workstream:** w14-automate · Automate
**Slice:** 9/10
**SSOT:** `docs/SOURCEA_SITE_SCORE_UP_1000_BATCH2_LOCKED_v1.md`
**Prerequisite:** batch-1 pack or equivalent shipped slices

## North star

Batch-2 raises site score **78 → 93+** — enterprise-credible · cryptographically verifiable · conversion-measured.

## Task

Grade-A P3 — research ·  intel · defer

**Deliverable:** Automate downloadable security one-pager PDF from /trust

## Anti-duplication

Must NOT repeat any `sa-score-*` batch-1 title. This plan is batch-2 only.

## Verify

```bash
cd ~/Desktop/SourceA && bash scripts/validate-sourcea-site-score-up-1000-batch2-v1.sh
bash scripts/validate-sourcea-modern-stack-e2e-v1.sh
```

## Closeout

1. `status: done` in batch-2 REGISTRY.json
2. Set `score_delta` (expected +0.1 to +0.5 site-wide)
3. Live proof URL in closeout note

---
agent_tag: AGENT-AUTO-SOURCEA-SITE-B2
trigger: WORK sa-score2 bounded batch-2
generator: generate_sourcea_site_score_up_1000_plans_batch2_v1.py v2
