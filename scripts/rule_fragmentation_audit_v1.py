#!/usr/bin/env python3
"""Audit .cursor/rules for duplication, alwaysApply cap violations, superseded stubs."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / ".cursor" / "rules"
SSOT = ROOT / "data" / "cursor-cost-intelligence-routing-v1.json"
OUT = ROOT / "data" / "rule-fragmentation-audit-v1.json"

SUPERSEDED_MARKERS = ("SUPERSEDED", "supersedes:", "Do not apply", "Do not follow")
CONFLICT_PAIRS = [
    (".cursor/rules/000-founder-rules.mdc", ".cursor/rules/agent-founder-intent-first.mdc", "raw-json-only vs plain English"),
    (".cursor/rules/036-agent-execution-discipline-v1.mdc", ".cursor/rules/agent-founder-intent-first.mdc", "no summaries vs explain founder"),
    (".cursor/rules/sina-command-ui.mdc", ".cursor/rules/agent-disk-live-wire-first.mdc", "museum UI vs Hub-only live wire"),
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    cap = json.loads(SSOT.read_text(encoding="utf-8"))
    allowed = set(cap["alwaysapply_cap"]["allowed_files"])
    max_count = cap["alwaysapply_cap"]["max_count"]

    always_on: list[str] = []
    superseded: list[str] = []
    sina_command_stale: list[str] = []
    for path in sorted(RULES.glob("*.mdc")):
        text = path.read_text(encoding="utf-8")
        rel = f".cursor/rules/{path.name}"
        if re.search(r"alwaysApply:\s*true", text):
            always_on.append(rel)
        head = text[:800]
        if any(m in head for m in SUPERSEDED_MARKERS) and "alwaysApply: true" not in head:
            superseded.append(rel)
        if "sina-command" in path.name.lower() and "SUPERSEDED" not in head and path.name not in (
            "sina-command-readonly.mdc",
        ):
            if "museum retired" not in head.lower():
                sina_command_stale.append(rel)

    extra = sorted(set(always_on) - allowed)
    missing = sorted(allowed - set(always_on))
    cap_ok = len(always_on) == max_count and not extra and not missing

    conflicts = []
    for a, b, reason in CONFLICT_PAIRS:
        if (ROOT / a[2:]).is_file() and (ROOT / b[2:]).is_file():
            ta = (ROOT / a[2:]).read_text(encoding="utf-8")
            if "SUPERSEDED" not in ta[:400]:
                conflicts.append({"a": a, "b": b, "reason": reason, "status": "active_conflict"})
            else:
                conflicts.append({"a": a, "b": b, "reason": reason, "status": "resolved_superseded"})

    row = {
        "schema": "rule-fragmentation-audit-v1",
        "at": _now(),
        "ok": cap_ok and not sina_command_stale,
        "alwaysapply_cap": {
            "ok": cap_ok,
            "max": max_count,
            "found": len(always_on),
            "always_on": always_on,
            "extra": extra,
            "missing": missing,
            "allowed": sorted(allowed),
        },
        "superseded_stubs": superseded,
        "sina_command_stale": sina_command_stale,
        "known_conflicts": conflicts,
        "unify_law": "Eight alwaysApply only — per data/cursor-cost-intelligence-routing-v1.json",
    }
    OUT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"RULE_FRAGMENTATION ok={row['ok']} alwaysApply={len(always_on)}/{max_count} extra={len(extra)}")
    return 0 if row["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
