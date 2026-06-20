#!/usr/bin/env python3
"""Cross-lane edit guard — block writes outside caller agent ownership.

Law: brain-os/incidents/SINA_CROSS_LANE_EDIT_FORBIDDEN_INCIDENT_LOCKED_v1.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_LOG = Path.home() / ".sina" / "governance-events.jsonl"

# agent_id -> allowed path prefixes (resolved at check time)
LANE_WRITE_PREFIXES: dict[str, list[str]] = {
    "sourcea_execution_core": [
        str(ROOT),
    ],
    "sourcea_worker": [
        str(ROOT / "prompts"),
        str(ROOT / "scripts"),
        str(ROOT / "brain-os/plan-registry"),
        str(ROOT / "brain-os/law/enforcement"),
        str(ROOT / "SourceA-landing"),
        str(ROOT / "receipts"),
        str(ROOT / "os"),
        str(ROOT / "agent-control-panel"),
        str(ROOT / "data"),
        str(ROOT / "sina-bowl"),
        str(ROOT / ".cursor/rules"),
        str(ROOT / ".cursor/skills"),
        str(ROOT / ".sina-loop"),
        str(ROOT / "cursor-plugin"),
        str(ROOT / "packages"),
    ],
    "research_acquisitor": [
        str(ROOT / "RESEARCH"),
        str(ROOT / "docs/research-vault"),
        str(Path.home() / ".sina/agent-workspaces/research-acquisitor"),
    ],
    "cursor_os_pro_research_lane_b": [
        str(Path.home() / "Desktop/Cursor OS Pro/docs/research"),
        str(Path.home() / "Desktop/Cursor OS Pro/scripts/investor-data-200.json"),
        str(Path.home() / "Desktop/Cursor OS Pro/scripts/canada-voice-100.json"),
        str(Path.home() / "Desktop/Cursor OS Pro/scripts/generate-investor-200.js"),
        str(Path.home() / "Desktop/Cursor OS Pro/scripts/generate-canada-voice-100-json.js"),
        str(Path.home() / "Desktop/Cursor OS Pro/scripts/generate-voice-composition-brain-v1.js"),
        str(Path.home() / "Desktop/Cursor OS Pro/scripts/refresh-investor-canvas.js"),
        str(Path.home() / "Desktop/Cursor OS Pro/scripts/refresh-lane-research.sh"),
        str(Path.home() / "Desktop/Cursor OS Pro/docs/research/incidents"),
    ],
    "cursor_os_pro_product": [
        str(Path.home() / "Desktop/Cursor OS Pro"),
    ],
}

# Paths no non-owner may ever write (even with sloppy "save")
GLOBAL_FORBIDDEN_UNLESS_PRODUCT: list[str] = [
    str(Path.home() / "Desktop/Cursor OS Pro/AGENTS.md"),
    str(Path.home() / "Desktop/Cursor OS Pro/docs/SINGLE-SOURCE-OF-TRUTH.md"),
    str(Path.home() / "Desktop/Cursor OS Pro/docs/VOICE_AGENT_ROADMAP_LOCKED_v1.md"),
]

GLOBAL_FORBIDDEN_UNLESS_BRAIN: list[str] = [
    str(ROOT / "brain-os/laws"),
    str(ROOT / "brain-os/incidents"),
    str(ROOT / "ACTIVE_NOW.md"),
]

EDIT_ALLOWED_RE = re.compile(
    r"EDIT\s+ALLOWED:\s*(?P<path>.+?)(?:\s+ACTION:|\s*$)",
    re.I | re.M,
)


def _resolve(path: str) -> Path:
    return Path(path).expanduser().resolve()


def _has_explicit_order(text: str, target: Path) -> bool:
    if not text.strip():
        return False
    for m in EDIT_ALLOWED_RE.finditer(text):
        allowed = _resolve(m.group("path").strip().strip("`\"'"))
        try:
            target.relative_to(allowed)
            return True
        except ValueError:
            if target == allowed:
                return True
    return False


def _prefix_allowed(target: Path, prefixes: list[str]) -> bool:
    for pref in prefixes:
        base = _resolve(pref)
        try:
            target.relative_to(base)
            return True
        except ValueError:
            if target == base:
                return True
    return False


def _log_block(row: dict) -> None:
    if row.get("ok"):
        return
    try:
        GOVERNANCE_LOG.parent.mkdir(parents=True, exist_ok=True)
        from datetime import datetime, timezone

        entry = {**row, "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "event": "cross_lane_block"}
        with GOVERNANCE_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _resolve_agent_id(agent: str, explicit_order: str = "") -> tuple[str, dict | None]:
    """Resolve cursor/unknown via SASCIP before lane check."""
    agent = (agent or "unknown").strip()
    if agent not in ("cursor", "unknown", ""):
        return agent, None
    try:
        from stranger_agent_safety_lib_v1 import resolve_cross_lane_agent  # noqa: WPS433

        row = resolve_cross_lane_agent(agent, role_hint="any", explicit_order=explicit_order)
        if row.get("ok") and row.get("resolved_agent_id"):
            return str(row["resolved_agent_id"]), row
        return agent, row
    except Exception:
        return agent, None


def check_edit(
    *,
    agent: str,
    path: str,
    explicit_order: str = "",
) -> dict:
    target = _resolve(path)
    agent = (agent or "unknown").strip()
    resolve_meta: dict | None = None
    if agent in ("cursor", "unknown", ""):
        agent, resolve_meta = _resolve_agent_id(agent, explicit_order)
        if resolve_meta and not resolve_meta.get("ok"):
            row = {
                "ok": False,
                "allowed": False,
                "reason": resolve_meta.get("reason") or "STRANGER_QUARANTINE",
                "agent": agent,
                "path": str(target),
                "law": "STRANGER_AGENT_SAFETY_CONTROL_PIPELINE_LOCKED_v1.md",
                "message": resolve_meta.get("message")
                or "Stranger agent quarantined — founder must issue EDIT ALLOWED + ACTION",
                "stranger_meta": {
                    "trust_tier": resolve_meta.get("trust_tier"),
                    "fingerprint_id": resolve_meta.get("fingerprint_id"),
                },
            }
            _log_block(row)
            return row

    if _has_explicit_order(explicit_order, target):
        return {
            "ok": True,
            "allowed": True,
            "reason": "founder_explicit_edit_allowed",
            "agent": agent,
            "path": str(target),
        }

    if agent in ("cursor_os_pro_research_lane_b", "research_acquisitor"):
        for forbidden in GLOBAL_FORBIDDEN_UNLESS_PRODUCT + GLOBAL_FORBIDDEN_UNLESS_BRAIN:
            try:
                target.relative_to(_resolve(forbidden))
                return {
                    "ok": False,
                    "allowed": False,
                    "reason": "CROSS_LANE_SSOT_FORBIDDEN",
                    "agent": agent,
                    "path": str(target),
                    "law": "SINA_CROSS_LANE_EDIT_FORBIDDEN_INCIDENT_LOCKED_v1.md",
                    "message": "Research/advise agent cannot edit product SSOT or Brain law — founder must issue EDIT ALLOWED + ACTION",
                }
            except ValueError:
                if target == _resolve(forbidden):
                    return {
                        "ok": False,
                        "allowed": False,
                        "reason": "CROSS_LANE_SSOT_FORBIDDEN",
                        "agent": agent,
                        "path": str(target),
                        "law": "SINA_CROSS_LANE_EDIT_FORBIDDEN_INCIDENT_LOCKED_v1.md",
                        "message": "Research/advise agent cannot edit product SSOT or Brain law",
                    }

    prefixes = LANE_WRITE_PREFIXES.get(agent)
    if prefixes and _prefix_allowed(target, prefixes):
        return {"ok": True, "allowed": True, "reason": "lane_prefix_match", "agent": agent, "path": str(target)}

    if agent == "unknown" or not prefixes:
        return {
            "ok": False,
            "allowed": False,
            "reason": "AGENT_UNREGISTERED_OR_AMBIGUOUS",
            "agent": agent,
            "path": str(target),
            "message": "Unregistered agent — no write until founder issues EDIT ALLOWED + ACTION",
        }

    return {
        "ok": False,
        "allowed": False,
        "reason": "CROSS_LANE_PATH_FORBIDDEN",
        "agent": agent,
        "path": str(target),
        "law": "SINA_CROSS_LANE_EDIT_FORBIDDEN_INCIDENT_LOCKED_v1.md",
        "message": "Path outside agent write allowlist — 100% founder clarification required",
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Cross-lane edit guard")
    p.add_argument("cmd", choices=("check",))
    p.add_argument("--agent", required=True)
    p.add_argument("--path", required=True)
    p.add_argument("--explicit-order", default="")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    row = check_edit(agent=args.agent, path=args.path, explicit_order=args.explicit_order)
    if not row.get("ok"):
        _log_block(row)
    if args.json:
        print(json.dumps(row, indent=2))
        return 0  # machine callers inspect row["ok"]
    print(json.dumps(row))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
