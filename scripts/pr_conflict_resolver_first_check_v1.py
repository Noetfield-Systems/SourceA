#!/usr/bin/env python3
"""PR conflict resolver FIRST CHECK — mandatory before resolving governance merge conflicts.

Law: brain-os/law/enforcement/PR_CONFLICT_RESOLVER_MANDATORY_LOCKED_v1.md
SSOT: data/pr-conflict-resolver-mandatory-v1.json
Wire receipt: ~/.sina/pr-conflict-resolver-first-check-receipt-v1.json
Ack receipt: ~/.sina/pr-conflict-resolver-ack-v1.json
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
SINA = Path.home() / ".sina"
SSOT = ROOT / "data/pr-conflict-resolver-mandatory-v1.json"
WIRE_RECEIPT = SINA / "pr-conflict-resolver-first-check-receipt-v1.json"
ACK_RECEIPT = SINA / "pr-conflict-resolver-ack-v1.json"
SURFACES = SINA / "agent-live-surfaces-v1.json"

ACK_TTL_HOURS = 12
FOUNDER_BYPASS = re.compile(
    r"(PR\s*CONFLICT|CONFLICT\s*RESOLVER|EDIT\s*ALLOWED|SAVE\s*AND\s*LOCK|ASF:)",
    re.I,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def _parse_ts(raw: str) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def _fresh_enough(raw: str, *, hours: int = ACK_TTL_HOURS) -> bool:
    ts = _parse_ts(raw)
    if not ts:
        return False
    age = datetime.now(timezone.utc) - ts
    return age.total_seconds() < hours * 3600


def load_ssot() -> dict:
    return _read(SSOT)


def _rel_path(path: str) -> str:
    p = Path(path.replace("~/", str(Path.home()) + "/"))
    if not p.is_absolute():
        p = (ROOT / p).resolve()
    else:
        p = p.resolve()
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def is_governance_sensitive(path: str, ssot: dict | None = None) -> bool:
    ssot = ssot or load_ssot()
    rel = _rel_path(path).replace("\\", "/")
    for pat in ssot.get("governance_sensitive_globs") or []:
        if fnmatch.fnmatch(rel, pat):
            return True
    return False


def has_conflict_markers(path: str) -> bool:
    p = Path(path.replace("~/", str(Path.home()) + "/"))
    if not p.is_absolute():
        p = (ROOT / p).resolve()
    if not p.is_file():
        return False
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return "<<<<<<<" in text and ">>>>>>>" in text


def merge_in_progress() -> bool:
    git_dir = ROOT / ".git"
    return (git_dir / "MERGE_HEAD").is_file()


def _run_sg_verifier() -> tuple[bool, str]:
    ssot = load_ssot()
    sg_root = Path(str(ssot.get("sg_ssot_root") or "").replace("~/", str(Path.home()) + "/"))
    verifier = sg_root / "scripts/verify_pr_conflict_skill_v1.py"
    if not verifier.is_file():
        return False, "missing_sg_verifier"
    try:
        proc = subprocess.run(
            [sys.executable, str(verifier), "--mac-desktop", "--json"],
            cwd=str(sg_root),
            capture_output=True,
            text=True,
            timeout=60,
        )
        tail = (proc.stdout or proc.stderr or "").strip()[-500:]
        return proc.returncode == 0, tail
    except Exception as exc:
        return False, str(exc)


def wire() -> dict:
    ssot = load_ssot()
    val_ok, val_tail = _run_sg_verifier()
    line = (
        "PR-CONFLICT-FIRST-CHECK · skill=pr-conflict-resolver · "
        f"sg_lock={'PASS' if val_ok else 'FAIL'} · eval_app=~/Desktop/PR-Conflict-Resolver-Report.app"
    )
    receipt = {
        "schema": "pr-conflict-resolver-first-check-receipt-v1",
        "saved_at": _now(),
        "ok": val_ok,
        "wire_ok": val_ok,
        "line": line,
        "law": ssot.get("sourcea_law"),
        "skill": ssot.get("canonical_skill"),
        "desktop_app": ssot.get("desktop_app"),
        "validator_tail": val_tail,
        "ack_required": True,
        "first_check_cmd": "python3 scripts/pr_conflict_resolver_first_check_v1.py --ack --json",
        "skill_cmd": "Read skills/pr-conflict-resolver/SKILL.md (SG SSOT) before any governance conflict resolve",
    }
    _write(WIRE_RECEIPT, receipt)
    if SURFACES.is_file():
        surf = _read(SURFACES)
        surf["pr_conflict_resolver_first_check_line"] = line
        surf["pr_conflict_resolver_first_check"] = {
            "id": "pr_conflict_resolver_first_check",
            "ok": val_ok,
            "wire_ok": val_ok,
            "law": receipt["law"],
            "ack_required": True,
        }
        _write(SURFACES, surf)
    return receipt


def acknowledge() -> dict:
    ssot = load_ssot()
    sg_skill = Path(str(ssot.get("sg_ssot_root") or "").replace("~/", str(Path.home()) + "/")) / str(
        ssot.get("canonical_skill") or ""
    )
    skill_ok = sg_skill.is_file()
    ack = {
        "schema": "pr-conflict-resolver-ack-v1",
        "saved_at": _now(),
        "ok": skill_ok,
        "skill_path": str(sg_skill),
        "skill_read_required": True,
        "classification_table": [
            "receipts → append-only",
            "data/*_registry_v1.json → structural JSON merge",
            "ssot/*LOCKED* → escalate founder",
            "generated → regenerate",
            "workflows/code → normal merge + validators",
        ],
        "stop_triggers": [
            "same task_cell different owners",
            "LOCKED doc conflict",
            "merge-ready without resolution receipt",
        ],
    }
    _write(ACK_RECEIPT, ack)
    line = (
        "PR-CONFLICT-ACK · skill loaded · L1 stop on duplicate ownership · "
        "receipt required before merge-ready"
    )
    return {"ok": skill_ok, "line": line, "ack": ack, "acks_path": str(ACK_RECEIPT)}


def check_write(*, path: str, explicit_order: str = "") -> dict:
    ssot = load_ssot()
    rel = _rel_path(path)
    sensitive = is_governance_sensitive(path, ssot)
    markers = has_conflict_markers(path)
    merging = merge_in_progress()

    if not sensitive and not markers and not merging:
        return {"ok": True, "skipped": True, "reason": "not_governance_conflict_context", "path": rel}

    if explicit_order and FOUNDER_BYPASS.search(explicit_order):
        return {
            "ok": True,
            "path": rel,
            "reason": "founder_explicit_order",
            "sensitive": sensitive,
            "markers": markers,
            "merge_in_progress": merging,
        }

    wire_row = _read(WIRE_RECEIPT)
    ack_row = _read(ACK_RECEIPT)
    wire_ok = bool(wire_row.get("wire_ok"))
    ack_fresh = _fresh_enough(str(ack_row.get("saved_at") or ""))

    if markers and not ack_fresh:
        return {
            "ok": False,
            "path": rel,
            "blockers": ["PR_CONFLICT_MARKERS_PRESENT", "PR_CONFLICT_ACK_REQUIRED"],
            "law": ssot.get("sourcea_law"),
            "message": (
                "PR CONFLICT FIRST CHECK required — file still has git conflict markers. "
                "Read SG skills/pr-conflict-resolver/SKILL.md · classify file · do not blind-pick. "
                "Run: python3 scripts/pr_conflict_resolver_first_check_v1.py --ack --json"
            ),
            "first_check_cmd": "python3 scripts/pr_conflict_resolver_first_check_v1.py --ack --json",
        }

    if sensitive and merging and not ack_fresh:
        return {
            "ok": False,
            "path": rel,
            "blockers": ["PR_CONFLICT_MERGE_ACTIVE", "PR_CONFLICT_ACK_REQUIRED"],
            "law": ssot.get("sourcea_law"),
            "message": (
                "Merge in progress on governance-sensitive path — ack pr-conflict-resolver skill first. "
                "Run: python3 scripts/pr_conflict_resolver_first_check_v1.py --ack --json"
            ),
            "first_check_cmd": "python3 scripts/pr_conflict_resolver_first_check_v1.py --ack --json",
        }

    if not wire_ok:
        return {
            "ok": False,
            "path": rel,
            "blockers": ["PR_CONFLICT_WIRE_NOT_PASS"],
            "message": "Run: python3 scripts/pr_conflict_resolver_first_check_v1.py --wire --json",
        }

    return {
        "ok": True,
        "path": rel,
        "reason": "pr_conflict_ack_fresh",
        "sensitive": sensitive,
        "markers": markers,
        "merge_in_progress": merging,
        "ack_saved_at": ack_row.get("saved_at"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="PR conflict resolver first check")
    ap.add_argument("--wire", action="store_true")
    ap.add_argument("--ack", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--path", default="")
    ap.add_argument("--explicit-order", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.wire:
        row = wire()
    elif args.ack:
        row = acknowledge()
    elif args.check:
        if not args.path:
            print("FAIL: --path required for --check", file=sys.stderr)
            return 2
        row = check_write(path=args.path, explicit_order=args.explicit_order)
    else:
        row = wire()

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("line") or row.get("message") or json.dumps(row, indent=2))
    if args.wire:
        return 0 if row.get("wire_ok") else 1
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
