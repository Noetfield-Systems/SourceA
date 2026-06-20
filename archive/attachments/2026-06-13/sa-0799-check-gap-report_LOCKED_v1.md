# sa-0799 CHECK — Harden essay mark-best POST without ASF as sole actor

**Saved:** 2026-06-13T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-13T21:20Z · **Turn:** CHECK · **Worker:** SourceA  
**Prior:** `archive/attachments/2026-06-11/sa-0799-mark-best-post-without-asf-sole-actor-crosswalk_LOCKED_v1.md` (ACT doc — gaps still open)

## Task (read-only)

Cross-check `POST /api/essay-discourse` `action: mark_best` vs locked law — identify gaps for hardening **without** making ASF the machine verify/progress authority.

## Live disk (CHECK 2026-06-13)

| Signal | Value |
|--------|-------|
| Essays logged | **9** (`~/.sina/essay-discourse/essays.jsonl`) |
| Active subject | `governance-drift-detection` |
| `best-by-subject.json` | **absent** — no best marked yet |
| Fleet nudges | **0** · scoreboard **8/8** verified |
| `mark_best_essay()` | No `actor` / auth param — writes best map + `essay_best_marked` event |

## Authority (unchanged)

| Layer | Truth |
|-------|-------|
| `AGENT_ESSAY_DISCOURSE_LOCKED_v1.md` §0 | ASF marks best **qualitatively** (founder click) |
| Fleet verify | `auto_pass` + governance-fleet — **not** mark_best |
| sa-0799 intent | Add **machine guardrails + co-actors** on POST — **not** replace broker VERIFY |

## Gaps vs task (ACT scope)

| ID | Gap | Severity | ACT fix line |
|----|-----|----------|--------------|
| **GAP-1** | No actor auth — any `:13020` localhost POST can set best | **high** | Require `actor` + `founder_attestation` or hub session token in handler |
| **GAP-2** | `audit_backend_e2e.py` — no essay-discourse / mark_best probe | medium | Optional E2E sub-step |
| **GAP-3** | No `validate-essay-mark-best-v1.sh` | medium | Round-trip POST + schema check on best file |
| **GAP-4** | Law §0 ASF-only wording — no documented co-actor clause | low | Law addendum (Maintainer) |
| **GAP-5** | 9 essays / 8 agents — possible duplicate row | low | Hygiene (sa-0791 OPEN-3) |

## Recommended ACT minimal diff (Worker scripts only — no hub panel edit)

**Line A+E** from prior crosswalk:

1. `agent_essay_discourse.py` — `mark_best_essay(..., actor=, attestation=)` fail-closed without `founder` or `maintainer` + receipt
2. `scripts/validate-essay-mark-best-v1.sh` — handler import test + optional live POST when hub up
3. Attachment refresh + RECEIPT — **no** scoreboard verify wiring

**Out of scope:** mark_best as REGISTRY done · `eval_1b_gate_ok` · hub `app.js` edits (Maintainer repair lane)

## Preflight validators (CHECK)

| Validator | Result |
|-----------|--------|
| `validate-governance-fleet-v1.sh` | PASS |
| `validate-dispatch-policy-v1.sh` | PASS |
| `validate-incident-028-fast-v1.sh` | PASS |

## Verdict

**CHECK complete** — gaps confirmed; prior ACT doc still accurate; **ready for ACT** (scripts hardening). **STOP** — no implement · no closeout.

*End sa-0799 CHECK*
