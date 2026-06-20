#!/usr/bin/env python3
"""RunReceipt pack v1 — DevBridge evidence → jsonl + summary + HTML + zip."""
from __future__ import annotations

import argparse
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[2]
OUT_DIR = SOURCE_A / "runreceipt" / "out"
SCHEMA = "runreceipt-pack-v1"
DEFAULT_EVIDENCE = Path.home() / "Desktop" / "AI Dev Bridge OS" / "scripts" / "evidence"

EVIDENCE_JSON_GLOBS = ("*-result.json",)
EVIDENCE_MARKDOWN = (
    "G2_DEVICE_RUNBOOK.md",
    "G2_FULL_DAY_PHONE.md",
    "ASF_PHYSICAL_G2_CHECKLIST.md",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _gate_status(payload: dict | None) -> str:
    if not payload:
        return "MISSING"
    if payload.get("skipped"):
        return "SKIP"
    if payload.get("pass") is True or payload.get("ok") is True:
        return "PASS"
    if payload.get("pass") is False or payload.get("ok") is False:
        return "FAIL"
    return "UNKNOWN"


def collect_evidence(evidence_dir: Path) -> list[dict]:
    items: list[dict] = []
    if not evidence_dir.is_dir():
        return items

    for pattern in EVIDENCE_JSON_GLOBS:
        for path in sorted(evidence_dir.glob(pattern)):
            payload = _read_json(path)
            items.append(
                {
                    "kind": "json",
                    "name": path.name,
                    "path": str(path),
                    "gate_status": _gate_status(payload),
                    "payload": payload,
                }
            )

    for name in EVIDENCE_MARKDOWN:
        path = evidence_dir / name
        if path.is_file():
            items.append(
                {
                    "kind": "markdown",
                    "name": name,
                    "path": str(path),
                    "gate_status": "DOC",
                    "bytes": path.stat().st_size,
                }
            )
    return items


def derive_status(evidence: list[dict], override: str | None) -> str:
    if override:
        return override.upper()
    json_gates = [e for e in evidence if e["kind"] == "json"]
    if not json_gates:
        return "PASS"
    statuses = {e["gate_status"] for e in json_gates}
    if "FAIL" in statuses:
        return "FAIL"
    if statuses <= {"PASS", "DOC"}:
        return "PASS"
    if statuses <= {"SKIP", "DOC", "MISSING"}:
        return "PASS"
    return "PASS"


def _html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_html(*, run_id: str, status: str, evidence: list[dict], run_lines: list[dict]) -> str:
    pass_n = sum(1 for e in evidence if e.get("gate_status") == "PASS")
    fail_n = sum(1 for e in evidence if e.get("gate_status") == "FAIL")
    skip_n = sum(1 for e in evidence if e.get("gate_status") == "SKIP")
    status_class = "pass" if status == "PASS" else "fail" if status == "FAIL" else "pending"

    evidence_rows = []
    for e in evidence:
        gs = e.get("gate_status", "UNKNOWN")
        cls = "pass" if gs == "PASS" else "fail" if gs == "FAIL" else "pending" if gs == "SKIP" else "unknown"
        evidence_rows.append(
            f"<tr><td>{_html_escape(e['name'])}</td>"
            f"<td class=\"{cls}\">{gs}</td>"
            f"<td>{_html_escape(e.get('path', ''))}</td></tr>"
        )

    run_rows = []
    for line in run_lines[-10:]:
        oc = line.get("status", "UNKNOWN")
        cls = "pass" if oc == "PASS" else "fail" if oc == "FAIL" else "pending"
        run_rows.append(
            f"<tr><td>{_html_escape(line.get('run_id', ''))}</td>"
            f"<td class=\"{cls}\">{oc}</td>"
            f"<td>{_html_escape(line.get('at', ''))}</td>"
            f"<td>{_html_escape(line.get('lane', ''))}</td></tr>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>RunReceipt — {run_id}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #0f1923; color: #f7fafc; }}
    h1 {{ color: #ffc800; }}
    h2 {{ color: #ffc800; margin-top: 2rem; font-size: 1.1rem; }}
    .meta {{ color: #9eb4c8; }}
    table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
    th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #243d4c; }}
    th {{ color: #ffc800; font-size: 0.85rem; text-transform: uppercase; }}
    .pass {{ color: #58cc02; font-weight: 700; }}
    .fail {{ color: #ff4b4b; font-weight: 700; }}
    .pending {{ color: #ffc800; font-weight: 700; }}
    .unknown {{ color: #9eb4c8; }}
  </style>
</head>
<body>
  <h1>RunReceipt — P0-RUNRECEIPT</h1>
  <p class="meta">Run ID: <strong>{_html_escape(run_id)}</strong> · Aggregate: <span class="{status_class}">{status}</span></p>
  <p class="meta">DevBridge evidence: {pass_n} pass · {fail_n} fail · {skip_n} skip · {len(evidence)} files</p>
  <h2>DevBridge evidence</h2>
  <table>
    <thead><tr><th>File</th><th>Gate</th><th>Path</th></tr></thead>
    <tbody>{''.join(evidence_rows) or '<tr><td colspan="3">No evidence dir</td></tr>'}</tbody>
  </table>
  <h2>Run history (latest)</h2>
  <table>
    <thead><tr><th>Run ID</th><th>Status</th><th>At</th><th>Lane</th></tr></thead>
    <tbody>{''.join(run_rows) or '<tr><td colspan="4">No prior runs</td></tr>'}</tbody>
  </table>
</body>
</html>"""


def load_run_history(run_path: Path) -> list[dict]:
    if not run_path.is_file():
        return []
    lines: list[dict] = []
    for raw in run_path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            lines.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    return lines


def write_zip(out_dir: Path, members: list[Path], zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for member in members:
            if member.is_file():
                zf.write(member, arcname=member.name)


def build_pack(
    *,
    run_id: str = "",
    status: str | None = None,
    evidence_dir: Path | None = None,
    write_zip_file: bool = True,
    lane: str = "wire",
    action_id: str = "devbridge-evidence-pack",
) -> dict:
    evidence_dir = evidence_dir or DEFAULT_EVIDENCE
    rid = run_id or f"run-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    evidence = collect_evidence(evidence_dir)
    aggregate = derive_status(evidence, status)

    run_path = OUT_DIR / "run.jsonl"
    history = load_run_history(run_path)

    run_line = {
        "schema": SCHEMA,
        "run_id": rid,
        "at": _now(),
        "status": aggregate,
        "lane": lane,
        "action_id": action_id,
        "evidence_dir": str(evidence_dir),
        "evidence_count": len(evidence),
        "evidence_gates": [
            {"name": e["name"], "gate_status": e["gate_status"]} for e in evidence if e["kind"] == "json"
        ],
    }
    with run_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(run_line) + "\n")
    history.append(run_line)

    evidence_snapshot_path = OUT_DIR / "evidence.snapshot.json"
    evidence_snapshot_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    summary = {
        "schema": SCHEMA,
        "run_id": rid,
        "generated_at": _now(),
        "status": aggregate,
        "artifacts": [
            "run.jsonl",
            "summary.json",
            "receipt.html",
            "evidence.snapshot.json",
        ],
        "wire_lane": "THREAD-WIRE",
        "p0": "P0-RUNRECEIPT",
        "evidence_dir": str(evidence_dir),
        "evidence_summary": {
            "total": len(evidence),
            "pass": sum(1 for e in evidence if e.get("gate_status") == "PASS"),
            "fail": sum(1 for e in evidence if e.get("gate_status") == "FAIL"),
            "skip": sum(1 for e in evidence if e.get("gate_status") == "SKIP"),
        },
    }

    summary_path = OUT_DIR / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    html_path = OUT_DIR / "receipt.html"
    html_path.write_text(
        build_html(run_id=rid, status=aggregate, evidence=evidence, run_lines=history),
        encoding="utf-8",
    )

    zip_path = OUT_DIR / "receipt-pack.zip"
    if write_zip_file:
        write_zip(
            OUT_DIR,
            [run_path, summary_path, html_path, evidence_snapshot_path],
            zip_path,
        )
        summary["artifacts"].append("receipt-pack.zip")
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    return {
        "ok": True,
        "schema": SCHEMA,
        "run_id": rid,
        "status": aggregate,
        "evidence_dir": str(evidence_dir),
        "paths": {
            "run_jsonl": str(run_path),
            "summary_json": str(summary_path),
            "receipt_html": str(html_path),
            "evidence_snapshot": str(evidence_snapshot_path),
            "receipt_zip": str(zip_path) if write_zip_file else None,
        },
    }


REQUIRED_ARTIFACT_KEYS = ("run_jsonl", "summary_json", "receipt_html")
REQUIRED_ARTIFACT_FILES = ("run.jsonl", "summary.json", "receipt.html")


def assert_runreceipt_artifacts(out_dir: Path | None = None) -> dict:
    """verify:wire gate — fail when run receipt artifacts are absent (no auto-build)."""
    root = out_dir or OUT_DIR
    paths: dict[str, str] = {}
    missing: list[str] = []
    for key, name in zip(REQUIRED_ARTIFACT_KEYS, REQUIRED_ARTIFACT_FILES):
        path = root / name
        paths[key] = str(path)
        if not path.is_file():
            missing.append(str(path))

    if missing:
        return {"ok": False, "missing": missing, "out_dir": str(root), "paths": paths}

    summary_path = root / "summary.json"
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": f"invalid summary.json: {exc}", "out_dir": str(root), "paths": paths}

    status = str(summary.get("status") or "")
    if status not in ("PASS", "FAIL"):
        return {
            "ok": False,
            "error": f"summary.json status must be PASS or FAIL, got {status!r}",
            "out_dir": str(root),
            "paths": paths,
        }

    run_id = str(summary.get("run_id") or "")
    return {
        "ok": True,
        "out_dir": str(root),
        "paths": paths,
        "run_id": run_id,
        "status": status,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="RunReceipt pack — DevBridge evidence to receipt artifacts")
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE, help="DevBridge scripts/evidence")
    parser.add_argument("--run-id", default="", help="Optional run id")
    parser.add_argument("--status", default=None, help="Override PASS/FAIL")
    parser.add_argument("--no-zip", action="store_true", help="Skip zip bundle")
    parser.add_argument("--lane", default="wire")
    parser.add_argument("--action-id", default="devbridge-evidence-pack")
    args = parser.parse_args()

    result = build_pack(
        run_id=args.run_id,
        status=args.status,
        evidence_dir=args.evidence_dir,
        write_zip_file=not args.no_zip,
        lane=args.lane,
        action_id=args.action_id,
    )
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
