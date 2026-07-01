#!/usr/bin/env python3
"""Publish packages/sourcea-boot to public GitHub repo sourcea-io/sourcea-boot."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "packages" / "sourcea-boot"
DEFAULT_REPO = "sourcea-io/sourcea-boot"
DEFAULT_REMOTE = f"https://github.com/{DEFAULT_REPO}.git"
RECEIPT = Path.home() / ".sina" / "sourcea-boot-public-publish-receipt-v1.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run(cmd: list[str], *, cwd: Path | None = None, check: bool = True, input: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=check,
        input=input,
    )


def github_token() -> str | None:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return token
    proc = run(
        ["git", "credential", "fill"],
        cwd=ROOT,
        check=False,
        input="protocol=https\nhost=github.com\n\n",
    )
    for line in proc.stdout.splitlines():
        if line.startswith("password="):
            value = line.split("=", 1)[1]
            return value or None
    return None


def create_github_repo(slug: str, *, token: str, private: bool = False) -> dict[str, object]:
    owner, name = slug.split("/", 1)
    payload = json.dumps(
        {
            "name": name,
            "description": "PASS or BLOCK before any agent executes — four disk checks, one receipt.",
            "private": private,
            "has_issues": True,
            "auto_init": False,
        }
    ).encode("utf-8")
    urls = [
        f"https://api.github.com/orgs/{owner}/repos",
        "https://api.github.com/user/repos",
    ]
    last_error = ""
    for url in urls:
        req = urllib.request.Request(
            url,
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "User-Agent": "sourcea-boot-publish/1",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                return {"ok": True, "status": resp.status, "full_name": body.get("full_name"), "html_url": body.get("html_url")}
        except urllib.error.HTTPError as exc:
            last_error = exc.read().decode("utf-8", errors="replace")[:500]
            if exc.code in (404, 422):
                continue
            return {"ok": False, "status": exc.code, "error": last_error}
        except urllib.error.URLError as exc:
            return {"ok": False, "status": 0, "error": str(exc)}
    return {"ok": False, "status": 0, "error": last_error or "repo create failed"}


def github_repo_exists(slug: str) -> tuple[bool, int]:
    url = f"https://api.github.com/repos/{slug}"
    req = urllib.request.Request(url, headers={"User-Agent": "sourcea-boot-publish/1", "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return True, resp.status
    except urllib.error.HTTPError as exc:
        return False, exc.code
    except urllib.error.URLError:
        return False, 0


def copytree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".publish-export", "__pycache__", "*.pyc", ".pytest_cache"))


def build_export(export_root: Path) -> None:
    if export_root.exists():
        shutil.rmtree(export_root)
    export_root.mkdir(parents=True, exist_ok=True)
    for name in ("pyproject.toml", "README.md", "LICENSE"):
        shutil.copy2(PKG / name, export_root / name)
    shutil.copy2(PKG / "publish" / "gitignore", export_root / ".gitignore")
    shutil.copytree(
        PKG / "src",
        export_root / "src",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"),
    )
    scripts_dir = export_root / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PKG / "publish" / "validate-sourcea-boot-v1.sh", scripts_dir / "validate-sourcea-boot-v1.sh")
    (scripts_dir / "validate-sourcea-boot-v1.sh").chmod(0o755)
    workflow_dir = export_root / ".github" / "workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PKG / "publish" / "validate-sourcea-boot-v1.yml", workflow_dir / "validate-sourcea-boot-v1.yml")


def validate_export(export_root: Path) -> dict[str, object]:
    proc = run(["bash", "scripts/validate-sourcea-boot-v1.sh"], cwd=export_root)
    return {"ok": proc.returncode == 0, "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip()}


def patch_readme_for_public(export_root: Path) -> None:
    readme = export_root / "README.md"
    text = readme.read_text(encoding="utf-8")
    pypi_block = (
        "Or from PyPI:\n\n"
        "```bash\n"
        "pip install sourcea-boot\n"
        "sourcea-boot --json\n"
        "```\n"
    )
    honest = (
        "PyPI (Phase 0b — coming soon):\n\n"
        "```bash\n"
        "# pip install sourcea-boot   # not on PyPI yet — clone + editable install below\n"
        "sourcea-boot --json\n"
        "```\n"
    )
    if pypi_block in text:
        text = text.replace(pypi_block, honest)
    readme.write_text(text, encoding="utf-8")


def git_publish(export_root: Path, *, remote_url: str, dry_run: bool) -> dict[str, object]:
    if dry_run:
        return {"ok": True, "dry_run": True, "remote_url": remote_url}

    git_dir = export_root / ".git"
    if git_dir.exists():
        shutil.rmtree(git_dir)

    run(["git", "init", "-b", "main"], cwd=export_root)
    run(["git", "add", "-A"], cwd=export_root)
    commit = run(["git", "commit", "-m", "sourcea-boot v0.1.0 — public eval gate"], cwd=export_root)
    run(["git", "remote", "add", "origin", remote_url], cwd=export_root)

    push = run(["git", "push", "-u", "origin", "main", "--force"], cwd=export_root, check=False)
    return {
        "ok": push.returncode == 0,
        "commit_stdout": commit.stdout.strip(),
        "push_stdout": push.stdout.strip(),
        "push_stderr": push.stderr.strip(),
        "remote_url": remote_url,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Publish sourcea-boot public GitHub repo")
    ap.add_argument("--repo", default=DEFAULT_REPO, help="GitHub slug owner/repo")
    ap.add_argument("--remote-url", default="", help="Override git remote URL")
    ap.add_argument("--dry-run", action="store_true", help="Build + validate only; no git push")
    ap.add_argument("--push-existing", action="store_true", help="Skip create; push export to --repo")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    remote_url = args.remote_url or f"https://github.com/{args.repo}.git"
    export_root = PKG / ".publish-export"

    exists_before, status_before = github_repo_exists(args.repo)
    build_export(export_root)
    patch_readme_for_public(export_root)
    validation = validate_export(export_root)

    receipt: dict[str, object] = {
        "schema": "sourcea-boot-public-publish-receipt-v1",
        "at": utc_now(),
        "repo": args.repo,
        "remote_url": remote_url,
        "github_exists_before": exists_before,
        "github_status_before": status_before,
        "export_root": str(export_root),
        "validation": validation,
        "dry_run": args.dry_run,
    }

    if not validation["ok"]:
        receipt["ok"] = False
        receipt["phase"] = "validate_failed"
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        if args.json:
            print(json.dumps(receipt, indent=2))
        else:
            print("FAIL: export validation failed", file=sys.stderr)
            print(validation.get("stderr") or validation.get("stdout"), file=sys.stderr)
        return 1

    create_result: dict[str, object] | None = None
    effective_remote = remote_url
    if not exists_before and not args.dry_run and not args.push_existing:
        token = github_token()
        if token:
            create_result = create_github_repo(args.repo, token=token)
            receipt["create_repo"] = create_result
            if create_result.get("ok") and create_result.get("full_name"):
                created_slug = str(create_result["full_name"])
                effective_remote = f"https://github.com/{created_slug}.git"
                receipt["effective_repo"] = created_slug
                receipt["effective_remote_url"] = effective_remote
                exists_before = True
        else:
            receipt["create_repo"] = {"ok": False, "error": "no GitHub token available"}

    publish = git_publish(export_root, remote_url=effective_remote, dry_run=args.dry_run)
    receipt["publish"] = publish
    exists_after, status_after = github_repo_exists(args.repo) if not args.dry_run else (exists_before, status_before)
    effective_slug = str(receipt.get("effective_repo") or args.repo)
    if not args.dry_run and publish.get("ok"):
        exists_after, status_after = github_repo_exists(effective_slug)
    receipt["github_exists_after"] = exists_after
    receipt["github_status_after"] = status_after
    receipt["ok"] = bool(validation["ok"] and (publish.get("ok") or args.dry_run))
    receipt["phase"] = "published" if publish.get("ok") and not args.dry_run else ("dry_run" if args.dry_run else "push_failed")

    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(json.dumps(receipt, indent=2))
    return 0 if receipt["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
