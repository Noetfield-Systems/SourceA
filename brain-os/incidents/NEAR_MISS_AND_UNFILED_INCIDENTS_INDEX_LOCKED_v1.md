# Near-miss & unfiled incident surfaces — master index (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 LOCKED  
**sequence_id:** SA-2026-06-10-NEAR-MISS-INDEX  
**Canonical incidents:** `AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md` (001–025)  
**Subject taxonomy:** `INCIDENT_SUBJECT_INDEX_LOCKED_v1.md`  
**Rule:** Bodies live in `brain-os/incidents/` · root = pointer only · archive = mirror/tombstone only

---

## A — Filed late (now in `brain-os/incidents/`)

| Item | Body | Was |
|------|------|-----|
| Maintainer self-audit (005b) | `SINA_COMMAND_MAINTAINER_SELF_AUDIT_INCIDENT_LOCKED_v1.md` | Root-only body |
| Incident Room procedure | `SINA_AGENT_INCIDENT_ROOM_LOCKED_v1.md` | Root-only body |
| Rule conflict audit | `AGENT_RULE_CONFLICT_AND_STALE_TRUTH_AUDIT_LOCKED_v1.md` | Root-only adjunct |
| 023 STOP conduct | `SINA_FACTORY_STOP_IGNORED_AUTODRAIN_INCIDENT_023_LOCKED_v1.md` | Body ok · root pointer added |
| 024 stale prompt feed | `SINA_STATIC_PROMPT_FEED_STALE_LIST_INCIDENT_024_LOCKED_v1.md` | Body ok · root pointer added |
| 025 Advisor track naming | `SINA_AGENT_HUB_NAME_FRAGMENTATION_ADVISOR_TRACK_INCIDENT_025_LOCKED_v1.md` | Filed 2026-06-10 |

---

## B — Archive mirrors (do not cite as canonical)

| Archive path | Maps to | Note |
|--------------|---------|------|
| `archive/superseded/incidents/INCIDENT-015-agent-ignored-stop-resumed-drain-loop_LOCKED_REPORT_v1.md` | **INCIDENT-023** | Pre-registry conduct draft |
| `archive/attachments/2026-06-10/INCIDENT-022-maintainer-2-stale-autorun-advice_LOCKED_REPORT_v1.md` | **INCIDENT-022** | Mirror only |
| `archive/attachments/2026-06-10/SOURCEA_BRAIN_REPAIR_AUDIT_AND_INCIDENT_014_COMPLETION_LOCKED_v1.md` | **INCIDENT-014** adjunct | Completion essay |
| `archive/superseded/incidents/SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_INCIDENT_012_LOCKED_v1.md` | **INCIDENT-013** | Superseded duplicate |
| `archive/superseded/incidents/SINA_GOAL1_LOOP_UNVALIDATED_PROOF_INCIDENT_LOCKED_v1.md` | **INCIDENT-003a** | Root duplicate archived |

Tombstone: `SINA_ARCHIVE_015_CONDUCT_DRAFT_SUPERSEDED_LOCKED_v1.md`

---

## C — Near-misses (audit C01–C12 · S01–S10)

Source: `AGENT_RULE_CONFLICT_AND_STALE_TRUTH_AUDIT_LOCKED_v1.md`

| ID | Near-miss | Status |
|----|-----------|--------|
| C01 | INCIDENT-015 double meaning (ID vs conduct) | **Resolved** — 015 = ID · 023 = conduct |
| C02 | Hub edit `.mdc` vs EDIT_LOCK | **Resolved** 2026-06-10 — Hub Rules read-only Worker; Maintainer lane |
| C03 | Compendium ends 010 vs registry 025 | **Resolved** 2026-06-10 — Part A supplement 011–025 + registry pointer |
| C04 | INCIDENT-012 superseded body | **Archived** |
| C05 | Mandatory read `os/chat-handoffs/` empty | **Resolved** 2026-06-10 — `os/chat-handoffs/README_INDEX_LOCKED_v1.md` |
| C06 | Brain rules in Worker chat | **Resolved** 2026-06-10 — role-scoped `.mdc` + validate-cursor-rules-scoping |
| C07 | Prompt feed vs run inbox | **Resolved** — LIVE_ONGOING_PROMPTS |
| C08 | S10 vs bash subject | **Resolved** — INCIDENT-019/020 + tombstone |
| C09 | Duplicate bodies root + brain-os | **Remediation** — pointers only at root |
| C10 | START_HERE path drift | **Resolved** 2026-06-10 — `START_HERE.md` + `brain-os/entry/` + `entry/README` redirect |
| C11 | INCIDENT-011 jsonl reuse | **Resolved** — 014 monitor |
| C12 | Maintainer editor vs EDIT_LOCK | **Resolved** 2026-06-10 — same as C02 · Maintainer + Hub Rules scope |

---

## D — Advise-only mirrors (never SSOT)

| Path | Use instead |
|------|-------------|
| `RESEARCH/.../agent-auto-mono-2026-06-10-incidents-compendium-full.md` | Registry + compendium LOCKED |
| `RESEARCH/.../INCIDENT_FULL_SUMMARY_LOCKED_2026.md` | TrustField mirror only |
| `ECOSYSTEM_INCIDENTS_INDEX_LOCKED_v1.md` (root) | Hub builder index — not incident body |

---

## E — WTM adjunct incidents (`brain-os/wtm/`)

| ID | Body |
|----|------|
| 002a | `WORLD_TARGET_MODEL_UI_INCIDENT_REPORT_LOCKED_v1.md` |
| 002b | `WORLD_TARGET_MODEL_PHASE_NAMING_INCIDENT_REPORT_LOCKED_v1.md` |

---

## F — Remediation pending (not incidents)

| Path | Type |
|------|------|
| `brain-os/remediation/INCIDENT-005_FIX_BATCH_PENDING_ASF_CONFIRMATION_v1.md` | Remediation batch |

---

**END** — agents: new incident → registry row + body here + subject index update.
