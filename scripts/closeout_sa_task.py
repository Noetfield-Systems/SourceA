#!/usr/bin/env python3
"""Closeout one sa-XXXX task — REGISTRY + prompt + PRIORITY + execution log.

GATED: receipt + broker VERIFY only (closeout_gate_v1). No batch stamp.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / "REGISTRY.json"
PRIORITY = ROOT / "brain-os" / "plan-registry" / "SOURCEA-PRIORITY.md"
LOGS = ROOT / "REPO_EXECUTION_LOGS" / "sourcea"
SCRIPTS = ROOT / "scripts"
RECEIPTS = ROOT / "receipts"


class ReceiptGateError(Exception):
    """Closeout aborted — no honest receipt logged."""


def _require_receipt_on_disk(task_id: str) -> dict:
    """Hard gate: receipt file must exist and must not be batch-stamped."""
    path = RECEIPTS / f"{task_id}-receipt.json"
    if not path.is_file():
        raise ReceiptGateError(f"MISSING_RECEIPT: {path}")
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReceiptGateError(f"INVALID_RECEIPT: {path}") from exc
    if str(receipt.get("status") or "") == "BATCH_CLOSEOUT_ONLY":
        raise ReceiptGateError(f"BATCH_CLOSEOUT_ONLY receipt blocked for {task_id}")
    return receipt


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def closeout(
    *,
    task_id: str,
    evidence: str,
    next_task: str = "",
    authorized_source: str = "",
    round_type: str = "",
    critical_bugs: int = 0,
) -> dict:
    _require_receipt_on_disk(task_id)

    sys.path.insert(0, str(SCRIPTS))
    from closeout_gate_v1 import check_closeout_allowed  # noqa: WPS433

    gate = check_closeout_allowed(
        task_id=task_id,
        evidence=evidence,
        authorized_source=authorized_source,
        round_type=round_type,
        critical_bugs=critical_bugs,
    )
    if not gate.get("ok"):
        return {"ok": False, "gate": gate}

    data = json.loads(REG.read_text(encoding="utf-8"))
    title = task_id
    for pl in data["plans"]:
        if pl.get("id") == task_id:
            pl["status"] = "done"
            title = pl.get("title") or task_id
            path = pl.get("path") or ""
            md = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / path
            if md.is_file():
                text = md.read_text(encoding="utf-8")
                for old in ("status: backlog", "status: in_progress", "status: active"):
                    if old in text:
                        md.write_text(text.replace(old, "status: done", 1), encoding="utf-8")
                        break
            break
    REG.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    row = f"| {_now()[:10]} | {task_id} {title[:48]} | {evidence[:80]} · critical 0 |\n"
    pri = PRIORITY.read_text(encoding="utf-8")
    if task_id not in pri or f"| {task_id} " not in pri:
        pri = pri.replace("## Verdicts baked into pack", row + "\n## Verdicts baked into pack", 1)
        PRIORITY.write_text(pri, encoding="utf-8")

    reporter = authorized_source or "goal1_lane_broker"
    slug = task_id.replace("/", "-")
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M")
    yaml_body = (
        f"schema_version: 1\nrepo: sourcea\ntask: {task_id} — {title}\nstatus: done\n"
        f"verify_passed: true\nevidence:\n  task_id: {task_id}\n"
        f"tests:\n  status: passed\n  output_snippet: {evidence}\n"
        f"reported_at: '{_now()}'\nreporter: {reporter}\n"
        f"gate_mode: {gate.get('mode')}\n"
    )
    (LOGS / f"{stamp}_plan-with-no-asf-{slug}.yaml").write_text(yaml_body, encoding="utf-8")

    if not next_task:
        from queue_sa_pick_lib_v1 import queue_sa_from_disk  # noqa: WPS433

        next_task = queue_sa_from_disk() or ""
        if not next_task:
            import subprocess

            proc = subprocess.run(
                [sys.executable, str(SCRIPTS / "pick-sourcea-no-asf-plan.py"), "--any-tier", "--limit", "1", "--json"],
                capture_output=True,
                text=True,
                cwd=str(ROOT),
            )
            if proc.returncode == 0 and proc.stdout.strip():
                try:
                    picked = json.loads(proc.stdout)
                    if picked:
                        next_task = picked[0].get("id") or ""
                except json.JSONDecodeError:
                    pass
    latest = (
        f"schema_version: 1\nrepo: sourcea\nlast_task: {task_id}\nstatus: done\n"
        f"verify_passed: true\nnext_task: {next_task}\nreported_at: '{_now()}'\n"
    )
    (LOGS / "latest.yaml").write_text(latest, encoding="utf-8")

    from worker_turn_lib import close_turn  # noqa: WPS433

    close_turn(sa_id=task_id, force=True)

    try:
        from execution_event_log_v1 import append_event  # noqa: WPS433

        if critical_bugs == 0:
            append_event(
                event="VALIDATOR_PASS",
                actor="broker_validators",
                trace_id=task_id,
                data={"sa_id": task_id, "round_type": round_type or "verify"},
            )
        append_event(
            event="TASK_CLOSED",
            actor="broker_validators",
            trace_id=task_id,
            data={"sa_id": task_id, "evidence": evidence[:200]},
        )
        append_event(
            event="BROKER_ACK",
            actor=authorized_source or "goal1_lane_broker",
            trace_id=task_id,
            data={"sa_id": task_id, "round_type": round_type or "verify", "closeout": True},
        )
    except Exception:
        pass

    brain_sync: dict = {}
    rt = (round_type or "verify").lower().strip()
    if rt in ("verify", "verify_backend", "closeout"):
        try:
            from brain_sync_lib_v1 import sync_brain_snapshot  # noqa: WPS433

            brain_sync = sync_brain_snapshot(mode="light", caller=f"closeout:{task_id}")
        except Exception as exc:
            brain_sync = {"ok": False, "error": str(exc)}

    outbound_post_ship: dict = {"skipped": True}
    try:
        from outbound_post_ship_v1 import maybe_rebuild_if_outbound  # noqa: WPS433

        outbound_post_ship = maybe_rebuild_if_outbound(sa_id=task_id)
    except Exception as exc:
        outbound_post_ship = {"ok": False, "error": str(exc)}

    return {
        "ok": True,
        "task_id": task_id,
        "next_task": next_task,
        "gate": gate,
        "brain_sync": brain_sync,
        "outbound_post_ship": outbound_post_ship,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--id", required=True)
    p.add_argument("--evidence", required=True)
    p.add_argument("--next", default="")
    p.add_argument("--source", default="", help="goal1_lane_broker only")
    p.add_argument("--round-type", default="verify")
    p.add_argument("--critical", type=int, default=0)
    args = p.parse_args()
    try:
        out = closeout(
            task_id=args.id,
            evidence=args.evidence,
            next_task=args.next,
            authorized_source=args.source,
            round_type=args.round_type,
            critical_bugs=args.critical,
        )
    except ReceiptGateError as exc:
        out = {"ok": False, "error": str(exc), "gate": "receipt_hard"}
        print(json.dumps(out, indent=2))
        raise SystemExit(1) from exc
    print(json.dumps(out, indent=2))
    if not out.get("ok"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
