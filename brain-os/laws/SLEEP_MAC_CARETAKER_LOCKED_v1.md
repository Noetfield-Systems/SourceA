# Sleep Mac Caretaker (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.1 · **Locked:** 2026-06-08  
**Authority:** ASF  
**Parent:** `PRE_SLEEP_TRANSITION_LOCKED_v1.md` · `QUEUE_STATE_TRANSITION_LOCKED_v1.md`  
**Mechanism:** `scripts/sleep_mac_caretaker_v1.py` (event-driven — **no timer poll**)

---

## One sentence

**Caretaker runs on events only — after each sleep dispatch turn — not on a wasteful 300s loop.**

---

## Triggers (ONLY these)

| Trigger | When | What |
|---------|------|------|
| `post_dispatch` | End of every `autorun_dispatcher_v1.py` turn | Sync ACTIVE_NOW if drift · poll orchestrator · clear poison · sidecars on advance |
| `stuck_recovery` | Dispatcher failed 3× same pos OR overnight pid dead | Deliver · restart overnight once · log |

**Forbidden:** fixed-interval caretaker watch (300s / 180s poll) — cost leak, no value.

**Sleep sensor:** `APPLE_HEALTH_SLEEP_SIGNAL_LOCKED_v1.md` — Health `sleep_start`/`sleep_end`, not clock.

---

## When mandatory

Only while `founder_absent` + `Sleep Escalation: on`.

Hooked in `arm-sleep-mode-v1.sh` → overnight loop → dispatcher → **caretaker post_dispatch**.

---

## Founder law

- Executor owns Mac care during sleep — founder reads logs in morning
- `~/.sina/sleep-mac-caretaker-v1.jsonl` — one row per dispatch turn, not per timer

---

*LOCKED — Real player: act on state change, not on the clock.*
