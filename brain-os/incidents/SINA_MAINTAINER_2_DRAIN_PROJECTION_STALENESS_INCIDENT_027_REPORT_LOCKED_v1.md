
**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
[MAINTAINER_AGENT_REF · sinaai_maintainer · MAINT-REF-INCIDENT-027-001]

| Field | Value |
|-------|-------|
| **ref_tag** | `MAINT-REF-INCIDENT-027-001` |
| **trace_id** | `MAINT-REF-2026-06-11-INCIDENT-027-001` |
| **agent_id** | `sinaai_maintainer` |
| **mega_anchor** | `MAINTAINER_2` |
| **transcript_id** | `74f5ccab-d080-41a2-9f6d-b7c37c9aadc5` |
| **written** | `2026-06-11` |
| **canonical** | `false` (pointer — body in `brain-os/incidents/`) |

# INCIDENT-027 — Maintainer 2 drain/projection staleness (pointer)

**Classification:** High · Maintainer read wrong SSOT after form v2 fill  
**LOCKED body:** `brain-os/incidents/SINA_MAINTAINER_2_DRAIN_PROJECTION_STALENESS_INCIDENT_027_LOCKED_v1.md`  
**Archive mirror:** `archive/attachments/2026-06-11/INCIDENT-027-maintainer-2-drain-projection-staleness_LOCKED_REPORT_v1.md`

## One screen

After form **v2 FILLED** and **RT-LIVE-GATE** became Maintainer P0, Maintainer 2 kept headlining **factory drain** (`sa-0798`, Valid YES %, resume max 1) from **hub projection** and a **stale SCAN brief** (`needs_asf_fill: true`) instead of reading `PROGRAM_PROGRESS.founder_open`, `SESSION_LOG` Maintainer-next, and form §4. ASF: *"MOVE ON FROM DRAIN. READ THE DISK."*

## Disk proof

- Form JSON: `needs_asf_fill: false` · `open_questions_count: 0`
- `PROGRAM_PROGRESS` `founder_open`: RT LIVE gate · Phases 3–10 paused
- `SESSION_LOG`: Maintainer next = RT LIVE + FR-003
- Stale projection cited: `command-data.json` `p0.next_action` still has `sa-0798` · Worker INBOX

## Fix (Maintainer P0)

1. SCAN order: form JSON → PROGRAM_PROGRESS → SESSION_LOG → (projection last, labeled LAG)  
2. Hub P0 demote drain copy when RT-LIVE-GATE open  
3. Ship `validate-maintainer-scan-p0-v1.sh` (proposed)

**Do not** tell founder to run Terminal.
