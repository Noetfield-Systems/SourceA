from __future__ import annotations

import json
import subprocess
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from scripts import sandbox_executor_adapter_v1 as sx
from scripts.fbe_cloud_worker_http_v1 import FbeWorkerHandler, _auth_ok, _executor_auth

BASE_SHA = "a" * 40

# Server-configured executor argv (NO shell): creates the expected output file from the run id.
EXEC_ARGV = [
    "python3", "-c",
    "import os,pathlib;d=pathlib.Path('products/field-audit-compiler-v1');d.mkdir(parents=True,exist_ok=True);(d/'output.txt').write_text(os.environ.get('SANDBOX_RUN_ID',''))",
]


def job(**overrides):
    row = {
        "job_id": "job-001",
        "target_repository": "Noetfield-Systems/SANDBOX",
        "base_branch": "main",
        "base_sha": BASE_SHA,
        "working_branch": "automation/job-001",
        "sandbox_job": {},
        "allowed_paths": ["products/field-audit-compiler-v1/**"],
        "verification_contract": {"checks": ["fixture_schema"]},
        "receipt_callback": None,
    }
    row.update(overrides)
    return row


class _FakeHandler:
    def __init__(self, auth: str | None = None):
        self.headers = {} if auth is None else {"Authorization": auth}


@pytest.fixture()
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(sx, "STATE_DIR", tmp_path / "state")
    monkeypatch.setattr(sx, "WORK_ROOT", tmp_path / "work")
    monkeypatch.setenv("SOURCEA_SANDBOX_ALLOWED_REPOSITORIES", "Noetfield-Systems/SANDBOX")
    monkeypatch.delenv("SOURCEA_SANDBOX_VERIFICATION_CHECKS_JSON", raising=False)
    yield tmp_path


def set_executor(monkeypatch, argv=None):
    monkeypatch.setenv("SOURCEA_SANDBOX_EXECUTOR_ARGV_JSON", json.dumps(argv or EXEC_ARGV))


def init_remote(tmp_path: Path):
    src = tmp_path / "src"
    remote = tmp_path / "remote.git"
    src.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=src, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=src, check=True)
    subprocess.run(["git", "config", "user.name", "Tester"], cwd=src, check=True)
    (src / "products/field-audit-compiler-v1").mkdir(parents=True)
    (src / "products/field-audit-compiler-v1/README.md").write_text("fixture\n")
    subprocess.run(["git", "add", "."], cwd=src, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=src, check=True, capture_output=True)
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=src, text=True).strip()
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    subprocess.run(["git", "remote", "add", "origin", str(remote)], cwd=src, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=src, check=True, capture_output=True)
    return remote, sha


# ---------------------------------------------------------------- validation / core

def test_request_validation_and_prohibited_repo(isolated):
    assert "base_sha_invalid" in sx.validate_request(job(base_sha="bad"))
    assert "target_repository_not_allowed" in sx.validate_request(job(target_repository="Other/Repo"))
    assert "allowed_paths_invalid" in sx.validate_request(job(allowed_paths=["../secret/**"]))
    assert "allowed_paths_invalid" in sx.validate_request(job(allowed_paths=["*"]))
    assert "allowed_paths_invalid" in sx.validate_request(job(allowed_paths=[".github/**"]))


def test_branch_naming(isolated):
    assert "working_branch_invalid" in sx.validate_request(job(working_branch="main"))
    assert "working_branch_invalid" in sx.validate_request(job(working_branch="automation/../escape"))
    assert not sx.validate_request(job(working_branch="automation/safe-branch"))


def test_recursive_allowed_paths_are_explicit(isolated):
    assert sx._path_allowed(
        "products/field-audit-compiler-v1/nested/deep/output.json",
        ["products/field-audit-compiler-v1/**"],
    )
    assert not sx._path_allowed(
        "products/other/output.json",
        ["products/field-audit-compiler-v1/**"],
    )


def test_idempotency_persistent_state(isolated):
    row1 = sx.execute(job(base_sha="bad"))
    row2 = sx.execute(job(base_sha="bad"))
    assert row1["run_id"] == row2["run_id"]
    assert sx.load_state(row1["run_id"])["blocker"] == "base_sha_invalid"


def test_orphaned_running_state_is_recovered(isolated, tmp_path, monkeypatch):
    remote, sha = init_remote(tmp_path)
    monkeypatch.setattr(sx, "_repo_url", lambda repo: str(remote))
    monkeypatch.setattr(sx, "_open_pr", lambda *a, **k: ("https://x/pull/10", [{"step": "fake_pr", "returncode": 0}]))
    set_executor(monkeypatch)
    body = job(job_id="job-stale", base_sha=sha, working_branch="automation/job-stale")
    run_id = sx.run_id_for(body["job_id"])
    sx.save_state({"run_id": run_id, "job_id": body["job_id"], "status": "RUNNING"})
    code, row = sx.handle_post(body)
    assert code == 200
    assert row["status"] == "PASS"
    assert row["accepted"] is True


def test_missing_executor_argv_blocks(isolated, tmp_path, monkeypatch):
    remote, sha = init_remote(tmp_path)
    monkeypatch.setattr(sx, "_repo_url", lambda repo: str(remote))
    monkeypatch.delenv("SOURCEA_SANDBOX_EXECUTOR_ARGV_JSON", raising=False)
    row = sx.execute(job(job_id="job-missing-argv", base_sha=sha, working_branch="automation/job-missing-argv"))
    assert row["status"] == "BLOCKED"
    assert row["blocker"] == "missing SOURCEA_SANDBOX_EXECUTOR_ARGV_JSON"


def test_executor_failure(isolated, tmp_path, monkeypatch):
    remote, sha = init_remote(tmp_path)
    monkeypatch.setattr(sx, "_repo_url", lambda repo: str(remote))
    set_executor(monkeypatch, ["python3", "-c", "import sys; sys.exit(7)"])
    row = sx.execute(job(job_id="job-exec-fail", base_sha=sha, working_branch="automation/job-exec-fail"))
    assert row["status"] == "FAIL"
    assert row["blocker"] == "coding_executor_failed"


def test_allowed_path_violation(isolated, tmp_path, monkeypatch):
    remote, sha = init_remote(tmp_path)
    monkeypatch.setattr(sx, "_repo_url", lambda repo: str(remote))
    set_executor(monkeypatch, ["python3", "-c", "open('outside.txt','w').write('bad')"])
    row = sx.execute(job(job_id="job-path-fail", base_sha=sha, working_branch="automation/job-path-fail"))
    assert row["status"] == "BLOCKED"
    assert row["blocker"].startswith("allowed_path_violation")


def test_isolated_worktree_and_terminal_receipt_schema(isolated, tmp_path, monkeypatch):
    remote, sha = init_remote(tmp_path)
    monkeypatch.setattr(sx, "_repo_url", lambda repo: str(remote))
    monkeypatch.setattr(sx, "_open_pr", lambda *a, **k: ("https://github.com/Noetfield-Systems/SANDBOX/pull/1", [{"step": "fake_pr", "returncode": 0}]))
    set_executor(monkeypatch)
    row = sx.execute(job(job_id="job-pass", base_sha=sha, working_branch="automation/job-pass"))
    assert row["status"] == "PASS"
    assert row["commit_sha"] and len(row["commit_sha"]) == 40
    assert row["pull_request_url"].endswith("/pull/1")
    assert row["changed_paths"] == ["products/field-audit-compiler-v1/output.txt"]
    assert (sx.WORK_ROOT / row["run_id"] / "repo" / "products/field-audit-compiler-v1/output.txt").is_file()


def test_github_token_not_leaked_in_evidence(isolated, tmp_path, monkeypatch):
    remote, sha = init_remote(tmp_path)
    monkeypatch.setattr(sx, "_repo_url", lambda repo: str(remote))
    monkeypatch.setenv("GITHUB_TOKEN", "ghs_secret_token_for_test")
    monkeypatch.delenv("SOURCEA_SANDBOX_EXECUTOR_ARGV_JSON", raising=False)
    row = sx.execute(job(job_id="job-redact", base_sha=sha, working_branch="automation/job-redact"))
    assert "ghs_secret_token_for_test" not in json.dumps(row)


# ---------------------------------------------------------------- correction 2: no request shell

def test_raw_commands_are_rejected(isolated):
    errs = sx.validate_request(job(verification_contract={"commands": ["rm -rf /"]}))
    assert "verification_contract_commands_forbidden" in errs
    assert "verification_contract_checks_invalid" in errs  # commands is not checks


def test_unknown_check_id_is_rejected(isolated):
    assert any(e.startswith("verification_check_unknown:") for e in sx.validate_request(job(verification_contract={"checks": ["definitely_not_a_real_check"]})))
    assert not sx.validate_request(job())  # fixture_schema is a registered default


def test_registered_check_executes_without_a_shell(isolated, tmp_path, monkeypatch):
    remote, sha = init_remote(tmp_path)
    monkeypatch.setattr(sx, "_repo_url", lambda repo: str(remote))
    monkeypatch.setattr(sx, "_open_pr", lambda *a, **k: ("https://x/pull/9", [{"step": "fake_pr", "returncode": 0}]))
    monkeypatch.setenv("SOURCEA_SANDBOX_VERIFICATION_CHECKS_JSON", json.dumps({"proof": ["python3", "-c", "print('CHECK_RAN')"]}))
    set_executor(monkeypatch)
    row = sx.execute(job(job_id="job-check", base_sha=sha, working_branch="automation/job-check", verification_contract={"checks": ["proof"]}))
    assert row["status"] == "PASS"
    step = next(e for e in row["verification_evidence"] if e["step"] == "verification_proof")
    assert step["returncode"] == 0 and "CHECK_RAN" in step["stdout"]
    assert step["cmd"] == ["python3", "-c", "print('CHECK_RAN')"]  # argv, not a shell string
    assert "bash" not in json.dumps(row)


def test_verification_check_failure(isolated, tmp_path, monkeypatch):
    remote, sha = init_remote(tmp_path)
    monkeypatch.setattr(sx, "_repo_url", lambda repo: str(remote))
    monkeypatch.setenv("SOURCEA_SANDBOX_VERIFICATION_CHECKS_JSON", json.dumps({"boom": ["python3", "-c", "import sys; sys.exit(9)"]}))
    set_executor(monkeypatch)
    row = sx.execute(job(job_id="job-vfail", base_sha=sha, working_branch="automation/job-vfail", verification_contract={"checks": ["boom"]}))
    assert row["status"] == "FAIL" and row["blocker"] == "verification_failed"


# ---------------------------------------------------------------- correction 3: fixed argv executor

def test_executor_argv_executes_without_a_shell(isolated, tmp_path, monkeypatch):
    remote, sha = init_remote(tmp_path)
    monkeypatch.setattr(sx, "_repo_url", lambda repo: str(remote))
    monkeypatch.setattr(sx, "_open_pr", lambda *a, **k: ("https://x/pull/3", [{"step": "fake_pr", "returncode": 0}]))
    set_executor(monkeypatch)
    row = sx.execute(job(job_id="job-argv", base_sha=sha, working_branch="automation/job-argv"))
    exec_step = next(e for e in row["verification_evidence"] if e["step"] == "coding_executor")
    assert exec_step["cmd"][0] == "python3" and "bash" not in exec_step["cmd"]


def test_secrets_absent_from_child_environment(isolated, tmp_path, monkeypatch):
    remote, sha = init_remote(tmp_path)
    monkeypatch.setattr(sx, "_repo_url", lambda repo: str(remote))
    monkeypatch.setattr(sx, "_open_pr", lambda *a, **k: ("https://x/pull/4", [{"step": "fake_pr", "returncode": 0}]))
    monkeypatch.setenv("GITHUB_TOKEN", "ghs_leaktest")
    monkeypatch.setenv("SOURCEA_SANDBOX_EXECUTOR_SECRET", "exec_secret_leaktest")
    set_executor(monkeypatch, ["python3", "-c",
        "import os,json,pathlib;d=pathlib.Path('products/field-audit-compiler-v1');d.mkdir(parents=True,exist_ok=True);(d/'output.txt').write_text(json.dumps(sorted(os.environ.keys())))"])
    row = sx.execute(job(job_id="job-env", base_sha=sha, working_branch="automation/job-env"))
    dumped = (sx.WORK_ROOT / row["run_id"] / "repo" / "products/field-audit-compiler-v1/output.txt").read_text()
    keys = json.loads(dumped)
    assert "GITHUB_TOKEN" not in keys
    assert "GITHUB_PERSONAL_ACCESS_TOKEN" not in keys
    assert "FBE_INTERNAL_SECRET" not in keys
    assert "SOURCEA_SANDBOX_EXECUTOR_SECRET" not in keys
    assert "SANDBOX_RUN_ID" in keys  # non-secret run context still passed through


def test_sanitized_env_strips_all_secret_keys(monkeypatch):
    for k in ("GITHUB_TOKEN", "GITHUB_PERSONAL_ACCESS_TOKEN", "FBE_INTERNAL_SECRET", "SOURCEA_SANDBOX_EXECUTOR_SECRET"):
        monkeypatch.setenv(k, "x")
    env = sx._sanitized_env({"SANDBOX_RUN_ID": "sx-abc"})
    for k in ("GITHUB_TOKEN", "GITHUB_PERSONAL_ACCESS_TOKEN", "FBE_INTERNAL_SECRET", "SOURCEA_SANDBOX_EXECUTOR_SECRET"):
        assert k not in env
    assert env["SANDBOX_RUN_ID"] == "sx-abc"


# ---------------------------------------------------------------- correction 1: executor-only auth

def test_legacy_fbe_auth_unchanged(monkeypatch):
    monkeypatch.delenv("FBE_INTERNAL_SECRET", raising=False)
    assert _auth_ok(_FakeHandler()) is True  # legacy fail-open PRESERVED for existing FBE routes
    monkeypatch.setenv("FBE_INTERNAL_SECRET", "fbe")
    assert _auth_ok(_FakeHandler("Bearer fbe")) is True
    assert _auth_ok(_FakeHandler("Bearer wrong")) is False


def test_executor_auth_fails_closed_independently(monkeypatch):
    monkeypatch.delenv("SOURCEA_SANDBOX_EXECUTOR_SECRET", raising=False)
    assert _executor_auth(_FakeHandler()) == (503, "executor_not_configured")
    monkeypatch.setenv("SOURCEA_SANDBOX_EXECUTOR_SECRET", "es")
    assert _executor_auth(_FakeHandler()) == (401, "unauthorized")
    assert _executor_auth(_FakeHandler("Bearer nope")) == (403, "forbidden")
    assert _executor_auth(_FakeHandler("Bearer es")) is None


# ---------------------------------------------------------------- correction 4: concurrency

def test_max_two_concurrent_and_third_gets_429(isolated):
    slot0 = sx._acquire_capacity_slot("sx-" + "a" * 24)
    slot1 = sx._acquire_capacity_slot("sx-" + "b" * 24)
    assert slot0 is not None and slot1 is not None
    try:
        code, row = sx.handle_post(job())  # third -> capacity
        assert code == 429 and row["error"] == "capacity_reached"
    finally:
        sx._release_capacity_slot(slot0)
        sx._release_capacity_slot(slot1)


# ---------------------------------------------------------------- regression: three current review findings

def test_path_prefix_boundary_rejects_lookalike_prefix(isolated):
    evil = "products/field-audit-compiler-v1-evil/**"
    assert "allowed_paths_invalid" in sx.validate_request(job(allowed_paths=[evil]))
    assert not sx._safe_pattern(evil)
    assert sx._safe_pattern("products/field-audit-compiler-v1/**")
    assert sx._safe_pattern("products/field-audit-compiler-v1/nested/**")


def test_invalid_post_returns_422_without_execute_or_disk(isolated, monkeypatch):
    called = {"execute": 0}

    def _boom(*_a, **_k):
        called["execute"] += 1
        raise AssertionError("execute must not run for invalid POST")

    monkeypatch.setattr(sx, "execute", _boom)
    body = job(base_sha="bad")
    code, row = sx.handle_post(body)
    assert code == 422
    assert row["accepted"] is False
    assert row["status"] == "BLOCKED"
    assert "base_sha_invalid" in row["blocker"]
    assert called["execute"] == 0
    assert not list(sx.STATE_DIR.glob("*.json"))


def test_durable_run_claim_blocks_cross_process_duplicate(isolated):
    run_id = sx.run_id_for("job-dup-claim")
    claimed1, _ = sx._try_acquire_run_claim(run_id)
    claimed2, _ = sx._try_acquire_run_claim(run_id)
    assert claimed1 is True
    assert claimed2 is False
    sx._release_run_claim(run_id)
    claimed3, _ = sx._try_acquire_run_claim(run_id)
    assert claimed3 is True
    sx._release_run_claim(run_id)


def test_handle_post_duplicate_job_returns_accepted_without_second_execute(isolated, monkeypatch):
    remote_calls = {"n": 0}
    original_execute = sx.execute

    def counting_execute(body, **kwargs):
        remote_calls["n"] += 1
        return original_execute(body, **kwargs)

    monkeypatch.setattr(sx, "execute", counting_execute)
    body = job(job_id="job-dup-post", base_sha="bad")  # invalid -> fast 422, no execute
    code1, row1 = sx.handle_post(body)
    code2, row2 = sx.handle_post(body)
    assert code1 == 422 and code2 == 422
    assert remote_calls["n"] == 0
    assert not list(sx.STATE_DIR.glob("*.json"))

    # valid body: second concurrent claim should not re-enter execute
    body_ok = job(job_id="job-dup-post-ok")
    sx._try_acquire_run_claim(sx.run_id_for(body_ok["job_id"]))
    code3, row3 = sx.handle_post(body_ok)
    assert code3 == 202 and row3["accepted"] is True
    assert remote_calls["n"] == 0
    sx._release_run_claim(sx.run_id_for(body_ok["job_id"]))


# ---------------------------------------------------------------- correction: traversal + HTTP e2e

def test_load_state_rejects_traversal_and_bad_run_id(isolated):
    assert sx.load_state("../../etc/passwd") is None
    assert sx.load_state("sx-not-hex-XXXX") is None
    assert sx.load_state("") is None
    assert sx.load_state("sx-" + "a" * 24) is None


def test_fbe_http_execution_routes_e2e(isolated, tmp_path, monkeypatch):
    remote, sha = init_remote(tmp_path)
    monkeypatch.setattr(sx, "_repo_url", lambda repo: str(remote))
    monkeypatch.setattr(sx, "_open_pr", lambda *a, **k: ("https://github.com/Noetfield-Systems/SANDBOX/pull/2", [{"step": "fake_pr", "returncode": 0}]))
    monkeypatch.setitem(sys.modules, "sandbox_executor_adapter_v1", sx)
    set_executor(monkeypatch)
    monkeypatch.setenv("SOURCEA_SANDBOX_EXECUTOR_SECRET", "exec-secret")
    server = ThreadingHTTPServer(("127.0.0.1", 0), FbeWorkerHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        body = job(job_id="job-http", base_sha=sha, working_branch="automation/job-http")
        # missing auth -> 401
        with pytest.raises(urllib.error.HTTPError) as e401:
            urllib.request.urlopen(urllib.request.Request(base + "/v1/executions", data=json.dumps(body).encode(), method="POST", headers={"Content-Type": "application/json"}), timeout=30)
        assert e401.value.code == 401
        # authorized POST -> 202
        req = urllib.request.Request(base + "/v1/executions", data=json.dumps(body).encode(), method="POST",
                                     headers={"Content-Type": "application/json", "Authorization": "Bearer exec-secret"})
        accepted = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
        assert accepted["accepted"] is True
        # GET requires auth too
        with pytest.raises(urllib.error.HTTPError) as g401:
            urllib.request.urlopen(base + accepted["status_url"], timeout=30)
        assert g401.value.code == 401
        status = json.loads(urllib.request.urlopen(urllib.request.Request(base + accepted["status_url"], headers={"Authorization": "Bearer exec-secret"}), timeout=30).read().decode())
        assert status["status"] == "PASS"
        assert status["changed_paths"] == ["products/field-audit-compiler-v1/output.txt"]
    finally:
        server.shutdown()
        thread.join(timeout=5)
