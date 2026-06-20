# HUB_STABILIZATION_v5.1_FINAL
**Prompt ID:** HUB_STABILIZATION_v5.1_FINAL  
**Status:** LOCKED — ASF Final Decision 2026-06-10  
**Supersedes:** All prior hub-rebuild prompts (7-hub, Claude v1–v4, Claude 2, GPT drafts)  
**Do not modify this file.** Implement exactly as written.  
**Post-N1 amendment (2026-06):** Sections below amended to match shipped external worker on `:13030` (stabilization backlog P1–P9). Historical v5.1 text preserved in SUPERSEDED blocks.

---

## POST-N1 IMPLEMENTATION STATUS

| Phase | Status |
|-------|--------|
| **A–E** | DONE — four NEVER rules, light E2E, tier router |
| **N1** | DONE — external rebuild worker on `:13030` |
| **P1–P6** | DONE — generation_id, kill symmetry, validator preflight, heavy E2E parity, FCB worker probe, PORT_CATALOG |
| **P7** | DONE — SSOT doc alignment |
| **P8** | DONE — ecosystem safety unblock (`validate-ecosystem-safety-v1.sh`) |
| **P9** | DONE — founder one-tap `founder-restart-rebuild-worker` + `:13030` Safety chip |
| **P10** | DONE — Gate N formal close (`validate-hub-stabilization-gate-n-v1.sh`) + N1 receipt |

---

## TASK

Stabilize the SourceA Control Hub on `:13020` using a **Modular Monolith** pattern.  
Hub browser entry stays `:13020`. Rebuild worker is an **approved sidecar** on `:13030` (Phase N1; registered in `PORT_CATALOG.json` + port law).  
No Flask. Not microservices — two processes, one queue contract (`hub_queue_lib_v1.py`).

---

## REAL SUCCESS METRIC

The hub is fixed when the request thread permanently satisfies all four:

| # | Rule |
|---|------|
| ① | NEVER calls `build_payload()` |
| ② | NEVER writes `command-data.json` or `command-data-shell.json` |
| ③ | NEVER runs validators |
| ④ | NEVER runs the refresh pipeline |

When those hold, latency follows automatically:
- `clear_session` < 1s
- `POST /refresh` → 202 in < 1s
- `GET /api/hub-sync` < 200ms

`grep hub_after_mutation` is a proxy. The four NEVER rules are truth.  
The light E2E must grep both server files and fail on any request-path violation.

---

## CLOSED CONFLICTS — NEVER REOPEN

| ID | Rule |
|----|------|
| C-H01 | `:13021` = Monitor · `:13022` = Mono · `:13023` = Chat Unify — all occupied. Phase N uses `:13030+` only. |
| C-H02 | `queue_sa.json` does not exist logged. Never reference it. |
| C-H10 | `t.get("queue_sa")` → None. Use `t.get("queue", {}).get("sa_id")` or `queue_sa_from_disk()`. |
| C-H04 | `run_branch_action` lines ~2197–2733 — 25 inline build paths. Phase C covers this. Not skippable. |
| C-H05 | Broken POST-in-GET: move to `do_POST`, keep GET reads. |
| C-GPT | No `threading.Thread()` per mutation. One worker, fcntl JSONL, dirty coalesce. |

**Parallel tracks (not hub gates):** INCIDENT-023 conduct · `inbox.truth_match: false` · 595 vs 596 monitor drift · FREEZE must stay ON.

---

## IMPLEMENTATION CONSTANTS

| Wrong | Correct |
|-------|---------|
| Flask `@app.route` | `SinaCommandHandler.do_GET` / `do_POST` |
| `self._send_json()` | `self._json(code, dict)` |
| `POST /api/refresh` | `POST /refresh` (line ~1021) |
| `POST /api/clear-session` | `POST /api/intelligence-circle` + `{"action":"clear_session"}` |
| Cwd-relative shell path | `SOURCE_A / "agent-control-panel" / "command-data-shell.json"` |
| `queue_sa.json` | `~/.sina/run-inbox-disk-truth-v1.json` → `t.get("queue",{}).get("sa_id")` |
| `generation` | `generation_id` (everywhere, including shell JSON and hub-sync response) |
| Thread per event | One worker, fcntl JSONL queue, dirty coalesce |

---

## PHASE PLAN

| Phase | File(s) | Goal | Gate |
|-------|---------|------|------|
| **A** | `sina-command-server.py` only | Read path pure; enqueue stub; shared queue lib | hub-sync <200ms · /refresh 202 <1s · clear_session <1s |
| **B** | `sina-command-server.py` only | L0/L1/L2 — no sync build in request handlers | 0 sync `build_payload`/`hub_after_mutation` in request thread |
| **C** | `sina_command_lib.py` + `hub_rebuild_worker_v1.py` + external worker `:13030` | Lib branch → enqueue; one worker consumes queue | Four NEVER rules true · 10 mutations → 1–2 rebuilds |
| **E** | `audit_backend_e2e_light_v1.py` + wire `find_critical_bugs` | Machine proof + receipt | Light E2E PASS <30s · critical 0 <120s |
| **N1** | `serve-hub-rebuild-worker.sh` + `hub_rebuild_worker_v1.py` | **DONE** — standalone worker `:13030` + health | `curl :13030/health` · coalesce · lock present |
| **P1–P6** | Stabilization backlog (see status table) | Hardening after N1 | Port catalog · FCB probe · generation_id · kill symmetry |
| **N2+** | Future separate services | Only after N1 green + ASF explicit approval | Ports 13031+ after `lsof` check |

**v5.1 change:** C and D merged — worker ships in same phase as lib fix. No "enqueue with no consumer" gap.  
**N1 change:** Worker moved out of `:13020` process to `:13030` sidecar (C3 boot hook superseded).

---

## STEP 0 — BASELINE (mandatory, no code before this)

```bash
cat ~/Desktop/SourceA/architecture_audit/REBUILD_TRIGGER_MAP.md
cat ~/Desktop/SourceA/architecture_audit/STATE_MAP.md
cat ~/Desktop/SourceA/architecture_audit/HOTSPOTS.md

curl -s http://127.0.0.1:13020/health
grep -c "hub_after_mutation" scripts/sina-command-server.py   # expect 29
time curl -s http://127.0.0.1:13020/api/hub-sync             # expect ~7s (the bug)
python3 -c "
import json; from pathlib import Path
t = json.loads((Path.home()/'.sina'/'run-inbox-disk-truth-v1.json').read_text())
print('queue.sa_id:', t.get('queue',{}).get('sa_id'))
"   # expect sa-0778
```

**REPORT all 4 results. Do not touch any file until reported.**

---

## PHASE A — READ PATH

**File:** `scripts/sina-command-server.py` ONLY  
**Edit targets confirmed logged:** lines 159–171 (hub-sync), 1021–1031 (/refresh)

### A0 — Create shared queue lib first

Create `scripts/hub_queue_lib_v1.py`:

```python
#!/usr/bin/env python3
"""Shared fcntl-safe queue append. Used by server AND lib — one writer pattern."""
from __future__ import annotations
import fcntl, json, time
from pathlib import Path

QUEUE = Path.home() / ".sina" / "hub-rebuild-queue-v1.jsonl"

def enqueue_rebuild(source: str = "", run_refresh: bool = False) -> None:
    QUEUE.parent.mkdir(exist_ok=True)
    evt = {"ts": time.time(), "source": source, "run_refresh": run_refresh}
    with open(QUEUE, "a") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(json.dumps(evt) + "\n")
        fcntl.flock(f, fcntl.LOCK_UN)
```

### A1 — Fix GET /api/hub-sync (line ~159, currently 7.46s)

Replace the `build_payload()` call block with:

```python
import json as _j
from hub_queue_lib_v1 import enqueue_rebuild as _enqueue  # noqa
_shell_path = SOURCE_A / "agent-control-panel" / "command-data-shell.json"
try:
    s = _j.loads(_shell_path.read_text())
    self._json(200, {
        "ok":             True,
        "built_at":       s.get("built_at"),
        "generation_id":  s.get("generation_id", 0),
        "nav":            s.get("nav"),
        "factory_now":    s.get("factory_now"),
        "freeze_status":  s.get("freeze_status"),
        "hub_essentials": s.get("hub_essentials"),
        "command_center": s.get("command_center"),
    })
except Exception as e:
    self._json(500, {"ok": False, "error": str(e)})
```

**Regression watch:** Slim shell read may drop `goal1_hub_status_bundle` fields.  
After Phase A gate passes, confirm Goal1 card still updates in the browser.  
If missing, add: `"goal1_status": s.get("goal1_hub_status_bundle")` to the response dict.

### A2 — Fix POST /refresh (line ~1021, currently synchronous 230s)

Replace `hub_after_mutation(run_refresh_scripts=True, write_html=True)` block with:

```python
from hub_queue_lib_v1 import enqueue_rebuild as _enqueue
_enqueue(source="POST /refresh", run_refresh=True)
self._json(202, {
    "ok": True,
    "status": "queued",
    "message": "Rebuild queued. Poll /api/hub-sync generation_id for completion."
})
```

**Phase A caveat:** Between A and C, /refresh returns 202 but the worker does not exist yet.  
The rebuild will not run until Phase C. Report this explicitly in the Phase A gate output.

### A3 — Fix remaining direct build_payload() in GET threads

Lines 1131, 1194, and the `/command-data.json` route: replace each with direct disk reads.  
Pattern:
```python
self._json(200, _j.loads(
    (SOURCE_A / "agent-control-panel" / "command-data.json").read_text()
))
```

### GATE A

```bash
rm -f ~/.sina/*.lock
SINA_FORCE_RESTART=1 bash scripts/serve-sina-command.sh && sleep 3

time curl -s http://127.0.0.1:13020/api/hub-sync \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('built_at:', d.get('built_at'))"
# MUST: <200ms

time curl -s -X POST http://127.0.0.1:13020/refresh \
  -H "Content-Type: application/json" -d '{}'
# MUST: 202 in <1s (note: no rebuild fires yet until Phase C — expected)

time curl -s -X POST http://127.0.0.1:13020/api/intelligence-circle \
  -H "Content-Type: application/json" -d '{"action":"clear_session"}'
# MUST: <1s

grep -c "hub_after_mutation" scripts/sina-command-server.py
# Expect: still ~29 (latency only — Phase A does not remove logic)
```

**STOP. Report 4 results (3 timings + count). Await: `ASF: Phase B approved`**

---

## PHASE B — TIER ROUTER

**File:** `scripts/sina-command-server.py` ONLY

### B1 — Add classifier before do_GET

```python
_L0_IC = frozenset({
    "clear_session", "clear_maintainer", "clear_advisor",
    "select_agent", "ping", "status", "inject_skipped",
})
_L1_ROUTES = frozenset({
    "/api/prompt-queue", "/api/prompt-direction",
    "/api/commitments", "/api/founder-requests",
    "/api/founder-agent-guide", "/api/audit-backlog",
    "/api/advisor/chat", "/api/founder-advisor-discussion",
    "/api/agent-scoreboard", "/api/essay-discourse",
    "/api/agent-research", "/api/workspace-vault",
})

def _tier(route: str, action: str = "") -> str:
    if route == "/api/intelligence-circle" and action in _L0_IC:
        return "L0"
    if route in _L1_ROUTES:
        return "L1"
    return "L2"
```

### B2 — Apply tier in every POST handler

For each of the ~29 `hub_after_mutation()` call sites, determine tier and replace:

```python
_tv = _tier(path, body.get("action", ""))

# L0 — IC cheap actions (already uses invalidate_hub_cache — keep, just ensure no build follows)

# L1 — SSOT-write-only routes:
#   [existing SSOT write stays exactly as-is]
#   invalidate_hub_cache()
#   self._json(200, {"ok": True})
#   # UI reloads tab data via /api/<tab> on next poll

# L2 — genuine state changes:
#   [existing SSOT write stays exactly as-is]
#   from hub_queue_lib_v1 import enqueue_rebuild as _enqueue
#   _enqueue(source=path, run_refresh=("rule" in path or "todo" in path))
#   self._json(202, {"ok": True, "status": "queued"})
```

### B3 — Remove dead POST-in-GET branches

In `do_GET`, find `if self.command == "POST":` blocks inside:
- `/api/eval-packet-v1b`
- `/api/event-bus-v1`  
- `/api/agent-rules-in-charge-v1`

Delete only the `if self.command == "POST": ...` blocks. Keep GET read logic intact.

### GATE B

```bash
# Four-rule check — must be 0 lines
grep -n "build_payload\|hub_after_mutation\|write_panel_outputs\|run_refresh_pipeline" \
  scripts/sina-command-server.py \
  | grep -v "def \|#\|_enqueue\|hub_queue_lib\|import"
# MUST: 0 lines

time curl -s -X POST http://127.0.0.1:13020/api/prompt-queue \
  -H "Content-Type: application/json" -d '{"action":"list"}'
# MUST: <500ms
```

**STOP. Report grep result + timing. Await: `ASF: Phase C approved`**

---

## PHASE C — SINGLE DURABLE WORKER + LIB FIX

**Files:** `scripts/sina_command_lib.py` (lines ~2197–2733) + `scripts/hub_rebuild_worker_v1.py` + external worker on `:13030` (N1)

### C1 — Fix hidden rebuild path in sina_command_lib.py

Add at top of `sina_command_lib.py` (after existing imports):

```python
from hub_queue_lib_v1 import enqueue_rebuild as _lib_enqueue  # noqa
```

Read lines 2197–2733 in full. For each of the 25 `build_payload` + `write_panel_outputs` pairs:

```python
# REMOVE every instance of:
payload = build_payload(run_refresh_scripts=True)   # or False
write_panel_outputs(payload)
return payload

# REPLACE with:
_lib_enqueue(source="branch_action", run_refresh=<was_True_or_False>)
return {"ok": True}
```

### C2 — scripts/hub_rebuild_worker_v1.py (in the repository — N1)

Standalone service on `:13030` (health HTTP) + daemon queue consumer thread.  
**Canonical source:** `scripts/hub_rebuild_worker_v1.py` — do not duplicate here.

Key behaviors (shipped):
- `fcntl` lock at `~/.sina/hub-rebuild-worker-v1.lock` — one instance
- `ThreadingHTTPServer` on `127.0.0.1:13030` → `GET /health`
- Dirty coalesce: `SETTLE=3.0` seconds after last enqueue
- Rebuild via `hub_after_mutation()` then `bump_shell_generation_id()` from `sina_command_lib` (does not touch `built_at`)

### C3 — SUPERSEDED (pre-N1 boot hook)

> **HISTORICAL — do not implement.** Original v5.1 planned embedding the worker as a daemon thread inside `:13020` via a server boot hook. Phase N1 moved the worker to a standalone process on `:13030`. `sina-command-server.py` has no worker import.

### PHASE N1 — EXTERNAL WORKER (shipped)

| Script | Role |
|--------|------|
| `scripts/serve-hub-rebuild-worker.sh` | Start/restart worker on `:13030` |
| `scripts/kill-hub-rebuild-worker.sh` | Stop worker (after hub stop) |
| `scripts/serve-sina-command.sh` | **Worker-first** — calls `serve-hub-rebuild-worker.sh` then starts hub |
| `scripts/ensure-hub-rebuild-worker-v1.sh` | Validator preflight (Phase P3) |

Serve order: worker → hub. Kill order: hub → worker (Phase P2 symmetry).

### GATE C

```bash
SINA_FORCE_RESTART=1 bash scripts/serve-sina-command.sh && sleep 3
# serve-sina-command.sh starts worker (:13030) then hub (:13020)

# Worker health (N1)
curl -sf http://127.0.0.1:13030/health

# Four-rule proof — both files, must be 0
grep -n "build_payload\|hub_after_mutation\|write_panel_outputs\|run_refresh_pipeline" \
  scripts/sina-command-server.py scripts/sina_command_lib.py \
  | grep -v "def \|#\|_enqueue\|hub_queue_lib\|worker\|_lib_enqueue\|import"
# MUST: 0 lines

# Worker running
ls ~/.sina/hub-rebuild-worker-v1.lock

# Coalesce proof: 10 events → 1 rebuild (PYTHONPATH=scripts required)
for i in $(seq 1 10); do
  PYTHONPATH=scripts python3 -c "
from hub_queue_lib_v1 import enqueue_rebuild
enqueue_rebuild(source='coalesce_test_$i', run_refresh=False)"
done
sleep 8
grep -c "coalesce_test" ~/.sina/hub-rebuild-done-v1.jsonl   # 10 consumed
# Worker output must show: "coalescing 10 events → 1 rebuild" (not 10 rebuilds)

# Lib path fast
time curl -s -X POST http://127.0.0.1:13020/api/action \
  -H "Content-Type: application/json" \
  -d '{"branch":"hq-status","action":"status"}'
# MUST: <500ms
```

**STOP. Report: 4-rule grep (must be 0) + worker lock + coalesce count + action timing.**  
**Await: `ASF: Phase E approved`**

---

## PHASE E — LIGHT E2E + FINAL RECEIPT

### Create scripts/audit_backend_e2e_light_v1.py

```python
#!/usr/bin/env python3
"""
Light E2E gate — SourceA hub.
No blocking /refresh. Completes in < 30s.
Includes four-rule static proof.
"""
from __future__ import annotations
import json, subprocess, sys, time, urllib.request
from pathlib import Path

HUB  = "http://127.0.0.1:13020"
FAIL: list[str] = []


def chk(name: str, method: str, path: str,
        body=None, max_ms: int = 2000, expect: int = 200):
    t0   = time.time()
    data = json.dumps(body).encode() if body else None
    req  = urllib.request.Request(
        f"{HUB}{path}", data=data, method=method,
        headers={"Content-Type": "application/json"} if data else {},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            ms = int((time.time() - t0) * 1000)
            json.loads(r.read())
            if r.status != expect:
                FAIL.append(f"STATUS  {name}: got {r.status}, want {expect}")
            elif ms > max_ms:
                FAIL.append(f"SLOW    {name}: {ms}ms > {max_ms}ms limit")
            else:
                print(f"PASS    {name} ({ms}ms)")
    except Exception as e:
        FAIL.append(f"ERROR   {name}: {e}")


# --- Latency checks ---
chk("health",        "GET",  "/health",                  max_ms=500)
chk("hub-sync",      "GET",  "/api/hub-sync",            max_ms=200)
chk("agent-loop",    "GET",  "/api/agent-loop",          max_ms=3000)
chk("ic-get",        "GET",  "/api/intelligence-circle", max_ms=3000)
chk("prompt-queue",  "GET",  "/api/prompt-queue",        max_ms=3000)
chk("clear-session", "POST", "/api/intelligence-circle",
    body={"action": "clear_session"}, max_ms=1000)
chk("refresh-async", "POST", "/refresh",
    body={}, max_ms=1000, expect=202)

# --- generation_id must be present ---
try:
    with urllib.request.urlopen(f"{HUB}/api/hub-sync", timeout=5) as r:
        d = json.loads(r.read())
        gid = d.get("generation_id")
        if gid is not None:
            print(f"PASS    generation_id={gid}")
        else:
            FAIL.append("FAIL    generation_id missing from hub-sync response")
except Exception as e:
    FAIL.append(f"ERROR   generation_id check: {e}")

# --- Queue truth (C-H10 corrected) ---
truth = Path.home() / ".sina" / "run-inbox-disk-truth-v1.json"
if truth.exists():
    t   = json.loads(truth.read_text())
    sa  = t.get("queue", {}).get("sa_id", "MISSING")
    (print(f"PASS    queue.sa_id={sa}")
     if sa.startswith("sa-")
     else FAIL.append(f"FAIL    queue.sa_id unexpected: {sa}"))
else:
    FAIL.append("FAIL    run-inbox-disk-truth-v1.json missing")

# --- Worker running ---
wl = Path.home() / ".sina" / "hub-rebuild-worker-v1.lock"
(print("PASS    worker lock present")
 if wl.exists()
 else FAIL.append("FAIL    worker not running (lock missing)"))

# --- Four-rule static proof ---
r = subprocess.run(
    ["grep", "-n",
     r"build_payload\|write_panel_outputs\|hub_after_mutation\|run_refresh_pipeline",
     "scripts/sina-command-server.py",
     "scripts/sina_command_lib.py"],
    capture_output=True, text=True,
)
violations = [
    line for line in r.stdout.splitlines()
    if not any(x in line for x in
               ("def ", "#", "_enqueue", "hub_queue_lib",
                "worker", "_lib_enqueue", "import"))
]
if violations:
    FAIL.append(f"FAIL    four-rule violations: {len(violations)} line(s)")
    for v in violations:
        print(f"  VIOLATION: {v}")
else:
    print("PASS    four request-thread rules satisfied")

# --- Result ---
if FAIL:
    print("\nFAILURES:")
    for f in FAIL:
        print(" ", f)
    sys.exit(1)

print("\nPASS    all light E2E checks")
sys.exit(0)
```

### Final gate sequence

```bash
bash scripts/validate-hub-stabilization-e2e-light-v1.sh   # SSOT + port catalog + worker ensure + light E2E
python3 scripts/find_critical_bugs.py                        # critical 0; includes :13030 probe (P5)
```

`validate-ecosystem-safety-v1.sh` — PASS when hub + worker healthy (P8 unblocked session index + Safety API + live pack idle checks).

### Write receipt

```python
python3 -c "
import yaml, time, json
from pathlib import Path
t  = json.loads((Path.home()/'.sina'/'run-inbox-disk-truth-v1.json').read_text())
sa = t.get('queue', {}).get('sa_id', 'sa-0778')
yaml.dump({
  'rebuilt_at':                      time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
  'prompt_id':                       'HUB_STABILIZATION_v5.1_FINAL',
  'architecture':                    'modular-monolith+tier-router+single-worker+dirty-coalesce',
  'four_rules':                      'request thread never builds/writes/validates/refreshes',
  'hub_after_mutation_request_thread': 0,
  'hub_sync_latency':                '<200ms',
  'worker':                          'hub_rebuild_worker_v1.py standalone :13030',
  'worker_health':                   'http://127.0.0.1:13030/health',
  'coalescing':                      True,
  'generation_id':                   True,
  'ports':                           [13020, 13030],
  'gate':                            'PASS',
  'next_task':                       sa,
}, open('latest.yaml', 'w'))
print('Receipt written. next_task:', sa)
"
```

---

## TRACK 2 — Projection disposable acceptance (P1 / G3)

**Criterion:** Hub is a **projection**, not state. **P1 split:** materializer writes **canonical** + **runtime** views; validator hashes **canonical only** (no exclusion-list decay).

| File | Role |
|------|------|
| `command-data-canonical.json` | Deterministic SSOT render — **fingerprint target** |
| `command-data-runtime.json` | Ephemeral mirrors (`agent_loop`, `fleet`, queues, timestamps) |
| `command-data.json` | Full hub (canonical + runtime) for `:13020` backward compat |

| Step | Action |
|------|--------|
| 1 | Snapshot canonical fingerprint (`hub_projection_canonical_v1.py`) |
| 2 | Delete hub projection files (full + canonical + runtime + shell) |
| 3 | Run materializer: `python3 scripts/align_command_data_ui_v1.py` |
| 4 | Compare canonical fingerprint — **PASS** if equal |

**Gate:**

```bash
cd ~/Desktop/SourceA && bash scripts/validate-hub-projection-disposable-v1.sh
```

**Law:** `brain-os/law/GOVERNANCE_RUNTIME_GOLDEN_RULE_LOCKED_v1.md` — *Projections are disposable.*

**Note:** `generation_id` drift alone is not a PASS failure if semantic content matches; persistent semantic drift means hub still holds unique state (P1 load-bearing).

---

## ABSOLUTE CONSTRAINTS

1. **FREEZE active.** No drain, no factory resume, no `factory_control_v1.py` changes.
2. **Ports 13021–13023 occupied.** New ports (Phase N only): 13030+, after `lsof` check and ASF approval.
3. **Queue truth:** `~/.sina/run-inbox-disk-truth-v1.json` → `t.get("queue",{}).get("sa_id")`.
4. **Sequential phases.** A → B → C → E. One phase = one gate report = one approval.
5. **Zero Flask.** Hub = one process on `:13020`. Worker = separate process on `:13030` (N1). Not microservices — shared queue only.
6. **`hub_queue_lib_v1.py` is the only queue writer.** Both server and lib import it. Never duplicate the fcntl append pattern inline.
7. **`generation_id` everywhere** (not `generation`). Worker bumps via `bump_shell_generation_id()`; hub-sync returns it.
8. Restart via `serve-sina-command.sh` (worker-first chain). Use `kill-sina-command.sh` then `kill-hub-rebuild-worker.sh` for clean stop (P2).
9. `SINA_FORCE_RESTART=1 bash scripts/serve-sina-command.sh && sleep 3` after any server or worker edit.
10. **Do not run `audit_backend_e2e.py`** unless opt-in (`SINA_E2E_FORCE=1`). Default gate: `validate-hub-stabilization-e2e-light-v1.sh`.
11. **Conduct/INCIDENT-023/orchestrator desync:** parallel tracks — not hub gates.
12. **N1 shipped** (`:13030`). N2+ separate services require explicit ASF approval + `lsof` port check.

---

## APPROVAL PHRASES (strict — one phase at a time)

| To start | Say exactly |
|----------|-------------|
| Phase A | `ASF: EDIT ALLOWED — Phase A only` |
| Phase B | `ASF: Phase B approved` |
| Phase C | `ASF: Phase C approved` |
| Phase E | `ASF: Phase E approved` |
| Phase N | `ASF: Phase N approved` |

**Implementation: A–E + N1 + P1–P10 DONE.**  
Phases A–E and N1 shipped logged; stabilization backlog P1–P10 complete (Gate N receipt 2026-06-10).

### N2 candidates (deferred — ASF explicit approval + `lsof`)

| Candidate | Port | Scope | When |
|-----------|------|-------|------|
| State service | `:13031` | Sole writer: queue truth, `PROGRAM_PROGRESS`, inbox projection | After Track 2 L5 green |
| Agent runtime | `:13032` | FREEZE, IC sessions, agent-loop spawn gate | After State stable 1 week |
| IC path extract | — | Move intelligence-circle heavy paths off gateway | N2+ |
| Agent-loop extract | — | Loop spawn + inbox deliver off gateway | N2+ |

Do not start N2 without `ASF: Phase N2 approved` and empty `lsof :13031`.
