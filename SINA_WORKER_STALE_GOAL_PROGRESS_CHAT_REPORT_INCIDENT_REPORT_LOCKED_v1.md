# Worker chat stale goal_progress & false repeating steps — incident report (pointer)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**LOCKED body:** `brain-os/incidents/SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_REPORT_INCIDENT_LOCKED_v1.md`
**trace_tag:** `AUTO-TRACE-WORKER-STALE-GOAL-PROGRESS-INCIDENT-v1.0`
**agent:** `Auto` · **role:** `SourceA-Worker` · **repo:** `sourcea`
**sequence_id:** SA-2026-06-10-INCIDENT-010
**MANDATORY READ:** SourceA Worker · Brain · Maintainer · all Cursor executor agents

**Summary:** Worker parroted stale inject `goal_progress` (**157/1000**) while disk advanced (**158/1000**). Queue moved (19/30 · sa-0090 CHECK) but chat felt like repeating steps. Three signals disagreed: honest bar · queue cursor · TRACK BACKLOG.

**Never forget:** Run `goal-progress-v1.py` every progress claim — never copy INBOX SESSION MEMORY. Honest +1 only on VERIFY closeout, not per inbox turn.

Read the full incident at the path above before reporting progress or draining the healthy queue.
