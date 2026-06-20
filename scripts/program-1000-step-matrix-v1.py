#!/usr/bin/env python3
"""Live 1000-step proof matrix — recipe + validation + receipt + verify for monitor."""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "brain-os/plan-registry/sourcea-1000"
REG = PACK / "REGISTRY.json"
LOGS = ROOT / "REPO_EXECUTION_LOGS/sourcea"
QUAR = LOGS / "QUARANTINE_BATCH_YAML"
MATRIX_JSON = Path.home() / ".sina" / "PROGRAM_1000_STEP_MATRIX.json"
MATRIX_CSV = Path.home() / ".sina" / "audits" / "PROGRAM_1000_STEP_MATRIX_LIVE.csv"
REPO_CSV = LOGS / "PROGRAM_1000_STEP_MATRIX_LIVE.csv"
RECONCILE_LOG = Path.home() / ".sina" / "reconcile-1000-machine-pass-v1.jsonl"
QUEUE_HOME = Path.home() / ".sina" / "healthy-queue-30-active.json"
QUEUE_REPO = PACK / "prompts/healthy-queue-30-active.json"

sys.path.insert(0, str(ROOT / "scripts"))
from closeout_audit_lib_v1 import (  # noqa: E402
    HONEST_RECEIPT,
    load_closeouts,
    load_receipts,
    proof_verdict,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _md_status(path: Path) -> str:
    if not path.is_file():
        return ""
    head = path.read_text(encoding="utf-8")[:800]
    m = re.search(r"^status:\s*(\S+)", head, re.MULTILINE)
    return m.group(1) if m else ""


def _quarantined_sas() -> set[str]:
    out: set[str] = set()
    if not QUAR.is_dir():
        return out
    for p in QUAR.glob("*.yaml"):
        m = re.search(r"(sa-\d{4})", p.name)
        if m:
            out.add(m.group(1))
    return out


def _active_queue_sas() -> dict[str, dict]:
    qpath = QUEUE_HOME if QUEUE_HOME.is_file() else QUEUE_REPO
    if not qpath.is_file():
        return {}
    try:
        q = json.loads(qpath.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    out: dict[str, dict] = {}
    for i, item in enumerate(q.get("queue") or [], start=1):
        sa = str(item.get("sa_id") or "")
        if sa.startswith("sa-"):
            out[sa] = {"queue_pos": i, "queue_role": item.get("queue_role") or "?"}
    return out


def _reconcile_latest() -> dict[str, dict]:
    out: dict[str, dict] = {}
    if not RECONCILE_LOG.is_file():
        return out
    for line in RECONCILE_LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        sa = str(row.get("sa_id") or "")
        if sa.startswith("sa-"):
            out[sa] = {
                "machine_verify": "PASS",
                "machine_verify_at": row.get("at") or "",
                "machine_verify_tail": (row.get("evidence") or "")[-120:],
            }
    return out


def _validation(reg_st: str, proof: str, md_exists: bool, md_status: str, issues: list[str]) -> str:
    if issues:
        return "FAIL"
    if reg_st == "done" and proof in ("HONEST_RECEIPT", "RECEIPT_AND_BATCH_YAML"):
        return "PASS_DONE"
    if reg_st == "backlog":
        return "STRUCT_OK"
    return "PASS_DONE" if reg_st == "done" else "STRUCT_OK"


def _missing_gaps(
    *,
    reg_st: str,
    proof: str,
    quarantined: bool,
    in_queue: bool,
    machine: dict | None,
) -> str:
    if reg_st == "done":
        if proof == "HONEST_RECEIPT":
            return ""
        if proof == "RECEIPT_AND_BATCH_YAML":
            return "WEAK_BATCH_YAML"
        return "UNPROVEN_DONE"
    gaps: list[str] = []
    if quarantined:
        gaps.append("VALIDATE_FIRST")
    else:
        gaps.append("NOT_DONE")
    if in_queue:
        gaps.append("IN_QUEUE")
    if machine and machine.get("machine_verify") == "PASS":
        gaps.append("MACHINE_PASS_PENDING_CLOSE")
    return ",".join(gaps)


def build_matrix() -> dict:
    reg = json.loads(REG.read_text(encoding="utf-8"))
    plans = reg.get("plans") or []
    receipts = load_receipts()
    closeouts = load_closeouts()
    quarantined = _quarantined_sas()
    queue = _active_queue_sas()
    reconcile = _reconcile_latest()

    steps: list[dict] = []
    for pl in plans:
        sa = pl.get("id") or ""
        rel = pl.get("path") or ""
        md_path = PACK / rel if rel else Path()
        md_exists = md_path.is_file()
        md_status = _md_status(md_path) if md_exists else ""
        reg_st = pl.get("status") or "backlog"
        verify = str(pl.get("verify") or "")
        rec = receipts.get(sa)
        clo = closeouts.get(sa)
        proof = proof_verdict(sa, reg_st, rec, clo)

        issues: list[str] = []
        if not md_exists:
            issues.append("MISSING_RECIPE")
        elif "agent_tag: AGENT-AUTO-SOURCEA" not in md_path.read_text(encoding="utf-8")[:1200]:
            issues.append("MISSING_AGENT_TAG")
        if md_status and md_status != reg_st:
            issues.append(f"STATUS_DRIFT")
        if reg_st == "done" and proof not in ("HONEST_RECEIPT", "RECEIPT_AND_BATCH_YAML"):
            issues.append(f"UNPROVEN:{proof}")

        qinfo = queue.get(sa)
        mach = reconcile.get(sa)
        val = _validation(reg_st, proof, md_exists, md_status, issues)
        honest = proof in ("HONEST_RECEIPT", "RECEIPT_AND_BATCH_YAML")
        bucket = "done" if honest and reg_st == "done" else (
            "validate_first" if reg_st == "backlog" and sa in quarantined else (
                "never_touched" if reg_st == "backlog" else "backlog"
            )
        )

        steps.append(
            {
                "sa_id": sa,
                "phase": pl.get("phase") or "",
                "tier": pl.get("tier") or "",
                "title": (pl.get("title") or "")[:120],
                "registry_status": reg_st,
                "recipe": {
                    "ok": md_exists,
                    "path": rel,
                    "md_status": md_status,
                },
                "verify_recipe": verify,
                "validation": val,
                "validation_issues": issues,
                "proof_verdict": proof,
                "honest_proof": honest and reg_st == "done",
                "receipt": {
                    "has": bool(rec),
                    "status": (rec or {}).get("receipt_status", ""),
                    "at": (rec or {}).get("receipt_at", ""),
                    "path": (rec or {}).get("receipt_path", ""),
                },
                "closeout": {
                    "has_yaml": bool(clo),
                    "reporter": (clo or {}).get("closeout_reporter", ""),
                    "at": (clo or {}).get("closeout_reported_at", ""),
                    "evidence": (clo or {}).get("closeout_evidence", ""),
                },
                "quarantined_yaml": sa in quarantined,
                "bucket": bucket,
                "queue": qinfo or None,
                "machine_verify": mach.get("machine_verify") if mach else None,
                "machine_verify_at": (mach or {}).get("machine_verify_at", ""),
                "missing_gaps": _missing_gaps(
                    reg_st=reg_st,
                    proof=proof,
                    quarantined=sa in quarantined,
                    in_queue=bool(qinfo),
                    machine=mach,
                ),
                "worker_cycle": {
                    "check": bool(clo or rec or sa in quarantined),
                    "act": bool(clo and clo.get("closeout_reporter") in ("cursor-worker", "goal1_lane_broker")),
                    "verify": bool(rec and str(rec.get("receipt_status", "")).upper() in HONEST_RECEIPT),
                },
            }
        )

    steps.sort(key=lambda s: int(s["sa_id"].split("-")[1]))
    proof_counts = Counter(s["proof_verdict"] for s in steps)
    val_counts = Counter(s["validation"] for s in steps)
    bucket_counts = Counter(s["bucket"] for s in steps)
    honest_done = sum(1 for s in steps if s["honest_proof"])

    return {
        "schema": "program-1000-step-matrix-v1",
        "updated_at": _now(),
        "summary": {
            "total": len(steps),
            "honest_done": honest_done,
            "backlog": len(steps) - honest_done,
            "recipe_ok": sum(1 for s in steps if s["recipe"]["ok"]),
            "validation": dict(val_counts),
            "proof_verdict": dict(proof_counts),
            "buckets": dict(bucket_counts),
            "in_active_queue": len(queue),
            "quarantined": len(quarantined),
        },
        "steps": steps,
        "paths": {
            "matrix_json": str(MATRIX_JSON),
            "matrix_csv": str(MATRIX_CSV),
            "repo_csv": str(REPO_CSV),
        },
    }


def write_matrix(row: dict | None = None) -> dict:
    row = row or build_matrix()
    MATRIX_JSON.parent.mkdir(parents=True, exist_ok=True)
    MATRIX_JSON.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")

    fields = [
        "sa_id", "phase", "tier", "title", "registry_status", "bucket",
        "recipe_ok", "recipe_path", "verify_recipe", "validation", "proof_verdict",
        "honest_proof", "has_receipt", "receipt_status", "closeout_reporter",
        "quarantined_yaml", "machine_verify", "missing_gaps",
        "cycle_check", "cycle_act", "cycle_verify", "queue_pos", "queue_role",
    ]
    csv_rows = []
    for s in row["steps"]:
        csv_rows.append(
            {
                "sa_id": s["sa_id"],
                "phase": s["phase"],
                "tier": s["tier"],
                "title": s["title"],
                "registry_status": s["registry_status"],
                "bucket": s["bucket"],
                "recipe_ok": "yes" if s["recipe"]["ok"] else "no",
                "recipe_path": s["recipe"]["path"],
                "verify_recipe": s["verify_recipe"],
                "validation": s["validation"],
                "proof_verdict": s["proof_verdict"],
                "honest_proof": "yes" if s["honest_proof"] else "no",
                "has_receipt": "yes" if s["receipt"]["has"] else "no",
                "receipt_status": s["receipt"]["status"],
                "closeout_reporter": s["closeout"]["reporter"],
                "quarantined_yaml": "yes" if s["quarantined_yaml"] else "no",
                "machine_verify": s.get("machine_verify") or "",
                "missing_gaps": s["missing_gaps"],
                "cycle_check": "yes" if s["worker_cycle"]["check"] else "no",
                "cycle_act": "yes" if s["worker_cycle"]["act"] else "no",
                "cycle_verify": "yes" if s["worker_cycle"]["verify"] else "no",
                "queue_pos": (s.get("queue") or {}).get("queue_pos", ""),
                "queue_role": (s.get("queue") or {}).get("queue_role", ""),
            }
        )
    MATRIX_CSV.parent.mkdir(parents=True, exist_ok=True)
    with MATRIX_CSV.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(csv_rows)
    REPO_CSV.write_text(MATRIX_CSV.read_text(encoding="utf-8"), encoding="utf-8")
    return row


def filter_steps(row: dict, *, bucket: str = "", phase: str = "", q: str = "", limit: int = 50, offset: int = 0) -> dict:
    steps = row["steps"]
    if bucket == "FAIL":
        steps = [s for s in steps if s["validation"] == "FAIL"]
    elif bucket == "done":
        steps = [s for s in steps if s.get("honest_proof")]
    elif bucket:
        steps = [s for s in steps if s["bucket"] == bucket or s["proof_verdict"] == bucket]
    if phase:
        steps = [s for s in steps if s["phase"] == phase]
    if q:
        ql = q.lower()
        steps = [s for s in steps if ql in s["sa_id"] or ql in (s["title"] or "").lower()]
    total = len(steps)
    page = steps[offset : offset + limit]
    return {
        "ok": True,
        "updated_at": row["updated_at"],
        "summary": row["summary"],
        "filter": {"bucket": bucket, "phase": phase, "q": q, "offset": offset, "limit": limit},
        "total_filtered": total,
        "steps": page,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    p.add_argument("--write", action="store_true", help="Write matrix JSON + CSV")
    p.add_argument("--bucket", default="")
    p.add_argument("--phase", default="")
    p.add_argument("--q", default="")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--offset", type=int, default=0)
    args = p.parse_args()

    if args.write or not (args.bucket or args.phase or args.q):
        row = write_matrix()
    else:
        if MATRIX_JSON.is_file():
            row = json.loads(MATRIX_JSON.read_text(encoding="utf-8"))
        else:
            row = write_matrix()

    if args.bucket or args.phase or args.q or args.offset or args.limit != 50:
        out = filter_steps(row, bucket=args.bucket, phase=args.phase, q=args.q, limit=args.limit, offset=args.offset)
    elif args.write:
        out = {"ok": True, "updated_at": row["updated_at"], "summary": row["summary"], "paths": row["paths"]}
    else:
        out = row

    if args.json or args.write:
        print(json.dumps(out, indent=2))
    else:
        s = row["summary"]
        print(f"MATRIX: {s['honest_done']}/{s['total']} honest · recipe {s['recipe_ok']} · buckets {s['buckets']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
