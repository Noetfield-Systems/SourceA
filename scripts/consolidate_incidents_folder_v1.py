#!/usr/bin/env python3
"""File missing incident bodies + near-miss index into brain-os/incidents/ (INCIDENT-021 law)."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INC = ROOT / "brain-os/incidents"

POINTER = """# {title} — root pointer

**Canonical body:** `brain-os/incidents/{body_name}`
**Registry:** `brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md`
**Near-miss index:** `brain-os/incidents/NEAR_MISS_AND_UNFILED_INCIDENTS_INDEX_LOCKED_v1.md`

Read canonical body at path above (INCIDENT-021).
"""

NEAR_MISS_INDEX = """# Near-miss & unfiled incident surfaces — master index (LOCKED v1)

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
| C02 | Hub edit `.mdc` vs EDIT_LOCK | Open — scope by role |
| C03 | Compendium ends 010 vs registry 025 | Open — compendium pointer |
| C04 | INCIDENT-012 superseded body | **Archived** |
| C05 | Mandatory read `os/chat-handoffs/` empty | Open — paths → brain-os |
| C06 | Brain rules in Worker chat | Open — role globs |
| C07 | Prompt feed vs run inbox | **Resolved** — LIVE_ONGOING_PROMPTS |
| C08 | S10 vs bash subject | **Resolved** — INCIDENT-019/020 + tombstone |
| C09 | Duplicate bodies root + brain-os | **Remediation** — pointers only at root |
| C10 | START_HERE path drift | Open |
| C11 | INCIDENT-011 jsonl reuse | **Resolved** — 014 monitor |
| C12 | Maintainer editor vs EDIT_LOCK | Open |

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
"""


def copy_body_if_missing(src: Path, dest_name: str) -> None:
    dest = INC / dest_name
    if dest.exists() and dest.stat().st_size > 500:
        return
    if not src.is_file():
        return
    shutil.copy2(src, dest)


def write_pointer(root_name: str, body_name: str, title: str) -> None:
    path = ROOT / root_name
    text = POINTER.format(title=title, body_name=body_name)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    INC.mkdir(parents=True, exist_ok=True)

    copy_body_if_missing(
        ROOT / "SINA_COMMAND_MAINTAINER_SELF_AUDIT_INCIDENT_LOCKED_v1.md",
        "SINA_COMMAND_MAINTAINER_SELF_AUDIT_INCIDENT_LOCKED_v1.md",
    )
    write_pointer(
        "SINA_COMMAND_MAINTAINER_SELF_AUDIT_INCIDENT_LOCKED_v1.md",
        "SINA_COMMAND_MAINTAINER_SELF_AUDIT_INCIDENT_LOCKED_v1.md",
        "INCIDENT-005b Maintainer self-audit",
    )

    copy_body_if_missing(
        ROOT / "SINA_AGENT_INCIDENT_ROOM_LOCKED_v1.md",
        "SINA_AGENT_INCIDENT_ROOM_LOCKED_v1.md",
    )
    write_pointer(
        "SINA_AGENT_INCIDENT_ROOM_LOCKED_v1.md",
        "SINA_AGENT_INCIDENT_ROOM_LOCKED_v1.md",
        "Agent Incident Room procedure",
    )

    copy_body_if_missing(
        ROOT / "AGENT_RULE_CONFLICT_AND_STALE_TRUTH_AUDIT_LOCKED_v1.md",
        "AGENT_RULE_CONFLICT_AND_STALE_TRUTH_AUDIT_LOCKED_v1.md",
    )
    write_pointer(
        "AGENT_RULE_CONFLICT_AND_STALE_TRUTH_AUDIT_LOCKED_v1.md",
        "AGENT_RULE_CONFLICT_AND_STALE_TRUTH_AUDIT_LOCKED_v1.md",
        "Agent rule conflict & stale truth audit",
    )

    (INC / "NEAR_MISS_AND_UNFILED_INCIDENTS_INDEX_LOCKED_v1.md").write_text(
        NEAR_MISS_INDEX, encoding="utf-8"
    )

    tombstone_015 = """# ARCHIVE — 015-CONDUCT draft (SUPERSEDED)

**Do not cite.** Pre-registry conduct report filed before INCIDENT-023.

| Use | Path |
|-----|------|
| **Canonical conduct** | `SINA_FACTORY_STOP_IGNORED_AUTODRAIN_INCIDENT_023_LOCKED_v1.md` |
| **ID collision only** | `SINA_AGENT_INCIDENT_ID_COLLISION_WITHOUT_REGISTRY_CHECK_INCIDENT_015_LOCKED_v1.md` |
| **Archived full draft** | `archive/superseded/incidents/INCIDENT-015-agent-ignored-stop-resumed-drain-loop_LOCKED_REPORT_v1.md` |

**Registry:** INCIDENT-023 = STOP ignored · **015** = registry ID filing mistake only.
"""
    (INC / "SINA_ARCHIVE_015_CONDUCT_DRAFT_SUPERSEDED_LOCKED_v1.md").write_text(
        tombstone_015, encoding="utf-8"
    )

    adjunct_014 = """# INCIDENT-014 completion adjunct (LOCKED)

**Version:** 1.0 — adjunct to INCIDENT-014  
**Canonical incident:** `SINA_MONITOR_BRAIN_COLUMN_SNAPSHOT_DRIFT_INCIDENT_014_LOCKED_v1.md`  
**Full essay (archive):** `archive/attachments/2026-06-10/SOURCEA_BRAIN_REPAIR_AUDIT_AND_INCIDENT_014_COMPLETION_LOCKED_v1.md`

## Summary

Brain PEND on green rows = stale `brain-goal1-validation-v1.json` — not redo Worker turns.  
Shipped: `brain_sync_lib_v1.py` hooks · `validate-brain-snapshot-sync-v1.sh` · hub refresh path.

**Fix:** `brain_validate_goal1.py --write-receipt` + monitor refresh.
"""
    (INC / "SINA_BRAIN_REPAIR_INCIDENT_014_COMPLETION_ADJUNCT_LOCKED_v1.md").write_text(
        adjunct_014, encoding="utf-8"
    )

    write_pointer(
        "SINA_FACTORY_STOP_IGNORED_AUTODRAIN_INCIDENT_023_REPORT_LOCKED_v1.md",
        "SINA_FACTORY_STOP_IGNORED_AUTODRAIN_INCIDENT_023_LOCKED_v1.md",
        "INCIDENT-023 Factory STOP ignored",
    )

    (ROOT / "SINA_STATIC_PROMPT_FEED_STALE_LIST_INCIDENT_024_REPORT_LOCKED_v1.md").write_text(
        """# INCIDENT-024 pointer — Static Prompt feed stale 10-pack

**Canonical body:** `brain-os/incidents/SINA_STATIC_PROMPT_FEED_STALE_LIST_INCIDENT_024_LOCKED_v1.md`  
**Remediation:** `SOURCEA_LIVE_ONGOING_PROMPTS_LOCKED_v1.md`  
**Status:** remediated 2026-06-10
""",
        encoding="utf-8",
    )

    print("OK: consolidate_incidents_folder_v1")


if __name__ == "__main__":
    main()
