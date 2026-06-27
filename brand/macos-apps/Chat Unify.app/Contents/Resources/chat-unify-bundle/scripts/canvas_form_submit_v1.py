#!/usr/bin/env python3
"""FORM_OFFICIAL batch submit — Canvas confirms → disk → hub (founder Submit only)."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def submit(*, cascade_hub: bool = True, strict_hub: bool = True, canvas_data: Path | None = None, actor: str = "agent", channel: str = "cli") -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from form_founder_supremacy_guard_v1 import assert_founder_submit_allowed  # noqa: WPS433

    block = assert_founder_submit_allowed(actor=actor, action="canvas_form_submit", channel=channel)
    if block.get("blocked"):
        return block

    from canvas_form_apply_picks_v1 import apply, CANVAS_DATA  # noqa: WPS433

    canvas_path = canvas_data if canvas_data is not None else CANVAS_DATA
    apply_result = apply(canvas_path=canvas_path, dry_run=False, actor=actor, channel=channel)

    steps: list[dict] = [{"step": "canvas_apply", **apply_result}]

    def _run(label: str, cmd: list[str], *, timeout: int = 300) -> dict:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
        return {
            "step": label,
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout_tail": (proc.stdout or "")[-400:],
            "stderr_tail": (proc.stderr or "")[-400:],
        }

    steps.append(_run("write_receipt", [sys.executable, str(SCRIPTS / "live_founder_decision_form_v1.py"), "--write-receipt"]))
    steps.append(_run("sync_picks_locked", [sys.executable, str(SCRIPTS / "sync_picks_locked_v1.py")]))
    steps.append(_run("generate_canvas", [sys.executable, str(SCRIPTS / "generate_integrity_canvas_form_data_v1.py")]))
    steps.append(_run("form_reconcile", [sys.executable, str(SCRIPTS / "form_open_questions_reconcile_v1.py"), "--json"]))
    steps.append(_run("form_official_wire", [sys.executable, str(SCRIPTS / "form_official_wire_e2e_v1.py"), "--no-regen", "--json"]))
    steps.append(_run("judge_alarm_strip", [sys.executable, str(SCRIPTS / "hub_judge_alarm_strip_v1.py"), "--refresh-judge"]))

    if cascade_hub:
        steps.append(
            _run(
                "build_hub",
                [sys.executable, str(SCRIPTS / "build-sina-command-panel.py")],
                timeout=300,
            )
        )
        steps.append(_run("hub_self_refresh", [sys.executable, str(SCRIPTS / "hub_self_refresh_v1.py")]))
        steps.append(
            _run(
                "governance_cascade",
                [sys.executable, str(SCRIPTS / "governance_propagation_cascade_v1.py"), "--reason", "form-canvas-submit"],
            )
        )

    from live_founder_decision_form_v1 import payload  # noqa: WPS433

    form = payload()
    core_labels = {"canvas_apply", "write_receipt", "sync_picks_locked", "generate_canvas", "form_reconcile", "form_official_wire", "judge_alarm_strip"}
    hub_labels = {"build_hub", "hub_self_refresh", "governance_cascade"}
    core_ok = bool(apply_result.get("ok")) and all(
        s.get("ok") for s in steps if s.get("step") in core_labels
    )
    hub_ok = all(s.get("ok") for s in steps if s.get("step") in hub_labels) if cascade_hub else True
    return {
        "ok": core_ok,
        "hub_synced": hub_ok,
        "applied_now": apply_result.get("applied_now", 0),
        "open_questions_count": form.get("open_questions_count"),
        "open_question_ids": [q.get("id") for q in (form.get("open_questions") or [])],
        "steps": steps,
        "shipped": apply_result.get("shipped") or [],
        "canvas_data": str(canvas_path),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Batch submit M1 Canvas confirms → disk + hub")
    ap.add_argument("--canvas-data", default="", help="Canvas .data.json path (default: M1 FORM_OFFICIAL)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-hub", action="store_true", help="Disk + canvas only — skip hub rebuild")
    args = ap.parse_args()
    canvas_path = Path(args.canvas_data).expanduser() if args.canvas_data else None
    result = submit(cascade_hub=not args.no_hub, canvas_data=canvas_path)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            f"{'OK' if result.get('ok') else 'FAIL'}: applied_now={result.get('applied_now')} "
            f"open={result.get('open_questions_count')}"
        )
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
