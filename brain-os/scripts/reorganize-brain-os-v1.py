#!/usr/bin/env python3
"""One-time reorganize: unify Brain/disk/enforcement docs under brain-os/."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # SourceA root
BRAIN_OS = ROOT / "brain-os"

# dest_subdir -> list of (source_relative, filename stays same)
MOVES: dict[str, list[str]] = {
    "entry": [
        "entry/START_HERE_LOCKED_v1.md",
        "entry/MANDATORY_READ_BY_ROLE_LOCKED_v1.md",
        "entry/LAW_ROOT_INDEX_LOCKED_v1.md",
    ],
    "law": [
        "os/chat-handoffs/BRAIN_UNIFIED_RULES_LOCKED_v1.md",
        "os/chat-handoffs/BRAIN_RULES_AUTHORITY_INDEX_LOCKED_v1.md",
        "CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md",
        "SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md",
        "DISPATCH_POLICY_LOCKED_v1.md",
        "AGENT_RULES_IN_CHARGE_LOCKED_v1.md",
    ],
    "memory": [
        "os/chat-handoffs/BRAIN_MASTER_MEMORY_LOCKED_v1.md",
        "os/chat-handoffs/BRAIN_KNOWLEDGE_INDEX_LOCKED_v1.md",
        "os/chat-handoffs/BRAIN_FOUNDER_INTENT_REGISTRY_LOCKED_v1.md",
        "os/chat-handoffs/BRAIN_FULL_SYSTEM_MAP_LOCKED_v1.md",
        "os/chat-handoffs/BRAIN_RESEARCH_LIBRARY_LOCKED_v1.md",
    ],
    "contract": [
        "os/chat-handoffs/MANDATORY_BRAIN_CHAT_LOCKED_v1.md",
        "os/chat-handoffs/BRAIN_CORE_EXECUTOR_LOCKED_v1.md",
        "os/chat-handoffs/BRAIN_COMPLETE_TRANSFER_LOCKED_v1.md",
        "os/chat-handoffs/BRAIN_FULL_TRANSFER_PROMPT_LOCKED_v1.md",
        "os/chat-handoffs/BRAIN_HEAL_PROMPT_LOCKED_v1.md",
        "os/chat-handoffs/FOUNDER_ADVISOR_PROFILE_LOCKED_v1.md",
    ],
    "enforcement": [
        "os/chat-handoffs/BRAIN_DISK_BEFORE_CHAT_SESSION_LOOP_LOCKED_v1.md",
        "os/chat-handoffs/BRAIN_ENFORCEMENT_AUDIT_PROMPT_LOCKED_v1.md",
        "os/chat-handoffs/GOAL1_LOOP_ACTIVATION_CHAIN_LOCKED_v1.md",
        "os/chat-handoffs/GOAL1_EXECUTION_SOLUTION_LOCKED_v1.md",
        "os/chat-handoffs/GOAL1_BATCH_CHECKPOINT_LOCKED_v1.md",
        "os/chat-handoffs/ONE_SA_PER_TURN_MECHANICAL_LOCKED_v1.md",
        "os/chat-handoffs/REGISTRY_DRAIN_RAIL_LOCKED_v1.md",
        "os/chat-handoffs/SINA_GOAL1_OPERATING_MODEL_LOCKED_v1.md",
        "os/chat-handoffs/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md",
    ],
    "incidents": [
        "SINA_BRAIN_WORKER_LANE_CROSS_INCIDENT_LOCKED_v1.md",
        "SINA_GOAL1_LOOP_UNVALIDATED_PROOF_INCIDENT_LOCKED_v1.md",
        "CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_LOCKED_v1.md",
        "SINA_HEALTHY_DRAIN_PROMPT_FEASIBILITY_INCIDENT_REPORT_LOCKED_v1.md",
        "SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md",
    ],
    "system": [
        "os/chat-handoffs/GOVERNED_EXECUTION_OS_MASTER_LOCKED_v1.md",
        "os/chat-handoffs/GOAL_EXECUTION_ACTIVE_LOCKED_v1.md",
        "os/chat-handoffs/GOAL_HIERARCHY_LOCKED_v1.md",
        "os/chat-handoffs/FOUNDER_DAILY_OPERATING_MODEL_LOCKED_v1.md",
        "os/chat-handoffs/WORKER_ASSIGNMENT_AND_CHAT_ROUTING_LOCKED_v1.md",
        "os/chat-handoffs/ECOSYSTEM_BRAIN_ROLLOUT_LOCKED_v1.md",
        "os/chat-handoffs/AGENT_MISS_DISK_FIRST_CORRECTION_LOOP_LOCKED_v1.md",
        "os/chat-handoffs/UNIFIED_RESEARCH_ROOT_LOCKED_v1.md",
        "os/chat-handoffs/SINAAIDB_ARCHIVE_RETIREMENT_HANDOFF_LOCKED_v1.md",
        "os/chat-handoffs/ENTRY_POINTER_LOCKED_v1.md",
        "os/chat-handoffs/README_INDEX_LOCKED_v1.md",
    ],
}

PLAN_REGISTRY_SRC = ROOT / "os" / "plan-library"
PLAN_REGISTRY_DST = BRAIN_OS / "plan-registry"


def stub_text(canonical: str) -> str:
    return (
        f"# MOVED — canonical SSOT\n\n"
        f"**Do not edit this stub.**\n\n"
        f"Canonical path: `{canonical}`\n\n"
        f"Law: `brain-os/INDEX_LOCKED_v1.md`\n"
    )


def move_file(src_rel: str, dest_dir: Path) -> Path | None:
    src = ROOT / src_rel
    if not src.is_file():
        print(f"SKIP missing: {src_rel}")
        return None
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name
    if dest.exists():
        print(f"SKIP exists: {dest}")
        return dest
    shutil.move(str(src), str(dest))
    canonical = str(dest.relative_to(ROOT))
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text(stub_text(canonical), encoding="utf-8")
    print(f"OK {src_rel} -> {canonical}")
    return dest


def main() -> int:
    for sub, files in MOVES.items():
        dest_dir = BRAIN_OS / sub
        for rel in files:
            move_file(rel, dest_dir)

    if PLAN_REGISTRY_SRC.is_dir() and not PLAN_REGISTRY_DST.exists():
        shutil.move(str(PLAN_REGISTRY_SRC), str(PLAN_REGISTRY_DST))
        PLAN_REGISTRY_SRC.mkdir(parents=True, exist_ok=True)
        (PLAN_REGISTRY_SRC / "MOVED.md").write_text(
            stub_text("brain-os/plan-registry"), encoding="utf-8"
        )
        print("OK brain-os/plan-registry -> brain-os/plan-registry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
