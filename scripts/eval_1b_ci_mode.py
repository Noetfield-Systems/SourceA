#!/usr/bin/env python3
"""Probe Eval-1b CI mode — live vs structural-only when OpenRouter returns 402."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

SINA_HOME = Path.home() / ".sina"
MODE_PATH = SINA_HOME / "eval_1b_ci_mode_v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def probe_openrouter() -> tuple[bool, str]:
    try:
        from eval_packet_v1b.runner import _chat_eval  # noqa: WPS433

        ok, detail = _chat_eval([{"role": "user", "content": "ping"}], system="reply ok")
        if ok:
            return True, detail or "ok"
        if "HTTP 402" in (detail or ""):
            return False, "openrouter_402"
        return False, detail or "probe_failed"
    except Exception as e:
        return False, str(e)


def write_mode(*, mode: str, reason: str, live_ok: bool) -> dict:
    SINA_HOME.mkdir(parents=True, exist_ok=True)
    row = {
        "schema": "eval-1b-ci-mode-v1",
        "updated_at": _now(),
        "mode": mode,
        "reason": reason,
        "live_probe_ok": live_ok,
        "strict_build_live_gate": live_ok,
        "structural_fallback": not live_ok,
        "restore_action": "Top up OpenRouter credits — then re-run validate-eval-packet-v1b-live.sh",
        "law": "STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md §5 Phase 1",
    }
    MODE_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def sync_after_live_report() -> dict | None:
    """Clear structural_fallback when disk report is live+live_ok (sa-0140 hygiene)."""
    report_path = SINA_HOME / "eval_packet_v1b_report.json"
    if not report_path.is_file():
        return None
    try:
        rep = json.loads(report_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if rep.get("mode") != "live" or not rep.get("live_ok"):
        return None
    live_pct = rep.get("live_pilot_win_pct")
    if live_pct is None:
        live_pct = rep.get("packet_win_pct")
    if int(live_pct or 0) < 80:
        return None
    return write_mode(mode="live", reason="live_report_pass", live_ok=True)


def resolve_mode() -> dict:
    synced = sync_after_live_report()
    if synced:
        return synced
    live_ok, reason = probe_openrouter()
    if live_ok:
        return write_mode(mode="live", reason=reason, live_ok=True)
    if reason == "openrouter_402":
        return write_mode(mode="structural_only", reason=reason, live_ok=False)
    return write_mode(mode="structural_only", reason=reason, live_ok=False)


def main() -> None:
    row = resolve_mode()
    print(json.dumps(row, indent=2))


if __name__ == "__main__":
    main()
