# SourceA / Sina Command — Runbook

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Audience:** Maintainer (executor) runs shell; Founder uses hub **Refresh** + **Actions** only.  
**Updated:** 2026-06-06 (worker `:13030` note 2026-06-10)  
**Emergency stop:** Hub **Actions** or `scripts/kill-sina-command.sh` (executor only)

---

## 1. Daily health check (founder)

1. Open `http://127.0.0.1:13020/`
2. Tap **Refresh** (rebuilds panel + runs validators)
3. Check **Today** tab — P0 thread + ops cards
4. Check **Track** — lane attest status
5. If red: read ops card action text (no Terminal steps)

**Healthy signals:** build log shows `OK: validate-*` · `find_critical_bugs` critical = 0

---

## 2. Start / stop hub (executor)

```bash
# Start (or no-op if already healthy) — worker :13030 first, then hub :13020
bash ~/Desktop/SourceA/scripts/serve-sina-command.sh

# Health
curl -sf http://127.0.0.1:13020/health
curl -sf http://127.0.0.1:13030/health

# Stop (graceful) — hub first, then worker
curl -sf -X POST http://127.0.0.1:13020/shutdown
bash ~/Desktop/SourceA/scripts/kill-hub-rebuild-worker.sh
# Then restart if needed
bash ~/Desktop/SourceA/scripts/serve-sina-command.sh
```

**Hub logs/PID:** `~/.sina/command-server.log` · `~/.sina/command-server.pid`  
**Worker logs/PID:** `~/.sina/hub-rebuild-worker.log` · `~/.sina/hub-rebuild-worker.pid`

---

## 3. Strict build (executor)

Full panel rebuild + validator chain:

```bash
cd ~/Desktop/SourceA/scripts
SINA_RUN_BACKEND_E2E=0 python3 build-sina-command-panel.py
python3 find_critical_bugs.py
```

| Env var | Effect |
|---------|--------|
| `SINA_AUDIT_STRICT=0` | Warn instead of fail on some audits |
| `SINA_RUN_BACKEND_E2E=1` | Include long `/refresh` E2E (~4+ min) |
| `SINA_EVAL_1B_LIVE=1` | Require live Eval-1b (fails if OpenRouter 402) |

---

## 4. Key validators (executor)

| Script | Proves |
|--------|--------|
| `validate-dispatch-policy-v1.sh` | Dispatch API + task-class evaluate |
| `validate-dispatch-policy-alignment-v1.sh` | Dual-layer classifier ↔ allowlist |
| `validate-graph-executor-pos-dispatch-v1.sh` | `pos-dispatch` stays `suggest`, no auto |
| `validate-runtime-orchestrator-v1.sh` | C1–C6 pipeline + shadow decision |
| `validate-dispatch-ready-lock-v1.sh` | No `dispatch_ready: true` bypass |
| `validate-spine-bridge-founder-v1.sh` | Founder spine bridge gate |
| `validate-governance-fleet-v1.sh` | 8-agent fleet scoreboard |
| `validate-eval-packet-v1b-live.sh` | Eval-1b live A/B (needs credits) |

Run individually from `scripts/` after hub is up.

---

## 5. Founder Actions (hub — no Terminal)

| Action | When |
|--------|------|
| **Refresh** | After maintainer ship; pick up new panel data |
| **Enqueue eval spine bridge** | After structural/live eval gate |
| **MP-SHIP: Vercel protection** | MergePack UI 401 |
| **Audit MergePack ship** | After Vercel fix |
| **TrustField pilot (Track)** | Lane attest |
| **Start n8n** | Automation spine (see `scripts/N8N_FOUNDER_RUNBOOK.md`) |

Full list: `/api/founder/actions` or hub **Actions** panel.

---

## 6. Runtime smoke (executor)

```bash
cd ~/Desktop/SourceA/scripts
python3 -c "
from runtime.orchestrator.orchestrator_engine import run_runtime_orchestration
r = run_runtime_orchestration(goal_tool_id='pos-run', task_id='runbook-smoke-1')
print('dispatch_ready', r.get('dispatch_ready'), 'task_class', r.get('task_class'))
print('decision', (r.get('dispatch_decision') or {}).get('reason'))
"

curl -sf http://127.0.0.1:13020/api/dispatch-policy-v1 | python3 -m json.tool | head -20
curl -sf "http://127.0.0.1:13020/api/dispatch-policy-v1?task_class=validate-only&eval_tier=structural" | python3 -m json.tool | head -25
```

---

## 7. SSOT files to inspect

| File | Contents |
|------|----------|
| `~/.sina/dispatch_policy_v1.json` | Policy + alignment + last_decision |
| `~/.sina/eval_packet_v1b_report.json` | Eval-1b scaffold/live results |
| `~/.sina/eval_1b_ci_mode_v1.json` | structural_only vs live |
| `~/.sina/runtime_orchestrator_v1.json` | Latest orchestrator run |
| `~/.sina/graph_executor_v1.json` | Spine bridge state |
| `PROGRAM_PROGRESS.json` | Whole-program progress |
| `os/plan-library/SOURCEA-PRIORITY.md` | Machine truth + evidence log |

---

## 8. Incidents

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Hub 404 / connection refused | Server down | `serve-sina-command.sh` (executor) |
| Build fails on dispatch validators | Stale hub code | Restart hub after `runtime/` edits |
| Eval-1b live FAIL | OpenRouter 402 | Structural CI mode; top up credits |
| `dispatch_ready` lock FAIL | Code bypass | Revert `dispatch_ready: true` in runtime |
| MergePack UI 401 | Vercel Deployment Protection | Founder Action → disable protection |
| Agent loop stale | Hub stopped | Ignore `.sina-loop/INBOX.md` when inactive |

**Incident room:** hub tab **Incident Room** · `CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_LOCKED_v1.md`

---

## 9. Maintainer session closeout

After substantive multi-file work:

```bash
cd ~/Desktop/SourceA/scripts
python3 cursor_agent_self_audit.py session-close \
  --summary "…" \
  --files "…" \
  --verify "build PASS" \
  --next "blocker"
```

Closeout disk: `~/.sina/agent-workspaces/<agent>/SESSION_CLOSEOUT_LATEST.md`

---

## 10. Related runbooks

- n8n: `scripts/N8N_FOUNDER_RUNBOOK.md`  
- Morning route: `README_SOURCE_A.md` § Morning execution route  
- Strategic priorities: `STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md` §7
