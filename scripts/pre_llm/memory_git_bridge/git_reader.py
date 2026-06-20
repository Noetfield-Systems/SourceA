"""Read-only git lineage for D6 — never writes to repo."""
from __future__ import annotations

import subprocess
from pathlib import Path


def _run_git(repo: Path, *args: str) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            timeout=30,
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


def read_git_commits(repo_root: Path, *, limit: int = 15) -> list[dict]:
    root = repo_root.expanduser().resolve()
    if not git_available(root):
        return []

    code, out = _run_git(
        root,
        "log",
        f"-n{limit}",
        "--format=%H|%s|%an|%aI",
    )
    if code != 0 or not out:
        return []

    slots: list[dict] = []
    for line in out.splitlines():
        parts = line.split("|", 3)
        if len(parts) < 4:
            continue
        sha, subject, author, ts = parts
        slots.append(
            {
                "slot_id": f"git-{sha[:12]}",
                "kind": "git_commit",
                "sha": sha,
                "summary": subject.strip(),
                "author": author.strip(),
                "timestamp": ts.strip(),
                "path": str(root),
                "producer": "D6",
            }
        )
    return slots


def read_git_diff_stat(repo_root: Path, *, commits_back: int = 3) -> list[dict]:
    root = repo_root.expanduser().resolve()
    if not git_available(root):
        return []

    code, out = _run_git(root, "diff", "--stat", f"HEAD~{commits_back}", "HEAD")
    if code != 0 or not out:
        return []

    return [
        {
            "slot_id": f"git-diff-stat-{commits_back}",
            "kind": "git_diff_stat",
            "summary": f"diff stat HEAD~{commits_back}..HEAD",
            "excerpt": out[:1200],
            "path": str(root),
            "timestamp": None,
            "producer": "D6",
        }
    ]
