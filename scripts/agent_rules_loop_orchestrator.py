#!/usr/bin/env python3
"""Rules-in-charge loop — agents MUST check existing laws before acting.

Supersession: a rule stays in charge until a newer LOCKED doc or .mdc explicitly supersedes it.
Never add parallel duplicate rules — extend or supersede the canonical one.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SOURCE_A = Path(__file__).resolve().parents[1]
RECEIPT_LOG = Path.home() / ".sina" / "agent_rules_loop_receipt_v1.jsonl"
STATE_PATH = Path.home() / ".sina" / "agent_rules_loop_state_v1.json"
LAW_DOC = "AGENT_RULES_IN_CHARGE_LOCKED_v1.md"

# alwaysApply .mdc hooks agents must have loaded (SourceA maintainer + loop executor)
SOURCE_A_REQUIRED_MDC = frozenset(
    {
        "000-dead-law-stubs.mdc",
        "agent-memory-mirror.mdc",
        "agent-loop.mdc",
        "sina-governance-entry.mdc",
        "agent-smart-judgment.mdc",
    }
)

# Topics that must not have duplicate alwaysApply rules (basename patterns)
FORBIDDEN_DUPLICATE_TOPICS = (
    (re.compile(r"founder.*no.*terminal|no-terminal", re.I), "founder-no-terminal"),
    (re.compile(r"agent-loop", re.I), "agent-loop"),
    (re.compile(r"governance-entry", re.I), "sina-governance-entry"),
)

LOOP_PHASES = frozenset({"session_start", "loop_round", "pre_ship", "founder_rule_change", "maintainer_preflight"})


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_receipt(row: dict) -> None:
    RECEIPT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with RECEIPT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def _save_state(patch: dict) -> None:
    state: dict = {}
    if STATE_PATH.is_file():
        try:
            state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            state = {}
    state.update(patch)
    state["updated_at"] = _now()
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _scan_cursor_rules(workspace: Path) -> dict[str, Any]:
    rules_dir = workspace / ".cursor" / "rules"
    files: list[dict] = []
    if rules_dir.is_dir():
        for p in sorted(rules_dir.glob("*.mdc")):
            text = p.read_text(encoding="utf-8", errors="replace")
            always = "alwaysApply: true" in text or "alwaysapply: true" in text.lower()
            files.append(
                {
                    "name": p.name,
                    "path": str(p),
                    "always_apply": always,
                    "size": p.stat().st_size,
                }
            )
    always_names = [f["name"] for f in files if f["always_apply"]]
    return {
        "workspace": str(workspace),
        "rule_files": files,
        "always_apply_count": len(always_names),
        "always_apply_names": always_names,
    }


def _duplicate_topic_warnings(always_names: list[str]) -> list[str]:
    warnings: list[str] = []
    for pattern, topic in FORBIDDEN_DUPLICATE_TOPICS:
        hits = [n for n in always_names if pattern.search(n)]
        if len(hits) > 1:
            warnings.append(f"Duplicate alwaysApply rules for topic '{topic}': {', '.join(hits)}")
    return warnings


def _missing_required_mdc(workspace: Path, always_names: list[str]) -> list[str]:
    if workspace.resolve() != SOURCE_A.resolve():
        return []
    rules_dir = workspace / ".cursor" / "rules"
    missing = []
    for name in SOURCE_A_REQUIRED_MDC:
        path = rules_dir / name
        if not path.is_file():
            missing.append(name)
            continue
        text = path.read_text(encoding="utf-8")
        if "alwaysApply: true" not in text and "globs:" not in text:
            missing.append(name)
    return missing


def _rules_in_charge(*, light: bool = False) -> dict:
    from agent_rules_in_charge import rules_in_charge_payload  # noqa: WPS433

    hub: dict = {}
    try:
        if light:
            from sina_command_lib import get_hub_payload, warm_hub_cache_from_disk  # noqa: WPS433

            warm_hub_cache_from_disk()
            hub = get_hub_payload()
        else:
            from sina_command_lib import get_hub_payload  # noqa: WPS433

            hub = get_hub_payload()
    except Exception:
        hub = {}
    return rules_in_charge_payload(hub_payload=hub)


def _agent_affirmation_lines(ric: dict, *, phase: str) -> list[str]:
    lines = [
        f"RULES LOOP ({phase}): Read in-charge laws before acting.",
        f"Law: {LAW_DOC} · API: /api/agent-rules-in-charge-v1",
        "Supersession: old rule stays in charge until a NEW rule explicitly supersedes it — never duplicate.",
    ]
    for r in (ric.get("in_charge_now") or [])[:8]:
        title = r.get("title") or r.get("path") or "rule"
        reason = (r.get("charge_reason") or r.get("why") or "")[:120]
        lines.append(f"  • {title} — {reason}")
    ctx = ric.get("context_now") or {}
    if ctx.get("wtm_do_now"):
        lines.append(f"  • WTM now: {ctx.get('wtm_do_now')}")
    if ctx.get("p0_next"):
        lines.append(f"  • P0 next: {ctx.get('p0_next')}")
    lines.append("If a founder rule conflicts with chat: founder live + LOCKED wins — cite which rule governs.")
    return lines


def run_rules_loop_check(
    *,
    phase: str = "session_start",
    workspace: str | Path | None = None,
    agent_id: str = "executor",
    write_receipt: bool = True,
) -> dict[str, Any]:
    phase = (phase or "session_start").strip()
    if phase not in LOOP_PHASES:
        phase = "session_start"
    freeze_flag = Path.home() / ".sina" / "auto-run-disabled-v1.flag"
    if freeze_flag.is_file():
        result = {
            "ok": True,
            "schema": "agent-rules-loop-v1",
            "phase": phase,
            "agent_id": agent_id,
            "generated_at": _now(),
            "mode": "mac_focus_freeze",
            "skipped": True,
            "note": "rules loop deferred during Mac focus freeze",
        }
        if write_receipt:
            _append_receipt(result)
        return result
    ws = Path(workspace or SOURCE_A).expanduser().resolve()
    ric = _rules_in_charge(light=(phase in ("session_start", "maintainer_preflight")))
    scan = _scan_cursor_rules(ws)
    always = scan.get("always_apply_names") or []
    dup_warn = _duplicate_topic_warnings(always)
    missing_mdc = _missing_required_mdc(ws, always)
    affirm = _agent_affirmation_lines(ric, phase=phase)

    ok = ric.get("ok", True) and not missing_mdc and not dup_warn
    result = {
        "ok": ok,
        "schema": "agent-rules-loop-v1",
        "phase": phase,
        "agent_id": agent_id,
        "generated_at": _now(),
        "law_doc": LAW_DOC,
        "supersession_law": "Rule in charge until superseded by newer LOCKED_vN or explicit .mdc supersession note",
        "in_charge_count": ric.get("in_charge_count", 0),
        "in_charge_now": (ric.get("in_charge_now") or [])[:12],
        "context_groups": ric.get("context_groups") or [],
        "cursor_rules_scan": scan,
        "missing_required_mdc": missing_mdc,
        "duplicate_warnings": dup_warn,
        "agent_affirmation": affirm,
        "receipt_log": str(RECEIPT_LOG),
        "procedure": [
            "1. GET /api/agent-rules-in-charge-v1 (or run this orchestrator) — never invent parallel rules",
            "2. Read in_charge_now + founder_live — these govern NOW",
            "3. Before ship: re-run phase=pre_ship",
            "4. New founder rule → update LOCKED or .mdc with supersedes: field — archive old to archive/superseded/",
            "5. Each agent-loop round: phase=loop_round at round start",
        ],
    }
    if write_receipt:
        _append_receipt(
            {
                "at": result["generated_at"],
                "phase": phase,
                "agent_id": agent_id,
                "ok": ok,
                "in_charge_count": result["in_charge_count"],
                "missing_mdc": missing_mdc,
                "duplicate_warnings": dup_warn,
            }
        )
        _save_state({"last_check": result["generated_at"], "last_phase": phase, "last_ok": ok})
    return result


def rules_loop_banner(*, phase: str = "loop_round", max_lines: int = 10) -> str:
    """Short text injected into agent-loop prompts."""
    check = run_rules_loop_check(phase=phase, write_receipt=False)
    lines = check.get("agent_affirmation") or []
    body = "\n".join(lines[:max_lines])
    return f"<!-- RULES_IN_CHARGE_LOOP -->\n{body}\n---\n\n"


def handle_api(body: dict | None = None) -> dict:
    body = body or {}
    action = (body.get("action") or "check").strip().lower()
    if action == "banner":
        return {
            "ok": True,
            "banner": rules_loop_banner(phase=body.get("phase") or "loop_round"),
        }
    return run_rules_loop_check(
        phase=body.get("phase") or "session_start",
        workspace=body.get("workspace") or SOURCE_A,
        agent_id=body.get("agent_id") or "executor",
    )


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Rules-in-charge loop check")
    ap.add_argument("--phase", default="session_start", choices=sorted(LOOP_PHASES))
    ap.add_argument("--workspace", default=str(SOURCE_A))
    ap.add_argument("--agent-id", default="executor")
    ap.add_argument("--json-only", action="store_true")
    args = ap.parse_args()
    out = run_rules_loop_check(
        phase=args.phase,
        workspace=args.workspace,
        agent_id=args.agent_id,
    )
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
