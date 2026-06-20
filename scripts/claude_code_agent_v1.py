#!/usr/bin/env python3
"""SourceA Claude Code CLI Worker — glass-box execution engine.

Uses `claude -p --output-format stream-json` so every tool call (Bash, Read,
Write, Edit) is captured in real time.  Full execution trace + receipt saved
per task.  Drop-in replacement for claude_api_agent_v1.py.

Usage:
    python3 scripts/claude_code_agent_v1.py            # run one turn
    python3 scripts/claude_code_agent_v1.py --dry-run  # validate queue only
    python3 scripts/claude_code_agent_v1.py --trace    # print live tool calls

Law: brain-os/laws/  (all governance files apply)
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT        = Path(__file__).resolve().parents[1]
SCRIPTS     = ROOT / "scripts"
sys.path.insert(0, str(ROOT / "scripts"))
from healthy_queue_ssot_lib import (  # noqa: E402
    healthy_queue_state_path,
    is_commercial_default_queue,
    load_healthy_queue,
    queue_items,
)
RESULTS_DIR = Path.home() / ".sina" / "cc-agent-results"
LOG_PATH    = Path.home() / ".sina" / "claude-code-agent-v1.jsonl"
TRACE_DIR   = Path.home() / ".sina" / "exec-traces"

# ── Full-stack routing ──────────────────────────────────────────────────────
# CLI agent handles HIGH-TOOL tasks (act/build/fix/implement).
# Low-tool tasks (verify/check) are better served by API agent — but CLI can
# run them too when called directly.  Model is picked by role.
MODEL_HAIKU  = "claude-haiku-4-5-20251001"
MODEL_SONNET = "claude-sonnet-4-6"

# Roles that expect real filesystem tool use → Sonnet
ACT_ROLES   = {"act", "implement", "build", "fix", "patch", "create", "write", "exec"}
# Roles that are reasoning-only → Haiku (CLI can still run them)
CHECK_ROLES = {"check", "verify", "audit", "review", "test", "validate", "read", "assess"}

# Per-turn budget caps — safety valve
BUDGET_SONNET = 0.30   # $0.30 max for complex act turns
BUDGET_HAIKU  = 0.02   # $0.02 max for check turns


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(row: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({**row, "at": _now()}) + "\n")


def _pick_model(role: str) -> tuple[str, float]:
    """Route by tool complexity:
    act/build/implement → Sonnet (needs real tool use)
    verify/check/audit  → Haiku  (reasoning only, no tools needed)
    unknown             → Sonnet (safe default)
    """
    r = (role or "").lower()
    for cr in CHECK_ROLES:
        if cr in r:
            return MODEL_HAIKU, BUDGET_HAIKU
    return MODEL_SONNET, BUDGET_SONNET


def _queue() -> list[dict]:
    _, raw = load_healthy_queue()
    if is_commercial_default_queue(raw):
        raise RuntimeError(
            "INCIDENT-004: commercial queue forbidden as CLI default — use ~/.sina eval-dispatch"
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


def _complete_via_orchestrator(*, sa_id: str, role: str) -> dict:
    """Write round report + let orchestrator advance (single queue writer)."""
    sys.path.insert(0, str(SCRIPTS))
    from worker_turn_lib import write_round_report  # noqa: WPS433

    write_round_report(sa_id=sa_id, round_type=role or "implement")
    import subprocess

    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "healthy-drain-orchestrator-v1.py"), "poll"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    try:
        body = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except json.JSONDecodeError:
        body = {"raw": proc.stdout, "stderr": proc.stderr}
    return {"ok": proc.returncode == 0, "orchestrator": body}


def _receipt_exists_cli(sa_id: str) -> bool:
    """Return True if a DONE receipt already exists for this sa_id."""
    receipt = ROOT / "receipts" / f"{sa_id}-receipt.json"
    if not receipt.is_file():
        return False
    try:
        data = json.loads(receipt.read_text(encoding="utf-8"))
        return data.get("status") == "DONE"
    except Exception:
        return False


def _build_worker_prompt(item: dict, pos: int, total: int) -> str:
    """Build the CLI Worker prompt — has real tools: Bash, Read, Write, Edit.

    Optimized for:
    - Receipt-skip guard (don't re-run DONE tasks)
    - Full task .md loaded (sources + verify commands + closeout steps)
    - Forbidden list handled as both list and string
    - live_eval_required flag surfaced
    - Explicit execution steps with receipt format
    """
    sa_id    = item.get("sa_id", "?")
    role     = item.get("queue_role", "act")
    title    = item.get("title", "") or item.get("sa_title", "")
    instr    = item.get("instruction", "")
    verify   = item.get("verify", "")
    phase    = item.get("phase", "")
    tier     = item.get("sa_tier", "")
    live_eval = item.get("live_eval_required", False)

    # forbidden — handle list or string
    raw_forbidd = item.get("forbidden", "")
    if isinstance(raw_forbidd, list):
        forbidd_str = "\n".join(f"  - {f}" for f in raw_forbidd)
    else:
        forbidd_str = str(raw_forbidd) if raw_forbidd else ""

    def _rf(p: Path, limit: int = 2000) -> str:
        try:
            return p.read_text(encoding="utf-8")[:limit]
        except Exception:
            return ""

    # Load mandatory governance reads (first 3, 1500 chars each)
    gov_parts = []
    for rel in (item.get("mandatory_reads") or [])[:3]:
        content = _rf(ROOT / rel, 1500)
        if content:
            gov_parts.append(f"=== {rel} ===\n{content}")
    # Fallback to mandatory worker chat if no reads found
    if not gov_parts:
        fallback = _rf(ROOT / "os" / "chat-handoffs" / "MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md", 2000)
        if fallback:
            gov_parts.append(f"=== MANDATORY_WORKER_CONTRACT ===\n{fallback}")
    gov = "\n\n".join(gov_parts)

    # Load full task .md
    sa_path = item.get("sa_path", "")
    sa_content = ""
    if sa_path:
        full = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / sa_path
        if not full.exists():
            full = ROOT / sa_path
        sa_content = _rf(full, 5000)

    # Check receipt state
    receipt_done = _receipt_exists_cli(sa_id)
    receipt_path = ROOT / "receipts" / f"{sa_id}-receipt.json"
    existing_receipt = _rf(receipt_path, 400) if receipt_path.is_file() else ""

    # ── Build prompt ────────────────────────────────────────────────────────
    receipt_json = (
        f'{{"sa_id":"{sa_id}","status":"DONE",'
        f'"files_written":[],"commands_run":[],"summary":"<one sentence>"}}'
    )
    blocked_json = (
        f'{{"sa_id":"{sa_id}","status":"BLOCKED",'
        f'"reason":"<why blocked>","files_written":[],"commands_run":[]}}'
    )

    from agent_turn_context_v1 import build_memory_block, role_law_block  # noqa: WPS433

    prompt = f"""You are SourceA Worker (CLI mode). You have tools: Bash, Read, Write, Edit.
Workspace: {ROOT}
Task: {sa_id} | role={role} | pos={pos}/{total} | phase={phase} | tier={tier}
Title: {title}

{build_memory_block(sa_id=sa_id, role=role, pos=pos, total=total)}

{role_law_block(role)}
"""

    if receipt_done:
        prompt += f"""
⚠ RECEIPT ALREADY EXISTS with status=DONE:
{existing_receipt}

GATE: Receipt is DONE. Do NOT re-implement. Verify the receipt is accurate:
1. Read receipts/{sa_id}-receipt.json
2. Confirm the claimed files/commands actually exist and are correct
3. If receipt is valid → exit (do nothing more)
4. If receipt is wrong → fix it and re-verify
"""
    else:
        prompt += f"""
=== INSTRUCTION ===
{instr}

=== VERIFY CRITERIA ===
{verify or "Run the §Verify commands from the task file. Confirm task is complete."}
"""

    if forbidd_str:
        prompt += f"""
=== FORBIDDEN — HARD STOP if any of these occur ===
{forbidd_str}
"""

    if live_eval:
        prompt += """
=== LIVE EVAL REQUIRED ===
This task requires live_eval_required=true.
Before implementing, check: curl -s http://127.0.0.1:13020/status | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('eval_credits_ok', False))"
If eval gateway is unavailable: write BLOCKED receipt and stop.
"""

    prompt += f"""
=== FULL TASK FILE ===
{sa_content or "(could not load — check sa_path in queue item)"}

=== GOVERNANCE ===
{gov}

=== EXECUTION CONTRACT (follow in order) ===
STEP 0 — FEASIBILITY:
  Run: python3 scripts/prompt_feasibility_gate.py --role worker --strict 2>/dev/null || echo "gate_not_found"
  If FEASIBILITY_BLOCKED → write BLOCKED receipt, stop.

STEP 1 — VALIDATE first (read task .md sources, run verify commands from §Verify section):
  Read the task file, identify §Verify bash commands, run them.

STEP 2 — ACT (only if role=act and task not already done):
  Implement the minimal diff required. No batch. No scope creep.

STEP 3 — RE-VERIFY:
  Run §Verify commands again. Confirm all pass.

STEP 4 — WRITE RECEIPT (mandatory):
  Write to: {ROOT}/receipts/{sa_id}-receipt.json
  If DONE: {receipt_json}
  If BLOCKED: {blocked_json}

STEP 5 — OUTPUT WORKER_ROUND_REPORT (mandatory — broker requires this):
  After writing receipt, end your FINAL TEXT with this exact YAML block:
  ```yaml
  worker_round_report:
    sa_id: {sa_id}
    role: {role}
    status: PASS
    summary: <one sentence what was done or verified>
    evidence: <receipt path or verify command output>
    gaps: <NONE or comma-separated list>
    next_action: <NONE or what the next turn should do>
  ```
  Use status: PASS if done/verified, FAIL if broken, BLOCKED if cannot proceed.

RULES:
- ONE task only. Stop after WORKER_ROUND_REPORT is output.
- NEVER ask the founder what to do next. next_action must be NONE or the next queue role only.
- If REGISTRY already marks this sa_id done → BLOCKED registry_already_done, zero tools, stop.
- Never modify governance files (os/, brain-os/laws/, .cursor/rules/).
- Never run "pick 30" or batch operations.
- If any verify step fails after 2 attempts → status=BLOCKED in receipt + WORKER_ROUND_REPORT.
"""
    return prompt


def _parse_stream(stream_output: str) -> dict:
    """Parse Claude Code CLI stream-json output.

    Event types emitted by `claude --verbose --output-format stream-json`:
      {"type":"system","subtype":"init",...}
      {"type":"assistant","message":{"content":[...],"usage":{...}}}
      {"type":"tool","name":"Bash","input":{...},"output":"..."}
      {"type":"result","subtype":"success","result":"...","total_cost_usd":...}
    """
    tool_calls: list[dict] = []
    files_written: list[str] = []
    commands_run: list[str] = []
    bash_outputs: list[str] = []
    final_text = ""
    cost_usd = 0.0
    input_tokens = 0
    output_tokens = 0

    for line in stream_output.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue

        etype = ev.get("type", "")

        # ── assistant turn: text + tool calls + usage ─────────────────────────
        if etype == "assistant":
            msg   = ev.get("message", {})
            usage = msg.get("usage", {})
            if usage.get("input_tokens"):
                input_tokens  = int(usage["input_tokens"])
            if usage.get("output_tokens"):
                output_tokens = int(usage["output_tokens"])
            for block in msg.get("content", []):
                if not isinstance(block, dict):
                    continue
                btype = block.get("type", "")
                if btype == "text":
                    final_text += block.get("text", "")
                elif btype == "tool_use":
                    name = block.get("name", "")
                    inp  = block.get("input") or {}
                    tool_calls.append({"tool": name, "input": inp})
                    if name == "Bash":
                        cmd = inp.get("command", "")
                        if cmd:
                            commands_run.append(cmd[:200])
                    elif name in ("Write", "Edit"):
                        fp = inp.get("file_path") or inp.get("path", "")
                        if fp:
                            files_written.append(fp)

        # ── tool result (bash stdout, file reads, etc.) ───────────────────────
        elif etype == "tool":
            out = ev.get("output", "")
            if out:
                bash_outputs.append(str(out)[:300])

        # ── final result event ────────────────────────────────────────────────
        elif etype == "result":
            cost_usd   = float(ev.get("total_cost_usd") or ev.get("cost_usd") or 0)
            final_text = final_text or (ev.get("result", "") or "")
            # Some CLI versions embed usage here too
            u = ev.get("usage", {})
            if u.get("input_tokens") and not input_tokens:
                input_tokens  = int(u["input_tokens"])
            if u.get("output_tokens") and not output_tokens:
                output_tokens = int(u["output_tokens"])

    return {
        "tool_calls":    tool_calls,
        "files_written": list(dict.fromkeys(files_written)),
        "commands_run":  commands_run,
        "bash_outputs":  bash_outputs,
        "final_text":    final_text[:2000],
        "cost_usd":      cost_usd,
        "input_tokens":  input_tokens,
        "output_tokens": output_tokens,
    }


def run_turn(*, dry_run: bool = False, trace: bool = False) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from paid_engine_gate_v1 import block_paid  # noqa: WPS433

    blocked = block_paid(engine="cli", caller="claude_code_agent")
    if blocked:
        print(f"[{_now()}] CLI BLOCKED — {blocked.get('reason')} ($0)")
        return {**blocked, "status": "BLOCKED", "billed": False}

    from active_now_v1 import heartbeat  # noqa: WPS433

    hb = heartbeat(caller="claude_code_agent")
    if not hb.get("ok") or not hb.get("heartbeat"):
        return {"ok": False, "step": "execution_law", **hb}

    from gatekeeper_v1 import run_gatekeeper  # noqa: WPS433

    queue = _queue()
    if not queue:
        return {"ok": False, "error": "QUEUE_EMPTY"}

    pos   = _current_pos()
    total = len(queue)
    if pos < 1 or pos > total:
        pos = 1
    item  = queue[pos - 1]
    sa_id = item.get("sa_id", f"sa-{pos:04d}")
    role  = item.get("queue_role", "act")
    phase = item.get("phase", "")

    from healthy_queue_ssot_lib import registry_status_for_sa  # noqa: WPS433

    role_lower = (role or "").lower()
    from overnight_turn_guard_v1 import is_cli_act_role  # noqa: WPS433

    if not is_cli_act_role(role):
        print(f"[{_now()}] REJECT {sa_id} — CLI only for ACT role={role} ($0, no claude call)")
        return {
            "ok": False,
            "sa_id": sa_id,
            "pos": pos,
            "role": role,
            "status": "BLOCKED",
            "stop_reason": "cli_act_only",
            "cost_usd": 0,
            "billed": False,
        }

    if _receipt_exists_cli(sa_id) and "act" in role_lower:
        print(f"[{_now()}] SKIP {sa_id} — receipt DONE, ACT redundant ($0)")
        return {
            "ok": False,
            "sa_id": sa_id,
            "pos": pos,
            "role": role,
            "status": "BLOCKED",
            "stop_reason": "receipt_already_done",
            "cost_usd": 0,
            "billed": False,
        }

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

    if _receipt_exists_cli(sa_id) and "check" in (role or "").lower():
        print(f"[{_now()}] SKIP {sa_id} — receipt DONE, CHECK redundant ($0)")
        return {
            "ok": False,
            "sa_id": sa_id,
            "pos": pos,
            "role": role,
            "status": "BLOCKED",
            "stop_reason": "receipt_already_done",
            "cost_usd": 0,
        }

    gate = run_gatekeeper(
        sa_id=sa_id,
        phase=phase,
        task_text=item.get("instruction", "") or item.get("title", ""),
        role=role.lower(),
        engine="cli",
        caller="claude_code_agent",
    )
    if not gate.get("safe_to_execute"):
        return {"ok": False, "step": "gatekeeper", **gate}

    model, budget = _pick_model(role)

    print(f"[{_now()}] CC-AGENT START {sa_id} role={role} pos={pos}/{total} model={model}")

    if dry_run:
        print(f"[DRY RUN] Would run claude CLI for {sa_id}")
        return {"ok": True, "dry_run": True, "sa_id": sa_id, "model": model}

    from healthy_prompt_turn_v1 import build_turn_prompt  # noqa: WPS433

    prompt = build_turn_prompt(item=item, pos=pos, total=total, engine="CLI")

    # Find claude path + load full shell env (picks up ANTHROPIC_API_KEY from .zshrc)
    _find = subprocess.run(
        ["zsh", "-lc", "source ~/.zshrc 2>/dev/null; which claude; echo '---ENV---'; env"],
        capture_output=True, text=True, timeout=20
    )
    lines = _find.stdout.splitlines()
    claude_path = ""
    shell_env: dict[str, str] = {}
    in_env = False
    for ln in lines:
        if ln == "---ENV---":
            in_env = True
            continue
        if not in_env:
            if ln.strip() and not claude_path:
                claude_path = ln.strip()
        else:
            if "=" in ln:
                k, _, v = ln.partition("=")
                shell_env[k] = v
    env = {**shell_env, **os.environ}  # os.environ wins for any conflicts
    print(f"[{_now()}] claude path: '{claude_path}'  ANTHROPIC_API_KEY={'set' if env.get('ANTHROPIC_API_KEY') else 'MISSING'}")
    if not claude_path:
        return {"ok": False, "sa_id": sa_id, "error": "CLAUDE_CLI_NOT_FOUND",
                "hint": "Run: npm install -g @anthropic-ai/claude-code"}

    # Call claude DIRECTLY as a list — prompt passed as a literal argument,
    # zero shell interpretation, no escaping issues, no stdin tricks needed.
    cmd = [
        claude_path,
        "-p", prompt,
        "--verbose",
        "--output-format", "stream-json",
        "--model", model,
        "--allowedTools", "Bash,Edit,Read,Write",
        "--add-dir", str(ROOT),
    ]

    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(ROOT),
            env=env,
        )
        elapsed = time.time() - t0
        raw_out = proc.stdout or ""
        raw_err = proc.stderr or ""
    except subprocess.TimeoutExpired:
        return {"ok": False, "sa_id": sa_id, "error": "TIMEOUT", "elapsed": 300}

    # Parse stream output
    parsed = _parse_stream(raw_out)

    if trace:
        print(f"\n{'='*50} EXECUTION TRACE {sa_id} {'='*50}")
        for i, tc in enumerate(parsed["tool_calls"], 1):
            tool = tc["tool"]
            inp  = tc["input"]
            if tool == "Bash":
                print(f"  [{i}] BASH: {inp.get('command','')[:120]}")
            elif tool in ("Write","Edit"):
                print(f"  [{i}] {tool}: {inp.get('file_path') or inp.get('path','')}")
            elif tool == "Read":
                print(f"  [{i}] READ: {inp.get('file_path','')}")
        for bo in parsed["bash_outputs"]:
            if bo.strip():
                print(f"  OUTPUT: {bo[:200]}")
        print(f"  FILES WRITTEN: {parsed['files_written']}")
        print(f"  COST: ${parsed['cost_usd']:.5f} | tokens in={parsed['input_tokens']} out={parsed['output_tokens']}")
        print('='*120)

    # Save execution trace
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    trace_file = TRACE_DIR / f"{sa_id}-trace.jsonl"
    trace_data = {
        "sa_id": sa_id, "role": role, "model": model,
        "pos": pos, "total": total, "elapsed": round(elapsed, 1),
        **parsed, "raw_err": raw_err[:500] if raw_err else "",
        "at": _now(),
    }
    trace_file.write_text(json.dumps(trace_data, indent=2), encoding="utf-8")

    from agent_turn_context_v1 import (  # noqa: WPS433
        normalize_status,
        parse_worker_round_report,
        persist_round_report,
        validate_report,
    )

    # Log stderr for debugging
    if raw_err:
        print(f"[{_now()}] STDERR: {raw_err[:400]}")
    _err_lower = raw_err.lower()
    _hard_error = any(e in _err_lower for e in ["error:", "fatal:", "unrecognized option", "unknown flag"])
    cli_ok = proc.returncode == 0 and not _hard_error

    report = parse_worker_round_report(parsed.get("final_text") or "")
    violations = validate_report(report=report, sa_id=sa_id, role=role)
    role_lower = (role or "").lower()
    if "check" in role_lower and any(tc.get("tool") in ("Write", "Edit") for tc in parsed.get("tool_calls") or []):
        violations.append("check_forbidden_write_edit")

    if violations:
        status = "BLOCKED"
        report = {
            "sa_id": sa_id,
            "role": role,
            "status": "BLOCKED",
            "summary": f"rule_violation: {', '.join(violations)}",
            "next_action": "NONE",
        }
        cli_ok = False
    elif report:
        status = normalize_status(report, fallback="BLOCKED" if not cli_ok else "PASS")
        persist_round_report(sa_id=sa_id, role=role, report=report, source="cli_agent")
    else:
        violations = ["missing_worker_round_report"]
        status = "BLOCKED"
        cli_ok = False

    ok = status == "PASS" and cli_ok and not violations

    # Save result
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    result_file = RESULTS_DIR / f"{sa_id}-result.json"
    result = {
        "ok": ok,
        "sa_id": sa_id,
        "role": role,
        "model": model,
        "status": status,
        "violations": violations,
        "pos": pos,
        "total": total,
        "elapsed": round(elapsed, 1),
        "cost_usd": parsed["cost_usd"],
        "input_tokens": parsed["input_tokens"],
        "output_tokens": parsed["output_tokens"],
        "files_written": parsed["files_written"],
        "commands_run": parsed["commands_run"],
        "tool_call_count": len(parsed["tool_calls"]),
        "trace_file": str(trace_file),
        "result_file": str(result_file),
        "returncode": proc.returncode,
        "error": raw_err[:300] if not ok else "",
        "at": _now(),
    }
    result_file.write_text(json.dumps(result, indent=2), encoding="utf-8")
    result["billed"] = True
    _log({"event": "CC_AGENT_BILLED", **{k: v for k, v in result.items() if k != "trace_file"}})

    print(f"[{_now()}] CC-AGENT {'DONE' if ok else 'ERROR'} {sa_id} "
          f"model={model} cost=${parsed['cost_usd']:.5f} "
          f"tools={len(parsed['tool_calls'])} files={len(parsed['files_written'])} "
          f"elapsed={elapsed:.1f}s")

    if ok and report:
        from active_now_v1 import load_active_now  # noqa: WPS433

        overnight = "absent" in (load_active_now().get("founder_mode") or "")
        if overnight:
            result["queue_advance"] = {
                "deferred": True,
                "reason": "dispatcher_complete_overnight_turn",
            }
        else:
            result["state_transition"] = _complete_via_orchestrator(sa_id=sa_id, role=role)

    # Always update registry after every turn — this moves the counter
    try:
        import importlib.util as _ilu2
        _rspec = _ilu2.spec_from_file_location("reg_upd", SCRIPTS / "registry_updater_v1.py")
        _rmod = _ilu2.module_from_spec(_rspec)
        _rspec.loader.exec_module(_rmod)
        rr = _rmod.run(dry_run=False)
        print(f"[{_now()}] REGISTRY {rr.get('registry_done','?')}/{rr.get('registry_total','?')} (+{rr.get('updated',0)})")
    except Exception as _re:
        pass  # non-fatal

    return result


def main() -> int:
    p = argparse.ArgumentParser(description="SourceA Claude Code CLI Worker")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--trace",   action="store_true", help="Print live tool calls")
    p.add_argument("--json",    action="store_true")
    args = p.parse_args()

    result = run_turn(dry_run=args.dry_run, trace=args.trace)
    if args.json:
        print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
