#!/usr/bin/env python3
"""Enforce RESEARCH_INTAKE_AND_SAVE_LOCK_LOCKED_v1 — mirror, meta, index, verify."""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml

SOURCEA = Path.home() / "Desktop/SourceA"
RESEARCH = SOURCEA / "RESEARCH"
GOV = RESEARCH / "_GOVERNANCE"
SUBJECTS_FILE = GOV / "SUBJECTS_REGISTRY.yaml"
WORKERS_FILE = GOV / "WORKERS_REGISTRY.yaml"
INDEX_FILE = RESEARCH / "INDEX.yaml"
SYNC_SCRIPT = SOURCEA / "scripts/research_root_sync.py"

SUPERSEDED_PREFIXES = ("RA-MKT-", "GOVGS-", "TF-COMM", "NF-COMM")


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _subjects() -> dict[str, Any]:
    return _load_yaml(SUBJECTS_FILE).get("subjects", {})


def _workers() -> dict[str, Any]:
    return _load_yaml(WORKERS_FILE).get("workers", {})


def _infer_date(trace_id: str, path: Path) -> str:
    for s in (trace_id, str(path)):
        m = re.search(r"20\d{2}-0[1-9]-[0-3]\d", s)
        if m:
            return m.group(0)
        m = re.search(r"20\d{6}", s)
        if m:
            d = m.group(0)
            return f"{d[:4]}-{d[4:6]}-{d[6:8]}"
    return str(date.today())


def _reject_superseded(trace_id: str) -> str | None:
    for p in SUPERSEDED_PREFIXES:
        if trace_id.upper().startswith(p.upper()):
            return f"superseded tag prefix: {p}"
    return None


def _mirror_dir(day: str, worker: str, subject: str, trace_id: str) -> Path:
    return RESEARCH / "by_date" / day / worker / subject / trace_id


def cmd_save(args: argparse.Namespace) -> int:
    src = Path(args.path).expanduser().resolve()
    if not src.is_file():
        print(f"FAIL: source not found: {src}")
        return 1

    worker = args.worker
    subject = args.subject
    trace_id = args.trace_id

    if worker not in _workers():
        print(f"FAIL: unknown worker_id: {worker}")
        return 1
    if subject not in _subjects():
        print(f"FAIL: unknown subject: {subject}")
        return 1
    if err := _reject_superseded(trace_id):
        print(f"FAIL: {err}")
        return 1

    day = args.date or _infer_date(trace_id, src)
    dest_dir = _mirror_dir(day, worker, subject, trace_id)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / src.name
    shutil.copy2(src, dest_file)

    subj = _subjects()[subject]
    meta = {
        "trace_id": trace_id,
        "worker_id": worker,
        "subject": subject,
        "subject_label": subj.get("label", subject),
        "thread": subj.get("thread", "THREAD-ECOSYSTEM"),
        "date": day,
        "source_path": str(src),
        "archive_path": str(dest_file.relative_to(RESEARCH)),
        "execution_authority": False,
        "enforcer": "research_save_enforcer.py",
        "law": "RESEARCH_INTAKE_AND_SAVE_LOCK_LOCKED_v1.md",
    }
    meta_path = dest_dir / "_META.yaml"
    meta_path.write_text(yaml.dump(meta, default_flow_style=False, sort_keys=False), encoding="utf-8")

    _append_index(meta)
    print(f"PASS: saved → {dest_file.relative_to(SOURCEA)}")

    if args.register:
        if SYNC_SCRIPT.is_file():
            bucket = args.bucket or subject
            rc = subprocess.call(
                [sys.executable, str(SYNC_SCRIPT), "register", "--path", str(src),
                 "--producer", worker, "--bucket", bucket],
            )
            if rc != 0:
                print("WARN: research_root_sync register returned non-zero")
        else:
            print("WARN: research_root_sync.py not found — skip register")

    return cmd_verify(argparse.Namespace(trace_id=trace_id, path=str(dest_dir)))


def _append_index(meta: dict[str, Any]) -> None:
    index = _load_yaml(INDEX_FILE)
    index.setdefault("schema_version", 1)
    index["root"] = str(RESEARCH)
    index["updated"] = str(date.today())
    arts: list[dict[str, Any]] = index.setdefault("artifacts", [])
    tid = meta["trace_id"]
    arts = [a for a in arts if not (a.get("trace_id") == tid and a.get("archive_path") == meta["archive_path"])]
    arts.append({
        "trace_id": meta["trace_id"],
        "worker_id": meta["worker_id"],
        "subject": meta["subject"],
        "date": meta["date"],
        "archive_path": meta["archive_path"],
        "source_path": meta["source_path"],
    })
    index["artifacts"] = sorted(arts, key=lambda x: (x.get("date", ""), x.get("worker_id", ""), x.get("trace_id", "")))
    index["artifact_count"] = len(index["artifacts"])
    INDEX_FILE.write_text(yaml.dump(index, default_flow_style=False, sort_keys=False), encoding="utf-8")


def _validate_folder(folder: Path) -> list[str]:
    errors: list[str] = []
    if not folder.is_dir():
        return [f"missing folder: {folder}"]

    meta_path = folder / "_META.yaml"
    if not meta_path.is_file():
        errors.append("missing _META.yaml")
        return errors

    meta = _load_yaml(meta_path)
    required = ("trace_id", "worker_id", "subject", "date", "archive_path", "source_path")
    for k in required:
        if not meta.get(k):
            errors.append(f"_META.yaml missing field: {k}")

    tid = str(meta.get("trace_id", ""))
    if err := _reject_superseded(tid):
        errors.append(err)

    artifacts = [p for p in folder.iterdir() if p.name != "_META.yaml" and p.is_file()]
    if not artifacts:
        errors.append("no artifact file beside _META.yaml")

    return errors


def cmd_verify(args: argparse.Namespace) -> int:
    if args.path:
        folder = Path(args.path).expanduser().resolve()
    elif args.trace_id:
        matches = list(RESEARCH.glob(f"by_date/*/*/*/{args.trace_id}"))
        if not matches:
            print(f"FAIL: no folder for trace_id: {args.trace_id}")
            return 1
        folder = matches[0]
    else:
        print("FAIL: provide --trace-id or --path")
        return 1

    errors = _validate_folder(folder)
    if errors:
        print(f"FAIL: {folder.relative_to(SOURCEA) if folder.is_relative_to(SOURCEA) else folder}")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"PASS: verify {folder.relative_to(SOURCEA)}")
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    failures = 0
    for meta_path in sorted(RESEARCH.glob("by_date/*/*/*/*/_META.yaml")):
        folder = meta_path.parent
        errors = _validate_folder(folder)
        if errors:
            failures += 1
            print(f"FAIL: {folder.relative_to(RESEARCH)}")
            for e in errors:
                print(f"  - {e}")
    if failures:
        print(f"\nAUDIT: {failures} folder(s) FAILED")
        return 1
    count = len(list(RESEARCH.glob("by_date/*/*/*/*/_META.yaml")))
    print(f"AUDIT: PASS — {count} artifact folder(s)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="RESEARCH save enforcer")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_save = sub.add_parser("save", help="Mirror vault file into RESEARCH + meta + index")
    p_save.add_argument("--path", required=True)
    p_save.add_argument("--worker", required=True)
    p_save.add_argument("--subject", required=True)
    p_save.add_argument("--trace-id", required=True)
    p_save.add_argument("--date", default=None)
    p_save.add_argument("--register", action="store_true", help="Also call research_root_sync register")
    p_save.add_argument("--bucket", default=None)
    p_save.set_defaults(func=cmd_save)

    p_verify = sub.add_parser("verify", help="Verify one trace folder")
    p_verify.add_argument("--trace-id", default=None)
    p_verify.add_argument("--path", default=None)
    p_verify.set_defaults(func=cmd_verify)

    p_audit = sub.add_parser("audit", help="Verify all by_date folders")
    p_audit.set_defaults(func=cmd_audit)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
