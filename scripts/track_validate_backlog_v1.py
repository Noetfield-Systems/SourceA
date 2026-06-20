#!/usr/bin/env python3
"""Live pending/unproven backlog + broker validation snapshot for monitor + Worker INBOX.

Law: INCIDENT-006 — dual proof (Worker receipt + broker/maintainer validation).
"""
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
SNAPSHOT = SINA / "track-validate-snapshot-v1.json"
BROKER_STATE = SINA / "goal1-lane-broker-v1.json"
BROKER_EVENTS = SINA / "goal1-lane-broker-events.jsonl"
MATRIX_JSON = SINA / "PROGRAM_1000_STEP_MATRIX.json"
QUEUE_HOME = SINA / "healthy-queue-30-active.json"

sys.path.insert(0, str(SCRIPTS))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _tail_events(n: int = 12) -> list[dict]:
    if not BROKER_EVENTS.is_file():
        return []
    lines = [ln for ln in BROKER_EVENTS.read_text(encoding="utf-8").splitlines() if ln.strip()]
    out: list[dict] = []
    for ln in lines[-n:]:
        try:
            out.append(json.loads(ln))
        except json.JSONDecodeError:
            continue
    return out


def _run_validator(script: str, timeout: int = 90) -> dict:
    path = SCRIPTS / script
    if not path.is_file():
        return {"ok": False, "script": script, "error": "missing"}
    try:
        proc = subprocess.run(
            ["bash", str(path)] if script.endswith(".sh") else [sys.executable, str(path)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        tail = (proc.stdout or proc.stderr or "")[-400:]
        return {"ok": proc.returncode == 0, "script": script, "exit": proc.returncode, "tail": tail.strip()}
    except subprocess.TimeoutExpired:
        return {"ok": False, "script": script, "error": "timeout"}
    except Exception as exc:
        return {"ok": False, "script": script, "error": str(exc)}


def broker_validation_snapshot(*, run_validators: bool = False) -> dict:
    broker = _load(BROKER_STATE)
    events = _tail_events(15)
    last_submit = next((e for e in reversed(events) if e.get("kind") == "WORKER_SUBMIT"), {})
    last_brain = next((e for e in reversed(events) if e.get("kind") == "BRAIN_ACK"), {})

    validators: list[dict] = []
    if run_validators:
        for script in (
            "validate-registry-honest-gate-v1.sh",
            "validate-monitor-honesty-v1.sh",
            "validate-goal1-lane-broker-v1.sh",
        ):
            validators.append(_run_validator(script))

    honest_gate = validators[0] if validators else {}
    monitor_gate = validators[1] if len(validators) > 1 else {}
    broker_gate = validators[2] if len(validators) > 2 else {}

    maintainer_ok = all(v.get("ok") for v in validators) if validators else True
    return {
        "at": _now(),
        "broker_status": broker.get("status"),
        "broker_updated_at": broker.get("updated_at"),
        "last_worker_submit": {
            "at": last_submit.get("at"),
            "sa_id": last_submit.get("sa_id"),
            "round_type": last_submit.get("round_type"),
            "ok": last_submit.get("ok"),
        },
        "last_brain_ack": {"at": last_brain.get("at"), "note": (last_brain.get("note") or "")[:120]},
        "recent_events": [
            {"at": e.get("at"), "kind": e.get("kind"), "sa_id": e.get("sa_id"), "round_type": e.get("round_type")}
            for e in events[-8:]
        ],
        "maintainer_proof": {
            "label": "Maintainer validation (broker + honest gate)",
            "at": _now(),
            "ok": maintainer_ok,
            "validators": validators,
            "honest_gate": honest_gate.get("tail") or honest_gate.get("error") or "",
            "monitor_gate": monitor_gate.get("tail") or monitor_gate.get("error") or "",
            "broker_gate": broker_gate.get("tail") or broker_gate.get("error") or "",
        },
        "law": "Worker receipt on disk + broker WORKER_SUBMIT + maintainer gates PASS",
    }


def _ensure_matrix() -> dict:
    if MATRIX_JSON.is_file():
        try:
            data = json.loads(MATRIX_JSON.read_text(encoding="utf-8"))
            if data.get("steps"):
                return data
        except (OSError, json.JSONDecodeError):
            pass
    import importlib.util

    spec = importlib.util.spec_from_file_location("matrix", SCRIPTS / "program-1000-step-matrix-v1.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    data = mod.build_matrix()
    MATRIX_JSON.parent.mkdir(parents=True, exist_ok=True)
    MATRIX_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


def build_backlog(*, limit: int = 120) -> dict:
    from registry_honest_lib_v1 import audit_registry_done  # noqa: WPS433

    audit = audit_registry_done()
    matrix = _ensure_matrix()
    steps = matrix.get("steps") or []
    step_map = {s["sa_id"]: s for s in steps if s.get("sa_id")}

    queue_items: list[dict] = []
    if QUEUE_HOME.is_file():
        try:
            q = json.loads(QUEUE_HOME.read_text(encoding="utf-8"))
            for i, item in enumerate(q.get("queue") or [], start=1):
                sa = str(item.get("sa_id") or "")
                if sa.startswith("sa-"):
                    queue_items.append(
                        {
                            "sa_id": sa,
                            "queue_pos": i,
                            "queue_role": item.get("queue_role") or "?",
                        }
                    )
        except (OSError, json.JSONDecodeError):
            pass

    pending: list[dict] = []
    unproven: list[dict] = []
    validate_first: list[dict] = []
    seen_turn: set[tuple[str, str]] = set()

    for qi in queue_items:
        sa = qi["sa_id"]
        role = str(qi.get("queue_role") or "?")
        key = (sa, role)
        if key in seen_turn:
            continue
        seen_turn.add(key)
        s = step_map.get(sa) or {"sa_id": sa, "title": "", "missing_gaps": "IN_QUEUE"}
        if s.get("honest_proof"):
            continue
        row = _row_from_step(s, priority="queue")
        row["queue_role"] = role
        row["queue_pos"] = qi.get("queue_pos")
        pending.append(row)

    queue_sas = {qi["sa_id"] for qi in queue_items}

    for s in steps:
        sa = s.get("sa_id") or ""
        if not sa:
            continue
        gaps = s.get("missing_gaps") or ""
        proof = s.get("proof_verdict") or ""
        reg = s.get("registry_status") or "backlog"

        if reg == "done" and not s.get("honest_proof"):
            unproven.append(_row_from_step(s, priority="unproven"))
        elif "VALIDATE_FIRST" in gaps or s.get("quarantined_yaml"):
            if sa not in queue_sas:
                validate_first.append(_row_from_step(s, priority="validate_first"))
        elif gaps and sa not in queue_sas and reg == "backlog":
            if "NOT_DONE" in gaps and s.get("validation") == "FAIL":
                validate_first.append(_row_from_step(s, priority="fail"))

    pending.sort(
        key=lambda r: (
            r.get("queue_pos") or 9999,
            {"check": 0, "act": 1, "verify": 2}.get(str(r.get("queue_role") or ""), 9),
        )
    )
    unproven.sort(key=lambda r: int(r["sa_id"].split("-")[1]))
    validate_first.sort(key=lambda r: int(r["sa_id"].split("-")[1]))

    combined = pending + unproven + validate_first
    seen: set[str] = set()
    deduped: list[dict] = []
    for row in combined:
        if row["sa_id"] in seen:
            continue
        seen.add(row["sa_id"])
        deduped.append(row)

    return {
        "at": _now(),
        "summary": {
            "honest_done": audit.get("honest_done", 0),
            "unproven_done": audit.get("unproven_done", 0),
            "queue_pending": len(pending),
            "validate_first": len(validate_first),
            "unproven_registry": len(unproven),
            "total_attention": len(deduped),
            "matrix_updated": matrix.get("updated_at"),
        },
        "queue_pending": pending[:limit],
        "unproven": unproven[:limit],
        "validate_first": validate_first[: min(limit, 80)],
        "all_attention": deduped[:limit],
        "founder_action": "Worker → run inbox · CHECK reports gaps · VERIFY writes receipt",
    }


def _row_from_step(s: dict, *, priority: str) -> dict:
    q = s.get("queue") or {}
    rec = s.get("receipt") or {}
    return {
        "sa_id": s.get("sa_id"),
        "priority": priority,
        "title": (s.get("title") or "")[:100],
        "registry_status": s.get("registry_status"),
        "proof_verdict": s.get("proof_verdict"),
        "validation": s.get("validation"),
        "missing_gaps": s.get("missing_gaps"),
        "queue_role": q.get("queue_role"),
        "queue_pos": q.get("queue_pos"),
        "recipe_path": (s.get("recipe") or {}).get("path"),
        "verify_recipe": (s.get("verify_recipe") or "")[:200],
        "worker_proof": rec.get("path") if rec.get("has") else "",
        "worker_proof_status": rec.get("status") or rec.get("receipt_status"),
        "honest": bool(s.get("honest_proof")),
    }


def build_snapshot(*, run_validators: bool = False) -> dict:
    backlog = build_backlog()
    broker = broker_validation_snapshot(run_validators=run_validators)
    return {
        "schema": "track-validate-snapshot-v1",
        "at": _now(),
        "backlog": backlog,
        "broker_validation": broker,
        "dual_proof_law": {
            "worker": "receipts/sa-XXXX-receipt.json DONE + evidence validators",
            "maintainer": "validate-registry-honest-gate-v1 + validate-goal1-lane-broker-v1 + broker WORKER_SUBMIT",
        },
    }


def format_inbox_block(*, limit: int = 25) -> str:
    snap = build_snapshot(run_validators=False)
    bl = snap["backlog"]
    br = snap["broker_validation"]
    try:
        from monitor_honesty_lib_v1 import audit_monitor  # noqa: WPS433

        mh = audit_monitor(filter_mode="road")
        prog = mh.get("progress") or {}
        progress_line = (
            f"Valid YES: {prog.get('valid_yes', '?')}/1000 ({prog.get('pct', '?')}%) · "
            f"receipts: {mh.get('receipt_done', '?')} · PARTIAL: {(mh.get('counts') or {}).get('valid_partial', 0)}"
        )
    except Exception:
        progress_line = f"Honest receipts: {bl['summary']['honest_done']}/1000"
    lines = [
        "═ TRACK BACKLOG — proof = receipt + validators PASS ═",
        progress_line,
        f"Queue pending: {bl['summary']['queue_pending']} · validate-first: {bl['summary']['validate_first']}",
        "",
        "PROOF: receipts/sa-XXXX-receipt.json + full broker CHECK→ACT→VERIFY · progress bar = Valid YES only.",
        "",
        f"BROKER STATUS: {br.get('broker_status')} · last submit: {br.get('last_worker_submit', {}).get('sa_id')} "
        f"{br.get('last_worker_submit', {}).get('round_type')} @ {br.get('last_worker_submit', {}).get('at')}",
        "",
    ]

    if bl["unproven"]:
        lines.append("## UNPROVEN (REGISTRY done — NO honest receipt) — FIX FIRST")
        for row in bl["unproven"][:10]:
            lines.append(f"- {row['sa_id']} · {row['proof_verdict']} · gaps={row['missing_gaps']}")
        lines.append("")

    lines.append("## ACTIVE QUEUE — pending honest close")
    for row in bl["queue_pending"][:limit]:
        role = row.get("queue_role") or "?"
        pos = row.get("queue_pos") or "?"
        lines.append(
            f"- {row['sa_id']} · {role} · Q{pos} · {row.get('title','')[:60]} · gaps={row.get('missing_gaps')}"
        )
    lines.append("")

    if bl["validate_first"]:
        lines.append("## VALIDATE-FIRST (quarantined fake YAML — need honest pass)")
        for row in bl["validate_first"][:15]:
            lines.append(f"- {row['sa_id']} · {row.get('title','')[:50]}")
        lines.append("")

    lines += [
        "THIS CHECK TURN: audit bound sa + table above · gap report only · no implement on CHECK.",
        "Reference: scripts/track_validate_backlog_v1.py · monitor /api/track-validate",
        "═ END TRACK BACKLOG ═",
        "",
    ]
    return "\n".join(lines)


def write_snapshot(*, run_validators: bool = False) -> dict:
    snap = build_snapshot(run_validators=run_validators)
    SINA.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(json.dumps(snap, indent=2) + "\n", encoding="utf-8")
    snap["snapshot_path"] = str(SNAPSHOT)
    return snap


def load_snapshot(*, refresh_if_stale_sec: int = 45) -> dict:
    if SNAPSHOT.is_file():
        try:
            snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
            at = snap.get("at") or ""
            if at:
                dt = datetime.strptime(at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                age = (datetime.now(timezone.utc) - dt).total_seconds()
                if age < refresh_if_stale_sec:
                    return snap
        except (OSError, json.JSONDecodeError, ValueError):
            pass
    return write_snapshot(run_validators=False)


def main() -> int:
    p = argparse.ArgumentParser(description="Track pending/unproven + broker validation snapshot")
    p.add_argument("--json", action="store_true")
    p.add_argument("--write", action="store_true", help="Write ~/.sina/track-validate-snapshot-v1.json")
    p.add_argument("--run-validators", action="store_true", help="Run honest gate + broker validators (slow)")
    p.add_argument("--inbox-block", action="store_true", help="Print INBOX preamble for Worker")
    p.add_argument("--limit", type=int, default=120)
    args = p.parse_args()

    if args.inbox_block:
        print(format_inbox_block(limit=min(args.limit, 30)))
        return 0

    if args.write or args.run_validators:
        snap = write_snapshot(run_validators=args.run_validators)
    else:
        snap = {"backlog": build_backlog(limit=args.limit), "broker_validation": broker_validation_snapshot()}

    if args.json:
        print(json.dumps(snap, indent=2))
    else:
        bl = snap.get("backlog") or snap
        if "summary" in bl:
            s = bl["summary"]
            print(
                f"TRACK: honest={s.get('honest_done')} queue_pending={s.get('queue_pending')} "
                f"unproven={s.get('unproven_registry')} validate_first={s.get('validate_first')}"
            )
        else:
            print(json.dumps(snap, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
