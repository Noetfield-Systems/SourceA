#!/usr/bin/env python3
"""G3 — LAW_TOUCHED → impact → projection queue → selective materializers + write gate."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from governance_paths_v1 import AUTHORITY_INDEX

SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
QUEUE_PATH = SINA / "governance-projection-queue-v1.jsonl"
GATE_PATH = SINA / "governance-projection-gate-v1.json"
RECEIPT_PATH = SINA / "governance-projection-g3-receipt-v1.json"
INDEX = AUTHORITY_INDEX

sys.path.insert(0, str(SCRIPTS))

from governance_event_spine_v1 import append_event, read_all_rows  # noqa: E402
from governance_reference_graph_v1 import impact_scan  # noqa: E402

MATERIALIZER_ORDER = ("hub", "monitor", "catalog", "truth_bundle", "live_form")
OPTIONAL_PROJECTIONS = frozenset({"live_form"})
MATERIALIZER_MAP = {
    "hub": ("align_command_data_ui_v1.py", "function"),
    "catalog": ("ecosystem_master_catalog_v1.py", "json"),
    "monitor": ("monitor_live_sync_v1.py", "sync"),
    "truth_bundle": ("agent_truth_bundle_v1.py", "json"),
    "live_form": ("live_founder_decision_form_v1.py", "write"),
}

GATE_TTL_SEC = 300


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_ts(iso: str) -> datetime | None:
    if not iso:
        return None
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return None


def _doc_for_row(law_row_id: str) -> str:
    if not INDEX.is_file():
        return ""
    for line in INDEX.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith(f"| `{law_row_id}`"):
            continue
        parts = [p.strip().strip("`") for p in line.split("|")]
        if len(parts) > 2:
            return parts[2]
    return ""


def run_materializer(projection: str, *, reason: str = "g3") -> dict:
    spec = MATERIALIZER_MAP.get(projection)
    if not spec:
        return {"ok": False, "error": f"unknown projection: {projection}"}
    script, mode = spec
    if mode == "function":
        try:
            from align_command_data_ui_v1 import align_command_data_ui  # noqa: WPS433

            align_command_data_ui()
            return {"ok": True, "projection": projection, "materializer": script, "reason": reason}
        except Exception as exc:
            return {"ok": False, "projection": projection, "error": str(exc), "materializer": script}
    if mode == "sync":
        try:
            from monitor_live_sync_v1 import sync_disk  # noqa: WPS433

            detail = sync_disk(force=True, reason=f"g3:{reason}", light=True)
            return {"ok": True, "projection": projection, "detail": detail}
        except Exception as exc:
            return {"ok": False, "projection": projection, "error": str(exc)}
    path = SCRIPTS / script
    args = [sys.executable, str(path)]
    if mode == "json":
        args.append("--json")
    if mode == "write":
        args.append("--write-receipt")
    proc = subprocess.run(args, cwd=str(ROOT), capture_output=True, text=True, timeout=180)
    return {
        "ok": proc.returncode == 0,
        "projection": projection,
        "materializer": script,
        "returncode": proc.returncode,
        "stdout_tail": (proc.stdout or proc.stderr or "")[-240:],
    }


def write_projection_gate(
    *,
    projections: list[str],
    source_event_id: str,
    reason: str,
    ttl_sec: int = GATE_TTL_SEC,
) -> dict:
    until = datetime.now(timezone.utc) + timedelta(seconds=ttl_sec)
    row = {
        "schema": "governance-projection-gate-v1",
        "at": _now(),
        "until": until.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "projections": sorted(set(projections)),
        "source_event_id": source_event_id,
        "reason": reason,
    }
    SINA.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def projection_write_allowed(projections: list[str]) -> tuple[bool, str]:
    if os.environ.get("SINA_G3_ENFORCE", "1") == "0":
        return True, "enforce_off"
    need = set(projections)
    if GATE_PATH.is_file():
        try:
            gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
            until = _parse_ts(str(gate.get("until") or ""))
            if until and datetime.now(timezone.utc) <= until:
                allowed = set(gate.get("projections") or [])
                if need <= allowed:
                    return True, "gate_file"
        except (OSError, json.JSONDecodeError):
            pass
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=GATE_TTL_SEC)
    for row in reversed(read_all_rows()[-40:]):
        at = _parse_ts(str(row.get("at") or ""))
        if at and at < cutoff:
            break
        targets = set(row.get("projection_targets") or [])
        if need <= targets and row.get("event_type") in (
            "LAW_TOUCHED",
            "PROPAGATION",
            "IMPACT_SCAN",
            "RECOVERY_FOUND",
            "VALIDATOR_PASS",
        ):
            return True, f"spine:{row.get('event_id')}"
    return False, "no_gate"


def assert_projection_write_allowed(projections: list[str]) -> None:
    ok, detail = projection_write_allowed(projections)
    if not ok:
        raise RuntimeError(
            "G3 projection write blocked — run governance_projection_g3_v1.py "
            f"--law-touched ROW_ID --drain (need {projections}, got {detail})"
        )


def authorize_projection_write(
    projections: list[str],
    *,
    reason: str,
    law_row_id: str = "LIVE_GOV_BP",
) -> dict:
    """Fast authorize for routine hub align — IMPACT_SCAN + gate file."""
    impact = impact_scan(object_id=law_row_id)
    aff = (impact.get("affected") if impact.get("ok") else {}) or {}
    targets = sorted(set(projections) | set(aff.get("projections") or []))
    res = append_event(
        event_type="IMPACT_SCAN",
        object_id=law_row_id,
        object_kind="law",
        agent_id="maintainer",
        law_id=law_row_id,
        skill_id="governance-projection-g3",
        validator_set=aff.get("validators") or ["validate-governance-projection-g3-v1.sh"],
        affected_objects=aff.get("objects") or [law_row_id],
        payload={"reason": reason, "authorize_only": True},
        projection_targets=targets,
        gate="governance_projection_g3_v1:authorize",
        proof="governance-projection-gate-v1.json",
    )
    event = res.get("event") or {}
    gate = write_projection_gate(
        projections=targets,
        source_event_id=str(event.get("event_id") or ""),
        reason=reason,
    )
    return {"ok": res.get("ok", False), "event_id": event.get("event_id"), "gate": gate}


def enqueue_from_impact(
    *,
    law_row_id: str,
    impact: dict,
    source_event_id: str,
    reason: str,
) -> dict:
    aff = impact.get("affected") or {}
    projections = list(aff.get("projections") or [])
    job = {
        "id": f"GPQ-{uuid.uuid4().hex[:10]}",
        "at": _now(),
        "law_row_id": law_row_id,
        "reason": reason,
        "source_event_id": source_event_id,
        "projections": projections,
        "materializer": aff.get("materializer"),
        "validators": aff.get("validators") or [],
        "status": "pending",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    with QUEUE_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(job, ensure_ascii=False) + "\n")
    return job


def read_pending_jobs(*, limit: int = 20) -> list[dict]:
    if not QUEUE_PATH.is_file():
        return []
    pending: list[dict] = []
    for line in QUEUE_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            job = json.loads(line)
        except json.JSONDecodeError:
            continue
        if job.get("status") == "pending":
            pending.append(job)
    return pending[-limit:]


def _mark_job_done(job_id: str) -> None:
    if not QUEUE_PATH.is_file():
        return
    lines: list[str] = []
    for line in QUEUE_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            job = json.loads(line)
        except json.JSONDecodeError:
            lines.append(line)
            continue
        if job.get("id") == job_id and job.get("status") == "pending":
            job["status"] = "done"
            job["done_at"] = _now()
            lines.append(json.dumps(job, ensure_ascii=False))
        else:
            lines.append(line)
    QUEUE_PATH.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def drain_projection_queue(*, dry_run: bool = False, limit: int = 5) -> dict:
    jobs = read_pending_jobs(limit=limit)
    if not jobs:
        return {"ok": True, "drained": 0, "steps": [], "dry_run": dry_run}
    steps: list[dict] = []
    projections: list[str] = []
    source_ids: list[str] = []
    for job in jobs:
        projections.extend(job.get("projections") or [])
        source_ids.append(str(job.get("source_event_id") or ""))
    ordered = [p for p in MATERIALIZER_ORDER if p in set(projections)]
    ordered.extend([p for p in sorted(set(projections)) if p not in ordered])
    if dry_run:
        for p in ordered:
            steps.append({"projection": p, "action": "would_materialize", "ok": True})
        return {"ok": True, "drained": len(jobs), "steps": steps, "dry_run": True}

    write_projection_gate(
        projections=ordered,
        source_event_id=source_ids[-1] if source_ids else "",
        reason="g3_drain",
    )
    for p in ordered:
        steps.append(run_materializer(p, reason="g3_drain"))
    if steps:
        ok = all(
            s.get("ok")
            for s in steps
            if str(s.get("projection") or "") not in OPTIONAL_PROJECTIONS
        )
    else:
        ok = True
    if ok:
        for job in jobs:
            _mark_job_done(str(job.get("id") or ""))
    return {"ok": ok, "drained": len(jobs), "steps": steps, "dry_run": False}


def emit_law_touched(
    *,
    law_row_id: str,
    reason: str = "maintainer_save",
    doc_path: str = "",
    enqueue: bool = True,
    drain: bool = False,
    dry_run: bool = False,
) -> dict:
    doc = doc_path or _doc_for_row(law_row_id)
    impact = impact_scan(object_id=law_row_id)
    if not impact.get("ok"):
        impact = impact_scan(object_id="GOV_EVENT_SPINE")
    aff = impact.get("affected") or {}
    targets = aff.get("projections") or ["catalog", "truth_bundle"]
    spine = append_event(
        event_type="LAW_TOUCHED",
        object_id=law_row_id,
        object_kind="law",
        agent_id="maintainer",
        law_id=law_row_id,
        skill_id="governance-projection-g3",
        validator_set=aff.get("validators") or ["validate-governance-projection-g3-v1.sh"],
        affected_objects=aff.get("objects") or [law_row_id],
        payload={"reason": reason, "doc": doc},
        projection_targets=targets,
        gate="governance_projection_g3_v1:law_touched",
        proof=str(INDEX),
    )
    event = spine.get("event") or {}
    job = None
    if enqueue and spine.get("ok"):
        job = enqueue_from_impact(
            law_row_id=law_row_id,
            impact=impact,
            source_event_id=str(event.get("event_id") or ""),
            reason=reason,
        )
    write_projection_gate(
        projections=targets,
        source_event_id=str(event.get("event_id") or ""),
        reason=f"law_touched:{reason}",
    )
    drain_result = None
    if drain:
        drain_result = drain_projection_queue(dry_run=dry_run)
    receipt = {
        "schema": "governance-projection-g3-receipt-v1",
        "at": _now(),
        "ok": spine.get("ok", False) and (drain_result is None or drain_result.get("ok", False)),
        "law_row_id": law_row_id,
        "reason": reason,
        "doc": doc,
        "event_id": event.get("event_id"),
        "replay_pointer": event.get("replay_pointer"),
        "impact_ok": impact.get("ok"),
        "projections": targets,
        "queue_job_id": (job or {}).get("id"),
        "drain": drain_result,
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="G3 projection layer")
    ap.add_argument("--law-touched", metavar="ROW_ID", default="")
    ap.add_argument("--reason", default="cli")
    ap.add_argument("--doc", default="")
    ap.add_argument("--no-enqueue", action="store_true")
    ap.add_argument("--drain", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--authorize", metavar="PROJ", nargs="*", default=[])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.authorize:
        out = authorize_projection_write(list(args.authorize), reason=args.reason)
    elif args.drain and not args.law_touched:
        out = drain_projection_queue(dry_run=args.dry_run)
    elif args.law_touched:
        out = emit_law_touched(
            law_row_id=args.law_touched,
            reason=args.reason,
            doc_path=args.doc,
            enqueue=not args.no_enqueue,
            drain=args.drain,
            dry_run=args.dry_run,
        )
    else:
        out = {
            "ok": False,
            "error": "use --law-touched ROW_ID [--drain] or --drain or --authorize hub ...",
        }

    print(json.dumps(out, indent=2))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
