#!/usr/bin/env python3
"""Classify dirty git paths by lane and optionally commit one atomic commit per lane."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
from sourcea_dirty_tree_lane_map_v1 import build_report, write_reports  # noqa: E402

LANE_COMMIT_ORDER = [
    "other_control",
    "brain_chat_runtime",
    "generated_brain_corpus",
    "docs_plan_registry",
    "ui_pro_444",
    "site_assets",
    "unclassified",
]

LANE_MESSAGES = {
    "other_control": "chore(control): dirty-tree policy, gitignore crawl mirror, deploy guard paths",
    "brain_chat_runtime": "feat(brain): voice SSOT retrieval, smart refresh, and live gate wiring",
    "generated_brain_corpus": "chore(brain): sync knowledge bundle and distilled corpus snapshots",
    "docs_plan_registry": "docs(ui): UI Pro 444 upgrade plan and research report",
    "ui_pro_444": "feat(landing): UI Pro 444 scripts, mechanical gate, and E2E audit tooling",
    "site_assets": "feat(landing): hero console, forge terminal embed, dist mirror, publish CSP",
    "unclassified": "chore: triage remaining session files",
}


def git(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=check)


def commit_lane(lane: str, paths: list[str], *, dry_run: bool) -> dict:
    for p in paths:
        git(["add", "--", p], check=False)
    diff = git(["diff", "--cached", "--name-only"], check=False)
    if not diff.stdout.strip():
        return {"lane": lane, "ok": True, "skipped": True, "reason": "nothing to stage", "paths": paths}
    msg = LANE_MESSAGES.get(lane, f"chore: clean dirty-tree lane {lane}")
    if dry_run:
        return {"lane": lane, "ok": True, "dry_run": True, "message": msg, "paths": diff.stdout.strip().splitlines()}
    commit = git(["commit", "-m", msg], check=False)
    return {
        "lane": lane,
        "ok": commit.returncode == 0,
        "message": msg,
        "paths": diff.stdout.strip().splitlines(),
        "stderr": commit.stderr.strip(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lane", action="append", default=[], help="Commit only these lane ids (repeatable).")
    ap.add_argument("--commit-all", action="store_true", help="One atomic git commit per lane.")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--write-report", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    report = build_report()
    if args.write_report:
        write_reports(report)

    lanes = report.get("lanes") or {}
    target_lanes = args.lane or (LANE_COMMIT_ORDER if args.commit_all else [])
    results: list[dict] = []
    for lane in target_lanes:
        items = lanes.get(lane) or []
        if not items:
            continue
        paths = [str(item["path"]) for item in items]
        if args.commit_all or args.lane:
            results.append(commit_lane(lane, paths, dry_run=args.dry_run))
        elif args.json:
            results.append({"lane": lane, "count": len(paths), "paths": paths})

    if args.commit_all or args.lane:
        out = {"ok": all(r.get("ok") for r in results), "commits": results, "dirty_remaining": len(git(["status", "--porcelain"]).stdout.splitlines())}
    else:
        out = report
        if results:
            out = {"report": report, "lanes": results}

    if args.json:
        print(json.dumps(out, indent=2))
    elif args.commit_all or args.lane:
        for row in results:
            if row.get("skipped"):
                print(f"SKIP {row['lane']}: {row.get('reason')}")
            elif row.get("dry_run"):
                print(f"DRY {row['lane']}: {len(row.get('paths') or [])} files — {row['message']}")
            elif row.get("ok"):
                print(f"OK {row['lane']}: {len(row.get('paths') or [])} files")
            else:
                print(f"FAIL {row['lane']}: {row.get('stderr')}", file=sys.stderr)
        if isinstance(out, dict) and "dirty_remaining" in out:
            print(f"dirty_remaining={out['dirty_remaining']}")
    else:
        print(f"dirty={report['dirty_count']}")
        for lane, row in report["summary"].items():
            print(f"  {lane}: {row['count']}")

    if args.commit_all or args.lane:
        return 0 if out.get("ok") else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
