#!/usr/bin/env python3
"""Governance Center — one tap: heal · stairlift · cascade · judge · thread · planner · drift."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT_PATH = SINA / "governance-center-receipt-v1.json"
DEFAULT_CHATS = "58148ac9,6245d9dd,e54ddfa8,74f5ccab"
JUDGE_RECEIPT = SINA / "judge-center" / "latest-run-receipt-v1.json"
THREAD_SPINE = SINA / "thread-room" / "latest-curation-v1.json"
WEEKLY_SEC = 7 * 86400


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _age_sec(path: Path) -> float | None:
    if not path.is_file():
        return None
    try:
        return datetime.now(timezone.utc).timestamp() - path.stat().st_mtime
    except OSError:
        return None


def _run(cmd: list[str], *, timeout: int = 180) -> dict:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(SCRIPTS),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        lines = out.strip().splitlines()
        tail = lines[-1][:240] if lines else f"exit {proc.returncode}"
        return {"ok": proc.returncode == 0, "exit": proc.returncode, "tail": tail}
    except subprocess.TimeoutExpired:
        return {"ok": False, "exit": -1, "tail": "timeout"}
    except OSError as exc:
        return {"ok": False, "exit": -1, "tail": str(exc)}


def _worker_inbox_sync_ok(*, py: str) -> dict:
    """Accept aligned outbound queue when phase-strict inject is disabled."""
    truth_path = SINA / "run-inbox-disk-truth-v1.json"
    inbox_path = SINA / "worker-prompt-inbox-v1.json"
    try:
        truth = json.loads(truth_path.read_text(encoding="utf-8")) if truth_path.is_file() else {}
        inbox = json.loads(inbox_path.read_text(encoding="utf-8")) if inbox_path.is_file() else {}
        q = truth.get("queue") or {}
        ib = truth.get("inbox") or {}
        if ib.get("truth_match") and (
            (q.get("sa_id") and not q.get("queue_exhausted"))
            or q.get("queue_exhausted")
        ):
            pending_bit = "pending" if (inbox.get("pending") or ib.get("pending")) else "idle"
            if q.get("queue_exhausted"):
                has_fd = "FOUNDER DIRECTIVE" in (inbox.get("prompt") or "")
                # #region agent log
                try:
                    import time

                    with open(
                        ROOT / ".cursor" / "debug-baabac.log",
                        "a",
                        encoding="utf-8",
                    ) as _df:
                        _df.write(
                            json.dumps(
                                {
                                    "sessionId": "baabac",
                                    "runId": "post-fix",
                                    "hypothesisId": "H2",
                                    "location": "governance_center_run_v1.py:_worker_inbox_sync_ok",
                                    "message": "queue_exhausted truth_match",
                                    "data": {"has_founder_directive": has_fd, "pending": pending_bit},
                                    "timestamp": int(time.time() * 1000),
                                }
                            )
                            + "\n"
                        )
                except OSError:
                    pass
                # #endregion
                if not has_fd:
                    pass
                else:
                    return {
                        "ok": True,
                        "exit": 0,
                        "tail": f"queue_exhausted_{pending_bit}",
                    }
            else:
                return {
                    "ok": True,
                    "exit": 0,
                    "tail": f"outbound_queue_{pending_bit} {q.get('sa_id')}",
                }
    except (OSError, json.JSONDecodeError):
        pass

    inbox_sync = _run([py, str(SINA / "activate-run-inbox-phase-strict-v1.py"), "--json"], timeout=120)
    if inbox_sync.get("ok"):
        return inbox_sync
    truth_path = SINA / "run-inbox-disk-truth-v1.json"
    inbox_path = SINA / "worker-prompt-inbox-v1.json"
    try:
        proc = subprocess.run(
            [py, str(SINA / "activate-run-inbox-phase-strict-v1.py"), "--json"],
            cwd=str(SCRIPTS),
            capture_output=True,
            text=True,
            timeout=120,
        )
        payload = json.loads(proc.stdout or "{}")
        deliver = payload.get("deliver") or {}
        dup = deliver.get("duplicate_guard") or {}
        if (
            payload.get("build", {}).get("ok")
            and dup.get("reason") == "COOLDOWN_SAME_TURN"
            and (payload.get("routing") or {}).get("enabled")
        ):
            return {"ok": True, "exit": 0, "tail": "cooldown_same_turn_skip_inject"}
        if payload.get("error") == "PHASE_STRICT_DISABLED":
            truth = json.loads(truth_path.read_text(encoding="utf-8")) if truth_path.is_file() else {}
            inbox = json.loads(inbox_path.read_text(encoding="utf-8")) if inbox_path.is_file() else {}
            q = truth.get("queue") or {}
            ib = truth.get("inbox") or {}
            if (
                q.get("sa_id")
                and not q.get("queue_exhausted")
                and ib.get("truth_match")
            ):
                pending_bit = "pending" if (inbox.get("pending") or ib.get("pending")) else "idle"
                return {
                    "ok": True,
                    "exit": 0,
                    "tail": f"outbound_queue_{pending_bit} {q.get('sa_id')}",
                }
    except (OSError, json.JSONDecodeError, subprocess.TimeoutExpired):
        pass
    return inbox_sync


def run_center(
    *,
    tier: str = "fast",
    chats: str = DEFAULT_CHATS,
    founder_text: str = "",
    skip_judge: bool = False,
    skip_thread: bool = False,
) -> dict:
    py = sys.executable
    steps: list[dict] = []

    def step(name: str, result: dict) -> None:
        steps.append({"step": name, **result})

    # 0 Governance meta-audit (auditor for Gov Specialist — veto if FAIL)
    meta = _run([py, "governance_meta_audit_v1.py", "--tier", tier, "--chats", chats, "--json"], timeout=240)
    step("governance_meta_audit", meta)

    # 1 Self-heal
    heal = _run([py, "governance_self_heal_daemon_v1.py", "--heal", "--json"])
    step("self_heal", heal)

    # 1b Agentic layer pipeline v2 (L1→Brain + L2 + health)
    pipe = _run([py, "agentic_layer_pipeline_v2.py", "--json", "--tier", "fast"], timeout=90)
    step("agentic_layer_pipeline_v2", pipe)

    # 2 Drift report
    drift = _run(
        [py, "-c", "from governance_drift_engine import run_drift_report; import json; print(json.dumps(run_drift_report()))"],
        timeout=120,
    )
    step("drift_engine", drift)

    # 2b Worker inbox ↔ queue head (clears stale pending after queue rebuild)
    step("worker_inbox_sync", _worker_inbox_sync_ok(py=py))
    drift_report = _run([py, "report_worker_inbox_queue_drift_v1.py"], timeout=30)
    step("worker_inbox_drift", drift_report)

    # 3 Founder cascade (one intake → all layers)
    cascade_cmd = [
        py,
        "founder_input_cascade_v1.py",
        "--text",
        founder_text or "governance center auto cycle",
        "--source",
        "governance_center",
        "--json",
    ]
    cascade = _run(cascade_cmd, timeout=60)
    step("founder_cascade", cascade)

    # 4 Stairlift
    sl_tier = "hot" if tier == "fast" else "full"
    stairlift = _run([py, "governance_stairlift_sync_v1.py", "--force", "--tier", sl_tier, "--json"])
    step("stairlift", stairlift)

    # 5 Planner (machine next-10 — not OpenRouter)
    planner = _run([py, "live_ongoing_prompts_v1.py", "--rebuild"], timeout=30)
    step("planner_next10", planner)

    # 6 Judge Center (Audit → Lawyer/Counsel → Bench) — weekly or full tier
    judge_age = _age_sec(JUDGE_RECEIPT)
    run_judge = tier == "full" or (judge_age is None or judge_age >= WEEKLY_SEC)
    if not skip_judge and run_judge:
        judge = _run([py, "judge_center_run_v1.py", "--chats", chats, "--json"], timeout=120)
        step("judge_center", judge)
    else:
        step("judge_center", {"ok": True, "exit": 0, "tail": "skipped fresh"})

    # 7 Thread Room (scout → cartographer → curator)
    thread_age = _age_sec(THREAD_SPINE)
    run_thread = tier == "full" or (thread_age is None or thread_age >= WEEKLY_SEC)
    if not skip_thread and run_thread:
        thread = _run([py, "thread_room_run_v1.py", "--chats", chats, "--json"], timeout=120)
        step("thread_room", thread)
    else:
        step("thread_room", {"ok": True, "exit": 0, "tail": "skipped fresh"})

    # 8 Fast validators
    for name, script in (
        ("validate_cascade", "validate-founder-input-cascade-v1.sh"),
        ("validate_ownership", "validate-incident-fix-ownership-v1.sh"),
    ):
        v = _run(["bash", script, "--fast"] if "ownership" in script else ["bash", script], timeout=90)
        step(name, v)

    ok = all(s.get("ok") for s in steps)
    receipt = {
        "schema": "governance-center-receipt-v1",
        "built_at": _now(),
        "tier": tier,
        "ok": ok,
        "steps": steps,
        "next_planner_ssot": str(SINA / "live-ongoing-prompts-next-10-v1.json"),
        "judge_spine": str(SINA / "judge-center" / "latest-resolution-v1.json"),
        "thread_spine": str(THREAD_SPINE),
        "brain_wire_ssot": str(SINA / "governance-brain-wire-v1.json"),
        "stairlift_ssot": str(SINA / "governance-stairlift-v1.json"),
        "meta_audit_ssot": str(SINA / "governance-meta-audit-receipt-v1.json"),
        "law": "SOURCEA_GOVERNANCE_CENTER_SELF_GOVERN_LOCKED_v1.md",
        "gov_meta_audit_law": "SOURCEA_GOV_META_AUDIT_LOCKED_v1.md",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="Governance Center orchestrator")
    ap.add_argument("--tier", choices=("fast", "full"), default="fast")
    ap.add_argument("--chats", default=DEFAULT_CHATS)
    ap.add_argument("--text", default="", help="Founder input for cascade")
    ap.add_argument("--skip-judge", action="store_true")
    ap.add_argument("--skip-thread", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    receipt = run_center(
        tier=args.tier,
        chats=args.chats,
        founder_text=args.text,
        skip_judge=args.skip_judge,
        skip_thread=args.skip_thread,
    )
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        fails = [s["step"] for s in receipt["steps"] if not s.get("ok")]
        print(f"GOVERNANCE-CENTER: ok={receipt['ok']} tier={receipt['tier']} fails={fails or 'none'}")
    return 0 if receipt.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
