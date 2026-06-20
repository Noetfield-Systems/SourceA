# Brain fast startup (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Locked:** 2026-06-14 · **Authority:** ASF  
**Script:** `scripts/brain_fast_startup_v1.py`  
**Receipt:** `~/.sina/brain-fast-startup-v1.json` (mirrors `brain-self-heal-startup-v1.json`)  
**Wired:** `brain-session-start.sh` (default) · `brain_self_heal_startup_v1.py` · `worker_turn_entry_v1.sh` · `brain_run_loop_v1.py`

---

## Default (commercial drain)

`SINA_BRAIN_FAST=1` is **ON by default** in `brain-session-start.sh` and `worker_turn_entry_v1.sh`.

| Step | Action | Max time |
|------|--------|----------|
| 1 | Hub health probe (no restart unless DOWN) | 3s |
| 2 | Validators + queue (skip if fast receipt <5 min) | 0–2s |
| 3 | Live-pack receipt refresh (only when stale) | 0–10s |
| 4 | Clear orchestrator ghost `stop_reason` | <1s |
| 5 | Heal bind mismatch (queue/inbox/turn) | <2s |
| 6 | Write `brain-goal1-validation-v1.json` → route Worker INBOX | <1s |

**Target:** session start **<3s** when receipt fresh.

---

## Health + wisdom (every tick)

Receipt includes `health` + `health.wise`:

| Field | Meaning |
|-------|---------|
| `health.healthy` | Composite disk truth — hub · bind · honesty · chain |
| `health.score` | e.g. `8/8` checks passed |
| `health.wise.do_now` | Single action — usually Worker RUN INBOX |
| `health.wise.do_not` | Forbidden in Brain chat (implement · E2E · re-deliver) |
| `health.wise.why` | One-line routing reason from disk |

Brain is **wise** when it routes Worker without diagnosing, lying about progress, or crossing the beneficial line.

- **Route only** — Worker executes INBOX  
- **Forbidden on start:** hospital · maze · orientation · E2E full/standard · hub rebuild sync  
- **Forbidden in Brain chat:** `&&` validator chains · implement · closeout  

---

## Env flags (machine)

| Flag | Effect |
|------|--------|
| `SINA_BRAIN_FAST=1` | Fast startup + skip hub projection on brain_sync |
| `SINA_COMMERCIAL_LOOP=1` | Skip 10s live-pack on orchestrator deliver |
| `SINA_BROKER_FAST=1` | Skip slow broker brain_sync on submit |

---

## Validator

`bash scripts/validate-brain-fast-startup-v1.sh`

---

*End BRAIN_FAST_STARTUP_LOCKED_v1*
