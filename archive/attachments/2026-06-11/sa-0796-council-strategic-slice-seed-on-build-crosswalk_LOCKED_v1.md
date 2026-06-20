# sa-0796 ACT — Council strategic slice seed on build crosswalk

**Saved:** 2026-06-11T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Worker:** SourceA · T3 research spike · **no code diff** (CHECK + validators green)

## Task scope

Document that **`seed_council_strategic_slice_v1.run_seed()`** runs on every **full panel build** via `_run_council_strategic_slice_seed`, is **idempotent** (marker skip), and leaves council + founder disk artifacts for the strategic-slice WTM thread.

## Authority order

| Layer | Source | Role |
|-------|--------|------|
| Build hook | `scripts/build-sina-command-panel.py` `_run_council_strategic_slice_seed` (sa-0218) | Called after L0/Eval seed + `_sync_command_data_eval`; strict build fails on seed/marker error |
| Seed module | `scripts/seed_council_strategic_slice_v1.py` | Idempotent seed: directive · mind share · topic · track cards · marker |
| Brief law | `COUNCIL_BRIEF_STRATEGIC_SLICE_EVAL_L0_ENFORCE_LOCKED_v1.md` | Council brief referenced by all seed rows |
| CI proof | `scripts/validate-phase-s2-hub-build-ci-v1.sh` sa-0243 | Asserts `_run_council_strategic_slice_seed` in BUILD text |
| Hub refresh | `scripts/hub_self_refresh_v1.py` | **Does not** re-run seed — only `align_command_data_ui_v1` (OPEN-1) |
| Prior closeout | **sa-0771** (T2) | Same task title; receipt `receipts/sa-0771-receipt.json` |

## Build chain (machine contract)

```
build-sina-command-panel.py (strict)
  → … post-build L0/Eval seed …
  → _sync_command_data_eval(payload)
  → _run_council_strategic_slice_seed(strict)
       → run_seed()           # skip if marker + brief_doc match
       → verify_seed_marker() # schema + brief_doc proof
  → (strict) eval-packet validators …
```

**Strict behavior:** seed failure or marker mismatch → `SystemExit(1)` (build red).  
**Non-strict:** WARN + continue (seed returns 0 on soft fail).

## Seed outputs (idempotent targets)

| Artifact | Path | Content |
|----------|------|---------|
| Seed marker | `~/.sina/council-room/strategic-slice-v1.seed.json` | `schema: strategic-slice-seed-v1` · `brief_doc` · `results` |
| Council brief | `COUNCIL_BRIEF_STRATEGIC_SLICE_EVAL_L0_ENFORCE_LOCKED_v1.md` | Eval-1 + L0/L1 + ENFORCE map (not new D-module) |
| Founder directive | `~/.sina/founder-directives.jsonl` | STRATEGIC SLICE verdict row (skip if brief_doc in text) |
| Mind share | `~/.sina/council-room/mind-share.jsonl` | `STRATEGIC-SLICE-EVAL-L0-ENFORCE-v1` procedure row |
| Council topic | `~/.sina/council-room/topics.jsonl` | "Strategic slice: Eval-1 + L0/L1 + ENFORCE map …" |
| Track cards | `~/.sina/founder-commitments.json` | 3 pinned: `track-strategic-slice-v1`, `track-trustfield-slice-v1`, `track-wire-slice-v1` |

## Live disk proof (ACT)

| Check | Result |
|-------|--------|
| Marker logged | **YES** · `at: 2026-06-06T01:15:24Z` |
| `run_seed()` re-run | **skipped** · `ok: true` |
| `verify_seed_marker()` | **PASS** · `ok` |
| Strategic-slice topic | **1** row in `topics.jsonl` |
| Pinned track cards | **3** in `founder-commitments.json` |
| Brief doc logged | **YES** at SourceA root |

## Hub P0 alignment

Command center P0 thread **STRATEGIC-SLICE** (`command-data*.json`) titles execution spine — WTM strategic slice — consistent with seeded track card `track-strategic-slice-v1` and council brief.

## OPEN (informational — maintainer)

1. **OPEN-1:** `hub_self_refresh_v1.py` / light refresh does **not** invoke `_run_council_strategic_slice_seed` — only full `build-sina-command-panel.py` does. Founder hub Refresh ≠ re-seed.
2. **OPEN-2:** Duplicate 1000-pack prompts (sa-0218, sa-0243, sa-0268, sa-0293) share title — REGISTRY backlog; sa-0796 T3 crosswalk is current queue proof.
3. **OPEN-3:** Seed `force` flag exists (`--force` CLI) — maintainer-only; normal build uses idempotent skip.

## Validators (ACT)

- `validate-governance-fleet-v1.sh` — PASS · nudges 0 · verify_gap 0
- `validate-spine-bridge-founder-v1.sh` — PASS · spine-smoke-echo
- `validate-dispatch-policy-v1.sh` — PASS · gate_ok=True
- `validate-governance-event-spine-v1.sh` — PASS
- `find_critical_bugs.py` — critical **0**

## Verdict

**ACT complete** — build hook wired (sa-0218); disk marker + council/founder artifacts present; idempotent skip verified; no code change required for T3 spike.
