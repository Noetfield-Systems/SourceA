from __future__ import annotations

import json
import subprocess
import sys
import threading
import urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from scripts import sandbox_executor_adapter_v1 as sx
from scripts.fbe_cloud_worker_http_v1 import FbeWorkerHandler

BASE_SHA = "a" * 40


def job(**overrides):
    row = {
        "job_id": "job-001",
        "target_repository": "Noetfield-Systems/SANDBOX",
        "base_branch": "main",
        "base_sha": BASE_SHA,
        "working_branch": "automation/job-001",
        "sandbox_job": {},
        "allowed_paths": ["products/field-audit-compiler-v1/**"],
        "verification_contract": {"commands": ["test -f products/field-audit-compiler-v1/output.txt"]},
        "receipt_callback": None,
    }
    row.update(overrides)
    return row


@pytest.fixture()
def isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(sx, "STATE_DIR", tmp_path / "state")
    monkeypatch.setattr(sx, "WORK_ROOT", tmp_path / "work")
    monkeypatch.setenv("SOURCEA_SANDBOX_ALLOWED_REPOSITORIES", "Noetfield-Systems/SANDBOX")
    yield tmp_path


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


def test_request_validation_and_prohibited_repo(isolated):
    assert "base_sha_invalid" in sx.validate_request(job(base_sha="bad"))
    assert "target_repository_not_allowed" in sx.validate_request(job(target_repository="Other/Repo"))
    assert "allowed_paths_invalid" in sx.validate_request(job(allowed_paths=["../secret/**"]))


def test_branch_naming(isolated):
    assert "working_branch_invalid" in sx.validate_request(job(working_branch="main"))
    assert "working_branch_invalid" in sx.validate_request(job(working_branch="automation/../escape"))
    assert not sx.validate_request(job(working_branch="automation/safe-branch"))


def test_idempotency_persistent_state(isolated):
    row1 = sx.execute(job(base_sha="bad"))
    row2 = sx.execute(job(base_sha="bad"))
    assert row1["run_id"] == row2["run_id"]
    assert sx.load_state(row1["run_id"])["blocker"] == "base_sha_invalid"


def test_missing_credentials_blocks(isolated, tmp_path, monkeypatch):
    remote, sha = init_remote(tmp_path)
    monkeypatch.setattr(sx, "_repo_url", lambda repo: str(remote))
    monkeypatch.delenv("SOURCEA_SANDBOX_EXECUTOR_CMD", raising=False)
    row = sx.execute(job(job_id="job-missing-cmd", base_sha=sha, working_branch="automation/job-missing-cmd"))
    assert row["status"] == "BLOCKED"
    assert row["blocker"] == "missing SOURCEA_SANDBOX_EXECUTOR_CMD"


def test_executor_failure(isolated, tmp_path, monkeypatch):
    remote, sha = init_remote(tmp_path)
    monkeypatch.setattr(sx, "_repo_url", lambda repo: str(remote))
    monkeypatch.setenv("SOURCEA_SANDBOX_EXECUTOR_CMD", "exit 7")
    row = sx.execute(job(job_id="job-exec-fail", base_sha=sha, working_branch="automation/job-exec-fail"))
    assert row["status"] == "FAIL"
    assert row["blocker"] == "coding_executor_failed"


def test_verification_failure(isolated, tmp_path, monkeypatch):
    remote, sha = init_remote(tmp_path)
    monkeypatch.setattr(sx, "_repo_url", lambda repo: str(remote))
    monkeypatch.setenv("SOURCEA_SANDBOX_EXECUTOR_CMD", "mkdir -p products/field-audit-compiler-v1 && echo x > products/field-audit-compiler-v1/output.txt")
    row = sx.execute(job(job_id="job-verify-fail", base_sha=sha, working_branch="automation/job-verify-fail", verification_contract={"commands": ["exit 9"]}))
    assert row["status"] == "FAIL"
    assert row["blocker"] == "verification_failed"


def test_allowed_path_violation(isolated, tmp_path, monkeypatch):
    remote, sha = init_remote(tmp_path)
    monkeypatch.setattr(sx, "_repo_url", lambda repo: str(remote))
    monkeypatch.setenv("SOURCEA_SANDBOX_EXECUTOR_CMD", "echo bad > outside.txt")
    row = sx.execute(job(job_id="job-path-fail", base_sha=sha, working_branch="automation/job-path-fail"))
    assert row["status"] == "BLOCKED"
    assert row["blocker"].startswith("allowed_path_violation")


def test_isolated_worktree_and_terminal_receipt_schema(isolated, tmp_path, monkeypatch):
    remote, sha = init_remote(tmp_path)
    monkeypatch.setattr(sx, "_repo_url", lambda repo: str(remote))
    monkeypatch.setattr(sx, "_open_pr", lambda *args, **kwargs: ("https://github.com/Noetfield-Systems/SANDBOX/pull/1", [{"step": "fake_pr", "returncode": 0}]))
    monkeypatch.setenv("SOURCEA_SANDBOX_EXECUTOR_CMD", "mkdir -p products/field-audit-compiler-v1 && echo $SANDBOX_RUN_ID > products/field-audit-compiler-v1/output.txt")
    monkeypatch.setenv("SOURCEA_SANDBOX_SKIP_PUSH", "1")
    body = job(job_id="job-pass", base_sha=sha, working_branch="automation/job-pass")
    row = sx.execute(body)
    assert row["status"] == "PASS"
    assert row["commit_sha"] and len(row["commit_sha"]) == 40
    assert row["pull_request_url"].endswith("/pull/1")
    assert row["changed_paths"] == ["products/field-audit-compiler-v1/output.txt"]
    assert row["completed_at"]
    assert (sx.WORK_ROOT / row["run_id"] / "repo" / "products/field-audit-compiler-v1/output.txt").is_file()


def test_github_token_not_leaked_in_evidence(isolated, tmp_path, monkeypatch):
    remote, sha = init_remote(tmp_path)
    monkeypatch.setattr(sx, "_repo_url", lambda repo: str(remote))
    monkeypatch.setenv("GITHUB_TOKEN", "ghs_secret_token_for_test")
    monkeypatch.delenv("SOURCEA_SANDBOX_EXECUTOR_CMD", raising=False)
    row = sx.execute(job(job_id="job-redact", base_sha=sha, working_branch="automation/job-redact"))
    serialized = json.dumps(row)
    assert "ghs_secret_token_for_test" not in serialized


def test_fbe_http_execution_routes_e2e(isolated, tmp_path, monkeypatch):
    remote, sha = init_remote(tmp_path)
    monkeypatch.setattr(sx, "_repo_url", lambda repo: str(remote))
    monkeypatch.setattr(sx, "_open_pr", lambda *args, **kwargs: ("https://github.com/Noetfield-Systems/SANDBOX/pull/2", [{"step": "fake_pr", "returncode": 0}]))
    monkeypatch.setitem(sys.modules, "sandbox_executor_adapter_v1", sx)
    monkeypatch.setenv("SOURCEA_SANDBOX_EXECUTOR_CMD", "mkdir -p products/field-audit-compiler-v1 && echo http > products/field-audit-compiler-v1/output.txt")
    monkeypatch.setenv("SOURCEA_SANDBOX_SKIP_PUSH", "1")
    monkeypatch.setenv("FBE_INTERNAL_SECRET", "http-secret")
    server = ThreadingHTTPServer(("127.0.0.1", 0), FbeWorkerHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_port}/v1/executions"
        body = job(job_id="job-http", base_sha=sha, working_branch="automation/job-http")
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json", "Authorization": "Bearer http-secret"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            accepted = json.loads(resp.read().decode("utf-8"))
        assert accepted["accepted"] is True
        status_req = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}{accepted['status_url']}",
            headers={"Authorization": "Bearer http-secret"},
        )
        with urllib.request.urlopen(status_req, timeout=30) as resp:
            status = json.loads(resp.read().decode("utf-8"))
        assert status["status"] == "PASS"
        assert status["changed_paths"] == ["products/field-audit-compiler-v1/output.txt"]
        assert status["pull_request_url"].endswith("/pull/2")
    finally:
        server.shutdown()
        thread.join(timeout=5)
