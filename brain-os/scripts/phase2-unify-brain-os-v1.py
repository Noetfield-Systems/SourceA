#!/usr/bin/env python3
"""Phase 2 — scripts, WTM, lanes, cursor mirror; collapse os/ stubs."""
from __future__ import annotations

import os
import shutil
import stat
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BO = ROOT / "brain-os"
BO_SCRIPTS = BO / "scripts"
BO_WTM = BO / "wtm"
BO_LANES = BO / "lanes"
BO_CURSOR = BO / "cursor" / "rules"

BRAIN_SCRIPTS = [
    "brain-session-start.sh",
    "brain_run_loop_trace_v1.py",
    "brain_narrate_loop_v1.py",
    "brain_validate_goal1_v1.py",
    "brain_gather_rules_v1.py",
    "brain_run_loop_v1.py",
    "brain_execute_turn_v1.py",
    "brain_intent_gate_v1.py",
    "brain_timing_enforce_v1.py",
    "brain_watch_loop_v1.py",
    "brain_lane_guard.py",
    "brain_enforcement_audit_v1.py",
    "brain_research_register.py",
    "cursor_entry_gate.py",
    "sync-brain-pack.sh",
    "brain_os_paths.py",
    "validate-brain-unified-rules-v1.sh",
    "validate-brain-disk-before-chat-v1.sh",
    "validate-brain-narrate-loop-v1.sh",
    "validate-brain-narrate-not-execute-v1.sh",
    "validate-brain-rules-narrate-v1.sh",
    "validate-brain-run-loop-v1.sh",
    "validate-brain-enforcement-audit-v1.sh",
    "validate-goal1-brain-validation-v1.sh",
    "validate-brain-os-complete-v1.sh",
    "reorganize-brain-os-v1.py",
    "phase2-unify-brain-os-v1.py",
]

WTM_ROOT = [
    "WORLD_TARGET_MODEL_MAP_LOCKED_v5.md",
    "WORLD_TARGET_MODEL_AUTHORITY_LAW_LOCKED_v1.md",
    "WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v2.md",
    "WORLD_TARGET_MODEL_STEP_ID_MIGRATION_LOCKED_v1.md",
    "WORLD_TARGET_MODEL_ARCHITECTURE_DIAGRAM_LOCKED_v1.md",
    "WORLD_TARGET_MODEL_UI_RESEARCH_LOCKED_v1.md",
    "WORLD_TARGET_MODEL_UI_INCIDENT_REPORT_LOCKED_v1.md",
    "WORLD_TARGET_MODEL_PHASE_NAMING_INCIDENT_REPORT_LOCKED_v1.md",
    "WORLD_TARGET_MODEL_FULL_BLUEPRINT_FOR_REVIEW_v1.md",
    "WORLD_TARGET_MODEL_FULL_BLUEPRINT_FOR_REVIEW_v2.md",
    "SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2.md",
    "SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md",
]

LANES = [
    "MANDATORY_TRUSTFIELD_CHAT_LOCKED_v1.md",
    "MANDATORY_NOETFIELD_CHAT_LOCKED_v1.md",
    "MANDATORY_DEVBRIDGE_WIRE_CHAT_LOCKED_v1.md",
    "MANDATORY_CURSOR_OS_PRO_CHAT_LOCKED_v1.md",
    "MANDATORY_SINAPROMPTOS_CHAT_LOCKED_v1.md",
    "MANDATORY_VIRLUX_CHAT_LOCKED_v1.md",
    "MANDATORY_777_FOUNDATION_CHAT_LOCKED_v1.md",
    "MANDATORY_SINAAI_MONOREPO_CHAT_LOCKED_v1.md",
    "GOAL_SPECIALIST_CHAT_PACK_LOCKED_v1.md",
    "MANDATORY_CHAT_HANDOFF_INDEX_LOCKED_v1.md",
    "CURSOR_OS_PRO_TWO_CHAT_POLICY_LOCKED_v1.md",
]

CURSOR_RULES = [
    "000-brain-unified.mdc",
    "000-entry-gate.mdc",
    "agent-loop.mdc",
    "agent-smart-judgment.mdc",
    "sina-governance-entry.mdc",
    "sina-command-readonly.mdc",
    "chatgpt-external-critic.mdc",
    "000-workspace-lock.mdc",
    "099-worker-inbox-active.mdc",
]

STUB = """# MOVED — canonical SSOT

**Do not edit this stub.**

Canonical path: `{canonical}`

Law: `brain-os/INDEX_LOCKED_v1.md`
"""


def stub_at(src: Path, canonical: str) -> None:
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text(STUB.format(canonical=canonical), encoding="utf-8")


def move_file(src: Path, dest: Path, *, stub_src: bool = True) -> None:
    if not src.is_file():
        print(f"SKIP missing {src}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest.unlink()
    shutil.move(str(src), str(dest))
    canonical = str(dest.relative_to(ROOT))
    print(f"OK {src.relative_to(ROOT)} -> {canonical}")
    if stub_src and src.parent != BO:
        stub_at(src, canonical)


def patch_python_root(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "parents[2]" in text and "brain-os" in str(path):
        return
    text = text.replace(
        "ROOT = Path(__file__).resolve().parents[1]",
        "ROOT = Path(__file__).resolve().parents[2]  # SourceA root",
    )
    text = text.replace(
        'ROOT="$(cd "$(dirname "$0")/.." && pwd)"',
        'ROOT="$(cd "$(dirname "$0")/../.." && pwd)"',
    )
    if "SCRIPTS = ROOT / \"scripts\"" in text:
        text = text.replace(
            'SCRIPTS = ROOT / "scripts"',
            'SCRIPTS = ROOT / "brain-os" / "scripts"',
        )
    path.write_text(text, encoding="utf-8")


def shim_shell(name: str) -> None:
    shim = ROOT / "scripts" / name
    shim.write_text(
        f"""#!/usr/bin/env bash
# Shim → brain-os/scripts/{name}
set -euo pipefail
exec "$(cd "$(dirname "$0")/.." && pwd)/brain-os/scripts/{name}" "$@"
""",
        encoding="utf-8",
    )
    shim.chmod(shim.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def shim_python(name: str) -> None:
    shim = ROOT / "scripts" / name
    shim.write_text(
        f"""#!/usr/bin/env python3
\"\"\"Shim → brain-os/scripts/{name}\"\"\"
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).resolve().parents[1] / "brain-os/scripts/{name}"), run_name="__main__")
""",
        encoding="utf-8",
    )
    shim.chmod(shim.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def main() -> int:
    BO_SCRIPTS.mkdir(parents=True, exist_ok=True)
    BO_WTM.mkdir(parents=True, exist_ok=True)
    BO_LANES.mkdir(parents=True, exist_ok=True)
    BO_CURSOR.mkdir(parents=True, exist_ok=True)

    for name in BRAIN_SCRIPTS:
        src = ROOT / "scripts" / name
        if not src.is_file() and (BO_SCRIPTS / name).is_file():
            continue
        if src.is_file():
            move_file(src, BO_SCRIPTS / name, stub_src=False)
        dest = BO_SCRIPTS / name
        if dest.suffix == ".py":
            patch_python_root(dest)
        if name.endswith(".sh"):
            shim_shell(name)
        elif name.endswith(".py"):
            shim_python(name)

    for name in WTM_ROOT:
        move_file(ROOT / name, BO_WTM / name)

    handoffs = ROOT / "os" / "chat-handoffs"
    for name in LANES:
        move_file(handoffs / name, BO_LANES / name)

    # Remove brain stub clutter in os/chat-handoffs
    if handoffs.is_dir():
        for f in list(handoffs.iterdir()):
            if f.is_file():
                text = f.read_text(encoding="utf-8", errors="replace")
                if text.startswith("# MOVED"):
                    f.unlink()
                    print(f"DEL stub {f.name}")

    (ROOT / "os" / "MOVED.md").write_text(
        STUB.format(canonical="brain-os/INDEX_LOCKED_v1.md"), encoding="utf-8"
    )
    if handoffs.is_dir() and not any(handoffs.iterdir()):
        handoffs.rmdir()
        print("DEL empty os/chat-handoffs")

    for name in CURSOR_RULES:
        src = ROOT / ".cursor" / "rules" / name
        if src.is_file():
            shutil.copy2(src, BO_CURSOR / name)
            print(f"COPY cursor {name} -> brain-os/cursor/rules/")

    # Fix validate paths inside brain-os scripts
    for sh in BO_SCRIPTS.glob("validate-brain*.sh"):
        text = sh.read_text(encoding="utf-8")
        text = text.replace('$(cd "$(dirname "$0")/.." && pwd)', '$(cd "$(dirname "$0")/../.." && pwd)')
        text = text.replace("scripts/", "brain-os/scripts/")
        text = text.replace("brain-os/scripts/brain-os/", "brain-os/scripts/")
        sh.write_text(text, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
