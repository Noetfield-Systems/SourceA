#!/usr/bin/env python3
"""Watcher mode: how Brain enforcement decides — per-step timing caps enforced."""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
WATCH_PATH = SINA / "brain-loop-watch-v1.json"

sys.path.insert(0, str(SCRIPTS))
from brain_timing_enforce_v1 import TimingBudget  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _step(
    steps: list,
    n: int,
    gate: str,
    check: str,
    result: dict,
    *,
    decision: str,
    reason: str,
    timing: dict,
    would_do: str | None = None,
):
    steps.append(
        {
            "n": n,
            "gate": gate,
            "check": check,
            "result": result,
            "decision": decision,
            "reason": reason,
            "would_do": would_do,
            "limit_sec": timing.get("limit_sec"),
            "elapsed_sec": timing.get("elapsed_sec"),
            "timing": timing.get("timing"),
            "timed_out": timing.get("timed_out", False),
        }
    )


def _run_json(budget: TimingBudget, gate: str, script: str, *args: str) -> dict:
    row = budget.run_subprocess(
        gate,
        [sys.executable, str(SCRIPTS / script), *args],
        cwd=str(ROOT),
    )
    body = (row.get("stdout") or "").strip()
    out: dict = {
        "ok": row.get("ok"),
        "exit_code": row.get("exit_code"),
        "timed_out": row.get("timed_out", False),
        "timing": row.get("timing"),
    }
    if body:
        try:
            out["json"] = json.loads(body)
        except json.JSONDecodeError:
            out["stdout"] = body[:1500]
    if row.get("stderr"):
        out["stderr"] = (row.get("stderr") or "")[:400]
    return out


def _skip_step(steps, n: int, gate: str, check: str, budget: TimingBudget) -> bool:
    if budget.remaining_total() <= 0:
        tb = budget.timing_block(gate, 0.0, timed_out=True)
        _step(
            steps,
            n,
            gate,
            check,
            {"skipped": True},
            decision="SKIP",
            reason="TOTAL_BUDGET_EXCEEDED — step not run",
            timing=tb,
        )
        return True
    return False


def watch_loop(*, founder_phrase: str = "run the loop") -> dict:
    steps: list[dict] = []
    budget = TimingBudget()
    o: dict = {}

    # 1 SYNC
    if not _skip_step(steps, 1, "SYNC", "hub_self_refresh_v1.py", budget):
        sync = _run_json(budget, "SYNC", "hub_self_refresh_v1.py", "--json")
        sj = sync.get("json") or {}
        tb = (sync.get("timing") or {})
        if sync.get("timed_out"):
            dec, reason = "TIMEOUT", "SYNC exceeded 12s — hub sync killed"
        else:
            dec = "PASS" if sync.get("ok") else "FAIL"
            reason = "Hub /api/hub-sync OK" if sync.get("ok") else "Hub sync failed"
        _step(
            steps, 1, "SYNC", "hub self-refresh", {"ok": sync.get("ok"), "path": sj.get("path"), "built_at": sj.get("built_at")},
            decision=dec, reason=reason, timing=tb, would_do="continue" if dec == "PASS" else "fix hub",
        )

    # 2 FEASIBILITY
    if not _skip_step(steps, 2, "FEASIBILITY", "prompt_feasibility_gate", budget):

        def _feas():
            from prompt_feasibility_gate import check_session  # noqa: WPS433

            return check_session(role="worker")

        feas, tb = budget.run("FEASIBILITY", _feas)
        if tb.get("skip") or tb.get("timed_out"):
            _step(steps, 2, "FEASIBILITY", "feasibility gate", {"timed_out": True}, decision="TIMEOUT", reason="FEASIBILITY exceeded 5s", timing=tb)
            return _out(steps, founder_phrase, budget, blocked_at=2)
        action = (feas or {}).get("action")
        if action == "STOP_INJECT":
            dec, reason = "STOP", "STOP_INJECT on queue item"
        elif action == "WARN_PICK_MISMATCH":
            dec, reason = "WARN", "Live pick ≠ queue sa — queue item still feasible"
        else:
            dec, reason = "PASS", "Feasibility OK for inject path"
        _step(
            steps, 2, "FEASIBILITY", "feasibility gate", {"action": action}, decision=dec, reason=reason, timing=tb,
        )
        if action == "STOP_INJECT":
            return _out(steps, founder_phrase, budget, blocked_at=2)

    # 3 ORCHESTRATOR
    if not _skip_step(steps, 3, "ORCHESTRATOR", "orchestrator status", budget):

        def _orch():
            spec = importlib.util.spec_from_file_location("orch", SCRIPTS / "healthy-drain-orchestrator-v1.py")
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)  # type: ignore[union-attr]
            return mod.status()

        orch, tb = budget.run("ORCHESTRATOR", _orch)
        o = (orch or {}).get("orchestrator") or {}  # noqa: PLW2901
        _step(
            steps, 3, "ORCHESTRATOR", "orchestrator status",
            {"expected_sa": o.get("expected_sa"), "expected_role": o.get("expected_role"), "queue_pos": (orch or {}).get("queue_pos"), "brief": (orch or {}).get("brief")},
            decision="PASS" if not tb.get("timed_out") else "TIMEOUT",
            reason=f"Next: {o.get('expected_sa')} role={o.get('expected_role')}",
            timing=tb,
        )

    # 4 INJECT
    if not _skip_step(steps, 4, "INJECT", "inbox status", budget):

        def _inbox():
            from worker_inject_lib import inbox_status  # noqa: WPS433

            return inbox_status()

        inbox, tb = budget.run("INJECT", _inbox)
        meta = (inbox or {}).get("meta") or {}
        inbox_sa = meta.get("sa_id")
        expected_sa = o.get("expected_sa")
        if inbox and inbox.get("pending") and inbox_sa == expected_sa:
            dec, reason = "PASS", f"INBOX pending {inbox_sa}"
        elif inbox and inbox.get("pending"):
            dec, reason = "WARN", f"INBOX {inbox_sa} ≠ expected {expected_sa}"
        else:
            dec, reason = "WAIT", "INBOX empty"
        _step(
            steps, 4, "INJECT", "inbox status",
            {"pending": (inbox or {}).get("pending"), "sa_id": inbox_sa, "queue_role": meta.get("queue_role")},
            decision=dec, reason=reason, timing=tb,
        )

    # 5 VALIDATE
    if not _skip_step(steps, 5, "VALIDATE", "broker brain-poll", budget):
        broker = _run_json(budget, "VALIDATE", "goal1_lane_broker.py", "brain-poll", "--json")
        bj = broker.get("json") or {}
        wr = bj.get("worker_report") or {}
        has_report = bool(wr.get("sa_focus"))
        tb = broker.get("timing") or {}
        _step(
            steps, 5, "VALIDATE", "broker poll",
            {"present": has_report, "sa_focus": wr.get("sa_focus"), "broker_state": (bj.get("broker") or {}).get("state")},
            decision="PASS" if has_report and not broker.get("timed_out") else ("TIMEOUT" if broker.get("timed_out") else "WAIT"),
            reason=f"Report sa_focus={wr.get('sa_focus')}" if has_report else "No report yet",
            timing=tb,
        )

    # 6 ONE_SA
    if not _skip_step(steps, 6, "ONE_SA", "one_sa gate", budget):

        def _one_sa():
            from one_sa_per_turn_gate_v1 import gate_status  # noqa: WPS433

            return gate_status()

        one_sa, tb = budget.run("ONE_SA", _one_sa)
        blk = (one_sa or {}).get("block")
        if blk:
            dec = "BLOCK"
            reason = blk.get("error") if isinstance(blk, dict) else str(blk)
        elif (one_sa or {}).get("turn_open"):
            dec, reason = "PASS", f"Turn open {(one_sa or {}).get('open_sa')}"
        else:
            dec, reason = "PASS", "No blocking turn"
        _step(steps, 6, "ONE_SA", "one_sa gate", {"turn_open": (one_sa or {}).get("turn_open"), "open_sa": (one_sa or {}).get("open_sa")}, decision=dec, reason=reason, timing=tb)

    # 7 ACTIVATE
    if not _skip_step(steps, 7, "ACTIVATE", "pgrep + prepare-only", budget):
        t0_cap = budget.remaining_total()
        t0 = __import__("time").monotonic()

        def _activate():
            proc = subprocess.run(
                ["pgrep", "-fl", "goal1_run_loop|goal1_worker_batch|agent -p"],
                capture_output=True,
                text=True,
                timeout=min(5, int(t0_cap)),
            )
            running = bool((proc.stdout or "").strip())
            prep = _run_json(budget, "ACTIVATE", "goal1_auto_loop_v1.py", "--prepare-only", "--turns=10")
            return running, prep

        try:
            running, prep = _activate()
        except subprocess.TimeoutExpired:
            elapsed = __import__("time").monotonic() - t0
            tb = budget.timing_block("ACTIVATE", elapsed, timed_out=True)
            _step(steps, 7, "ACTIVATE", "activate check", {"timed_out": True}, decision="TIMEOUT", reason="ACTIVATE check exceeded 15s", timing=tb)
            running, prep = True, {"json": {}, "timed_out": True}
        else:
            elapsed = __import__("time").monotonic() - t0
            tb = budget.timing_block("ACTIVATE", elapsed)

        pj = prep.get("json") or {}
        if prep.get("timed_out") or tb.get("timed_out"):
            dec, reason = "TIMEOUT", "prepare-only exceeded cap"
        elif running:
            dec, reason = "RUNNING", "Executor already running — no double-spawn"
        elif not pj.get("ok") and pj.get("step") == "busy":
            dec, reason = "BUSY", f"AUTO_LOOP_BUSY pid={pj.get('busy_pid')}"
        elif not pj.get("ok"):
            dec, reason = "BLOCK", f"prepare failed: {pj.get('error')}"
        else:
            dec, reason = "READY", "Would spawn if founder said activate"
        _step(
            steps, 7, "ACTIVATE", "activate check",
            {"executor_running": running, "prepare_ok": pj.get("ok"), "busy_pid": pj.get("busy_pid")},
            decision=dec, reason=reason, timing=tb,
        )

    # 8 PROOF
    if not _skip_step(steps, 8, "PROOF", "batch log tail", budget):

        def _proof():
            log_path = SINA / "goal1-worker-batch-latest.log"
            if not log_path.is_file():
                return None, []
            lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
            tail = [ln for ln in lines[-8:] if "AGENT" in ln or "mismatch" in ln][-3:]
            last_done = next((ln for ln in reversed(tail) if "AGENT DONE" in ln), None)
            return last_done, tail

        proof, tb = budget.run("PROOF", _proof)
        last_done, tail = proof if proof else (None, [])
        _step(
            steps, 8, "PROOF", "batch log",
            {"last_agent_done": last_done, "last_lines": tail},
            decision="PASS" if last_done and "broker=yes" in (last_done or "") else ("FAIL" if last_done else "NONE"),
            reason=last_done or "No AGENT DONE in tail",
            timing=tb,
        )

    # 9 CHAIN
    vj: dict = {}
    if not _skip_step(steps, 9, "CHAIN", "brain_validate", budget):
        val = _run_json(budget, "CHAIN", "brain_validate_goal1_v1.py", "--json")
        vj = val.get("json") or {}
        chain = vj.get("chain") or {}
        tb = val.get("timing") or {}
        _step(
            steps, 9, "CHAIN", "brain_validate summary",
            {"chain": chain, "brain_action": vj.get("brain_action")},
            decision="SUMMARY",
            reason=f"inject={chain.get('inject')} validate={chain.get('validate')} activate={chain.get('activate')} sync={chain.get('sync')}",
            timing=tb,
        )
    else:
        chain = {}

    return _out(steps, founder_phrase, budget, blocked_at=None, chain=vj.get("chain") or {}, bugs=_find_bugs(steps, vj))


def _find_bugs(steps: list, validation: dict) -> list[dict]:
    bugs: list[dict] = []
    for s in steps:
        if s.get("timing") == "VIOLATION" or s.get("timed_out"):
            bugs.append({"id": "timing_violation", "where": s.get("gate"), "symptom": f"{s.get('elapsed_sec')}s > {s.get('limit_sec')}s", "likely": "step exceeded mandatory cap"})
        if s.get("gate") == "PROOF" and s.get("decision") == "FAIL":
            bugs.append({"id": "broker_reject", "where": "batch log", "symptom": s.get("reason"), "likely": "sa_mismatch or broker=no"})
        if s.get("gate") == "ONE_SA" and s.get("decision") == "BLOCK":
            bugs.append({"id": "one_sa_turn_open", "where": "one_sa gate", "symptom": s.get("reason"), "likely": "stale turn state"})
    return bugs


def _out(steps, founder_phrase, budget: TimingBudget, *, blocked_at, chain=None, bugs=None) -> dict:
    timing = budget.summary()
    return {
        "status": "BRAIN_LOOP_WATCH",
        "mode": "watcher",
        "at": _now(),
        "founder_said": founder_phrase,
        "timing_enforcement": timing,
        "blocked_at_step": blocked_at,
        "steps": steps,
        "chain": chain or {},
        "bugs_suspected": bugs or [],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--phrase", default="run the loop")
    p.add_argument("--yaml", action="store_true")
    p.add_argument("--write", action="store_true")
    args = p.parse_args()
    watch = watch_loop(founder_phrase=args.phrase)
    if args.write:
        SINA.mkdir(parents=True, exist_ok=True)
        WATCH_PATH.write_text(json.dumps(watch, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(watch, indent=2) if not args.yaml else json.dumps(watch))
    te = watch.get("timing_enforcement") or {}
    return 1 if te.get("timing") == "VIOLATION" else 0


if __name__ == "__main__":
    raise SystemExit(main())
