#!/usr/bin/env python3
"""
Cursor agent self-audit loop — session memory, incident ack, closeout reports.

Storage (per agent id under ~/.sina/agent-workspaces/<id>/):
  MANDATORY_READ_CHAIN.md
  SESSION_LEDGER.jsonl
  SESSION_CLOSEOUT_LATEST.md
  incident-agent-state.json  (last_self_audit_at)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SOURCE_A = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from agent_incident_system import ensure_agent_incident_files, iso_week_id  # noqa: E402
from agent_workspace_registry import AGENT_WORKSPACES, get_workspace  # noqa: E402

SINA_HOME = Path.home() / ".sina"
WORKSPACES_ROOT = SINA_HOME / "agent-workspaces"
CONTEXT_INCIDENT = SOURCE_A / "CURSOR_AGENT_CONTEXT_MEMORY_INCIDENT_LOCKED_v1.md"
MAINTAINER_SELF_AUDIT_INCIDENT = SOURCE_A / "SINA_COMMAND_MAINTAINER_SELF_AUDIT_INCIDENT_LOCKED_v1.md"
AUTO_PASTE_INCIDENT = SOURCE_A / "SINAAI_AUTO_PASTE_INCIDENT_REPORT_LOCKED_v1.md"
BRAIN_CHAT_RECURSION_INCIDENT = (
    SOURCE_A / "brain-os/incidents/SINA_BRAIN_CHAT_VALIDATOR_RECURSION_INCIDENT_026_LOCKED_v1.md"
)
BRAIN_NO_FULL_E2E = SOURCE_A / "brain-os/law/enforcement/BRAIN_NO_FULL_E2E_SHELL_LOCKED_v1.md"
MAINTAINER_LOOP_SCRIPT = SCRIPT_DIR / "maintainer_self_audit_loop.py"
SKILL_PATH = Path.home() / ".cursor/skills/agent-self-audit-loop/SKILL.md"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _resolve_agent_id(explicit: str | None = None) -> str | None:
    if explicit:
        return explicit if get_workspace(explicit) else None
    cwd = Path.cwd().resolve()
    cwd_s = str(cwd)
    best: tuple[int, str] | None = None
    for spec in AGENT_WORKSPACES:
        root = Path(spec["repo_root"]).resolve()
        try:
            root.relative_to(cwd)
            depth = len(root.parts)
        except ValueError:
            try:
                cwd.relative_to(root)
                depth = len(cwd.parts) - len(root.parts)
            except ValueError:
                continue
        if best is None or depth < best[0]:
            best = (depth, spec["id"])
    if best:
        return best[1]
    hint = cwd.name.lower()
    for spec in AGENT_WORKSPACES:
        if spec.get("cursor_workspace_hint", "").lower() in cwd_s.lower():
            return spec["id"]
        if hint in spec.get("cursor_workspace_hint", "").lower().replace(" ", "-"):
            return spec["id"]
    if "noetfield-all-documents" in cwd_s.lower() or cwd.name == "Noetfield-All-Documents":
        return "noetfield_local"
    if cwd.name == "Noetfield":
        return "noetfield_cloud"
    if "trustfield" in cwd_s.lower():
        return "trustfield"
    return None


def _private_root(agent_id: str) -> Path:
    return WORKSPACES_ROOT / agent_id


def _ledger_path(agent_id: str) -> Path:
    return _private_root(agent_id) / "SESSION_LEDGER.jsonl"


def _append_ledger(agent_id: str, event: dict) -> None:
    p = _ledger_path(agent_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    row = {"ts": _now(), "agent_id": agent_id, **event}
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _load_state(agent_id: str) -> dict:
    p = _private_root(agent_id) / "incident-agent-state.json"
    if not p.is_file():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_audit_state(agent_id: str, patch: dict) -> None:
    p = _private_root(agent_id) / "incident-agent-state.json"
    st = _load_state(agent_id)
    st.update(patch)
    st["updated_at"] = _now()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(st, indent=2), encoding="utf-8")


def _build_mandatory_chain(spec: dict) -> str:
    agent_id = spec["id"]
    priv = _private_root(agent_id)
    n = 1
    lines = [
        f"# Mandatory read chain — {spec['label']}",
        "",
        f"**Agent:** `{agent_id}` · **Generated:** {_now()}",
        "",
        "Read in order **before editing**. Chat memory is not SSOT.",
        "",
        "**Law:** `SINA_COMMAND_DEACTIVATED_INCIDENT_READ_POLICY_LOCKED_v1.md` — session gate replaces read-all-incidents.",
        "",
        "## 1. Session gate (replaces incident compendium)",
        "",
        f"{n}. Run `python3 {SOURCE_A / 'scripts' / 'agent_session_gate_run_v1.py'} --role any` → `~/.sina/agent_session_gate_receipt_v1.json`",
    ]
    n += 1
    lines += [
        f"{n}. `{CONTEXT_INCIDENT}` — **summary only** if gate fails (do not paste full file)",
    ]
    n += 1
    lines += [
        "",
        "## 2. Optional incident ids (mirror only — not compendium)",
        "",
        "- INCIDENT-024 · 028 · 016 · 002 — read **only** when gate/truth bundle names one",
        "",
        "## 3. Deprecated (do not require every session)",
        "",
        f"- `{priv}/INCIDENT_REPORT_ALWAYS.md` — maintainer trim only; **never** founder-facing · **never** chat dump",
    ]
    n += 1
    if str(spec.get("repo_root", "")).endswith("SourceA"):
        lines += [
            f"- `{BRAIN_CHAT_RECURSION_INCIDENT}` — Brain chat only when routing validators",
            f"- `{BRAIN_NO_FULL_E2E}` §validator recursion",
        ]
    lines += [
        "",
        "## 4. Session memory",
        "",
        f"{n}. `{priv}/SESSION_CLOSEOUT_LATEST.md` (prior closeout — if missing, note first session)",
    ]
    n += 1
    lines.append(f"{n}. `{priv}/SESSION_LEDGER.jsonl` (tail last 5 events)")
    n += 1
    lines += [
        "",
        "## 5. Workspace law",
        "",
    ]
    session_prompt = priv / "WORKSPACE_SESSION_PROMPT_LOCKED.md"
    if session_prompt.is_file():
        lines.append(f"{n}. `{session_prompt}`")
        n += 1
    plan = Path(spec["repo_root"]) / "os" / "plan.json"
    if plan.is_file():
        lines.append(f"{n}. `{plan}`")
        n += 1
    if spec["id"] == "noetfield_local":
        lines.append(f"{n}. `~/Desktop/Noetfield/docs/ops/NOETFIELD_AGENT_TEAM_SYNC_LOCKED_v1.md` (if touching Noetfield ship)")
        n += 1
    if spec["id"] == "trustfield":
        lines.append(f"{n}. `docs/internal/AUTO_INTERNAL_PRIVACY_LOCK.md` (before www/GTM)")
        n += 1
    lines += [
        "",
        "## 4. Skill",
        "",
        f"- `@agent-self-audit-loop` → `{SKILL_PATH}`",
        "",
        "## Forbidden roots (this agent)",
        "",
    ]
    for fr in spec.get("forbidden_roots", []):
        lines.append(f"- `{fr}`")
    lines += [
        "",
        "## Closeout command",
        "",
        "```bash",
        f"python3 {SCRIPT_DIR}/cursor_agent_self_audit.py session-close --summary \"...\"",
        "```",
        "",
    ]
    return "\n".join(lines)


def cmd_session_start(agent_id: str) -> int:
    spec = get_workspace(agent_id)
    if not spec:
        print(f"ERROR: unknown agent {agent_id}", file=sys.stderr)
        return 1
    ensure_agent_incident_files(agent_id)
    priv = _private_root(agent_id)
    chain_path = priv / "MANDATORY_READ_CHAIN.md"
    chain_path.write_text(_build_mandatory_chain(spec), encoding="utf-8")
    _append_ledger(agent_id, {"type": "session_start", "cwd": os.getcwd()})
    _save_audit_state(
        agent_id,
        {
            "last_session_start_at": _now(),
            "last_session_start_week": iso_week_id(),
            "mandatory_chain_path": str(chain_path),
        },
    )
    print(f"AGENT_SELF_AUDIT_START agent={agent_id} label={spec['label']}")
    print(f"READ_CHAIN={chain_path}")
    print(f"INCIDENT_ALWAYS={priv / 'INCIDENT_REPORT_ALWAYS.md'}")
    closeout = priv / "SESSION_CLOSEOUT_LATEST.md"
    print(f"PRIOR_CLOSEOUT={closeout} exists={closeout.is_file()}")
    print(f"CONTEXT_INCIDENT={CONTEXT_INCIDENT}")
    print(f"FORBIDDEN={','.join(spec.get('forbidden_roots', []))}")
    print(f"REPO_ROOT={spec['repo_root']}")
    return 0


def cmd_log_event(agent_id: str, summary: str, evidence: str) -> int:
    if len(summary.strip()) < 8:
        print("ERROR: --summary at least 8 chars", file=sys.stderr)
        return 1
    _append_ledger(
        agent_id,
        {"type": "milestone", "summary": summary.strip(), "evidence": evidence.strip()},
    )
    print(f"OK logged milestone for {agent_id}")
    return 0


def cmd_session_close(
    agent_id: str,
    summary: str,
    files: str,
    verify: str,
    next_steps: str,
    incidents: str,
) -> int:
    spec = get_workspace(agent_id)
    if not spec:
        return 1
    if len(summary.strip()) < 20:
        print("ERROR: --summary at least 20 chars", file=sys.stderr)
        return 1
    priv = _private_root(agent_id)
    body = f"""# Session closeout — {spec['label']}

**Agent:** `{agent_id}`  
**Closed:** {_now()}  
**CWD:** `{os.getcwd()}`

## Summary

{summary.strip()}

## Files touched

{files.strip() or "_(none listed)_"}

## Verify / evidence

{verify.strip() or "_(not run)_"}

## Incidents / near-misses

{incidents.strip() or "_(none)_"}

## Next

{next_steps.strip() or "_(founder or next session)_"}

---

*Generated by `cursor_agent_self_audit.py session-close` — chat is not SSOT.*
"""
    out = priv / "SESSION_CLOSEOUT_LATEST.md"
    priv.mkdir(parents=True, exist_ok=True)
    out.write_text(body, encoding="utf-8")
    _append_ledger(
        agent_id,
        {
            "type": "session_close",
            "summary": summary.strip()[:500],
            "closeout_path": str(out),
        },
    )
    _save_audit_state(agent_id, {"last_session_close_at": _now(), "last_closeout_path": str(out)})
    insights = priv / "INCIDENT_MY_INSIGHTS.md"
    if insights.is_file():
        line = f"| {_now()[:10]} | Closeout: {summary.strip()[:120]} |"
        with insights.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    print(f"OK closeout written: {out}")
    return 0


def cmd_audit(agent_id: str) -> int:
    spec = get_workspace(agent_id)
    if not spec:
        return 1
    priv = _private_root(agent_id)
    failures: list[str] = []
    required = [
        priv / "INCIDENT_REPORT_ALWAYS.md",
        priv / "MANDATORY_READ_CHAIN.md",
        CONTEXT_INCIDENT,
        SKILL_PATH,
    ]
    for p in required:
        if not p.is_file():
            failures.append(f"missing: {p}")
    st = _load_state(agent_id)
    if not st.get("last_session_start_at"):
        failures.append("no session_start this workspace — run session-start")
    ledger = _ledger_path(agent_id)
    if not ledger.is_file():
        failures.append(f"missing ledger: {ledger}")
    brain_lib = Path.home() / "Desktop/SourceA/scripts/brain_sync_lib_v1.py"
    if brain_lib.is_file():
        try:
            import sys

            sys.path.insert(0, str(brain_lib.parent))
            from brain_sync_lib_v1 import brain_snapshot_status  # noqa: WPS433

            bst = brain_snapshot_status()
            if not bst.get("dual_proof_ok"):
                failures.append(
                    f"brain snapshot GAP live_vy={bst.get('live_vy')} brain_vy={bst.get('brain_vy')} "
                    "(run brain_sync_lib or hub Fix Brain sync)"
                )
        except Exception as exc:
            failures.append(f"brain_snapshot_status error: {exc}")
    if failures:
        print("AUDIT_FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"AUDIT_PASS agent={agent_id}")
    print(f"  last_session_start={st.get('last_session_start_at')}")
    print(f"  last_session_close={st.get('last_session_close_at', 'never')}")
    return 0


def cmd_bootstrap_all() -> int:
    for spec in AGENT_WORKSPACES:
        cmd_session_start(spec["id"])
    print(f"OK bootstrapped {len(AGENT_WORKSPACES)} agents")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Cursor agent self-audit loop")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_start = sub.add_parser("session-start", help="Ack session; write read chain")
    p_start.add_argument("--agent", default=None)

    p_log = sub.add_parser("log-event", help="Append milestone to SESSION_LEDGER")
    p_log.add_argument("--agent", default=None)
    p_log.add_argument("--summary", required=True)
    p_log.add_argument("--evidence", default="")

    p_close = sub.add_parser("session-close", help="Write SESSION_CLOSEOUT_LATEST.md")
    p_close.add_argument("--agent", default=None)
    p_close.add_argument("--summary", required=True)
    p_close.add_argument("--files", default="")
    p_close.add_argument("--verify", default="")
    p_close.add_argument("--next", default="", dest="next_steps")
    p_close.add_argument("--incidents", default="")

    p_audit = sub.add_parser("audit", help="Verify loop files exist")
    p_audit.add_argument("--agent", default=None)

    sub.add_parser("bootstrap-all", help="session-start for every registered agent")

    p_resolve = sub.add_parser("resolve-agent", help="Print agent id for cwd")
    p_resolve.add_argument("--agent", default=None)

    args = parser.parse_args()

    if args.cmd == "bootstrap-all":
        return cmd_bootstrap_all()

    agent_id = _resolve_agent_id(getattr(args, "agent", None))
    if args.cmd == "resolve-agent":
        print(agent_id or "UNKNOWN")
        return 0 if agent_id else 1

    if not agent_id:
        print("ERROR: could not resolve agent from cwd; pass --agent", file=sys.stderr)
        return 1

    if args.cmd == "session-start":
        return cmd_session_start(agent_id)
    if args.cmd == "log-event":
        return cmd_log_event(agent_id, args.summary, args.evidence)
    if args.cmd == "session-close":
        return cmd_session_close(
            agent_id, args.summary, args.files, args.verify, args.next_steps, args.incidents
        )
    if args.cmd == "audit":
        return cmd_audit(agent_id)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
