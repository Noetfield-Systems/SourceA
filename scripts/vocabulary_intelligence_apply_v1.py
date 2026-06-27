#!/usr/bin/env python3
"""Vocabulary Intelligence — apply Tier 1–2 motor_cloud patches from scan receipt."""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
DEFAULT_RECEIPT = SINA / "vocabulary-intelligence-scan-receipt-v1.json"
APPLY_RECEIPT = SINA / "vocabulary-intelligence-apply-receipt-v1.json"
REGISTRY_PATH = ROOT / "data" / "vocabulary-intelligence-registry-v1.json"

EXCLUDE_PATH_GLOBS = [
    "**/*.app/**",
    "**/cloud-workers-bundle/**",
    "**/chat-unify-bundle/**",
    "**/node_modules/**",
    "**/.git/**",
    "**/receipts/**",
    "**/secondary-cloud-drain-batch-*",
    "**/secondary-cloud-forge-run-batch-*",
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _excluded(rel: str) -> bool:
    for g in EXCLUDE_PATH_GLOBS:
        if fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(f"**/{rel}", g):
            return True
        frag = rel.replace("\\", "/")
        if fnmatch.fnmatch(frag, g.lstrip("**/")):
            return True
    return False


def _replace_once(line: str, match: str, suggestion: str) -> tuple[str, bool]:
    if not match or not suggestion:
        return line, False
    pat = re.compile(re.escape(match), re.IGNORECASE)
    if not pat.search(line):
        return line, False
    return pat.sub(suggestion, line, count=1), True


def _load_patch_hits(scan: dict[str, Any], *, tiers: tuple[int, ...]) -> list[dict[str, Any]]:
    hits = scan.get("hits") or scan.get("patch_queue") or []
    out = [
        h
        for h in hits
        if h.get("action") == "patch"
        and h.get("subject") == "motor_cloud"
        and int(h.get("tier", 9)) in tiers
    ]
    return sorted(out, key=lambda x: (x.get("file", ""), x.get("line", 0), -len(x.get("match") or "")))


def apply_patches(
    *,
    scan: dict[str, Any],
    tiers: tuple[int, ...] = (1, 2),
    dry_run: bool = False,
) -> dict[str, Any]:
    hits = _load_patch_hits(scan, tiers=tiers)
    by_file: dict[str, list[dict[str, Any]]] = {}
    for h in hits:
        by_file.setdefault(str(h.get("file") or ""), []).append(h)

    changed_files: list[dict[str, Any]] = []
    skipped_files: list[dict[str, Any]] = []
    line_edits = 0

    for rel, file_hits in sorted(by_file.items()):
        if not rel or _excluded(rel):
            skipped_files.append({"file": rel, "reason": "excluded_path", "hits": len(file_hits)})
            continue
        path = ROOT / rel
        if not path.is_file():
            skipped_files.append({"file": rel, "reason": "missing", "hits": len(file_hits)})
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
        except OSError as e:
            skipped_files.append({"file": rel, "reason": str(e), "hits": len(file_hits)})
            continue

        file_changed = False
        edits: list[dict[str, Any]] = []
        by_line: dict[int, list[dict[str, Any]]] = {}
        for h in file_hits:
            by_line.setdefault(int(h.get("line") or 0), []).append(h)

        for line_no, line_hits in by_line.items():
            if line_no < 1 or line_no > len(lines):
                continue
            idx = line_no - 1
            original = lines[idx]
            current = original
            for h in sorted(line_hits, key=lambda x: -len(x.get("match") or "")):
                new_line, ok = _replace_once(current, str(h.get("match") or ""), str(h.get("suggestion") or ""))
                if ok:
                    current = new_line
                    edits.append(
                        {
                            "line": line_no,
                            "match": h.get("match"),
                            "suggestion": h.get("suggestion"),
                            "tier": h.get("tier"),
                        }
                    )
                    line_edits += 1
            if current != original:
                lines[idx] = current
                file_changed = True

        if file_changed:
            if not dry_run:
                path.write_text("".join(lines), encoding="utf-8")
            changed_files.append({"file": rel, "edits": len(edits), "details": edits[:20]})

    return {
        "ok": True,
        "schema": "vocabulary-intelligence-apply-v1",
        "at": _now(),
        "dry_run": dry_run,
        "campaign_id": scan.get("campaign_id"),
        "tiers": list(tiers),
        "hits_considered": len(hits),
        "files_changed": len(changed_files),
        "line_edits": line_edits,
        "skipped_files": len(skipped_files),
        "changed_files": changed_files,
        "skipped": skipped_files[:50],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Apply VIM Tier 1–2 patches")
    ap.add_argument("--receipt", default=str(DEFAULT_RECEIPT))
    ap.add_argument("--rescan", action="store_true", help="Fresh scan before apply")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--tier", type=int, action="append", dest="tiers")
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.rescan:
        from vocabulary_intelligence_scan_v1 import run_scan  # noqa: WPS433

        scan = run_scan(campaign_id="motor-rename-v1", profiles=["sourcea_repo"])
    else:
        scan = _read_json(Path(args.receipt).expanduser())
        if not scan.get("ok"):
            print("FAIL: invalid or missing scan receipt — run scan first or use --rescan")
            return 1
        if not scan.get("hits"):
            from vocabulary_intelligence_scan_v1 import run_scan  # noqa: WPS433

            scan = run_scan(campaign_id="motor-rename-v1", profiles=["sourcea_repo"])

    tiers = tuple(args.tiers) if args.tiers else (1, 2)
    result = apply_patches(scan=scan, tiers=tiers, dry_run=args.dry_run)
    if args.write_receipt and not args.dry_run:
        _write_json(APPLY_RECEIPT, result)

    if args.json:
        slim = {k: v for k, v in result.items() if k != "changed_files"}
        slim["changed_sample"] = result.get("changed_files", [])[:30]
        print(json.dumps(slim, indent=2, ensure_ascii=False))
    else:
        print(
            f"VIM apply · dry_run={result['dry_run']} · files={result['files_changed']} · "
            f"line_edits={result['line_edits']} · skipped={result['skipped_files']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
