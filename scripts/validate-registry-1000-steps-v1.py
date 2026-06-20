#!/usr/bin/env python3
"""Validate all 1000 sourcea-1000 REGISTRY steps — structure + proof audit.

Outputs:
  ~/.sina/audits/REGISTRY_ALL_1000_VALIDATION_<date>.csv
  REPO_EXECUTION_LOGS/sourcea/REGISTRY_ALL_1000_VALIDATION_<date>.csv
  JSON summary on stdout with --json
"""
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
RECEIPTS = ROOT / "receipts"
AUDIT_DIR = Path.home() / ".sina/audits"

HONEST_RECEIPT = frozenset({"DONE", "PASS", "VERIFIED", "CHECK_PASSED"})


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_receipts() -> dict[str, dict]:
    out: dict[str, dict] = {}
    if not RECEIPTS.is_dir():
        return out
    for p in RECEIPTS.glob("sa-*-receipt.json"):
        m = re.match(r"(sa-\d+)", p.name)
        if not m:
            continue
        sa = m.group(1)
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            d = {}
        out[sa] = {
            "receipt_status": str(d.get("status") or ""),
            "receipt_at": str(d.get("at") or d.get("completed_at") or ""),
            "receipt_path": str(p),
        }
    return out


def _load_closeouts() -> dict[str, dict]:
    out: dict[str, dict] = {}
    if not LOGS.is_dir():
        return out
    for p in sorted(LOGS.glob("*.yaml")):
        if "plan-with-no-asf" not in p.name:
            continue
        m = re.search(r"(sa-\d+)", p.name)
        if not m:
            continue
        sa = m.group(1)
        text = p.read_text(encoding="utf-8")
        rep = re.search(r"reporter: (\S+)", text)
        sn = re.search(r"output_snippet: (.+)", text)
        at = re.search(r"reported_at: '([^']+)'", text)
        out[sa] = {
            "closeout_reporter": rep.group(1) if rep else "",
            "closeout_evidence": (sn.group(1).strip() if sn else "")[:200],
            "closeout_reported_at": at.group(1) if at else "",
            "closeout_yaml": p.name,
        }
    return out


def _md_front_status(path: Path) -> str:
    if not path.is_file():
        return ""
    head = path.read_text(encoding="utf-8")[:800]
    m = re.search(r"^status:\s*(\S+)", head, re.MULTILINE)
    return m.group(1) if m else ""


def _proof_verdict(sa: str, registry_status: str, rec: dict | None, clo: dict | None) -> str:
    if registry_status != "done":
        return "BACKLOG"
    if rec and rec.get("receipt_status", "").upper() in HONEST_RECEIPT:
        if clo and clo.get("closeout_reporter") == "cursor-worker-batch":
            return "RECEIPT_AND_BATCH_YAML"
        return "HONEST_RECEIPT"
    if clo:
        rep = clo.get("closeout_reporter") or "unknown"
        if rep == "cursor-worker-batch":
            return "BATCH_CLOSEOUT_ONLY"
        if rep == "cursor-worker":
            return "WORKER_YAML_ONLY"
        if rep == "cursor-maintainer":
            return "MAINTAINER_YAML_ONLY"
        return "YAML_ONLY_OTHER"
    return "DONE_NO_PROOF_ON_DISK"


def _step_validation(
    *,
    pl: dict,
    md_path: Path,
    md_status: str,
    proof: str,
) -> tuple[str, list[str]]:
    issues: list[str] = []
    reg_st = pl.get("status") or "backlog"

    if not md_path.is_file():
        issues.append("MISSING_PROMPT_MD")
    elif "agent_tag: AGENT-AUTO-SOURCEA" not in md_path.read_text(encoding="utf-8")[:1200]:
        issues.append("MISSING_AGENT_TAG")

    if md_status and md_status != reg_st:
        issues.append(f"STATUS_DRIFT registry={reg_st} md={md_status}")

    if reg_st == "done":
        if proof in ("BATCH_CLOSEOUT_ONLY", "DONE_NO_PROOF_ON_DISK"):
            issues.append(f"UNPROVEN_DONE:{proof}")
        elif proof == "BACKLOG":
            issues.append("DONE_WITHOUT_PROOF")

    if issues:
        return "FAIL", issues
    if reg_st == "done" and proof in ("HONEST_RECEIPT", "RECEIPT_AND_BATCH_YAML", "WORKER_YAML_ONLY", "MAINTAINER_YAML_ONLY", "YAML_ONLY_OTHER"):
        return "PASS_DONE", issues
    return "STRUCT_OK", issues


def validate_all() -> dict:
    reg = json.loads(REG.read_text(encoding="utf-8"))
    plans = reg.get("plans") or []
    if len(plans) != 1000:
        return {"ok": False, "error": f"expected 1000 plans got {len(plans)}"}

    receipts = _load_receipts()
    closeouts = _load_closeouts()
    rows: list[dict] = []

    for pl in plans:
        sa = pl.get("id") or ""
        rel = pl.get("path") or ""
        md_path = PACK / rel if rel else Path()
        md_status = _md_front_status(md_path)
        rec = receipts.get(sa)
        clo = closeouts.get(sa)
        proof = _proof_verdict(sa, pl.get("status") or "backlog", rec, clo)
        val_status, issues = _step_validation(pl=pl, md_path=md_path, md_status=md_status, proof=proof)

        rows.append(
            {
                "sa_id": sa,
                "phase": pl.get("phase") or "",
                "tier": pl.get("tier") or "",
                "registry_status": pl.get("status") or "",
                "md_status": md_status,
                "md_exists": "yes" if md_path.is_file() else "no",
                "prompt_path": rel,
                "proof_verdict": proof,
                "validation_status": val_status,
                "issues": "; ".join(issues),
                "has_receipt": "yes" if rec else "no",
                "receipt_status": (rec or {}).get("receipt_status", ""),
                "has_closeout_yaml": "yes" if clo else "no",
                "closeout_reporter": (clo or {}).get("closeout_reporter", ""),
                "closeout_reported_at": (clo or {}).get("closeout_reported_at", ""),
                "closeout_evidence": (clo or {}).get("closeout_evidence", ""),
            }
        )

    rows.sort(key=lambda r: int(r["sa_id"].split("-")[1]))

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    fields = list(rows[0].keys()) if rows else []
    paths = [
        AUDIT_DIR / f"REGISTRY_ALL_1000_VALIDATION_{stamp}.csv",
        LOGS / f"REGISTRY_ALL_1000_VALIDATION_{stamp}.csv",
    ]
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    for out in paths:
        with out.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

    val_counts = Counter(r["validation_status"] for r in rows)
    proof_counts = Counter(r["proof_verdict"] for r in rows)
    issue_counts = Counter()
    for r in rows:
        for iss in filter(None, (r.get("issues") or "").split("; ")):
            issue_counts[iss.split(":")[0]] += 1

    fail_rows = [r for r in rows if r["validation_status"] == "FAIL"]
    unproven_done = [r for r in rows if "UNPROVEN_DONE" in (r.get("issues") or "")]

    summary = {
        "ok": len(fail_rows) == 0,
        "schema": "validate-registry-1000-steps-v1",
        "at": _now(),
        "total": 1000,
        "registry_locked": bool(reg.get("locked")),
        "done": sum(1 for r in rows if r["registry_status"] == "done"),
        "backlog": sum(1 for r in rows if r["registry_status"] == "backlog"),
        "validation_status": dict(val_counts),
        "proof_verdict": dict(proof_counts),
        "top_issues": dict(issue_counts.most_common(12)),
        "structural_fail": len([r for r in fail_rows if "MISSING" in r.get("issues", "")]),
        "unproven_done": len(unproven_done),
        "honest_receipt_done": proof_counts.get("HONEST_RECEIPT", 0),
        "batch_only_done": proof_counts.get("BATCH_CLOSEOUT_ONLY", 0),
        "csv_paths": [str(p) for p in paths],
        "verdict": (
            "PASS"
            if len(fail_rows) == 0 and issue_counts.get("UNPROVEN_DONE", 0) == 0
            else "FAIL_UNPROVEN_DONE"
            if len([r for r in fail_rows if "MISSING" not in r.get("issues", "")]) == 0
            else "FAIL_STRUCTURAL"
        ),
    }
    summary["ok"] = summary["verdict"] == "PASS"
    return summary


def main() -> int:
    p = argparse.ArgumentParser(description="Validate all 1000 sourcea-1000 REGISTRY steps")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    summary = validate_all()
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"validate-registry-1000-steps-v1 · verdict={summary.get('verdict')}")
        print(f"  done={summary.get('done')} backlog={summary.get('backlog')}")
        print(f"  honest_receipt={summary.get('honest_receipt_done')} batch_only={summary.get('batch_only_done')} unproven_done={summary.get('unproven_done')}")
        print(f"  validation_status={summary.get('validation_status')}")
        print(f"  top_issues={summary.get('top_issues')}")
        for path in summary.get("csv_paths") or []:
            print(f"  csv: {path}")
    return 0 if summary.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
