"""Read-only git diff collection for D13 — never writes to repo."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def _run_git(repo: Path, *args: str) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            timeout=45,
            check=False,
        )
        out = (proc.stdout or "").strip()
        if proc.returncode != 0:
            err = (proc.stderr or "").strip()
            return proc.returncode, err or out
        return 0, out
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)


def git_available(repo_root: Path) -> bool:
    code, _ = _run_git(repo_root, "rev-parse", "--is-inside-work-tree")
    return code == 0


def _parse_name_status(lines: list[str]) -> dict[str, str]:
    kinds: dict[str, str] = {}
    for line in lines:
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status = parts[0].strip()
        if status.startswith("R") and len(parts) >= 3:
            kinds[parts[2].strip()] = "renamed"
            continue
        path = parts[-1].strip()
        if status == "A":
            kinds[path] = "added"
        elif status == "D":
            kinds[path] = "deleted"
        elif status.startswith("R"):
            kinds[path] = "renamed"
        else:
            kinds[path] = "modified"
    return kinds


def _parse_numstat(lines: list[str]) -> dict[str, dict[str, int]]:
    stats: dict[str, dict[str, int]] = {}
    for line in lines:
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        add_s, del_s, path = parts[0], parts[1], parts[2].strip()
        if add_s == "-" or del_s == "-":
            stats[path] = {"lines_added": 0, "lines_removed": 0, "binary": True}
        else:
            stats[path] = {
                "lines_added": int(add_s or 0),
                "lines_removed": int(del_s or 0),
                "binary": False,
            }
    return stats


def collect_git_changes(repo_root: Path, *, commits_back: int = 3) -> tuple[list[dict[str, Any]], str]:
    root = repo_root.expanduser().resolve()
    if not git_available(root):
        return [], "no_git"

    merged: dict[str, dict[str, Any]] = {}
    scopes: list[str] = []

    code, ns_work = _run_git(root, "diff", "--name-status", "HEAD")
    if code == 0 and ns_work:
        scopes.append("working_tree")
        kinds = _parse_name_status(ns_work.splitlines())
        _, num_work = _run_git(root, "diff", "--numstat", "HEAD")
        numstats = _parse_numstat(num_work.splitlines()) if num_work else {}
        for path, kind in kinds.items():
            st = numstats.get(path, {})
            merged[path] = {
                "path": path,
                "kind": kind,
                "lines_added": st.get("lines_added", 0),
                "lines_removed": st.get("lines_removed", 0),
                "binary": st.get("binary", False),
                "scope": "working_tree",
            }

    if commits_back > 0:
        code, ns_hist = _run_git(root, "diff", "--name-status", f"HEAD~{commits_back}", "HEAD")
        if code == 0 and ns_hist:
            scopes.append(f"HEAD~{commits_back}..HEAD")
            kinds = _parse_name_status(ns_hist.splitlines())
            _, num_hist = _run_git(root, "diff", "--numstat", f"HEAD~{commits_back}", "HEAD")
            numstats = _parse_numstat(num_hist.splitlines()) if num_hist else {}
            for path, kind in kinds.items():
                st = numstats.get(path, {})
                if path in merged:
                    merged[path]["scope"] = "working_tree+history"
                    continue
                merged[path] = {
                    "path": path,
                    "kind": kind,
                    "lines_added": st.get("lines_added", 0),
                    "lines_removed": st.get("lines_removed", 0),
                    "binary": st.get("binary", False),
                    "scope": f"HEAD~{commits_back}..HEAD",
                }

    changes = sorted(merged.values(), key=lambda c: c.get("path") or "")
    scope = "+".join(scopes) if scopes else "no_changes"
    return changes, scope
