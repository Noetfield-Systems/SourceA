#!/usr/bin/env python3
"""Capture Eval-1b report to ~/.sina during strict build (live or structural)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPORT_PATH = Path.home() / ".sina" / "eval_packet_v1b_report.json"
CI_MODE_PATH = Path.home() / ".sina" / "eval_1b_ci_mode_v1.json"
CAPTURE_META_PATH = Path.home() / ".sina" / "eval_packet_v1b_capture_v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def capture_eval_report(*, strict: bool = True, refresh: bool = False) -> dict[str, Any]:
    from eval_1b_ci_mode import resolve_mode  # noqa: WPS433
    from eval_packet_v1b.runner import run_eval  # noqa: WPS433

    mode_row = resolve_mode()
    use_live = bool(mode_row.get("live_probe_ok"))
    if refresh or not REPORT_PATH.is_file():
        rep = run_eval(write_report=True, live=use_live)
    else:
        rep = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        if rep.get("schema") != "eval-packet-v1b":
            rep = run_eval(write_report=True, live=use_live)
    meta = {
        "schema": "eval-packet-v1b-capture-v1",
        "captured_at": _now(),
        "strict_build": strict,
        "attempted_live": use_live,
        "ci_mode": mode_row.get("mode"),
        "ci_reason": mode_row.get("reason"),
        "report_path": str(REPORT_PATH),
        "report_mode": rep.get("mode"),
        "report_ok": rep.get("ok"),
        "live_ok": rep.get("live_ok"),
        "live_pilot_win_pct": rep.get("live_pilot_win_pct"),
    }
    if REPORT_PATH.is_file():
        try:
            on_disk = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
            on_disk["strict_build_capture"] = True
            on_disk["ci_mode"] = mode_row.get("mode")
            on_disk["ci_mode_path"] = str(CI_MODE_PATH)
            on_disk["captured_at"] = meta["captured_at"]
            REPORT_PATH.write_text(json.dumps(on_disk, indent=2) + "\n", encoding="utf-8")
            meta["report_path"] = str(REPORT_PATH)
        except (json.JSONDecodeError, OSError):
            pass
    CI_MODE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CAPTURE_META_PATH.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return meta


SYNTHESIS_PATH = Path(__file__).resolve().parents[1] / "brain-os" / "wtm" / "SINA_GPT_CLAUDE_WTM_SYNTHESIS_LOCKED_v1.md"


def sync_synthesis_eval_line_from_disk(*, strict: bool = True) -> dict[str, Any]:
    """Rewrite synthesis Eval-1b lines from ~/.sina/eval_packet_v1b_report.json (disk wins)."""
    import re

    if not REPORT_PATH.is_file():
        return {"ok": False, "error": "missing eval_packet_v1b_report.json"}
    if not SYNTHESIS_PATH.is_file():
        return {"ok": False, "error": "missing synthesis LOCKED doc"}
    rep = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    wins = int(rep.get("live_pilot_wins") or rep.get("packet_wins") or 0)
    count = int(rep.get("live_pilot_count") or rep.get("task_count") or 0)
    pct = int(rep.get("live_pilot_win_pct") or rep.get("packet_win_pct") or 0)
    ratio = f"{wins}/{count}"
    text = SYNTHESIS_PATH.read_text(encoding="utf-8")
    claim_line = (
        f"| No evaluation/ layer | ✅ Eval-1b live {count}/{count} pilots · "
        f"{ratio} wins ({pct}% live) — machine `{REPORT_PATH}` |"
    )
    pendings_line = (
        f"| Eval-1b | 5+ live pilots + CI | **done** ({count}/{count} pilots · "
        f"{ratio} wins · {pct}% live) |"
    )
    new_text, n1 = re.subn(
        r"^\| No evaluation/ layer \|[^\n]+$",
        claim_line,
        text,
        count=1,
        flags=re.MULTILINE,
    )
    new_text, n2 = re.subn(
        r"^\| Eval-1b \|[^\n]+$",
        pendings_line,
        new_text,
        count=1,
        flags=re.MULTILINE,
    )
    if n1 != 1 or n2 != 1:
        return {
            "ok": False,
            "error": "synthesis line replace failed",
            "claim_replaced": n1,
            "pendings_replaced": n2,
        }
    SYNTHESIS_PATH.write_text(new_text, encoding="utf-8")
    return {
        "ok": True,
        "path": str(SYNTHESIS_PATH),
        "ratio": ratio,
        "pct": pct,
        "report_mode": rep.get("mode"),
    }


def eval_synthesis_critic_drift_errors(
    synthesis_text: str,
    rep: dict[str, Any] | None,
    *,
    label: str = "SINA_GPT_CLAUDE_WTM_SYNTHESIS",
) -> list[str]:
    """sa-0019 — critic/GPT Eval claims must match ~/.sina/eval_packet_v1b_report.json."""
    if not rep or rep.get("schema") != "eval-packet-v1b":
        return []
    errors: list[str] = []
    wins = int(rep.get("live_pilot_wins") or rep.get("packet_wins") or 0)
    count = int(rep.get("live_pilot_count") or rep.get("task_count") or 0)
    pct = int(rep.get("live_pilot_win_pct") or rep.get("packet_win_pct") or 0)
    if str(rep.get("mode") or "") != "live" or not rep.get("live_ok", rep.get("ok")):
        return errors
    if pct < 100 and "100% live" in synthesis_text:
        errors.append(
            f"{label}: stale '100% live' — disk report {wins}/{count} ({pct}%)"
        )
    ratio = f"{wins}/{count}"
    if count and ratio not in synthesis_text and f"{pct}%" not in synthesis_text:
        errors.append(
            f"{label}: missing machine Eval line ({ratio} or {pct}%) vs disk report"
        )
    return errors


def eval_scaffold_live_regression_errors(
    rep: dict[str, Any] | None,
    *,
    label: str = "eval-1b report",
) -> list[str]:
    """Fail when mode=scaffold contradicts live_ok=true (stale mixed report)."""
    if not rep:
        return []
    if rep.get("mode") == "scaffold" and rep.get("live_ok") is True:
        return [
            f"{label} regression: mode=scaffold while live_ok=true — "
            "re-run capture_eval_report or validate-eval-packet-v1b-live.sh"
        ]
    return []


def cross_check_scaffold_survives_after_live() -> list[str]:
    """Machine proof scaffold arm passes (sa-0140) — read-only; does not overwrite live report."""
    from eval_packet_v1b.runner import run_eval  # noqa: WPS433

    errors: list[str] = []
    rep = run_eval(write_report=False, live=False)
    if rep.get("mode") != "scaffold":
        errors.append(f"expected mode=scaffold after live pass, got {rep.get('mode')!r}")
    if not rep.get("scaffold_ok"):
        errors.append(
            f"scaffold arm failed after live pass: {rep.get('scaffold_win_pct')}%"
        )
    if int(rep.get("scaffold_win_pct") or 0) < 70:
        errors.append(f"scaffold_win_pct below 70: {rep.get('scaffold_win_pct')}")
    errors.extend(eval_scaffold_live_regression_errors(rep))
    rows = rep.get("rows") or []
    if len(rows) < 3:
        errors.append(f"expected >=3 task rows, got {len(rows)}")
    return errors


def assert_capture_artifacts() -> list[str]:
    errors: list[str] = []
    if not REPORT_PATH.is_file():
        errors.append(f"missing {REPORT_PATH}")
        return errors
    try:
        rep = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        errors.append(f"invalid report: {exc}")
        return errors
    if rep.get("schema") != "eval-packet-v1b":
        errors.append(f"report schema {rep.get('schema')!r}")
    if str(rep.get("path")) != str(REPORT_PATH):
        errors.append(f"report.path must be {REPORT_PATH}")
    if not rep.get("generated_at"):
        errors.append("report missing generated_at")
    if not rep.get("strict_build_capture"):
        errors.append("report missing strict_build_capture — run capture_eval_report() on strict build")
    errors.extend(eval_scaffold_live_regression_errors(rep))
    if not CAPTURE_META_PATH.is_file():
        errors.append(f"missing {CAPTURE_META_PATH}")
    else:
        try:
            meta = json.loads(CAPTURE_META_PATH.read_text(encoding="utf-8"))
            if meta.get("schema") != "eval-packet-v1b-capture-v1":
                errors.append("capture meta schema invalid")
            if meta.get("report_mode") == "scaffold" and meta.get("live_ok") is True:
                errors.append(
                    "capture meta regression: report_mode=scaffold while live_ok=true"
                )
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"capture meta invalid: {exc}")
    return errors


def main() -> int:
    meta = capture_eval_report(strict=True)
    print(json.dumps(meta, indent=2))
    errs = assert_capture_artifacts()
    if errs:
        for e in errs:
            print(f"FAIL: {e}")
        return 1
    print(f"OK: eval report captured · {REPORT_PATH} · mode={meta.get('report_mode')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
