#!/usr/bin/env python3
"""One-shot archive pass — batches A–E (founder-approved 2026-05-27)."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ARCHIVE_BANNER = (
    "> **ARCHIVE ONLY — not canonical law.** "
    "Authority: `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` · "
    "`brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md`.\n\n"
)

POINTER_MOVED = """# MOVED — canonical SSOT

**Do not edit this stub.**

Canonical path: `{canonical}`

Archived stub copy: `{archive_path}`

Law: `brain-os/INDEX_LOCKED_v1.md`
"""

TOMBSTONE_012 = """# SUPERSEDED — do not cite (INCIDENT-012)

**Use instead:** `brain-os/incidents/SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_INCIDENT_013_LOCKED_v1.md`

Archived body: `archive/superseded/incidents/SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_INCIDENT_012_LOCKED_v1.md`
"""

TOMBSTONE_REPORT_WRONG = """# SUPERSEDED — do not cite (wrong id INCIDENT-010 reuse)

**Use instead:** **INCIDENT-013**
- `brain-os/incidents/SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_INCIDENT_013_LOCKED_v1.md`
- `SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_INCIDENT_013_REPORT_LOCKED_v1.md`

Archived body: `archive/superseded/incidents/SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_REPORT_INCIDENT_LOCKED_v1.md`
"""

POINTER_012_REPORT = """# SUPERSEDED — use INCIDENT-013

**Do not cite.** Canonical:
- `brain-os/incidents/SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_INCIDENT_013_LOCKED_v1.md`
- `SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_INCIDENT_013_REPORT_LOCKED_v1.md`

Archived duplicate: `archive/superseded/incidents/SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_INCIDENT_012_LOCKED_v1.md`
"""

POINTER_GOAL1_LOOP = """# Goal 1 loop unvalidated proof — LOCKED (root pointer)

**Canonical body:** `brain-os/incidents/SINA_GOAL1_LOOP_UNVALIDATED_PROOF_INCIDENT_LOCKED_v1.md`
**Root report:** `SINA_GOAL1_LOOP_UNVALIDATED_PROOF_INCIDENT_REPORT_LOCKED_v1.md`

Do not duplicate prose at repo root (INCIDENT-021).
"""

CONTRACT_POINTER = """# SUPERSEDED — archived

**Do not cite for current doctrine.**

Archived: `{archive_path}`

**Use instead:** `brain-os/laws/FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md`
"""

MOVED_ROOT_STUBS: list[tuple[str, str]] = [
    ("CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md", "brain-os/law/CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md"),
    ("AGENT_RULES_IN_CHARGE_LOCKED_v1.md", "brain-os/law/AGENT_RULES_IN_CHARGE_LOCKED_v1.md"),
    ("DISPATCH_POLICY_LOCKED_v1.md", "brain-os/law/DISPATCH_POLICY_LOCKED_v1.md"),
    ("WORLD_TARGET_MODEL_MAP_LOCKED_v5.md", "brain-os/wtm/WORLD_TARGET_MODEL_MAP_LOCKED_v5.md"),
    ("WORLD_TARGET_MODEL_AUTHORITY_LAW_LOCKED_v1.md", "brain-os/wtm/WORLD_TARGET_MODEL_AUTHORITY_LAW_LOCKED_v1.md"),
    ("WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v2.md", "brain-os/wtm/WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v2.md"),
    ("WORLD_TARGET_MODEL_STEP_ID_MIGRATION_LOCKED_v1.md", "brain-os/wtm/WORLD_TARGET_MODEL_STEP_ID_MIGRATION_LOCKED_v1.md"),
    ("WORLD_TARGET_MODEL_ARCHITECTURE_DIAGRAM_LOCKED_v1.md", "brain-os/wtm/WORLD_TARGET_MODEL_ARCHITECTURE_DIAGRAM_LOCKED_v1.md"),
    ("WORLD_TARGET_MODEL_UI_RESEARCH_LOCKED_v1.md", "brain-os/wtm/WORLD_TARGET_MODEL_UI_RESEARCH_LOCKED_v1.md"),
    ("WORLD_TARGET_MODEL_UI_INCIDENT_REPORT_LOCKED_v1.md", "brain-os/wtm/WORLD_TARGET_MODEL_UI_INCIDENT_REPORT_LOCKED_v1.md"),
    ("WORLD_TARGET_MODEL_PHASE_NAMING_INCIDENT_REPORT_LOCKED_v1.md", "brain-os/wtm/WORLD_TARGET_MODEL_PHASE_NAMING_INCIDENT_REPORT_LOCKED_v1.md"),
    ("WORLD_TARGET_MODEL_FULL_BLUEPRINT_FOR_REVIEW_v1.md", "brain-os/wtm/WORLD_TARGET_MODEL_FULL_BLUEPRINT_FOR_REVIEW_v1.md"),
    ("WORLD_TARGET_MODEL_FULL_BLUEPRINT_FOR_REVIEW_v2.md", "brain-os/wtm/WORLD_TARGET_MODEL_FULL_BLUEPRINT_FOR_REVIEW_v2.md"),
    ("SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md", "brain-os/wtm/SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md"),
    ("SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2.md", "brain-os/wtm/SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2.md"),
    ("SINA_BRAIN_WORKER_LANE_CROSS_INCIDENT_LOCKED_v1.md", "brain-os/incidents/SINA_BRAIN_WORKER_LANE_CROSS_INCIDENT_LOCKED_v1.md"),
    ("SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md", "brain-os/incidents/SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md"),
    ("CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_LOCKED_v1.md", "brain-os/incidents/CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_LOCKED_v1.md"),
    ("SINA_HEALTHY_DRAIN_PROMPT_FEASIBILITY_INCIDENT_REPORT_LOCKED_v1.md", "brain-os/incidents/SINA_HEALTHY_DRAIN_PROMPT_FEASIBILITY_INCIDENT_REPORT_LOCKED_v1.md"),
]

BATCH_A_BRAIN = [
    "SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_INCIDENT_012_LOCKED_v1.md",
    "SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_REPORT_INCIDENT_LOCKED_v1.md",
]

BATCH_D_MOVES = [
    ("brain-os/contract/AUTOMATION_CONVERGE_PROGRAM_LOCKED_v1.md", "archive/superseded/contract/"),
    ("brain-os/contract/TODAY_AUTORUN_50_PLAN_LOCKED_v1.md", "archive/superseded/contract/"),
    ("brain-os/contract/BRAIN_FULL_TRANSFER_PROMPT_LOCKED_v1.md", "archive/superseded/contract/"),
    ("brain-os/laws/AUTO_RUN_FULLY_AUTOMATIC_LOCKED_v1.md", "archive/superseded/laws/"),
]

ATTACHMENT_015 = (
    "archive/attachments/2026-06-10/"
    "INCIDENT-015-agent-ignored-stop-resumed-drain-loop_LOCKED_REPORT_v1.md"
)


def move_to_archive(src: Path, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name
    if src.exists():
        shutil.move(str(src), str(dest))
    return dest


def ensure_banner(path: Path) -> None:
    if not path.exists() or path.suffix not in {".md"}:
        return
    text = path.read_text(encoding="utf-8")
    if "ARCHIVE ONLY — not canonical law" in text:
        return
    path.write_text(ARCHIVE_BANNER + text, encoding="utf-8")


def main() -> None:
    # Batch A — tombstone bodies
    for name in BATCH_A_BRAIN:
        src = ROOT / "brain-os/incidents" / name
        if src.exists():
            move_to_archive(src, ROOT / "archive/superseded/incidents")
    (ROOT / "brain-os/incidents/SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_INCIDENT_012_LOCKED_v1.md").write_text(
        TOMBSTONE_012, encoding="utf-8"
    )
    (ROOT / "brain-os/incidents/SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_REPORT_INCIDENT_LOCKED_v1.md").write_text(
        TOMBSTONE_REPORT_WRONG, encoding="utf-8"
    )
    (ROOT / "SINA_WORKER_STALE_GOAL_PROGRESS_CHAT_INCIDENT_012_REPORT_LOCKED_v1.md").write_text(
        POINTER_012_REPORT, encoding="utf-8"
    )
    src015 = ROOT / ATTACHMENT_015
    if src015.exists():
        move_to_archive(src015, ROOT / "archive/superseded/incidents")
        banner_path = ROOT / "archive/superseded/incidents" / src015.name
        extra = (
            "> **SUPERSEDED conduct filing.** **015** = ID collision only. "
            "Conduct STOP ignored → **INCIDENT-023**.\n\n"
        )
        text = banner_path.read_text(encoding="utf-8")
        if "SUPERSEDED conduct filing" not in text:
            banner_path.write_text(ARCHIVE_BANNER + extra + text.lstrip(), encoding="utf-8")

    # Batch B — root duplicate LOCKED body
    goal1_root = ROOT / "SINA_GOAL1_LOOP_UNVALIDATED_PROOF_INCIDENT_LOCKED_v1.md"
    if goal1_root.exists():
        body = goal1_root.read_text(encoding="utf-8")
        if len(body.splitlines()) > 12:
            move_to_archive(goal1_root, ROOT / "archive/superseded/incidents")
            (ROOT / "SINA_GOAL1_LOOP_UNVALIDATED_PROOF_INCIDENT_LOCKED_v1.md").write_text(
                POINTER_GOAL1_LOOP, encoding="utf-8"
            )

    # Batch C — MOVED stubs
    for rel, canonical in MOVED_ROOT_STUBS:
        src = ROOT / rel
        if not src.exists():
            continue
        archive_dest = ROOT / "archive/superseded/pointers" / rel
        archive_dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, archive_dest)
        src.write_text(
            POINTER_MOVED.format(canonical=canonical, archive_path=f"archive/superseded/pointers/{rel}"),
            encoding="utf-8",
        )

    # Batch D — superseded contract/laws
    for rel, dest_rel in BATCH_D_MOVES:
        src = ROOT / rel
        if not src.exists():
            continue
        dest_dir = ROOT / dest_rel
        archived = move_to_archive(src, dest_dir)
        archive_rel = archived.relative_to(ROOT).as_posix()
        (ROOT / rel).write_text(CONTRACT_POINTER.format(archive_path=archive_rel), encoding="utf-8")

    # Batch E — archive attachment banners
    attach_dir = ROOT / "archive/attachments/2026-06-10"
    if attach_dir.is_dir():
        for path in sorted(attach_dir.iterdir()):
            ensure_banner(path)

    print("OK: archive_suppressed_docs_v1")


if __name__ == "__main__":
    main()
