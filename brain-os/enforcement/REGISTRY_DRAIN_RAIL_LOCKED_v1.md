# REGISTRY drain rail — LOCKED v1

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Locked:** 2026-06-06 · **Pack:** `sourcea-1000-locked`

## PICK ORDER (mechanical — not chat memory)

**Law:** `pick-sourcea-no-asf-plan.py` uses **phase-first** drain:

1. Walk phases `s0 → s9` in pack order  
2. Within each phase, tiers `T0 → T1 → T2 → T3`  
3. First agent-runnable `backlog` wins  

**Forbidden:**

| Anti-pattern | Why |
|--------------|-----|
| `pick 30` as Brain queue | Tier-global starvation skipped `sa-0226`–`sa-0300` while `sa-0301`+ ran |
| Trusting chat “next sa” | Only `bash scripts/plan-no-asf-run.sh pick 1` output counts |
| Batch closeout multiple sa | One `sa-XXXX` per Worker Composer turn |

**Validator:** `python3 scripts/validate-sourcea-pick-order-v1.py` (also in `validate-sourcea-1000-pack.sh`).

**Full E2E chain:** `bash scripts/validate-sourcea-e2e-full-v1.sh` — gates, pick, spine, strict build, hub alignment, backend E2E, `find_critical_bugs` critical 0.

---

## INBOX + hygiene (LOCKED — same every session)

**Brain:** `brain-os/enforcement/SINA_BRAIN_INBOX_PROCESS_LOCKED_v1.md` — route only; run `bash scripts/enforce-registry-hygiene-v1.sh` before progress replies.

**Worker:** INBOX role = CHECK | ACT | VERIFY (one per turn) · receipt on VERIFY only.

---

## Protocol (one sa-XXXX per worker session)

1. `python3 scripts/cursor_agent_self_audit.py session-start`
2. `bash scripts/validate-execution-spine-v1.sh` — must PASS before edits
3. `bash scripts/plan-no-asf-run.sh route implement sourcea --json` — trust `meta.pick_id`
4. Implement **only** that task per `MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md`
5. Verify per prompt §Verify; update REGISTRY + `plan.json`
6. Hub → Actions → **Mark task done** (or `POST /api/execution-state-v1` `mark_done`)

## First task

**sa-0202** — `SINA_AUDIT_STRICT=1 build` + `find_critical_bugs.py`

## Gates

- `dispatch_ready` stays **false** unless explicit ASF order
- Brain/meta chat routes; SourceA worker executes
- No batching multiple registry IDs per session

## Spine closeout

After verify PASS: `founder-mark-done` or `python3 scripts/founder_spine_close.py --action mark-done --lane sourcea`

---

## WORKER_ROUND_REPORT (mandatory every turn)

Law: `MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md` §EVERY ROUND ORDER.

Every Worker reply ends with `WORKER_ROUND_REPORT` YAML — validate first, one sa, stop.

## DRAIN CHECK — **OFF** (superseded)

ASF policy: **DRAIN_CHECK OFF**. Worker uses full `WORKER_ROUND_REPORT` instead of one-line pick echo.

| Thing | When |
|-------|------|
| **#0** | New Worker chat · drift · lost trust |
| **TASK paste** | Brain handoff one sa per round |
| **DRAIN CHECK** | **Disabled** — use WORKER_ROUND_REPORT `pick_1_live` field |
