# sa-0960 — No-ASF verify authority pattern (SourceA · mono · Noetfield · other repos)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Tier:** T2 research only · **No D-modules · No cross-repo implement**

## One-line law

> **ASF is never verify/progress authority.** Machine validators + broker receipt closeout decide PASS; founder clicks only — no Terminal, no manual REGISTRY edits, no chat claims without disk proof.

---

## Pattern stack (canonical — SourceA)

| Layer | SSOT | Machine signal | ASF role |
|-------|------|----------------|----------|
| **Trigger** | `PLAN WITH NO ASF` phrase | `plan-no-asf-run.sh` · `pick-sourcea-no-asf-plan.py` | Says trigger or taps RUN INBOX |
| **Recipe** | REGISTRY `title` + `prompts/.../sa-XXXX.md` + `verify` cmd | Three files exist; INBOX bind matches queue head | None |
| **Validation** | `worker_verify_fast/ultra` · spine · monitor honesty | Exit 0; broker ≠ STALE; no `sa_mismatch` | None |
| **Evidence** | `receipts/sa-XXXX-receipt.json` | Written after broker VERIFY PASS | None |
| **Closeout** | `worker_verify_closeout_v1.sh` | REGISTRY `done` · PRIORITY row · pack validate | None — never hand-edit REGISTRY |
| **Scoreboard** | `AGENT_SCOREBOARD_LOCKED_v1.md` | `auto_pass` / `verified_by: auto` | Force-verify only on exception |

**Law refs:** `WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md` · `FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md` §2 · `REGISTRY_DRAIN_RAIL_LOCKED_v1.md`

---

## Global no-ASF library (cross-repo index)

| Field | Path |
|-------|------|
| **Registry** | `~/.cursor/plans/no-asf-library/REGISTRY.json` |
| **Policy** | `~/.cursor/plans/no-asf-library/POLICY.md` |
| **Human backlog** | `~/.cursor/plans/no-asf-library/HUMAN_BACKLOG.md` |
| **Rule** | Trigger phrase only — not every plan |

**SourceA REGISTRY links:** `global_pack` · `mono_pack_ref` · `noetfield_pack_ref` in `brain-os/plan-registry/sourcea-1000/REGISTRY.json`.

---

## Per-repo mirror table (research — adopt, don't duplicate)

| Repo | Pack / queue | Pick / run | Verify bundle | Closeout | Gap |
|------|--------------|------------|---------------|----------|-----|
| **SourceA** | `sourcea-1000` | `plan-no-asf-run.sh` · RUN INBOX broker | `worker_verify_*` + `goal1_lane_broker.py` | `worker_verify_closeout_v1.sh` | **Reference implementation** |
| **SinaaiMonoRepo** | `mono-1000` (`mx-*`) | `plan-no-asf-run.sh` · `pick-mono-no-asf-plan.sh` | `full-e2e-mono.sh` · `agent-auto-audit.sh` | mx `done` + `last_verify` in `os/plan.json` | Receipt broker parity with SourceA optional |
| **Noetfield (mono ship)** | `nf-1000` / GTM WISE v14 | `make pick-wise` · `make pick-no-asf-plan` | `plan-with-no-asf-verify.sh` · `verify-agent-scope.sh` | `sync-prompt-pack-status.py` · `reports/cursor-reply-latest.txt` | Pack path `Noetfield/brain-os/...` **not present locally** — ship repo is `Noetfield-All-Documents/Noetfield` |
| **TrustField** | `os/plan.json` + no-asf picks | `pick_no_asf_plans.py` · `run_no_asf_sprint.sh` | `run_no_asf_verify.sh` (VERIFY_BASE_URL) | `close_no_asf_sprint.sh` | Portfolio lane — URL-bound verify |
| **Other portfolio** | Lane `os/plan.json` | Per-repo pick script when present | Per `PROGRAM_PROGRESS` / plan verify | PRIORITY / plan last_verify | Wire when ASF names lane |

---

## Noetfield mono — specific guidance

**Disk truth (2026-06-14):**

- REGISTRY declares `noetfield_pack_ref`: `/Users/sinakazemnezhad/Desktop/Noetfield/brain-os/plan-registry/noetfield-1000` — **path missing**; canonical ship tree is under `Noetfield-All-Documents/Noetfield/`.
- Rule `.cursor/rules/noetfield-no-asf-plans.mdc` already encodes no-ASF flow: pick → founder `implement` approve → verify bundle → status sync — **ASF not verify authority** for machine steps.
- **SKILL-007 gate:** propose without `implement` stops at step 4 — founder approval is **order**, not **verify**.

**Mono Noetfield pattern (copy from SourceA, not fork):**

```text
PLAN WITH NO ASF → pick (WISE or nf-1000) → implement ONE → verify script PASS → sync status done → receipt/report file
```

| Do | Don't |
|----|-------|
| Run `make verify-gtm` / `plan-with-no-asf-verify.sh` | Ask founder to Terminal-verify |
| Set `status: done` via sync scripts | Hand-edit REGISTRY in SourceA for NF tasks |
| Tag `[NF-LOCAL-REPO-AGENT]` on new docs | Edit `[NF-CLOUD-AGENT]` sections from Worker |
| Link evidence in `reports/cursor-reply-latest.txt` | Use chat PASS without script exit 0 |

---

## Duplicate sa titles (consolidation note)

Same task text appeared at **sa-0910**, **sa-0935**, **sa-0960**. This doc is the **canonical research** for VERIFY closeout of sa-0960; prior duplicates remain backlog unless ASF orders skip/mark.

---

## What is NOT no-ASF verify

| Claim | Treatment |
|-------|-----------|
| ASF taps Refresh / Safety / Actions | **Operator** — not verify authority |
| ChatGPT audit paste | `EXTERNAL_CRITIC` — compare only |
| `eval_1b_gate_ok` for research rail | Eligibility signal — not founder sign-off |
| Hub UI green pill | Projection — disk validators + receipt win |
| Cursor AUTO-RUN / 30-pack drain | Legacy — not P0 (`FOUNDER_AGENTIC_COMMERCIAL` §1) |

---

## Verdict

**No-ASF verify authority is shipped on SourceA** (broker + receipt + closeout script). **Mono** and **TrustField** have parallel pick/verify scripts. **Noetfield** has rule + verify bundle on ship repo but **pack_ref path drift** — adopt SourceA pattern via existing NF scripts; do not implement cross-repo wiring in this sa.

**One-line:** Machine validators + receipt closeout = PASS; ASF orders and clicks — never verifies.
