# Brain self-healing startup (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Locked:** 2026-06-08 · **Authority:** ASF  
**Script:** `scripts/brain_self_heal_startup_v1.py` · **Fast path:** `scripts/brain_fast_startup_v1.py` (default)  
**Receipt:** `~/.sina/brain-self-heal-startup-v1.json` · **Fast receipt:** `~/.sina/brain-fast-startup-v1.json`  
**Wired:** `brain_run_loop_v1.py` · `brain-session-start.sh` · `worker_turn_entry_v1.sh`  
**Law:** `BRAIN_FAST_STARTUP_LOCKED_v1.md` — `SINA_BRAIN_FAST=1` default on commercial drain

---

## Mandatory sequence (every Brain session start)

**Fast path (default):** `brain_fast_startup_v1.py` — route Worker INBOX in <3s. Skips hospital/E2E/hub rebuild.

**Full path:** only when `SINA_BRAIN_FAST=0`.

| # | Step | Action |
|---|------|--------|
| 1 | CHECK HUB | `curl -sf http://127.0.0.1:13020/health` — if DOWN `launchctl kickstart -k gui/$UID/com.sourcea.hub` (law: `HUB_LAUNCHD_SUPERVISOR_LOCKED_v1.md`), wait 2s, re-verify. Still down → **P0 stop** |
| 2 | RUN VALIDATORS | `validate-file-storage-v1.sh` + `validate-master-operating-tracker-v1.sh` — autfix P1/P2 (pointer sync) |
| 3 | CHECK QUEUE | `healthy-queue-30-active.json` populated · `next-execution-pointer-v1.json` current — rebuild from REGISTRY if missing |
| 4 | WINDOW PREFLIGHT | `open -a Cursor` · sleep 1s (via `cursor_window_preflight_v1.py`) |
| 5 | SURFACE | All pass → **"System ready. AUTO-RUN active — no tap."** · P0 only → report blocker |

---

## ASF rule

ASF does not debug. ASF does not verify. ASF only taps one button when told ready.

---

*End BRAIN_SELF_HEAL_STARTUP_LOCKED_v1*
