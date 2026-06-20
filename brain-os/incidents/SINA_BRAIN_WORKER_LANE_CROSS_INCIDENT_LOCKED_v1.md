# Brain / Worker lane cross — misdelivered prompt incident (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **sequence_id:** SA-2026-06-07-INCIDENT-003  
**Classification:** MANDATORY READ — Brain · executor autoloop  
**Incident:** Worker healthy-drain prompt appeared in Brain chat; Brain ran validators (wrong lane).

---

## Rule (never again)

| Chat | Sees `[GOAL1_HEALTHY_DRAIN]` or Worker paste | Action |
|------|-----------------------------------------------|--------|
| **Brain** | Yes | **REFUSE** — `BRAIN_REFUSE_WORKER_PROMPT` — no shell, no implement |
| **Worker** | Yes | Execute per `MANDATORY_SOURCEA_WORKER_CHAT` |

**Mechanical:** `python3 scripts/brain_lane_guard.py --stdin` on Brain turns containing worker signals.

**Before autoloop inject:** `brain_lane_guard.py --headsup` writes `~/.sina/worker-loop-headsup-v1.json` — ASF switches to Worker window.

---

## ASF heads-up (founder)

When executor starts Goal 1 loop turn:

1. Hub/state file updated — **not** “run in Brain”
2. Founder opens **SourceA Worker** chat
3. Worker reads INBOX or says **run inbox**
4. Brain stays available for routing questions only

---

*End incident*
