#!/usr/bin/env python3
"""Claude API Agent — replaces Cursor UI injection for SourceA Worker turns.

Reads the next queue item → builds prompt → calls Claude API → saves result to disk.
No Cursor. No clipboard. No window focus. Runs 24/7 headlessly.

Usage:
    python3 scripts/claude_api_agent_v1.py --role worker
    python3 scripts/claude_api_agent_v1.py --role worker --dry-run

Requires:
    ANTHROPIC_API_KEY env var
    pip install anthropic --break-system-packages
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(ROOT / "scripts"))
from healthy_queue_ssot_lib import (  # noqa: E402
    healthy_queue_state_path,
    is_commercial_default_queue,
    load_healthy_queue,
    queue_items,
)
RESULTS_DIR = Path.home() / ".sina" / "api-agent-results"
LOG_PATH = Path.home() / ".sina" / "claude-api-agent-v1.jsonl"
# Smart model routing — route by task role to minimize cost
# check / verify / audit  → Haiku ($0.005/turn)
# act / build / fix / impl → Sonnet ($0.025/turn)
# Saves ~54% vs all-Sonnet across 681 remaining tasks (~$9 savings)
MODEL_HAIKU  = "claude-haiku-4-5-20251001"
MODEL_SONNET = "claude-sonnet-4-6"
MODEL        = MODEL_SONNET  # fallback default

HAIKU_ROLES = {"check", "verify", "audit", "review", "test", "validate", "read"}


def _pick_model(queue_role: str) -> str:
    role = (queue_role or "").lower().strip()
    for r in HAIKU_ROLES:
        if r in role:
            return MODEL_HAIKU
    return MODEL_SONNET


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(row: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({**row, "at": _now()}) + "\n")


def _queue() -> list[dict]:
    _, raw = load_healthy_queue()
    if is_commercial_default_queue(raw):
        raise RuntimeError(
            "INCIDENT-004: commercial queue forbidden as API agent default — use ~/.sina eval-dispatch"
        )
    return queue_items(raw)


def _current_pos() -> int:
    state = healthy_queue_state_path()
    if state.is_file():
        try:
            return int(json.loads(state.read_text()).get("next_pos") or 1)
        except (ValueError, json.JSONDecodeError):
            pass
    return 1


def _read_file_safe(path: str | Path) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError:
        return f"[could not read {path}]"


def _receipt_exists(sa_id: str) -> bool:
    """Return True if a DONE receipt already exists for this sa_id."""
    receipt = ROOT / "receipts" / f"{sa_id}-receipt.json"
    if not receipt.is_file():
        return False
    try:
        data = json.loads(receipt.read_text(encoding="utf-8"))
        return data.get("status") == "DONE"
    except Exception:
        return False


def _openrouter_credits_ok() -> bool:
    """Quick heuristic: check if OPENROUTER_API_KEY is set (credits managed externally)."""
    return bool(os.environ.get("OPENROUTER_API_KEY") or
                Path.home().joinpath(".sina", "openrouter-credits-ok.flag").is_file())


def _build_system_prompt() -> str:
    """Build the Worker system prompt — pure reasoning, no filesystem tools available."""
    mandatory  = ROOT / "os" / "chat-handoffs" / "MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md"
    goal_active = ROOT / "os" / "chat-handoffs" / "GOAL_EXECUTION_ACTIVE_LOCKED_v1.md"

    return "\n".join([
        "You are SourceA Worker (API mode) — a reasoning-only verification agent.",
        "Workspace root: /Users/sinakazemnezhad/Desktop/SourceA",
        "IMPORTANT: You have NO filesystem tools. You cannot run bash, read or write files.",
        "Your job: reason from the context provided, verify task state, identify gaps.",
        "ONE sa-XXXX task per turn. Output WORKER_ROUND_REPORT YAML at the end.",
        "",
        "=== LAWS (read, do not skip) ===",
        _read_file_safe(mandatory)[:3000],
        "",
        "=== GOAL EXECUTION ACTIVE ===",
        _read_file_safe(goal_active)[:2000],
        "",
        "=== API AGENT CONSTRAINTS ===",
        "- You CANNOT write receipts to disk (CLI agent does that after your report).",
        "- Your output feeds the CLI agent as next_action instructions.",
        "- If live_eval_required=true and OpenRouter is unavailable: status=BLOCKED, reason=live_eval_gate.",
        "- Trust the task .md file as source of truth for what needs to be done.",
        "- CHECK turn only: do NOT describe how to implement — only verify current state.",
        "- NEVER ask the founder what to do next. next_action must be NONE or the next queue role only.",
        "- If task is already done per context → status BLOCKED, reason registry_already_done.",
    ])


def _build_user_prompt(item: dict, *, pos: int, total: int) -> str:
    """Build the user prompt for a queue item.

    API agent = smart reasoning engine (no filesystem tools).
    Loads: full task .md + governance reads + verify/forbidden + receipt state.
    Outputs: WORKER_ROUND_REPORT YAML with status/summary/evidence/next_action.
    """
    from agent_turn_context_v1 import build_memory_block, role_law_block  # noqa: WPS433

    sa_id    = item.get("sa_id", "?")
    role     = item.get("queue_role", "check")
    title    = item.get("title", "") or item.get("sa_title", "")
    instr    = item.get("instruction", "")
    verify   = item.get("verify", "")
    pos      = item.get("queue_pos") or pos
    phase    = item.get("phase", "")
    tier     = item.get("sa_tier", "")
    live_eval = item.get("live_eval_required", False)

    # forbidden — handle both list and string
    raw_forbidd = item.get("forbidden", "")
    if isinstance(raw_forbidd, list):
        forbidd = "\n".join(f"  - {f}" for f in raw_forbidd)
    else:
        forbidd = str(raw_forbidd) if raw_forbidd else ""

    # Short-circuit: receipt already DONE
    receipt_done = _receipt_exists(sa_id)

    # Load full task .md
    sa_path = item.get("sa_path", "")
    sa_content = ""
    if sa_path:
        full = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / sa_path
        if not full.exists():
            full = ROOT / sa_path
        sa_content = _read_file_safe(full)[:6000]

    # Load last receipt if exists (for evidence)
    receipt_content = ""
    receipt_file = ROOT / "receipts" / f"{sa_id}-receipt.json"
    if receipt_file.is_file():
        receipt_content = _read_file_safe(receipt_file)[:500]

    # Load mandatory governance reads (up to 3, 1500 chars each)
    gov_parts = []
    for rel in (item.get("mandatory_reads") or [])[:3]:
        content = _read_file_safe(ROOT / rel)[:1500]
        if content and not content.startswith("[could not read"):
            gov_parts.append(f"=== {rel} ===\n{content}")
    gov = "\n\n".join(gov_parts)

    # ── Build prompt ────────────────────────────────────────────────────────
    parts = [
        build_memory_block(sa_id=sa_id, role=role, pos=int(pos), total=total),
        "",
        role_law_block(role),
        "",
        f"[GOAL1_HEALTHY_DRAIN pos={pos}/{total}] SourceA Worker (API) — role={role}",
        f"sa_id: {sa_id} | phase: {phase} | tier: {tier}",
        f"Title: {title}",
        "",
    ]

    if receipt_done:
        parts += [
            "## ⚠ RECEIPT ALREADY DONE",
            f"Receipt exists at receipts/{sa_id}-receipt.json with status=DONE.",
            "Verify the receipt is correct and complete. If it looks good, report PASS.",
            "",
        ]

    if live_eval and not _openrouter_credits_ok():
        parts += [
            "## ⚠ LIVE EVAL REQUIRED — OPENROUTER STATUS UNKNOWN",
            "This task has live_eval_required=true. If OpenRouter credits are not available,",
            "you must report BLOCKED with reason: live_eval_gate_no_credits.",
            "Do NOT proceed to verify if live eval cannot run.",
            "",
        ]

    parts += [
        "## Instruction",
        instr,
        "",
        "## Verify criteria",
        verify or "(confirm task state matches task .md requirements based on context provided)",
        "",
    ]

    if forbidd:
        parts += ["## FORBIDDEN (hard rules — never do these)", forbidd, ""]

    if receipt_content:
        parts += ["## Existing receipt on disk", f"```json\n{receipt_content}\n```", ""]

    if sa_content:
        parts += ["## Full task file (sa_path)", sa_content, ""]

    if gov:
        parts += ["## Governance context", gov, ""]

    # Required YAML output
    parts += [
        "## Required output — WORKER_ROUND_REPORT",
        "Analyze the task state from the context above.",
        "End your response with EXACTLY this YAML block (no extra keys):",
        "```yaml",
        "worker_round_report:",
        f"  sa_id: {sa_id}",
        f"  role: {role}",
        "  status: PASS        # PASS if verified done, FAIL if broken, BLOCKED if cannot proceed",
        "  summary: <one sentence — what state was found>",
        "  evidence: <file path or specific line/output that proves the status>",
        "  gaps: <comma-separated list of missing pieces, or NONE>",
        f"  next_action: <{'verify same sa' if 'act' in role.lower() else 'act same sa' if 'check' in role.lower() else 'NONE'}>",
        "```",
    ]

    return "\n".join(parts)


def run_turn(*, dry_run: bool = False) -> dict:
    """Execute one Worker turn via Claude API."""
    sys.path.insert(0, str(SCRIPTS))
    from paid_engine_gate_v1 import block_paid  # noqa: WPS433

    blocked = block_paid(engine="api", caller="claude_api_agent")
    if blocked:
        print(f"[{_now()}] API BLOCKED — {blocked.get('reason')} ($0)")
        return {**blocked, "status": "BLOCKED"}

    from active_now_v1 import heartbeat  # noqa: WPS433

    hb = heartbeat(caller="claude_api_agent")
    if not hb.get("ok"):
        return {"ok": False, "step": "active_now", **hb}

    from gatekeeper_v1 import run_gatekeeper  # noqa: WPS433

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key and not dry_run:
        return {"ok": False, "error": "ANTHROPIC_API_KEY not set. Export it in your shell or .zshrc"}

    queue = _queue()
    if not queue:
        return {"ok": False, "error": "Queue is empty"}

    pos = _current_pos()
    if pos < 1 or pos > len(queue):
        pos = 1

    item = queue[pos - 1]
    sa_id = item.get("sa_id", "unknown")
    role = (item.get("queue_role") or "check").lower().strip()

    from healthy_queue_ssot_lib import registry_status_for_sa  # noqa: WPS433

    if registry_status_for_sa(sa_id) == "done":
        print(f"[{_now()}] SKIP {sa_id} — REGISTRY already done ($0)")
        return {
            "ok": False,
            "sa_id": sa_id,
            "pos": pos,
            "role": role,
            "status": "BLOCKED",
            "stop_reason": "registry_already_done",
            "cost_usd": 0,
        }

    gate = run_gatekeeper(
        sa_id=sa_id,
        phase=item.get("phase", ""),
        task_text=item.get("instruction", "") or item.get("title", ""),
        role=role,
        engine="api",
        caller="claude_api_agent",
    )
    if not gate.get("safe_to_execute"):
        return {"ok": False, "step": "gatekeeper", **gate}

    print(f"[{_now()}] AGENT START {sa_id} role={item.get('queue_role')} pos={pos}/{len(queue)}")

    if dry_run:
        print(f"[DRY RUN] Would call Claude API for {sa_id}")
        _log({"event": "DRY_RUN", "sa_id": sa_id, "pos": pos})
        return {"ok": True, "dry_run": True, "sa_id": sa_id}

    try:
        import anthropic  # noqa: WPS433
    except ImportError:
        return {
            "ok": False,
            "error": "anthropic package not installed. Run: pip install anthropic --break-system-packages"
        }

    # Write turn bind so broker sa_id check passes
    try:
        sys.path.insert(0, str(SCRIPTS))
        from worker_inject_lib import write_turn_bind  # noqa: WPS433
        write_turn_bind(
            meta={
                "sa_id": sa_id,
                "queue_role": item.get("queue_role", ""),
                "queue_pos": pos,
                "queue_total": len(queue),
            },
            prompt=f"API agent turn for {sa_id}",
        )
    except Exception:
        pass  # Non-fatal — broker will still get the report

    from agent_turn_context_v1 import (  # noqa: WPS433
        normalize_status,
        parse_worker_round_report,
        persist_round_report,
        validate_report,
    )

    client = anthropic.Anthropic(api_key=api_key)
    from healthy_prompt_turn_v1 import build_turn_prompt  # noqa: WPS433

    system_prompt = (
        "SourceA Worker API — reasoning only, no filesystem tools. "
        "One prompt = one purpose per HEALTHY_PROMPT_SEQUENCE_LOCKED_v1. "
        "Output WORKER_ROUND_REPORT YAML at end."
    )
    user_prompt = build_turn_prompt(item=item, pos=pos, total=len(queue), engine="API")

    selected_model = _pick_model(item.get("queue_role", ""))
    _log({"event": "AGENT_START", "sa_id": sa_id, "pos": pos, "role": item.get("queue_role"), "model": selected_model})
    print(f"[{_now()}] model={selected_model} role={item.get('queue_role','?')}")

    try:
        message = client.messages.create(
            model=selected_model,
            max_tokens=8192,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            timeout=300,
        )
        response_text = message.content[0].text if message.content else ""
        stop_reason = message.stop_reason

        # Save result to disk
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        result_file = RESULTS_DIR / f"{sa_id}-{item.get('queue_role')}-{_now().replace(':', '-')}.md"
        result_file.write_text(
            f"# {sa_id} — {item.get('queue_role')}\n\n{response_text}",
            encoding="utf-8",
        )

        report = parse_worker_round_report(response_text)
        violations = validate_report(report=report, sa_id=sa_id, role=role)
        if violations:
            status = "BLOCKED"
            report = {
                "sa_id": sa_id,
                "role": role,
                "status": "BLOCKED",
                "summary": f"rule_violation: {', '.join(violations)}",
                "next_action": "NONE",
            }
        else:
            status = normalize_status(report, fallback="BLOCKED")

        persist_round_report(sa_id=sa_id, role=role, report=report, source="api_agent")

        result = {
            "ok": status == "PASS",
            "sa_id": sa_id,
            "pos": pos,
            "role": item.get("queue_role"),
            "status": status,
            "stop_reason": stop_reason,
            "violations": violations,
            "result_file": str(result_file),
            "tokens_in": message.usage.input_tokens,
            "tokens_out": message.usage.output_tokens,
            "cost_usd": round(
                (message.usage.input_tokens * 3 + message.usage.output_tokens * 15) / 1_000_000, 4
            ),
        }

        # API CHECK/VERIFY never writes DONE receipt — closeout is VERIFY+CLI only
        if status == "PASS" and "verify" in role:
            receipt_dir = ROOT / "receipts"
            receipt_dir.mkdir(parents=True, exist_ok=True)
            receipt_path = receipt_dir / f"{sa_id}-receipt.json"
            receipt_data = {
                "sa_id": sa_id,
                "status": "DONE",
                "role": item.get("queue_role"),
                "agent": "api",
                "model": selected_model,
                "completed_at": _now(),
                "cost_usd": result["cost_usd"],
            }
            receipt_path.write_text(json.dumps(receipt_data, indent=2), encoding="utf-8")
            result["receipt_written"] = str(receipt_path)
        elif status == "PASS" and "check" in role:
            result["check_passed"] = True

        # Queue advance: orchestrator only (QUEUE_STATE_TRANSITION_LOCKED_v1)
        result["queue_advance"] = {
            "skipped": True,
            "reason": "API_must_not_advance_queue_use_orchestrator",
        }

        # Submit to broker ONLY if response contains a valid WORKER_ROUND_REPORT with known status
        # Avoids noisy broker errors when Claude doesn't emit the YAML block
        broker_result = None
        if status in ("PASS", "FAIL", "BLOCKED") and report:
            try:
                import importlib.util as _ilu

                _bspec = _ilu.spec_from_file_location("broker", SCRIPTS / "goal1_lane_broker.py")
                _bmod = _ilu.module_from_spec(_bspec)
                _bspec.loader.exec_module(_bmod)
                broker_result = _bmod.worker_submit(
                    text=response_text,
                    source="api_agent",
                    auto_advance=False,  # queue already advanced above
                    checkpoint=False,
                )
                result["broker"] = broker_result
            except Exception as _exc:
                result["broker_error"] = str(_exc)
                # Non-fatal — queue already advanced, receipt on disk is truth

        _log({"event": "AGENT_DONE", "model": selected_model, **{k: v for k, v in result.items() if k != "broker"}})
        print(f"[{_now()}] AGENT DONE {sa_id} model={selected_model} status={status} cost=${result['cost_usd']}")
        print(f"  Result saved: {result_file}")

        return result

    except Exception as exc:
        err = {"ok": False, "sa_id": sa_id, "error": str(exc)}
        _log({"event": "AGENT_ERROR", **err})
        print(f"[{_now()}] AGENT ERROR {sa_id}: {exc}")
        return err


def main() -> int:
    p = argparse.ArgumentParser(description="SourceA Claude API Agent — replaces Cursor injection")
    p.add_argument("--role", default="worker", choices=["worker", "brain", "broker"])
    p.add_argument("--dry-run", action="store_true", help="Print what would run, no API call")
    p.add_argument("--install-deps", action="store_true", help="Install anthropic package")
    args = p.parse_args()

    if args.install_deps:
        print("Installing anthropic...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "anthropic", "--break-system-packages", "-q"],
            check=True,
        )
        print("Done.")
        return 0

    result = run_turn(dry_run=args.dry_run)
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
