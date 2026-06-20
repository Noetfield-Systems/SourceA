# INCIDENT-031 — Worker ignored ASF no-hub stop (pointer)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**LOCKED body:** `brain-os/incidents/SINA_WORKER_IGNORED_ASF_NO_HUB_STOP_STALE_STEERING_INCIDENT_031_LOCKED_v1.md`

**What:** ASF said **no hub rebuild / no hub archive**. Agent said “no hub rebuild” then **steered to sa-0857 hub-ui**, hub refresh hygiene, and “continue hub lane” — **stupid stale template**.

**Owner:** Worker agent (main) · Machine latch gap (structural) — **fixed same day**.

**Permanent:** `scripts/worker_asf_directive_latch_v1.py` · `agent_turn_context_v1.py` injects ASF directive block.

**Latch:** **ON** — no hub steering until ASF clears.
