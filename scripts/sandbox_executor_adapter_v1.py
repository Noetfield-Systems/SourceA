#!/usr/bin/env python3
"""SANDBOX execution adapter v1 — bounded callable repository executor."""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = Path(os.environ.get("SOURCEA_SANDBOX_EXECUTOR_STATE_DIR", ROOT / ".sourcea" / "sandbox-executions-v1"))
WORK_ROOT = Path(os.environ.get("SOURCEA_SANDBOX_EXECUTOR_WORK_ROOT", tempfile.gettempdir())) / "sourcea-sandbox-executions-v1"
JOB_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{1,127}$")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
BRANCH_RE = re.compile(r"^(automation|codex|sandbox)/[A-Za-z0-9][A-Za-z0-9._/-]{0,180}$")
TERMINAL = {"PASS", "FAIL", "BLOCKED"}
_SECRET_ENV_KEYS = ("GITHUB_TOKEN", "GITHUB_PERSONAL_ACCESS_TOKEN")


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_id_for(job_id: str) -> str:
    return "sx-" + hashlib.sha256(job_id.encode("utf-8")).hexdigest()[:24]


def state_path(run_id: str) -> Path:
    return STATE_DIR / f"{run_id}.json"


def load_state(run_id: str) -> dict[str, Any] | None:
    path = state_path(run_id)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(row: dict[str, Any]) -> dict[str, Any]:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = state_path(str(row["run_id"])).with_suffix(".tmp")
    tmp.write_text(json.dumps(row, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(state_path(str(row["run_id"])))
    return row


def accepted(job_id: str) -> dict[str, Any]:
    run_id = run_id_for(job_id)
    return {"accepted": True, "run_id": run_id, "status_url": f"/v1/executions/{run_id}"}


def _allowed_repos() -> set[str]:
    raw = os.environ.get("SOURCEA_SANDBOX_ALLOWED_REPOSITORIES", "Noetfield-Systems/SANDBOX")
    return {x.strip() for x in raw.split(",") if x.strip()}


def validate_request(body: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not JOB_RE.match(str(body.get("job_id") or "")):
        errors.append("job_id_invalid")
    repo = str(body.get("target_repository") or "")
    if not REPO_RE.match(repo):
        errors.append("target_repository_invalid")
    elif repo not in _allowed_repos():
        errors.append("target_repository_not_allowed")
    if not str(body.get("base_branch") or ""):
        errors.append("base_branch_required")
    if not SHA_RE.match(str(body.get("base_sha") or "")):
        errors.append("base_sha_invalid")
    branch = str(body.get("working_branch") or "")
    if not BRANCH_RE.match(branch) or not _safe_branch(branch):
        errors.append("working_branch_invalid")
    if branch in {"main", "master", str(body.get("base_branch") or "")}:
        errors.append("working_branch_must_not_be_main_or_base")
    allowed = body.get("allowed_paths")
    if not isinstance(allowed, list) or not allowed or not all(isinstance(p, str) and _safe_pattern(p) for p in allowed):
        errors.append("allowed_paths_invalid")
    if not isinstance(body.get("sandbox_job"), dict):
        errors.append("sandbox_job_invalid")
    if not isinstance(body.get("verification_contract"), dict):
        errors.append("verification_contract_invalid")
    return errors


def _safe_pattern(pattern: str) -> bool:
    return bool(pattern and not pattern.startswith("/") and ".." not in Path(pattern).parts and not pattern.startswith(".git"))


def _safe_branch(branch: str) -> bool:
    parts = branch.split("/")
    return all(part not in {"", ".", ".."} for part in parts) and ".." not in branch and not branch.endswith(".")


def _path_allowed(path: str, patterns: list[str]) -> bool:
    clean = path.strip("/")
    if not clean or clean.startswith(".git/") or ".." in Path(clean).parts:
        return False
    return any(fnmatch.fnmatch(clean, pat) or fnmatch.fnmatch(clean + "/", pat.rstrip("/") + "/") for pat in patterns)


def _secret_values(env: dict[str, str] | None = None) -> list[str]:
    src = env or os.environ
    return [str(src.get(key) or "") for key in _SECRET_ENV_KEYS if src.get(key)]


def _redact_text(value: str, env: dict[str, str] | None = None) -> str:
    out = value
    for secret in _secret_values(env):
        if secret:
            out = out.replace(secret, "[REDACTED]")
    return out


def _redact_cmd(cmd: list[str], env: dict[str, str] | None = None) -> list[str]:
    return [_redact_text(str(part), env) for part in cmd]


def _run(cmd: list[str], cwd: Path, timeout: int = 300, env: dict[str, str] | None = None) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, timeout=timeout, env=env)
    return {
        "cmd": _redact_cmd(cmd, env),
        "returncode": proc.returncode,
        "stdout": _redact_text(proc.stdout[-4000:], env),
        "stderr": _redact_text(proc.stderr[-4000:], env),
    }


def _repo_url(repo: str) -> str:
    return f"https://github.com/{repo}.git"


def _git_auth_env(base: dict[str, str] | None = None) -> dict[str, str] | None:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN") or ""
    if not token:
        return base
    env = dict(base or os.environ.copy())
    env.update({
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": "http.https://github.com/.extraheader",
        "GIT_CONFIG_VALUE_0": f"AUTHORIZATION: bearer {token}",
    })
    return env


def _changed_paths(repo_dir: Path) -> list[str]:
    tracked = _run(["git", "diff", "--name-only", "HEAD"], repo_dir)
    untracked = _run(["git", "ls-files", "--others", "--exclude-standard"], repo_dir)
    paths = [x.strip() for x in (tracked["stdout"] + "\n" + untracked["stdout"]).splitlines() if x.strip()]
    return sorted(set(paths))


def _open_pr(repo: str, branch: str, base: str, title: str, body: str, cwd: Path) -> tuple[str, list[dict[str, Any]]]:
    evidence: list[dict[str, Any]] = []
    if shutil.which("gh"):
        row = _run(["gh", "pr", "create", "--repo", repo, "--base", base, "--head", branch, "--title", title, "--body", body], cwd, timeout=120)
        evidence.append({"step": "gh_pr_create", **row})
        if row["returncode"] == 0:
            return row["stdout"].strip().splitlines()[-1], evidence
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN") or ""
    if not token:
        return "", evidence + [{"step": "open_pr", "returncode": 1, "stderr": "missing GITHUB_TOKEN or GITHUB_PERSONAL_ACCESS_TOKEN"}]
    import urllib.request
    payload = json.dumps({"title": title, "head": branch, "base": base, "body": body}).encode()
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/pulls", data=payload, method="POST", headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "User-Agent": "sourcea-sandbox-executor"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
        return str(data.get("html_url") or ""), evidence + [{"step": "github_api_pr_create", "returncode": 0}]
    except Exception as exc:  # network/API failure is recorded as evidence
        return "", evidence + [{"step": "github_api_pr_create", "returncode": 1, "stderr": str(exc)}]


def execute(body: dict[str, Any]) -> dict[str, Any]:
    errors = validate_request(body)
    run_id = run_id_for(str(body.get("job_id") or ""))
    existing = load_state(run_id)
    if existing:
        return existing
    started = now()
    base = {"run_id": run_id, "job_id": body.get("job_id"), "status": "BLOCKED", "target_repository": body.get("target_repository"), "base_sha": body.get("base_sha"), "working_branch": body.get("working_branch"), "changed_paths": [], "commit_sha": None, "pull_request_url": None, "verification_evidence": [], "ci_check_references": [], "started_at": started, "completed_at": None, "blocker": None}
    if errors:
        base.update({"completed_at": now(), "blocker": ",".join(errors)})
        return save_state(base)
    save_state({**base, "status": "RUNNING"})
    evidence: list[dict[str, Any]] = []
    work = WORK_ROOT / run_id
    try:
        shutil.rmtree(work, ignore_errors=True)
        work.mkdir(parents=True, exist_ok=True)
        clone = work / "repo"
        git_env = _git_auth_env()
        clone_row = _run(["git", "clone", "--no-checkout", _repo_url(str(body["target_repository"])), str(clone)], work, timeout=600, env=git_env)
        evidence.append({"step": "git_clone", **clone_row})
        if clone_row["returncode"] != 0:
            raise RuntimeError("git_clone_failed")
        fetch = _run(["git", "fetch", "origin", str(body["base_sha"])], clone, timeout=300, env=git_env)
        evidence.append({"step": "git_fetch_base_sha", **fetch})
        if fetch["returncode"] != 0:
            raise RuntimeError("git_fetch_base_sha_failed")
        checkout = _run(["git", "checkout", "-B", str(body["working_branch"]), str(body["base_sha"])], clone)
        evidence.append({"step": "git_checkout_working_branch", **checkout})
        if checkout["returncode"] != 0:
            raise RuntimeError("git_checkout_working_branch_failed")
        cmd_tpl = os.environ.get("SOURCEA_SANDBOX_EXECUTOR_CMD", "").strip()
        if not cmd_tpl:
            raise RuntimeError("missing SOURCEA_SANDBOX_EXECUTOR_CMD")
        job_file = work / "sandbox_job.json"
        job_file.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
        env = os.environ.copy(); env.update({"SANDBOX_JOB_FILE": str(job_file), "SANDBOX_REPO_DIR": str(clone), "SANDBOX_RUN_ID": run_id})
        executor = _run(["bash", "-lc", cmd_tpl], clone, timeout=int(os.environ.get("SOURCEA_SANDBOX_EXECUTOR_TIMEOUT", "600")), env=env)
        evidence.append({"step": "coding_executor", **executor})
        if executor["returncode"] != 0:
            raise RuntimeError("coding_executor_failed")
        changed = _changed_paths(clone)
        base["changed_paths"] = changed
        bad = [p for p in changed if not _path_allowed(p, list(body["allowed_paths"]))]
        if bad:
            raise RuntimeError("allowed_path_violation:" + ",".join(bad))
        verify_cmds = body.get("verification_contract", {}).get("commands") or []
        for i, cmd in enumerate(verify_cmds):
            if not isinstance(cmd, str) or not cmd.strip():
                raise RuntimeError("verification_command_invalid")
            row = _run(["bash", "-lc", cmd], clone, timeout=300)
            evidence.append({"step": f"verification_{i+1}", **row})
            if row["returncode"] != 0:
                raise RuntimeError("verification_failed")
        if not changed:
            raise RuntimeError("no_changes_made")
        _run(["git", "config", "user.email", os.environ.get("GIT_AUTHOR_EMAIL", "sourcea-executor@noetfield.systems")], clone)
        _run(["git", "config", "user.name", os.environ.get("GIT_AUTHOR_NAME", "SourceA Sandbox Executor")], clone)
        add = _run(["git", "add", "--"] + changed, clone); evidence.append({"step": "git_add", **add})
        commit = _run(["git", "commit", "-m", f"Execute sandbox job {body['job_id']}"], clone); evidence.append({"step": "git_commit", **commit})
        if commit["returncode"] != 0:
            raise RuntimeError("git_commit_failed")
        sha = _run(["git", "rev-parse", "HEAD"], clone); evidence.append({"step": "git_rev_parse", **sha})
        base["commit_sha"] = sha["stdout"].strip()
        if os.environ.get("SOURCEA_SANDBOX_SKIP_PUSH") != "1":
            push = _run(["git", "push", "origin", f"HEAD:{body['working_branch']}"], clone, timeout=300, env=git_env); evidence.append({"step": "git_push", **push})
            if push["returncode"] != 0:
                raise RuntimeError("git_push_failed")
        else:
            evidence.append({"step": "git_push", "returncode": 0, "stdout": "skipped by SOURCEA_SANDBOX_SKIP_PUSH", "stderr": ""})
        pr_url, pr_evidence = _open_pr(str(body["target_repository"]), str(body["working_branch"]), str(body["base_branch"]), f"Sandbox job {body['job_id']}", "Automated bounded SourceA SANDBOX execution.", clone)
        evidence.extend(pr_evidence); base["pull_request_url"] = pr_url
        if not pr_url:
            raise RuntimeError("pull_request_create_failed")
        base.update({"status": "PASS", "blocker": None})
    except Exception as exc:
        base.update({"status": "FAIL" if str(exc) in {"coding_executor_failed", "verification_failed"} else "BLOCKED", "blocker": str(exc)})
    base.update({"verification_evidence": evidence, "completed_at": now()})
    return save_state(base)


def handle_post(body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    errors = validate_request(body)
    if errors:
        row = execute(body)
        return 422, row
    row = execute(body)
    return 202, accepted(str(body["job_id"]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["execute", "status", "validate"])
    ap.add_argument("--run-id")
    args = ap.parse_args()
    if args.action == "status":
        print(json.dumps(load_state(str(args.run_id)) or {"error": "not_found"}, indent=2)); return 0
    body = json.load(sys.stdin)
    row = execute(body) if args.action == "execute" else {"errors": validate_request(body)}
    print(json.dumps(row, indent=2)); return 0 if not row.get("errors") else 1


if __name__ == "__main__":
    raise SystemExit(main())
