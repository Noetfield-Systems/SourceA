#!/usr/bin/env python3
"""Audit private agent pages — registry, loop_workspaces, packs, no stale seeds."""
from __future__ import annotations

import json
import sys
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE_A / "scripts"))

from agent_private_workspaces import ensure_all_workspaces, loop_workspaces_payload, select_loop_workspace  # noqa: E402
from agent_workspace_registry import AGENT_WORKSPACES  # noqa: E402
from agent_loop import loop_payload  # noqa: E402

OPTIONAL_PACK_AGENTS = frozenset({"noetfield_local"})


def main() -> int:
    errors: list[str] = []
    ensure_all_workspaces()
    payload = loop_workspaces_payload()
    workspaces = payload.get("loop_workspaces") or []
    reg_ids = [w["id"] for w in AGENT_WORKSPACES]

    if len(workspaces) != len(reg_ids):
        errors.append(f"loop_workspaces count {len(workspaces)} != registry {len(reg_ids)}")

    for spec in AGENT_WORKSPACES:
        aid = spec["id"]
        row = next((w for w in workspaces if w["id"] == aid), None)
        if not row:
            errors.append(f"missing loop_workspaces row: {aid}")
            continue
        priv = Path(row.get("private_root") or "")
        if not priv.is_dir():
            errors.append(f"missing private dir: {priv}")
        if not (priv / "GOVERNANCE_LOCKED.md").is_file():
            errors.append(f"missing GOVERNANCE_LOCKED.md: {aid}")
        if not (priv / "vault").is_dir():
            errors.append(f"missing workspace vault: {aid}")
        if not (priv / "activity.jsonl").is_file():
            errors.append(f"missing activity.jsonl: {aid}")
        pid = spec.get("pack_id")
        n = len(row.get("pack_suggestions") or [])
        repo = Path(spec.get("repo_root") or "")
        pack_optional = aid in OPTIONAL_PACK_AGENTS and not repo.is_dir()
        if pid and not pack_optional:
            if not row.get("pack_ready"):
                errors.append(f"pack not ready: {aid}")
            if n != 10:
                errors.append(f"{aid}: expected 10 pack_suggestions, got {n}")
        elif pid and pack_optional:
            pass  # Wave 0 — portfolio repo absent on disk
        elif n != 0:
            errors.append(f"{aid}: no pack_id but has {n} pack_suggestions")
        mirror = row.get("workspace_mirror") or {}
        if not mirror.get("ok"):
            errors.append(f"workspace_mirror not ok: {aid}")
        else:
            for key in ("mission", "inbox", "vault", "memory", "skills", "stats"):
                if key not in mirror:
                    errors.append(f"workspace_mirror missing {key}: {aid}")
        if aid == "trustfield":
            act_path = priv / "activity.jsonl"
            disk_act = 0
            if act_path.is_file():
                disk_act = sum(1 for line in act_path.read_text(encoding="utf-8").splitlines() if line.strip())
            mir_act = int((row.get("workspace_mirror") or {}).get("memory", {}).get("history_count") or 0)
            if mir_act < disk_act:
                errors.append(f"trustfield mirror activity {mir_act} < disk {disk_act}")
            inbox_open = int((row.get("workspace_mirror") or {}).get("stats", {}).get("inbox_open") or 0)
            if inbox_open < 1:
                errors.append("trustfield mirror: expected >=1 open INBOX row (P0 outreach)")

    # Pack isolation: trustfield then semej → 0 global seeds
    select_loop_workspace("trustfield", sync_ui_file=True)
    al = loop_payload()
    if len(al.get("seed_suggestions") or []) != 10:
        errors.append(f"trustfield select: expected 10 seeds, got {len(al.get('seed_suggestions') or [])}")
    select_loop_workspace("semej", sync_ui_file=True)
    al2 = loop_payload()
    if len(al2.get("seed_suggestions") or []) != 0:
        errors.append(f"semej select: expected 0 seeds, got {len(al2.get('seed_suggestions') or [])}")

    cmd_path = SOURCE_A / "agent-control-panel" / "command-data.json"
    if cmd_path.is_file():
        data = json.loads(cmd_path.read_text(encoding="utf-8"))
        al3 = data.get("agent_loop") or {}
        if len(al3.get("loop_workspaces") or []) != len(reg_ids):
            errors.append("command-data.json loop_workspaces count mismatch")

    if errors:
        print("AUDIT FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK: {len(reg_ids)} private agent pages · packs · seed isolation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
