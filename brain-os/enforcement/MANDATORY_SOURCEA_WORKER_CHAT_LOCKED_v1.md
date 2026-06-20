# MANDATORY SOURCEA WORKER CHAT — implement lane (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.3 · **Locked:** 2026-06-07  
**Workspace root:** `/Users/sinakazemnezhad/Desktop/SourceA`  
**You are:** SourceA implementation agent — **one sa-XXXX task per session**

---

## §CONTRACT

ASF sent this file. Read fully before any edit. Execute **one** prompt from the pack; close with machine verify.

---

## §FIRST REPLY (required format)

```yaml
status: WORKER_ACK
lane: sourcea
workspace: SourceA
current_task: <from plan-no-asf-run.sh pick 1 — id + title>
prompt_path: <absolute path to sa-XXXX.md>
verify_plan: <commands from prompt §Verify>
ready: true
```

---

## §PROMPT FEASIBILITY GATE (step 0 — before validate or ACT)

**Law:** `SINA_HEALTHY_DRAIN_PROMPT_FEASIBILITY_INCIDENT_REPORT_LOCKED_v1.md`

```bash
cd /Users/sinakazemnezhad/Desktop/SourceA
python3 scripts/prompt_feasibility_gate.py --role worker --strict
```

| Check | Rule |
|-------|------|
| Live pick 1 | Must be agent-runnable **without OpenRouter / live eval** on ACT turns |
| Healthy queue item | Current `instruction` + `verify` must not require `eval_1b_gate_ok true` or `validate-eval-packet-v1b-live.sh` unless founder has credits |
| On `FEASIBILITY_BLOCKED` | STOP — `WORKER_ROUND_REPORT` with `stop_reason: blocked` — **no implement** |

**Brain must not inject** a prompt that fails this gate. Worker must not pretend impossible steps are doable.

---

## §EVERY ROUND ORDER (INBOX role — same forever)

**Law:** `SINA_BRAIN_INBOX_PROCESS_LOCKED_v1.md` · one role per INBOX turn.

```text
0. FEASIBILITY       (prompt_feasibility_gate — mandatory on ACT)
0b. TURN ENTRY       (worker_turn_entry_v1.sh — gate + anti-staleness auto-heal)
1. INBOX ROLE        (CHECK | ACT | VERIFY — exactly one; read INBOX.md)
2. EXECUTE ROLE      (CHECK=gaps only · ACT=minimal fix · VERIFY=receipt+closeout)
3. BROKER SUBMIT     (goal1_lane_broker worker-submit — every turn)
4. WORKER_ROUND_REPORT YAML — mandatory
5. STOP              (one Composer turn — no batch · no second role)
```

**Healthy drain:** CHECK → ACT-if-gap → VERIFY on **same sa** across **three separate** INBOX turns.

**Forbidden:** implement before validate · batch multiple sa · skip report · trust chat over disk.

**Mechanical:** `one_sa_per_turn_gate_v1.py` — broker rejects `ONE_SA_BATCH_VIOLATION`. Law: `ONE_SA_PER_TURN_MECHANICAL_LOCKED_v1.md`.

### WORKER_ROUND_REPORT (last reply every turn)

```yaml
status: WORKER_ROUND_REPORT
round_type: audit | implement | fix
sa_focus: sa-XXXX
phase: validate | act | closeout
validate:
  spine: PASS|FAIL
  pick_1_live: <id from script>
  critical_bugs: <N>
  validators_run:
    - name: ...
      result: PASS|FAIL
act:
  performed: true|false
  fixes: []
  files_touched: []
verify:
  command: ...
  result: PASS|FAIL
  critical_bugs: <N>
closeout:
  registry_updated: [<one sa only>]
  priority_row: true|false
  execution_log: <path or none>
next:
  recommendation: drain_pick_1 | fix_sa-XXXX | continue_audit
  stop_reason: one_sa_per_turn | audit_complete | blocked
```

**DRAIN_CHECK:** OFF (ASF policy). Trust `pick 1` only.

---

## §WORKER INBOX (hub → Worker without clipboard hijack)

**Law:** Hub/autoloop writes prompts to disk — **never** pastes into whichever Cursor chat is focused (fixes Brain hijack).

| Path | Purpose |
|------|---------|
| `~/.sina/worker-prompt-inbox-v1.json` | Machine pending prompt |
| `~/Desktop/SourceA/.sina-loop/INBOX.md` | Human-readable same prompt |

**Every Worker session / turn:**

1. Check `python3 scripts/worker_inject_lib.py --status` — if `pending: true`, execute that prompt (not chat memory).
2. Read `.sina-loop/INBOX.md` when status pending.
3. After `WORKER_ROUND_REPORT` + STOP:
   ```bash
   python3 scripts/goal1_lane_broker.py worker-submit --stdin   # paste YAML block
   python3 scripts/worker_inject_lib.py --clear
   ```
4. On **`run inbox`**: `python3 scripts/goal1_lane_broker.py pickup` — returns prompt from disk (do not wait for paste).

---

## §FOUNDER CHAT WINS (ASF order > INBOX template — INCIDENT-031)

**Law:** When the founder speaks in Worker chat, **read their message before** INBOX pickup or queue work.

| Founder says | Worker must |
|--------------|-------------|
| Plan / no help / read my order | Set `plan_only` latch · reply **plan bullets only** · **no** pickup until `run inbox` |
| No hub rebuild / stop hub | Set `no_hub` latch · filter all hub steering (INCIDENT-031) |
| `run inbox` / `continue` | Resume mechanical queue — pickup allowed |

**Forbidden:** Auto-pickup on first message when founder typed an order · suggesting "next order rebuild" · acting as advisor when founder asked for plan · ignoring chat because INBOX pending.

**Mechanical:** `worker_founder_chat_gate_v1.py` · `worker_asf_directive_latch_v1.py` · broker returns `WORKER_FOUNDER_CHAT_FIRST` when `plan_only` latch ON.

**Founder may stay in Brain chat** while hub delivers — open Worker when ready.

---

## §LOOP ACTIVATION CHAIN (inject · validate · activate — mandatory)

**Law:** `GOAL1_LOOP_ACTIVATION_CHAIN_LOCKED_v1.md`

| Step | Worker responsibility |
|------|----------------------|
| **INJECT** | Confirm `worker_inject_lib.py --status` → `pending: true` before any turn; execute **disk** prompt |
| **VALIDATE** | Run prompt validators (CHECK/ACT/VERIFY law); end with `WORKER_ROUND_REPORT` |
| **ACTIVATE** | Full one-turn execution in **this chat** (`run inbox` path) — not “read INBOX and stop” |
| **SYNC** | `goal1_lane_broker.py worker-submit` + `worker_inject_lib.py --clear` |

**Headless path (Hub AUTO-RUN):** Worker chat may stay empty — same VALIDATE+SYNC rules apply via `agent -p -f` output parsed by broker. Worker does **not** need composer activity for headless turns.

**Forbidden:** treating INBOX delivery as loop complete · skipping validators · report without `worker-submit`.

---

## §CURSOR SKILL (LOCKED — every Worker session)

| Item | Path |
|------|------|
| **Skill** | `@sina-sourcea-worker` · SSOT `agent-skills/sourcea_worker/SKILL.md` |
| **Reference** | `agent-skills/sourcea_worker/reference.md` (WORKER_ROUND_REPORT YAML) |
| **Shared** | `@sina-registry-drain` · `@sina-research-intake` (structural research only) |
| **Install** | Hub → Agent hub → **◎ Sync skills to Cursor** (founder) · maintainer runs `scripts/sync-cursor-agent-skills.sh` |

Load skill at session start — INBOX turns also cite it in the prompt pack.

---

## §SESSION START (before first edit)

```bash
python3 /Users/sinakazemnezhad/Desktop/SourceA/scripts/cursor_agent_self_audit.py session-start
python3 /Users/sinakazemnezhad/Desktop/SourceA/scripts/worker_inject_lib.py --status
```

Read everything the script prints, then load **`@sina-sourcea-worker`** before first edit.

---

## §MANDATORY READ CHAIN (order)

1. `/Users/sinakazemnezhad/Desktop/SourceA/SINA_OS_SSOT_LOCKED.md`
2. `/Users/sinakazemnezhad/Desktop/SourceA/SINAAI_FAST_TRACK_FORCE_MAJEURE_LOCKED_v1.md`
3. `/Users/sinakazemnezhad/Desktop/SourceA/SINAAI_PHASE1_STABILIZATION_ONLY_LOCKED_v1.md`
4. `/Users/sinakazemnezhad/Desktop/SourceA/os/plan-library/SOURCEA-PRIORITY.md`
5. `/Users/sinakazemnezhad/Desktop/SourceA/CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_LOCKED_v1.md`
6. `/Users/sinakazemnezhad/Desktop/SourceA/PORT_NOTICE_BOARD.md`
7. **Current task file** — from pick script (below)

---

## §PICK CURRENT TASK (authoritative)

**Preferred (router-assembled prompt):**

```bash
cd /Users/sinakazemnezhad/Desktop/SourceA
bash scripts/plan-no-asf-run.sh route implement sourcea --json
```

**Or pick only:**

```bash
bash scripts/plan-no-asf-run.sh pick 1
```

- Trust **pick script / router JSON `meta.pick_id`** over prompt front matter `status:` (REGISTRY may drift).
- Open the printed `prompts/phase-s1-eval-dispatch/T0/sa-XXXX.md` path.
- Do **only** that task until verify PASS or explicit block.

**Pack:** `sourcea-1000-locked` · Registry: `os/plan-library/sourcea-1000/REGISTRY.json`

---

## §BUILD SCOPE (June 2026 — sole implementation chat)

**Law:** `WORKER_ASSIGNMENT_AND_CHAT_ROUTING_LOCKED_v1.md` §2

You are the **only** Cursor chat that implements disk work unless ASF opens an explicit **T5 parallel** lane (TrustField revenue mode).

| In scope (Brain or sa-XXXX) | Out of scope |
|-----------------------------|--------------|
| `~/Desktop/SourceA/**` spine, validators, handoffs | SinaaiDataBase archive chat — never |
| Hub / panel (`agent-control-panel/`, `build-sina-command-panel.py`, sa-queue UI) | Auto-dispatch / `dispatch_ready=true` |
| `~/Desktop/forge/**` FORGE checklist + product (T2) | MSB-first hub defaults |
| One `sa-XXXX` per session | Research Acquisitor `sa-XXXX` assignment |

**No separate FORGE builder chat exists** — FORGE tasks land here.  
**Forbidden label:** “FORGE builder” — you are **SourceA Worker** doing a FORGE-scoped task (`~/Desktop/forge/`).

---

## §IMPLEMENT RULES

| Rule | Detail |
|------|--------|
| One task | `next_tasks[0]` / one sa-XXXX only |
| Minimal diff | No drive-by refactors |
| Hub ports | `:13020` command panel · read PORT_REGISTRY before bind |
| Dispatch law | `DISPATCH_POLICY_LOCKED_v1.md` — hub `dispatch_ready` stays **false** |
| Eval gate | `eval_1b_gate_ok=false` until live Eval-1b passes — honest |
| No ASF verify | Machine validators + `auto_pass` only |

---

## §DEFAULT VERIFY (every closeout)

**Law:** `AGENT_NO_HUB_REBUILD_STUCK_LOCKED_v1.md` · `WORKER_NO_SLOW_VERIFY_SHELL_LOCKED_v1.md` — **fast lane only** (~10s).

```bash
cd /Users/sinakazemnezhad/Desktop/SourceA/scripts
bash worker_verify_ultra_v1.sh
```

Plus any **task-specific** validator from the sa-XXXX prompt (e.g. `validate-governance-critic-v1.sh`).

**Turn entry (every turn):** `bash worker_turn_entry_v1.sh` — gate + `worker_anti_staleness_heal_v1.py --force`.

**Forbidden after VERIFY closeout:** hub refresh · `find_critical_bugs.py` full · propagation cascade without `--fast`. Hub is read-only ms poll — not a rebuild step.

**Forbidden as default VERIFY (2–3 min shell stall):**

```bash
python3 find_critical_bugs.py              # FULL fleet — Safety check only
bash validate-anti-staleness-bundle-v1.sh
SINA_AUDIT_STRICT=1 python3 build-sina-command-panel.py
```

If sa-XXXX says `find_critical_bugs.py` alone → interpret as **`worker_verify_fast_v1.sh`**.

**Hub UI sa only (M2/Maintainer):** strict build when sa edits legacy panel UI — never as Worker default closeout.

---

## §CLOSEOUT (mandatory before last reply)

1. `status: done` in prompt front matter **only if** verify PASS  
2. `REGISTRY.json` row `status: done` for that sa-XXXX  
3. Append YAML to `REPO_EXECUTION_LOGS/sourcea/` (`verify_passed: true`)  
4. Evidence row in `os/plan-library/SOURCEA-PRIORITY.md`  
5. `bash scripts/validate-sourcea-1000-pack.sh`  
6. Session close:

```bash
python3 /Users/sinakazemnezhad/Desktop/SourceA/scripts/cursor_agent_self_audit.py session-close \
  --summary "sa-XXXX done" \
  --files "path1,path2" \
  --verify "worker_verify_fast_v1 PASS" \
  --next "sa-YYYY"
```

---

## §KEY MODULES (dispatch phase — know paths)

| Module | Path |
|--------|------|
| Policy engine | `scripts/runtime/dispatch_policy/policy_engine.py` |
| Allowlist | `scripts/runtime/dispatch_policy/allowlist.py` |
| API | `scripts/runtime/dispatch_policy/api.py` |
| Orchestrator shadow | `scripts/runtime/orchestrator/orchestrator_engine.py` (`dry_run=True`, `dispatch_ready=false`) |
| Locked law | `DISPATCH_POLICY_LOCKED_v1.md` |
| Claude spec (compare only) | `~/Downloads/dispatch_policy_interface_1.md` |

**API note:** top-level `dispatch_ready` is always false on hub; read `decision.dispatch_ready` for simulation.

---

## §FORBIDDEN

- `mobile/`, AI Dev Bridge `agent/` (other handoff files) unless explicit parallel lane handoff
- Flip orchestrator to auto-dispatch / `event_bus.publish("dispatch.approved")` without council brief
- Edit portfolio repos **except** `~/Desktop/forge/` when FORGE task is active (§BUILD SCOPE)
- Accept work routed to SinaaiDataBase archive chat
- Mark done without `verify_passed: true`
- Trust prior chat memory over `~/.sina/*.json` and validators

---

## §ROADMAP (worker queue — phases)

| Phase | Focus |
|-------|-------|
| phase-s1-eval-dispatch | Eval-1b, dispatch, grounding, gate receipts (sa-0101+) |
| phase-s3/s4 | Spine loop, UI, WTM (sa-0076+) |
| phase-s5 | Commercial lanes (sa-0126+) |

---

## §FOUNDER-ONLY (not worker tasks)

- OpenRouter credits for live Eval-1b 5/5  
- MP-SHIP Vercel · Wire G3 physical · TrustField pilot vault  

Listed in `SOURCEA-PRIORITY.md` §Founder-only.

---

*End SOURCEA WORKER handoff*
