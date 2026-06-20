#!/usr/bin/env python3
"""OEGCC Controller — bounded repair loop (plain code, not a model).

Generator produces · Checker lints · Controller owns attempts, oscillation, escalate.
Law: docs/SOURCEA_OUTBOUND_EMAIL_GENERATOR_CHECKER_CONTROLLER_LOOP_LOCKED_v1.md
Receipt: ~/.sina/outbound-email-controller-receipt-v1.json
Log: ~/.sina/outbound-email-attempts-v1.jsonl
"""
from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "outbound-email-oegcc-v1.json"
ATTEMPTS_LOG = SINA / "outbound-email-attempts-v1.jsonl"
RECEIPT = SINA / "outbound-email-controller-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _failure_ids(lint_row: dict) -> set[str]:
    return {str(f.get("id") or "") for f in lint_row.get("failures") or [] if f.get("id")}


def detect_oscillation(failure_history: list[set[str]]) -> bool:
    """True when latest attempt reintroduces a failure fixed on the prior step."""
    if len(failure_history) < 3:
        return False
    before = failure_history[-3]
    middle = failure_history[-2]
    current = failure_history[-1]
    fixed_last_round = before - middle
    return bool(fixed_last_round & current)


def append_attempt_log(row: dict, *, path: Path = ATTEMPTS_LOG) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def run_controller_loop(
    generate_draft: Callable[[int, dict | None], str],
    *,
    lane: str = "",
    region: str = "canada",
    max_attempts: int | None = None,
    write_log: bool = True,
    case_id: str = "",
) -> dict:
    """Run bounded OEGCC loop. generate_draft(attempt, lint_row|None) -> subject+body text."""
    import sys

    sys.path.insert(0, str(SCRIPTS))
    from outbound_email_linter_v1 import lint_email  # noqa: WPS433

    cfg = _read_json(SSOT)
    cap = int(max_attempts or cfg.get("max_attempts") or 3)
    attempts: list[dict] = []
    failure_history: list[set[str]] = []
    temperature = 0.0
    outcome = "escalate_human"
    final_lint: dict = {}
    oscillation = False

    for attempt in range(1, cap + 1):
        prior_lint = attempts[-1]["lint"] if attempts else None
        draft = generate_draft(attempt, prior_lint)
        lint_row = lint_email(draft, lane=lane, region=region)
        fids = _failure_ids(lint_row)
        failure_history.append(fids)
        oscillation = detect_oscillation(failure_history)
        attempt_row = {
            "schema": "outbound-email-attempt-v1",
            "at": _now(),
            "case_id": case_id,
            "attempt": attempt,
            "temperature": temperature,
            "draft": draft,
            "lint": lint_row,
            "failure_ids": sorted(fids),
        }
        attempts.append(attempt_row)
        if write_log:
            append_attempt_log(attempt_row)
        final_lint = lint_row

        if lint_row.get("ok"):
            outcome = "linter_pass_human_queue"
            break
        if oscillation:
            outcome = "oscillation_stop_human_queue"
            break
        if attempt >= cap:
            outcome = "max_attempts_human_queue"
            break
        temperature += float(cfg.get("temperature_nudge_on_oscillation") or 0.15)

    ok = outcome == "linter_pass_human_queue"
    rule_hist: dict[str, int] = {}
    for a in attempts:
        for fid in a.get("failure_ids") or []:
            rule_hist[fid] = rule_hist.get(fid, 0) + 1

    receipt = {
        "schema": "outbound-email-controller-receipt-v1",
        "at": _now(),
        "ok": ok,
        "outcome": outcome,
        "attempts_used": len(attempts),
        "max_attempts": cap,
        "oscillation": oscillation,
        "never_auto_send": True,
        "exit": "human_queue",
        "final_lint": {
            "ok": final_lint.get("ok"),
            "line": final_lint.get("line"),
            "failures": final_lint.get("failures"),
            "warnings": final_lint.get("warnings"),
        },
        "rule_histogram": rule_hist,
        "law": "docs/SOURCEA_OUTBOUND_EMAIL_GENERATOR_CHECKER_CONTROLLER_LOOP_LOCKED_v1.md",
        "line": (
            f"oegcc · PASS · {len(attempts)}/{cap} · human_queue"
            if ok
            else f"oegcc · {outcome} · {len(attempts)}/{cap} · human_queue"
        ),
    }
    return {"receipt": receipt, "attempts": attempts}


def _write_receipt(receipt: dict) -> None:
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


def run_lint_only(*, body: str, lane: str = "", region: str = "canada") -> dict:
    import sys

    sys.path.insert(0, str(SCRIPTS))
    from outbound_email_linter_v1 import lint_email  # noqa: WPS433

    return lint_email(body, lane=lane, region=region)


def main() -> int:
    ap = argparse.ArgumentParser(description="OEGCC outbound email controller")
    ap.add_argument("--lint-file", type=Path, help="Lint a single draft file only")
    ap.add_argument("--simulate", action="store_true", help="Run fixture-backed simulation loop")
    ap.add_argument("--lane", default="")
    ap.add_argument("--region", default="canada")
    ap.add_argument("--max-attempts", type=int, default=0)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.lint_file:
        body = args.lint_file.read_text(encoding="utf-8") if args.lint_file.is_file() else ""
        row = run_lint_only(body=body, lane=args.lane, region=args.region)
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(row.get("line"))
        return 0 if row.get("ok") else 1

    if args.simulate:
        fix = ROOT / "scripts/fixtures/outbound-email-linter"
        fail_body = (fix / "fail_opener.txt").read_text(encoding="utf-8")
        pass_body = (fix / "pass.txt").read_text(encoding="utf-8")

        def _sim_gen(attempt: int, prior: dict | None) -> str:
            if attempt == 1:
                return fail_body
            return pass_body

        result = run_controller_loop(
            _sim_gen,
            max_attempts=args.max_attempts or None,
            case_id="simulate-opener-fix",
        )
        _write_receipt(result["receipt"])
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(result["receipt"].get("line"))
        return 0 if result["receipt"].get("ok") else 1

    print("Provide --lint-file or --simulate", file=__import__("sys").stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
