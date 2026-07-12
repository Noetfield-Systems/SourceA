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
PATH_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,255}$")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
RUN_ID_RE = re.compile(r"^sx-[0-9a-f]{24}$")
BRANCH_RE = re.compile(r"^(automation|codex|sandbox)/[A-Za-z0-9][A-Za-z0-9._/-]{0,180}$")
BASE_BRANCH_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,180}$")
TERMINAL = {"PASS", "FAIL", "BLOCKED"}
_SECRET_ENV_KEYS = ("GITHUB_TOKEN", "GITHUB_PERSONAL_ACCESS_TOKEN", "FBE_INTERNAL_SECRET", "SOURCEA_SANDBOX_EXECUTOR_SECRET")
_SANITIZE_ENV_KEYS = ("GITHUB_TOKEN", "GITHUB_PERSONAL_ACCESS_TOKEN", "FBE_INTERNAL_SECRET", "SOURCEA_SANDBOX_EXECUTOR_SECRET")

# Server-controlled verification checks: check_id -> argv. Overridable via env (server config), never the request.
_DEFAULT_VERIFICATION_CHECKS: dict[str, list[str]] = {
    "fixture_schema": ["python3", "-c", "import glob, json; [json.load(open(f)) for f in glob.glob('**/*.json', recursive=True)]; print('fixture_schema_ok')"],
    "targeted_tests": ["python3", "-m", "pytest", "-q"],
}
_MAX_CONCURRENCY = max(1, int(os.environ.get("SOURCEA_SANDBOX_MAX_CONCURRENCY", "2") or "2"))
_CLAIM_DIR_NAME = "claims"
_CAPACITY_DIR_NAME = "capacity-slots"
_CLAIM_STALE_SECONDS = max(60, int(os.environ.get("SOURCEA_SANDBOX_CLAIM_STALE_SECONDS", "3600") or "3600"))


def _claims_dir() -> Path:
    return STATE_DIR / _CLAIM_DIR_NAME


def _capacity_dir() -> Path:
    return STATE_DIR / _CAPACITY_DIR_NAME


def _safe_claim_name(run_id: str) -> str:
    return os.path.basename(f"{_validated(RUN_ID_RE, run_id, 'invalid_run_id')}.claim")


def _under_allowed_root(path: str, allowed_prefix: str) -> bool:
    """Strict prefix boundary: path == root OR path.startswith(root + '/')."""
    root = allowed_prefix.rstrip("/")
    return path == root or path.startswith(root + "/")


def _pattern_base_path(pattern: str) -> str:
    clean = pattern.strip("/")
    if clean.endswith("/**"):
        return clean[:-3].rstrip("/")
    wildcard_at = min((clean.find(ch) for ch in "*?[" if ch in clean), default=-1)
    if wildcard_at >= 0:
        return clean[:wildcard_at].rstrip("/")
    return clean


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _claim_is_stale(claim_path: Path) -> bool:
    try:
        data = json.loads(claim_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return True
    pid = data.get("pid")
    if isinstance(pid, int) and _pid_alive(pid):
        return False
    at = str(data.get("at") or "")
    if not at:
        return True
    try:
        claimed_at = datetime.strptime(at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return True
    age = (datetime.now(timezone.utc) - claimed_at).total_seconds()
    return age >= _CLAIM_STALE_SECONDS


def _try_acquire_run_claim(run_id: str) -> tuple[bool, bool]:
    """Cross-process atomic run claim via O_EXCL on the durable state backend."""
    _claims_dir().mkdir(parents=True, exist_ok=True)
    claim_path = _claims_dir() / _safe_claim_name(run_id)
    if claim_path.exists() and not _claim_is_stale(claim_path):
        return False, False
    if claim_path.exists():
        claim_path.unlink(missing_ok=True)
    payload = json.dumps({"pid": os.getpid(), "run_id": run_id, "at": now()}).encode("utf-8")
    try:
        fd = os.open(str(claim_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        return False, False
    try:
        os.write(fd, payload)
    finally:
        os.close(fd)
    existing = load_state(run_id)
    resume_stale = bool(existing and existing.get("status") == "RUNNING")
    return True, resume_stale


def _release_run_claim(run_id: str) -> None:
    claim_path = _claims_dir() / _safe_claim_name(run_id)
    try:
        claim_path.unlink(missing_ok=True)
    except OSError:
        pass


def _acquire_capacity_slot(run_id: str) -> int | None:
    """Cross-process concurrency cap via fixed O_EXCL slot files on the state backend."""
    slot_dir = _capacity_dir()
    slot_dir.mkdir(parents=True, exist_ok=True)
    payload = json.dumps({"pid": os.getpid(), "run_id": run_id, "at": now()}).encode("utf-8")
    for slot in range(_MAX_CONCURRENCY):
        slot_path = slot_dir / f"slot-{slot}"
        if slot_path.exists() and _claim_is_stale(slot_path):
            slot_path.unlink(missing_ok=True)
        try:
            fd = os.open(str(slot_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            continue
        try:
            os.write(fd, payload)
        finally:
            os.close(fd)
        return slot
    return None


def _release_capacity_slot(slot: int | None) -> None:
    if slot is None:
        return
    slot_path = _capacity_dir() / f"slot-{slot}"
    try:
        slot_path.unlink(missing_ok=True)
    except OSError:
        pass


def _validation_error_payload(body: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    job_id = str(body.get("job_id") or "")
    run_id = run_id_for(job_id) if JOB_RE.match(job_id) else None
    payload: dict[str, Any] = {
        "accepted": False,
        "status": "BLOCKED",
        "blocker": ",".join(errors),
        "job_id": body.get("job_id"),
    }
    if run_id and RUN_ID_RE.fullmatch(run_id):
        payload["run_id"] = run_id
        payload["status_url"] = f"/v1/executions/{run_id}"
    return payload


def _verification_registry() -> dict[str, list[str]]:
    """Server-controlled check_id -> argv registry. The HTTP request never supplies argv."""
    raw = os.environ.get("SOURCEA_SANDBOX_VERIFICATION_CHECKS_JSON", "").strip()
    if raw:
        try:
            reg = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        if isinstance(reg, dict) and all(
            isinstance(v, list) and v and all(isinstance(x, str) for x in v) for v in reg.values()
        ):
            return {str(k): [str(x) for x in v] for k, v in reg.items()}
        return {}
    return {k: list(v) for k, v in _DEFAULT_VERIFICATION_CHECKS.items()}


def _executor_argv(subst: dict[str, str]) -> list[str]:
    """Server-configured argv (SOURCEA_SANDBOX_EXECUTOR_ARGV_JSON). Only whole-token placeholders are
    substituted as individual argv values; the request controls neither the executable nor argv structure."""
    raw = os.environ.get("SOURCEA_SANDBOX_EXECUTOR_ARGV_JSON", "").strip()
    if not raw:
        raise RuntimeError("missing SOURCEA_SANDBOX_EXECUTOR_ARGV_JSON")
    try:
        tpl = json.loads(raw)
    except json.JSONDecodeError:
        raise RuntimeError("invalid SOURCEA_SANDBOX_EXECUTOR_ARGV_JSON")
    if not (isinstance(tpl, list) and tpl and all(isinstance(x, str) for x in tpl)):
        raise RuntimeError("invalid SOURCEA_SANDBOX_EXECUTOR_ARGV_JSON")
    return [subst.get(token, token) for token in tpl]


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_id_for(job_id: str) -> str:
    return "sx-" + hashlib.sha256(job_id.encode("utf-8")).hexdigest()[:24]


def _validated(pattern: "re.Pattern[str]", value: Any, error: str) -> str:
    """Return the regex-matched (sanitized) value, or raise. Used so the *matched* value flows to
    filesystem paths / subprocess args, which static analysis recognizes as sanitized."""
    match = pattern.fullmatch(str(value if value is not None else ""))
    if not match:
        raise RuntimeError(error)
    return match.group(0)


def state_path(run_id: str) -> Path:
    return STATE_DIR / os.path.basename(f"{_validated(RUN_ID_RE, run_id, 'invalid_run_id')}.json")


def load_state(run_id: str) -> dict[str, Any] | None:
    if not RUN_ID_RE.fullmatch(str(run_id)):
        return None
    # The opened path is sourced from a directory listing (not from run_id): run_id is only used in a
    # string-equality match, so no filesystem path is ever constructed from request input.
    wanted = os.path.basename(f"{run_id}.json")
    if not STATE_DIR.is_dir():
        return None
    for entry in STATE_DIR.iterdir():
        if entry.name == wanted and entry.is_file():
            return json.loads(entry.read_text(encoding="utf-8"))
    return None


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


def _allowed_path_prefixes() -> tuple[str, ...]:
    """Server-side ceiling: request patterns may narrow these roots, never widen them."""
    raw = os.environ.get(
        "SOURCEA_SANDBOX_ALLOWED_PATH_PREFIXES",
        "products/field-audit-compiler-v1/,products/sandbox-autorunner-v1/,"
        "automation-canary/,receipts/sourceb-canary/",
    )
    return tuple(x.strip().strip("/") + "/" for x in raw.split(",") if x.strip())


def validate_request(body: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not JOB_RE.match(str(body.get("job_id") or "")):
        errors.append("job_id_invalid")
    repo = str(body.get("target_repository") or "")
    if not REPO_RE.match(repo):
        errors.append("target_repository_invalid")
    elif repo not in _allowed_repos():
        errors.append("target_repository_not_allowed")
    base_branch = str(body.get("base_branch") or "")
    if not base_branch:
        errors.append("base_branch_required")
    elif not BASE_BRANCH_RE.match(base_branch):
        errors.append("base_branch_invalid")
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
    vc = body.get("verification_contract")
    if not isinstance(vc, dict):
        errors.append("verification_contract_invalid")
    else:
        if "commands" in vc:
            errors.append("verification_contract_commands_forbidden")
        checks = vc.get("checks")
        if not isinstance(checks, list) or not checks or not all(isinstance(c, str) for c in checks):
            errors.append("verification_contract_checks_invalid")
        else:
            registry = _verification_registry()
            if not registry:
                errors.append("verification_registry_unavailable")
            else:
                unknown = sorted({c for c in checks if c not in registry})
                if unknown:
                    errors.append("verification_check_unknown:" + ",".join(unknown))
    return errors


def _safe_pattern(pattern: str) -> bool:
    if not pattern or pattern.startswith("/") or ".." in Path(pattern).parts or pattern.startswith(".git"):
        return False
    # A request cannot use a root wildcard or name a repo-control surface. It must remain under
    # a server-configured canary prefix; only the server operator can widen this ceiling.
    root = pattern.split("/", 1)[0]
    if any(ch in root for ch in "*?[") or root in {".github", ".git"}:
        return False
    base = _pattern_base_path(pattern)
    return any(_under_allowed_root(base, prefix) for prefix in _allowed_path_prefixes())


def _safe_branch(branch: str) -> bool:
    parts = branch.split("/")
    return all(part not in {"", ".", ".."} for part in parts) and ".." not in branch and not branch.endswith(".")


def _path_allowed(path: str, patterns: list[str]) -> bool:
    clean = path.strip("/")
    if not clean or clean.startswith(".git/") or ".." in Path(clean).parts:
        return False
    for pattern in patterns:
        normalized = pattern.strip("/")
        if normalized.endswith("/**"):
            prefix = normalized[:-3].rstrip("/") + "/"
            if clean.startswith(prefix):
                return True
        elif fnmatch.fnmatchcase(clean, normalized):
            return True
    return False


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


def _sanitized_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    """Child env with secret env vars stripped, so request-run commands cannot read them."""
    env = os.environ.copy()
    for key in _SANITIZE_ENV_KEYS:
        env.pop(key, None)
    if extra:
        env.update(extra)
    return env


def _run(cmd: list[str], cwd: Path, timeout: int = 300, env: dict[str, str] | None = None) -> dict[str, Any]:
    # Enforce the invariant the suppression below relies on: cmd is always an explicit argv list of
    # strings, executed WITHOUT a shell. A string command (shell injection vector) is rejected outright.
    if not isinstance(cmd, list) or not all(isinstance(part, str) for part in cmd):
        raise TypeError("cmd_must_be_list_of_str")
    # False positive: all callers pass this argv list with strict-regex-validated values
    # (repo/base_sha/working_branch/job_id) or server-controlled values (executor argv / check registry),
    # and shell=False, so no command injection is possible. See PR #33 security review.
    # codeql[py/command-line-injection]
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


def execute(body: dict[str, Any], *, resume_stale: bool = False) -> dict[str, Any]:
    errors = validate_request(body)
    # run_id is a sha256-derived id; re-validate through the regex barrier so the *matched* value
    # (not the raw hash of request input) flows into the work/clone paths and git argv — CodeQL does
    # not treat hashing as a command-injection sanitizer, but re.Match.group() is recognized.
    run_id = _validated(RUN_ID_RE, run_id_for(str(body.get("job_id") or "")), "invalid_run_id")
    existing = load_state(run_id)
    if existing and not (resume_stale and existing.get("status") == "RUNNING"):
        # job_id is the immutable idempotency key. Replaying terminal truth never repeats side
        # effects. Only an orphaned RUNNING record may be resumed after the in-process owner is gone.
        return existing
    started = now()
    base = {"run_id": run_id, "job_id": body.get("job_id"), "status": "BLOCKED", "target_repository": body.get("target_repository"), "base_sha": body.get("base_sha"), "working_branch": body.get("working_branch"), "changed_paths": [], "commit_sha": None, "pull_request_url": None, "verification_evidence": [], "ci_check_references": [], "started_at": started, "completed_at": None, "blocker": None}
    if errors:
        base.update({"completed_at": now(), "blocker": ",".join(errors)})
        return save_state(base)
    save_state({**base, "status": "RUNNING"})
    safe_repo = _validated(REPO_RE, body.get("target_repository"), "target_repository_invalid")
    safe_sha = _validated(SHA_RE, body.get("base_sha"), "base_sha_invalid")
    safe_branch = _validated(BRANCH_RE, body.get("working_branch"), "working_branch_invalid")
    safe_base = _validated(BASE_BRANCH_RE, body.get("base_branch"), "base_branch_invalid")
    safe_job_id = _validated(JOB_RE, body.get("job_id"), "job_id_invalid")
    evidence: list[dict[str, Any]] = []
    work = WORK_ROOT / run_id
    try:
        shutil.rmtree(work, ignore_errors=True)
        work.mkdir(parents=True, exist_ok=True)
        clone = work / "repo"
        git_env = _git_auth_env()
        clone_row = _run(["git", "clone", "--no-checkout", _repo_url(safe_repo), str(clone)], work, timeout=600, env=git_env)
        evidence.append({"step": "git_clone", **clone_row})
        if clone_row["returncode"] != 0:
            raise RuntimeError("git_clone_failed")
        fetch = _run(["git", "fetch", "origin", safe_sha], clone, timeout=300, env=git_env)
        evidence.append({"step": "git_fetch_base_sha", **fetch})
        if fetch["returncode"] != 0:
            raise RuntimeError("git_fetch_base_sha_failed")
        checkout = _run(["git", "checkout", "-B", safe_branch, safe_sha], clone)
        evidence.append({"step": "git_checkout_working_branch", **checkout})
        if checkout["returncode"] != 0:
            raise RuntimeError("git_checkout_working_branch_failed")
        job_file = work / "sandbox_job.json"
        # Persist only the executor contract. Unknown request fields and callback metadata are
        # deliberately excluded so caller-supplied secrets cannot be copied into the worktree.
        job_payload = {
            key: body[key]
            for key in (
                "job_id", "target_repository", "base_branch", "base_sha", "working_branch",
                "sandbox_job", "allowed_paths", "verification_contract",
            )
            if key in body
        }
        job_file.write_text(json.dumps(job_payload, indent=2) + "\n", encoding="utf-8")
        env = _sanitized_env({"SANDBOX_JOB_FILE": str(job_file), "SANDBOX_REPO_DIR": str(clone), "SANDBOX_RUN_ID": run_id})
        argv = _executor_argv({"{job_file}": str(job_file), "{repo_dir}": str(clone), "{run_id}": run_id})
        executor = _run(argv, clone, timeout=int(os.environ.get("SOURCEA_SANDBOX_EXECUTOR_TIMEOUT", "600")), env=env)
        evidence.append({"step": "coding_executor", **executor})
        if executor["returncode"] != 0:
            raise RuntimeError("coding_executor_failed")
        changed = _changed_paths(clone)
        base["changed_paths"] = changed
        bad = [p for p in changed if not _path_allowed(p, list(body["allowed_paths"]))]
        if bad:
            raise RuntimeError("allowed_path_violation:" + ",".join(bad))
        registry = _verification_registry()
        if not registry:
            raise RuntimeError("verification_registry_unavailable")
        for check_id in body.get("verification_contract", {}).get("checks") or []:
            if check_id not in registry:
                raise RuntimeError("verification_check_unknown:" + str(check_id))
            row = _run(list(registry[check_id]), clone, timeout=300, env=_sanitized_env())
            evidence.append({"step": "verification_" + str(check_id), **row})
            if row["returncode"] != 0:
                raise RuntimeError("verification_failed")
        if not changed:
            raise RuntimeError("no_changes_made")
        _run(["git", "config", "user.email", os.environ.get("GIT_AUTHOR_EMAIL", "sourcea-executor@noetfield.systems")], clone)
        _run(["git", "config", "user.name", os.environ.get("GIT_AUTHOR_NAME", "SourceA Sandbox Executor")], clone)
        # Flow regex-matched values (not raw git output) into argv so static analysis sees the
        # sanitization barrier; these paths already passed _path_allowed above.
        safe_changed = [_validated(PATH_RE, p, "changed_path_invalid") for p in changed]
        add = _run(["git", "add", "--"] + safe_changed, clone); evidence.append({"step": "git_add", **add})
        commit = _run(["git", "commit", "-m", f"Execute sandbox job {safe_job_id}"], clone); evidence.append({"step": "git_commit", **commit})
        if commit["returncode"] != 0:
            raise RuntimeError("git_commit_failed")
        sha = _run(["git", "rev-parse", "HEAD"], clone); evidence.append({"step": "git_rev_parse", **sha})
        base["commit_sha"] = sha["stdout"].strip()
        if os.environ.get("SOURCEA_SANDBOX_SKIP_PUSH") == "1":
            evidence.append({"step": "git_push", "returncode": 1, "stdout": "", "stderr": "disabled by SOURCEA_SANDBOX_SKIP_PUSH"})
            raise RuntimeError("push_disabled")
        push = _run(["git", "push", "origin", f"HEAD:{safe_branch}"], clone, timeout=300, env=git_env); evidence.append({"step": "git_push", **push})
        if push["returncode"] != 0:
            raise RuntimeError("git_push_failed")
        pr_url, pr_evidence = _open_pr(safe_repo, safe_branch, safe_base, f"Sandbox job {safe_job_id}", "Automated bounded SourceA SANDBOX execution.", clone)
        evidence.extend(pr_evidence); base["pull_request_url"] = pr_url
        if not pr_url:
            raise RuntimeError("pull_request_create_failed")
        base.update({"status": "PASS", "blocker": None})
    except Exception as exc:
        base.update({"status": "FAIL" if str(exc) in {"coding_executor_failed", "verification_failed"} else "BLOCKED", "blocker": str(exc)})
    base.update({"verification_evidence": evidence, "completed_at": now()})
    return save_state(base)


def _http_result(row: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    """Return the synchronous terminal truth; never label FAIL/BLOCKED as accepted."""
    status = str(row.get("status") or "")
    run_id = str(row.get("run_id") or "")
    payload = dict(row)
    payload["accepted"] = status in {"RUNNING", "PASS"}
    if run_id:
        payload["status_url"] = f"/v1/executions/{run_id}"
    code = {"PASS": 200, "RUNNING": 202, "FAIL": 422, "BLOCKED": 409}.get(status, 500)
    return code, payload


def handle_post(body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    errors = validate_request(body)
    if errors:
        return 422, _validation_error_payload(body, errors)

    run_id = run_id_for(str(body["job_id"]))
    existing = load_state(run_id)
    if existing and existing.get("status") != "RUNNING":
        return _http_result(existing)

    slot = _acquire_capacity_slot(run_id)
    if slot is None:
        return 429, {"accepted": False, "error": "capacity_reached"}

    claimed, resume_stale = _try_acquire_run_claim(run_id)
    if not claimed:
        _release_capacity_slot(slot)
        existing = load_state(run_id)
        if existing and existing.get("status") != "RUNNING":
            return _http_result(existing)
        return 202, accepted(str(body["job_id"]))

    try:
        row = execute(body, resume_stale=resume_stale)
    finally:
        _release_run_claim(run_id)
        _release_capacity_slot(slot)
    return _http_result(row)


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
