#!/usr/bin/env python3
"""SourceA wrapper — verify PR conflict resolver lock (delegates to SG SSOT + local wiring)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SSOT = ROOT / "data/pr-conflict-resolver-mandatory-v1.json"


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def verify(*, mac_desktop: bool = True) -> dict:
    issues: list[str] = []
    ssot = _read(SSOT)
    checks: dict = {"sourcea_ssot": SSOT.is_file()}

    if not ssot:
        issues.append("missing:sourcea_ssot")

    for key in ("sourcea_lock_doc", "sourcea_law", "cursor_rule"):
        rel = str(ssot.get(key) or "")
        path = ROOT / rel if rel else None
        ok = bool(path and path.is_file())
        checks[f"{key}_exists"] = ok
        if not ok and rel:
            issues.append(f"missing:{rel}")

    sg_root = Path(str(ssot.get("sg_ssot_root") or "").replace("~/", str(Path.home()) + "/"))
    sg_verifier = sg_root / "scripts/verify_pr_conflict_skill_v1.py"
    checks["sg_verifier_exists"] = sg_verifier.is_file()
    sg_row: dict = {}
    if sg_verifier.is_file():
        args = [sys.executable, str(sg_verifier), "--json"]
        if mac_desktop:
            args.append("--mac-desktop")
        proc = subprocess.run(args, cwd=str(sg_root), capture_output=True, text=True, timeout=60)
        try:
            sg_row = json.loads(proc.stdout or "{}")
        except json.JSONDecodeError:
            sg_row = {"ok": False, "parse_error": True}
        checks["sg_verify_ok"] = proc.returncode == 0 and bool(sg_row.get("ok"))
        if not checks["sg_verify_ok"]:
            issues.extend(sg_row.get("issues") or ["sg_verify_failed"])
    else:
        issues.append("missing:sg_verifier")
        checks["sg_verify_ok"] = False

    first_check = ROOT / "scripts/pr_conflict_resolver_first_check_v1.py"
    validator_sh = ROOT / "scripts/validate-pr-conflict-resolver-mandatory-v1.sh"
    checks["first_check_script"] = first_check.is_file()
    checks["mandatory_validator"] = validator_sh.is_file()
    if not first_check.is_file():
        issues.append("missing:pr_conflict_resolver_first_check_v1.py")
    if not validator_sh.is_file():
        issues.append("missing:validate-pr-conflict-resolver-mandatory-v1.sh")

    ok = not issues
    return {
        "schema": "sourcea-pr-conflict-skill-verify-v1",
        "ok": ok,
        "issues": issues,
        "checks": checks,
        "sg": sg_row,
        "report_line": "pr_conflict_mandatory · ALL PASS" if ok else f"pr_conflict_mandatory · FAIL ({len(issues)})",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-mac-desktop", action="store_true")
    args = ap.parse_args()
    row = verify(mac_desktop=not args.no_mac_desktop)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
        for issue in row.get("issues") or []:
            print(f"  {issue}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
