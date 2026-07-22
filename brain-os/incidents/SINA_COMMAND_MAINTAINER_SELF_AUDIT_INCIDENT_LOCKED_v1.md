# Sina Command Maintainer — Repeat Mistake / No Memory Incident (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-05-27-INCIDENT-005  
**Classification:** INTERNAL — MANDATORY READ for `sinaai_maintainer` every session  
**Canonical location:** `brain-os/incidents/SINA_COMMAND_MAINTAINER_SELF_AUDIT_INCIDENT_LOCKED_v1.md`  
**Root pointer:** `SINA_COMMAND_MAINTAINER_SELF_AUDIT_INCIDENT_LOCKED_v1.md`  
**Companion:** `scripts/maintainer_self_audit_loop.py` · `scripts/cursor_agent_self_audit.py` · skill `@agent-self-audit-loop`

---

## 1. Executive summary

The maintainer agent **repeated the same class of mistakes** because **chat memory is not SSOT** and **no disk-backed self-audit loop ran** before/after hub work:

| # | Symptom | Founder impact |
|---|---------|----------------|
| 1 | "You have no memory" — perf fixes shipped without closeout | Same bugs re-investigated; trust lost |
| 2 | Investigation started, conversation summarized, fixes **not finished** | Mac still lagging; user thinks nothing changed |
| 3 | Hub server restart tasks **aborted** — no follow-up reported | Stale server (~800MB RAM) kept running |
| 4 | WTM layout fixed twice (B\|D\|D → 3-col → 4-col) without incident lesson on disk | Regression risk on next UI pass |
| 5 | `index.html` re-bloated to ~3MB when old server ran old code | Hub slow; audits failed silently until manual check |

**Severity:** **High** — wastes founder Mac resources, repeats expensive `build_payload()` work, and breaks the "pro app" promise.

---

## 2. Root causes (verified 2026-05-27)

| # | Root cause | Evidence |
|---|------------|----------|
| 1 | No `session-start` before hub edits | `MANDATORY_READ_CHAIN.md` stale; `last_session_start_at` missing |
| 2 | No `session-close` after substantive hub work | `SESSION_CLOSEOUT_LATEST.md` empty or missing perf evidence |
| 3 | Context summarization dropped investigation state | Conversation summary ≠ disk; no `SESSION_LEDGER.jsonl` milestones |
| 4 | `build_payload()` on every API call (~2s, 2.5MB) | 30+ routes in `sina-command-server.py` before cache fix |
| 5 | Intelligence `ping`/`keepalive` rebuilt full hub | Background CPU every ~90s |
| 6 | Client polled every 12s / loop every 5s | Constant wake-ups + full re-renders |
| 7 | Aborted shell tasks not re-run | Server left on old code path |

---

## 3. Mandatory maintainer self-audit loop (every session)

### A — Session start (before any SourceA edit)

```bash
python3 ~/Desktop/SourceA/scripts/maintainer_self_audit_loop.py start
```

Reads in order:

1. `~/.sina/agent-workspaces/sinaai_maintainer/INCIDENT_REPORT_ALWAYS.md`
2. `~/Desktop/SourceA/CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_LOCKED_v1.md`
3. `~/Desktop/SourceA/SINA_COMMAND_MAINTAINER_SELF_AUDIT_INCIDENT_LOCKED_v1.md` (this file)
4. `~/.sina/agent-workspaces/sinaai_maintainer/memory/MISTAKE_REGISTRY_LOCKED.md`
5. `~/.sina/agent-workspaces/sinaai_maintainer/SESSION_CLOSEOUT_LATEST.md`
6. Skill: `~/.cursor/skills/agent-self-audit-loop/SKILL.md`

### B — Pre-flight (before hub Python/JS change)

```bash
python3 ~/Desktop/SourceA/scripts/maintainer_self_audit_loop.py preflight
```

Gate: `AUDIT_PASS` from `cursor_agent_self_audit.py audit` + mistake registry reviewed.

### C — During work

```bash
python3 ~/Desktop/SourceA/scripts/maintainer_self_audit_loop.py log \
  --summary "Hub cache + json_only writes shipped" \
  --evidence "sina_command_lib.py hub_after_mutation"
```

### D — Post-flight (before last reply)

```bash
python3 ~/Desktop/SourceA/scripts/maintainer_self_audit_loop.py postflight \
  --summary "..." --files "..." --verify "find_critical_bugs PASS" --next "founder hard refresh"
```

Runs: `find_critical_bugs.py` · hub health · server RSS check · `session-close`.

### E — Record repeat mistake (when caught)

```bash
python3 ~/Desktop/SourceA/scripts/maintainer_self_audit_loop.py record-mistake \
  --pattern "no session-close after perf fix" --fix "run postflight before reply"
```

---

## 4. Never again (maintainer blocklist)

- Do **not** claim perf/app is fixed without **verify evidence** in closeout (server RSS, `/health`, audit PASS)
- Do **not** end a hub implementation turn without `postflight` / `session-close`
- Do **not** rely on conversation summary — read `SESSION_CLOSEOUT_LATEST.md` after context compression
- Do **not** leave aborted restart tasks — re-run `pkill + sina-command-server.py` and report health
- Do **not** call `write_panel_outputs` on read-only API paths (mirror get, intelligence ping)
- Do **not** skip `build-sina-command-panel.py` after `app.js` / `app.css` changes
- Do **not** tell founder "done" without **hard refresh** reminder when JS changed

---

## 5. Performance guards (post-fix baseline)

| Check | Healthy | Action if fail |
|-------|---------|----------------|
| Server RSS | &lt; 150 MB idle | Restart hub; check for rebuild storm |
| `GET /command-data.json` | &lt; 50 ms (cached) | Verify `command_data_response()` active |
| `find_critical_bugs.py` | `critical: 0` | Stop — fix before ship |
| `index.html` size | &lt; 10 KB | Old inline JSON regression — rebuild panel |

---

## 6. Weekly

Share one lesson in **Incident Room** tab. Valid topics: no-memory repeat, Mac lag root cause, aborted task follow-up.

---

*Chat is not SSOT. Disk wins. Run the loop.*
