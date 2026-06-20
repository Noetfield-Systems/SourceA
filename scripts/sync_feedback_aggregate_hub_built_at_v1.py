#!/usr/bin/env python3
"""Sync FEEDBACK_AGGREGATE execution_truth with hub command-data built_at (sa-0017).

No ASF eval/progress authority — machine validators + auto_pass only.
Rebuilds EXECUTION_TRUTH from REPO_EXECUTION_LOGS via SinaPromptOS execution_tracker;
stamps hub_built_at on FEEDBACK_AGGREGATE + EXECUTION_TRUTH to match panel build.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
FEEDBACK_AGGREGATE = SOURCE_A / "FEEDBACK_AGGREGATE.json"
EXECUTION_TRUTH = SOURCE_A / "EXECUTION_TRUTH.json"
SHELL = SOURCE_A / "agent-control-panel" / "command-data-shell.json"
PROMPTOS = Path("/Users/sinakazemnezhad/Desktop/SinaPromptOS")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _hub_built_at(explicit: str | None) -> str:
    if explicit and explicit.strip():
        return explicit.strip()
    if SHELL.is_file():
        data = json.loads(SHELL.read_text(encoding="utf-8"))
        built = data.get("built_at")
        if built:
            return str(built)
    raise SystemExit("hub built_at missing — pass --built-at or build panel first")


def _sync_local_stamp(*, hub_built_at: str) -> dict:
    """Stamp existing FEEDBACK/EXECUTION_TRUTH when SinaPromptOS modules unavailable."""
    synced_at = _stamp()
    truth: dict = {}
    if EXECUTION_TRUTH.is_file():
        try:
            truth = json.loads(EXECUTION_TRUTH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            truth = {}
    truth["hub_built_at"] = hub_built_at
    truth["hub_synced_at"] = synced_at
    truth.setdefault("generator", "SourceA/sync_feedback_aggregate_hub_built_at_v1.py")
    EXECUTION_TRUTH.write_text(json.dumps(truth, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    agg: dict = {}
    if FEEDBACK_AGGREGATE.is_file():
        try:
            agg = json.loads(FEEDBACK_AGGREGATE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            agg = {}
    exec_loaded = int(agg.get("executions_loaded") or 0)
    reports_loaded = int(agg.get("reports_loaded") or 0)
    agg.update(
        {
            "generated_at": synced_at,
            "generator": "SourceA/sync_feedback_aggregate_hub_built_at_v1.py",
            "hub_built_at": hub_built_at,
            "hub_synced_at": synced_at,
            "reports_loaded": reports_loaded,
            "executions_loaded": exec_loaded,
            "execution_truth": truth,
        }
    )
    FEEDBACK_AGGREGATE.write_text(json.dumps(agg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "mode": "local_stamp",
        "hub_built_at": hub_built_at,
        "hub_synced_at": synced_at,
        "reports_loaded": reports_loaded,
        "executions_loaded": exec_loaded,
    }


def sync_feedback_aggregate(*, hub_built_at: str) -> dict:
    if not PROMPTOS.is_dir():
        return _sync_local_stamp(hub_built_at=hub_built_at)

    # #region agent log
    try:
        from _debug_e2e_log_v1 import dbg  # noqa: WPS433

        shell_start = None
        if SHELL.is_file():
            try:
                shell_start = json.loads(SHELL.read_text(encoding="utf-8")).get("built_at")
            except (OSError, json.JSONDecodeError):
                pass
        dbg(
            hypothesis_id="A",
            location="sync_feedback_aggregate_hub_built_at_v1.py:sync_start",
            message="sync start",
            data={"hub_built_at_in": hub_built_at, "shell_built_at_start": shell_start},
        )
    except Exception:
        pass
    # #endregion

    sys.path.insert(0, str(PROMPTOS))
    try:
        from core.ecosystem_feedback import load_all_reports  # noqa: WPS433
        from core.execution_tracker import (  # noqa: WPS433
            build_truth_aggregate,
            load_all_executions,
            write_truth_aggregate,
        )
    except ModuleNotFoundError:
        return _sync_local_stamp(hub_built_at=hub_built_at)

    reports = load_all_reports()
    executions = load_all_executions()
    truth = build_truth_aggregate(reports, executions)
    synced_at = _stamp()
    # Re-read shell after truth rebuild — strict build/heal may bump built_at mid-sync (E2E sa-0017)
    if SHELL.is_file():
        try:
            fresh = json.loads(SHELL.read_text(encoding="utf-8")).get("built_at")
            if fresh:
                hub_built_at = str(fresh)
        except (OSError, json.JSONDecodeError):
            pass
    truth["hub_built_at"] = hub_built_at
    truth["hub_synced_at"] = synced_at
    write_truth_aggregate(truth)

    agg: dict = {}
    if FEEDBACK_AGGREGATE.is_file():
        try:
            agg = json.loads(FEEDBACK_AGGREGATE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            agg = {}
    agg.update(
        {
            "generated_at": synced_at,
            "generator": "SinaPromptOS/ecosystem_feedback",
            "hub_built_at": hub_built_at,
            "hub_synced_at": synced_at,
            "reports_loaded": len(reports),
            "executions_loaded": sum(len(v) for v in executions.values()),
            "execution_truth": truth,
        }
    )
    FEEDBACK_AGGREGATE.write_text(
        json.dumps(agg, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    # #region agent log
    try:
        from _debug_e2e_log_v1 import dbg  # noqa: WPS433

        shell_end = None
        if SHELL.is_file():
            try:
                shell_end = json.loads(SHELL.read_text(encoding="utf-8")).get("built_at")
            except (OSError, json.JSONDecodeError):
                pass
        dbg(
            hypothesis_id="B",
            location="sync_feedback_aggregate_hub_built_at_v1.py:sync_end",
            message="sync end",
            data={
                "hub_built_at_written": hub_built_at,
                "shell_built_at_end": shell_end,
                "drift": shell_end != hub_built_at if shell_end else None,
            },
        )
    except Exception:
        pass
    # #endregion
    return {
        "ok": True,
        "hub_built_at": hub_built_at,
        "hub_synced_at": synced_at,
        "reports_loaded": len(reports),
        "executions_loaded": sum(len(v) for v in executions.values()),
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Sync FEEDBACK_AGGREGATE to hub built_at (sa-0017)")
    parser.add_argument("--built-at", default="", help="Hub built_at ISO (default: command-data-shell.json)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    hub = _hub_built_at(args.built_at or None)
    out = sync_feedback_aggregate(hub_built_at=hub)
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(
            f"OK: FEEDBACK_AGGREGATE synced · hub_built_at={hub} · "
            f"executions={out['executions_loaded']} reports={out['reports_loaded']} (sa-0017)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
