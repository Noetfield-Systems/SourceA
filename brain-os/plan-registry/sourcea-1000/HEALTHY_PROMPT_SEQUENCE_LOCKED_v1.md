# Healthy Prompt Sequence — SourceA REGISTRY drain (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Law:** One prompt = one purpose. No multi-step “step 1–4 in one turn”. No UNATTENDED BATCH.

## Ten step types (Prompt-Fast Loop aligned)

| Type | Do | Do NOT |
|------|-----|--------|
| `snapshot` | Read disk + mandatory laws + goal progress | Edit code |
| `plan` | Plan one sa — criteria + risks (≤8 lines) | Implement |
| `analyze` | Search missing validators/files/gaps | Fix yet |
| `check` | Run validators only; log PASS/FAIL | Implement |
| `debug` | Reproduce one failure; root cause doc | Batch fix |
| `fix` | One minimal fix from prior debug/check | New features |
| `implement` | One sa-XXXX minimal diff | pick 30 / batch |
| `verify_backend` | strict build + find_critical_bugs | Skip closeout |
| `verify_ui` | Hub alignment / audit_backend_e2e spot | Terminal for founder |
| `delta` | Near-miss + blockers only (3 lines) | Code changes |

## 30-queue rhythm (3 prompts per sa)

For each REGISTRY sa in the active 30-pack:

1. **CHECK** — read `.md`, preflight validators, report gaps (no implement)
2. **ACT** — implement that sa only
3. **VERIFY** — verify_backend + closeout + WORKER_ROUND_REPORT + STOP

→ 30 prompts = 10 sa per pack slice (healthy, not build×30).

## Commercial blocker law (CHECK → STOP, never ACT)

If CHECK finds a sa needs **live Eval-1b / OpenRouter** and credits are blocked (HTTP 402):

- **STOP** after CHECK + WORKER_ROUND_REPORT — do **not** inject ACT or VERIFY for that sa
- **Do not** mark REGISTRY `done` or fake `eval_1b_gate_ok: true`
- Record BLOCKED in SOURCEA-PRIORITY · skip to next **achievable** sa in queue generation
- Executor: `advance-healthy-queue-v1.py --skip-sa-slice` after CHECK on blocked sa

Putting OpenRouter-dependent work in Step 2 (ACT) when Step 1 (CHECK) already proved it impossible is **forbidden**.

## Mandatory injection (every prompt)

- `brain-os/law/enforcement/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md`
- `brain-os/law/enforcement/REGISTRY_DRAIN_RAIL_LOCKED_v1.md` §PICK ORDER
- `brain-os/system/GOAL_EXECUTION_ACTIVE_LOCKED_v1.md`
- `brain-os/plan-registry/sourcea-1000/HEALTHY_PROMPT_SEQUENCE_LOCKED_v1.md`
- `brain-os/plan-registry/sourcea-1000/REGISTRY_DRAIN_PROCESS_LOCKED_v1.md`
- `.cursor/rules/000-entry-gate.mdc` / worker gate + one-sa turn

## Founder (no Terminal)

- **Copy healthy drain** — Worker chat **RUN INBOX** (legacy archive Actions if ASF enables)
- **Advance healthy queue** — after Worker STOP
- Paste clipboard into SourceA Worker only

## Executor scripts (Worker/agent — not founder)

- Generate pack: `scripts/generate-healthy-prompt-pack-v1.py`
- Validate: `scripts/validate-healthy-prompt-pack-v1.sh`
