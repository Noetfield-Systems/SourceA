# Brain — no leftover process (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-08  
**Law:** Brain must **never** end a turn with orphan Goal 1 / overnight / API / CLI processes.

---

## 0. One sentence

**After every Brain turn that spawns or touches the loop, run cleanup and prove `remaining_count: 0` — or STOP and do not claim the loop is running.**

---

## 1. What counts as a leftover (FORBIDDEN)

| Pattern | Why |
|---------|-----|
| `start-overnight-3engine-v1.sh` | Background daemon after chat timeout |
| `autorun_dispatcher_v1.py` | 30s tick without founder |
| `claude_api_agent_v1.py` / `claude_code_agent_v1.py` | Orphan API/CLI turn |
| `claude -p You are SourceA Worker` | Orphan CLI child |
| `goal1_*loop*` / `brain_execute_turn_v1.py` | Batch / execute orphans |
| Stale `~/.sina/overnight-3engine-v1.pid` | False “already running” |

**Cursor overnight from maintainer chat is also FORBIDDEN** — `FOUNDER_BUSY_OPERATING_MODEL` + no Cursor autorun.

---

## 2. Mandatory end-of-turn (Brain)

```bash
cd /Users/sinakazemnezhad/Desktop/SourceA
python3 scripts/cleanup-goal1-leftovers-v1.py --json
```

| Result | Brain must |
|--------|------------|
| `ok: true` · `remaining_count: 0` | Reply may cite loop state |
| `ok: false` | **STOP** — report `remaining_pids` — **no** “loop is running” |

Paste prompt: `brain-os/contract/BRAIN_END_TURN_NO_LEFTOVER_PROMPT_LOCKED_v1.md`

---

## 3. Executor (not founder)

- **Hub:** Actions → Stop Goal 1 executor  
- **Maintainer:** `python3 scripts/cleanup-goal1-leftovers-v1.py`  
- **Overnight start:** must call cleanup first if stale pid/procs exist  

Founder never runs Terminal — one-tap Actions only.

---

*End BRAIN NO LEFTOVER PROCESS v1*
