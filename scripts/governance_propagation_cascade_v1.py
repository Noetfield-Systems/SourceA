#!/usr/bin/env python3
"""G0/G1 change + worker completion → cascade to monitor/hub/inbox without human refresh."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from governance_paths_v1 import AUTHORITY_INDEX, GOVERNANCE_ENTRY, SINA_OS_SSOT

SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "governance-propagation-receipt-v1.json"

G0_G1_PATHS = (
    SINA_OS_SSOT,
    AUTHORITY_INDEX,
    GOVERNANCE_ENTRY,
    ROOT / "SOURCEA_INCIDENT_FIX_OWNERSHIP_GOVERNANCE_HARDENING_LOCKED_v1.md",
    ROOT / "SOURCEA_FOUNDER_MACHINE_TERMINOLOGY_DICTIONARY_LOCKED_v1.md",
    ROOT / "PROGRAM_PROGRESS.json",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _step(name: str, fn) -> dict:
    t0 = time.monotonic()
    try:
        out = fn()
        return {"ok": True, "step": name, "ms": int((time.monotonic() - t0) * 1000), "detail": out}
    except Exception as exc:
        return {"ok": False, "step": name, "ms": int((time.monotonic() - t0) * 1000), "error": str(exc)}


def cascade(*, reason: str = "manual", strict_hub: bool = False, fast: bool = False) -> dict:
    """Run propagation ladder — law: worker says done → machine updates projection."""
    steps: list[dict] = []

    if fast:
        def hub_invalidate():
            sys.path.insert(0, str(SCRIPTS))
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            invalidate_worker_hub_cache()
            return {"mode": "invalidate_only"}

        steps.append(_step("worker_hub_invalidate", hub_invalidate))

        def inbox_truth():
            sys.path.insert(0, str(SCRIPTS))
            from run_inbox_disk_truth_v1 import write_truth  # noqa: WPS433

            return write_truth(sync=False)

        steps.append(_step("run_inbox_truth", inbox_truth))

        def stairlift():
            proc = subprocess.run(
                [sys.executable, str(SCRIPTS / "governance_stairlift_sync_v1.py"), "--if-stale", "--tier", "warm", "--json"],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=15,
            )
            return {"returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-300:]}

        steps.append(_step("governance_stairlift", stairlift))

        ok = all(s.get("ok") for s in steps)
        row = {
            "schema": "governance-propagation-receipt-v1",
            "at": _now(),
            "reason": reason,
            "mode": "fast",
            "ok": ok,
            "steps": steps,
            "law": "SOURCEA_FAST_SYSTEM_LOAD_BUDGET_LOCKED_v1.md — Worker closeout",
        }
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        return row

    def monitor_sync():
        sys.path.insert(0, str(SCRIPTS))
        from monitor_live_sync_v1 import sync_disk  # noqa: WPS433

        return sync_disk(force=True, reason=f"governance_cascade:{reason}", light=True)

    steps.append(_step("monitor_live_sync", monitor_sync))

    def brain_sync():
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "brain_sync_lib_v1.py"), "--mode", "light"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=45,
        )
        return {"returncode": proc.returncode, "stdout_tail": (proc.stdout or "")[-400:]}

    steps.append(_step("brain_sync_if_changed", brain_sync))

    def hub_align():
        script = "build-sina-command-panel.py" if strict_hub else "align_command_data_ui_v1.py"
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / script)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=300 if strict_hub else 60,
        )
        return {"script": script, "returncode": proc.returncode}

    steps.append(_step("hub_projection", hub_align))

    def inbox_truth():
        sys.path.insert(0, str(SCRIPTS))
        from run_inbox_disk_truth_v1 import write_truth  # noqa: WPS433

        return write_truth(sync=False)

    steps.append(_step("run_inbox_truth", inbox_truth))

    def backlog_snapshot():
        sys.path.insert(0, str(SCRIPTS))
        from governance_completion_backlog_audit import audit  # noqa: WPS433

        return audit()

    steps.append(_step("completion_backlog", backlog_snapshot))

    ok = all(s.get("ok") for s in steps[:4])
    row = {
        "schema": "governance-propagation-receipt-v1",
        "at": _now(),
        "reason": reason,
        "ok": ok,
        "steps": steps,
        "law": "SOURCEA_LIVE_GOVERNANCE_BIG_PICTURE_LOCKED_v1.md §5",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")

    try:
        sys.path.insert(0, str(SCRIPTS))
        from governance_event_spine_v1 import append_event  # noqa: WPS433
        from governance_reference_graph_v1 import impact_scan  # noqa: WPS433

        impact = impact_scan(object_id="LIVE_GOV_BP")
        aff = impact.get("affected") or {}
        projections = aff.get("projections") or ["hub", "monitor", "truth_bundle"]
        spine_res = append_event(
            event_type="PROPAGATION",
            object_id="governance_propagation_cascade",
            object_kind="system",
            agent_id="maintainer",
            law_id="LIVE_GOV_BP",
            skill_id="truth-projection",
            validator_set=aff.get("validators") or ["validate-governance-propagation-live-v1.sh"],
            affected_objects=aff.get("objects") or ["LIVE_GOV_BP"],
            payload={"reason": reason, "ok": ok, "step_count": len(steps)},
            projection_targets=projections,
            gate="governance_propagation_cascade",
            proof=str(RECEIPT),
        )
        if spine_res.get("ok"):
            from governance_projection_g3_v1 import enqueue_from_impact, write_projection_gate  # noqa: WPS433

            ev = spine_res.get("event") or {}
            enqueue_from_impact(
                law_row_id="LIVE_GOV_BP",
                impact=impact,
                source_event_id=str(ev.get("event_id") or ""),
                reason=f"propagation:{reason}",
            )
            write_projection_gate(
                projections=projections,
                source_event_id=str(ev.get("event_id") or ""),
                reason=f"propagation:{reason}",
            )
    except Exception:
        pass

    return row


def g0_signature() -> str:
    parts = []
    for p in G0_G1_PATHS:
        if p.is_file():
            st = p.stat()
            parts.append(f"{p.name}:{st.st_mtime_ns}:{st.st_size}")
        else:
            parts.append(f"missing:{p.name}")
    return "|".join(parts)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--reason", default="cli")
    parser.add_argument("--strict-hub", action="store_true")
    parser.add_argument("--fast", action="store_true", help="Worker loop closeout — ms projection only")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    row = cascade(reason=args.reason, strict_hub=args.strict_hub, fast=args.fast)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"governance_propagation_cascade: ok={row['ok']} reason={args.reason}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
