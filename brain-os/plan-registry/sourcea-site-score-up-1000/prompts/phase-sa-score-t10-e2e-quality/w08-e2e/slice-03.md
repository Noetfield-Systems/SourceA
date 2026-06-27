# sa-score-0973 — E2E gate for score-up registry validate script PASS

**Saved at:** 2026-06-25T09:23:55Z
**Version:** 1 · **Tier:** T1 · **Phase:** MOONSHOT
**Score dimension:** E2E & quality gates (88→100)
**Market analog:** Playwright
**Workstream:** w08-e2e · E2E
**Slice:** 3/10
**SSOT:** `docs/SOURCEA_SITE_SCORE_UP_1000_PLANS_LOCKED_v1.md`

## North star

Raise SourceA site score toward **95+/100** — proof before call · stranger self-serve · deterministic routing.

## Task

P1 — next sprint; measurable score delta

**Deliverable:** E2E gate for score-up registry validate script PASS

Bounded paths: `SourceA-landing/green-unified/` · `cloud/workers/sourcea-site-pulse-v1/` · `scripts/validate-sourcea-modern-stack-e2e-v1.sh`

## Verify

```bash
cd ~/Desktop/SourceA && bash scripts/validate-sourcea-modern-stack-e2e-v1.sh
curl -sS https://sourcea.app/sourcea/data/sourcea-landing-cta-v1.json | python3 -m json.tool
```

## Closeout

1. `status: done` in `brain-os/plan-registry/sourcea-site-score-up-1000/REGISTRY.json` for `sa-score-0973`
2. Note score delta in plan row `score_delta`
3. Deploy proof: live URL or receipt path in commit message

---
agent_tag: AGENT-AUTO-SOURCEA-SITE
trigger: WORK sa-score bounded site score-up
generator: generate_sourcea_site_score_up_1000_plans_v1.py v1
