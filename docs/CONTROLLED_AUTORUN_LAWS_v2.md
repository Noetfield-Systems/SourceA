# Controlled Autorun Laws v2

**Schema:** `controlled-autorun-laws-v2`  
**Saved at (UTC):** 2026-07-02T12:00:00Z  
**Owner:** SourceA Loop Specialist (standing assignment)  
**Skill SSOT:** controlled-autorun v2 (Cursor skill)  
**Scope:** CF cron worker · Railway FBE motor · queue batches · cycle receipts · sink invariants · heartbeats · external verification · Kaizen improvement backlog

Operating system for continuous, parallel, self-improving multi-sandbox execution. Every law traces to a real production incident. v2 adds the ROI layer: the machine governs its own spend the way it governs its own state.

## L1 — One reconciler

One control authority per sandbox. New supervisors/registries extend `scripts/phase_reconciler_v1.py` or emit desired-state artifacts it consumes. Independent run/lock/state authority = rejected. Every consolidation report carries `reconciler authority: ONE / DUPLICATE`.

## L2 — IDLE_NO_WORK is healthy

Empty queue → `IDLE_NO_WORK` receipt. Never manufactured work, never fake PASS, never silence. States: `RUNNING` · `IDLE_NO_WORK` · `BLOCKED_WITH_REASON` · `COMPLETE` · `FAILED_WITH_RECEIPT` · `TRIAGE_REQUIRED` · `THROTTLED_ROI`.

## L3 — No decision without a reason

Every gate emission = `{decision, reason, evidence: command + output}`. Bare NO/BLOCKED is malformed. Summaries derive from actual row IDs; producer output validated against reality post-write, fail closed.

## L4 — Verify from outside

PASS is valid only from a probe the building agent does not control: external runner (`.github/workflows/external-verify.yml`), raw public hostname, redirects OFF, content markers + FULL-body hash, ≥60s after deploy. Local dist, same-machine curls, preview URLs = INVALID. Verify-time minus publish-time < 60s = auto-reject.

## L5 — Verifier freeze

Verifiers and pass criteria are founder-gated. A failing agent fixes the system, never the test. Weakening a failing check = immutability violation = BLOCKED until founder approves the diff.

## L6 — Commit before deploy

Deploys run from a clean committed SHA. Dirty guard fails closed; scoped exceptions only via founder-reviewed `dirty_scope_map`. Receipts live in repo under `receipts/cloud/`, not home directories only.

## L7 — Founder items never block, never vanish

Status `founder_blocked` (never `cancelled`), excluded from machine scan, present in every cycle receipt with count/oldest/priority/age. Aging founder P0s escalate in heartbeat after age threshold.

## L8 — Sinks are acked or blocked

Advance never decouples from sink ack. Invariant per cycle: `Σ(origin counts) == sink_count`, provenance-tagged per row. Mismatch → `BLOCKED_WITH_REASON`.

## L9 — Fail-closed refill

Expansion admits only rows passing the current rubric unmodified. 0 admitted is valid and reportable.

## L10 — Cross-sandbox reads via shared sink only

No sandbox reads another's disk/repo. Status flows through Supabase. Rows older than freshness window → `STALE_DATA`, never guessed.

## L11 — Every cycle has a cost; every loop earns its keep

Each cycle receipt carries `cost` (provider, model, tokens in/out, unit cost, $ total) and `value_class` (`revenue_path` · `proof_asset` · `risk_reduction` · `hygiene` · `none`). Loops report rolling cost-per-COMPLETE and spend-by-value_class in heartbeat. >30% trailing-window spend on `none` → `THROTTLED_ROI` (frequency cut, founder notified).

## L12 — Drift is detected, not discovered

Each heartbeat compares deployed truth to committed truth: live config hash vs repo hash, Railway deploy SHA vs `git rev-parse HEAD`, wrangler worker name vs `CF_VERSION_METADATA`, cron last-fire vs `*/10` schedule. Any mismatch → drift receipt with diff.

## Parallel orchestration (Tier 1+ — founder trigger required)

Lanes · concurrency keys · lock ordering · priority within tick · jitter · backpressure. **BLOCKED** until founder triggers Tier 1.

## Cycle anatomy (per tick)

1. Lock (per-sandbox)
2. Select one eligible item or `IDLE_NO_WORK`
3. Execute inside sandbox scope
4. Meter — capture tokens/cost at call site (L11)
5. Verify — internal checks may gate advance; only external proves ship (L4)
6. Ack sink (L8)
7. Receipt — `autonomous-forge-run-cycle-receipt-v2`
8. Heartbeat (daily): loops, states, sink invariants, cost table, drift (L12), founder_blocked escalations

## Kaizen — ROI-ranked self-improvement

Failed checks, DRIFT, `THROTTLED_ROI`, audit findings auto-file improvement candidates. `machine_safe` vs `founder_gated`. One highest-ROI `machine_safe` item per cycle. `founder_gated` → weekly digest in heartbeat.

## Standing duties (each session)

1. Read latest heartbeat + last 3 cycle receipts. Report: loops, states, sink invariant, drift, cost window (5 lines).
2. Surface `founder_blocked` (count, oldest, age). Never process or cancel.
3. If `BLOCKED_WITH_REASON` exists: fix or escalate before new work.

## Work rules

- One improvement per cycle, highest expected ROI, `machine_safe` only.
- Reports: SHAs, receipt paths, counts before/after, cost table, dirty state, gate receipts `{decision, reason, evidence}`.
- No narrative claims without command + output.

## Wired artifacts

| Artifact | Path |
|----------|------|
| Cloud runtime SSOT | `data/cloud-auto-runtime-v1.json` |
| Phase reconciler | `scripts/phase_reconciler_v1.py` |
| Autorun verifier | `scripts/verify_autorun_zero_manual_v1.py` |
| External verify Action | `.github/workflows/external-verify.yml` |
| CF cron worker | `cloud/workers/cloud-auto-runtime-tick-v1/` |
| Cycle receipts (repo) | `receipts/cloud/autonomous-forge-run-cycles/` |
| Heartbeat (repo) | `receipts/cloud/autonomous-forge-run-heartbeat/` |
| Loop specialist | `scripts/loop_specialist_tick_v1.py` |
| Observer API | Railway `/api/cloud-forge-run/observer/v1` |

## Out of scope

Sales copy · LinkedIn · product pages · NOOS repo · founder decisions.
