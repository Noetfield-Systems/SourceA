#!/usr/bin/env python3
"""Classify dirty git paths into SourceA ownership lanes."""
from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LANE_MAP_PATH = ROOT / "data/sourcea-dirty-tree-lane-map-v1.json"
REPORT_PATH = ROOT / "reports/sourcea-dirty-tree-lane-report-v1.json"
RECEIPT_PATH = Path.home() / ".sina/sourcea-dirty-tree-lane-map-v1.json"


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_map() -> dict[str, Any]:
    return json.loads(LANE_MAP_PATH.read_text(encoding="utf-8"))


def _matches(path: str, pattern: str) -> bool:
    p = path.strip()
    pat = pattern.strip()
    return fnmatch.fnmatch(p, pat) or fnmatch.fnmatch(p, pat.rstrip("/") + "/**")


def classify_path(path: str, lane_map: dict[str, Any] | None = None) -> dict[str, Any]:
    lane_map = lane_map or load_map()
    matches: list[dict[str, Any]] = []
    for lane in lane_map.get("lanes") or []:
        for pat in lane.get("globs") or []:
            if _matches(path, str(pat)):
                matches.append(
                    {
                        "lane": lane["id"],
                        "owner": lane.get("owner"),
                        "pattern": pat,
                        "freeze_default": bool(lane.get("freeze_default")),
                        "validator": lane.get("validator"),
                    }
                )
                break
    if not matches:
        return {
            "path": path,
            "lane": "unclassified",
            "owner": "Coordinator",
            "matches": [],
            "freeze_default": False,
            "validator": None,
        }
    chosen = next((match for match in matches if match.get("freeze_default")), matches[0])
    return {
        "path": path,
        "lane": chosen["lane"],
        "owner": chosen.get("owner"),
        "matches": matches,
        "freeze_default": chosen.get("freeze_default", False),
        "validator": chosen.get("validator"),
    }


def git_dirty_paths() -> list[dict[str, str]]:
    out = subprocess.check_output(["git", "status", "--porcelain=v1"], cwd=ROOT, text=True)
    rows: list[dict[str, str]] = []
    for line in out.splitlines():
        if not line.strip():
            continue
        rows.append({"status": line[:2], "path": line[3:]})
    return rows


def build_report() -> dict[str, Any]:
    lane_map = load_map()
    dirty = git_dirty_paths()
    lanes: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in dirty:
        classified = classify_path(row["path"], lane_map)
        lanes[classified["lane"]].append({**row, **classified})
    summary = {
        lane: {
            "count": len(items),
            "frozen_count": sum(1 for item in items if item.get("freeze_default")),
            "sample": [item["path"] for item in items[:12]],
        }
        for lane, items in sorted(lanes.items())
    }
    return {
        "schema": "sourcea-dirty-tree-lane-report-v1",
        "at": now(),
        "map_version": lane_map.get("version"),
        "dirty_count": len(dirty),
        "lane_count": len(summary),
        "summary": summary,
        "lanes": {lane: items for lane, items in sorted(lanes.items())},
        "rules": lane_map.get("global_rules") or [],
    }


def check_paths(lane: str, paths: list[str]) -> dict[str, Any]:
    rows = [classify_path(p) for p in paths]
    bad = [r for r in rows if r["lane"] != lane]
    frozen = [r for r in rows if r.get("freeze_default") and r["lane"] == lane]
    return {
        "ok": not bad,
        "lane": lane,
        "checked_count": len(rows),
        "bad": bad,
        "frozen": frozen,
        "rows": rows,
        "note": "Generated/frozen paths require explicit lane assignment." if frozen else "",
    }


def write_reports(report: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", action="append", default=[], help="Classify one path. Repeatable.")
    parser.add_argument("--lane", default="", help="Expected lane for --check-paths.")
    parser.add_argument("--check-paths", nargs="*", default=None, help="Fail if paths are outside --lane.")
    parser.add_argument("--write-report", action="store_true", help="Write report and receipt.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.check_paths is not None:
        if not args.lane:
            raise SystemExit("--lane is required with --check-paths")
        row = check_paths(args.lane, args.check_paths)
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(("OK" if row["ok"] else "BLOCK") + f" lane={args.lane} checked={row['checked_count']}")
        return 0 if row["ok"] else 2

    if args.path:
        rows = [classify_path(p) for p in args.path]
        if args.json:
            print(json.dumps({"ok": True, "rows": rows}, indent=2))
        else:
            for row in rows:
                print(f"{row['lane']}: {row['path']}")
        return 0

    report = build_report()
    if args.write_report:
        write_reports(report)
        report["report_path"] = str(REPORT_PATH)
        report["receipt_path"] = str(RECEIPT_PATH)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"dirty={report['dirty_count']} lanes={report['lane_count']}")
        for lane, row in report["summary"].items():
            print(f"{lane}: {row['count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
