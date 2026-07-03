#!/usr/bin/env python3
"""Read/trigger GitHub Actions via REST API — no gh CLI required.

Uses GITHUB_TOKEN or GH_TOKEN (or ~/.sina/secrets.env).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_REPO = "noetfield-systems/sourcea"
API = "https://api.github.com"


def _load_token() -> str:
    for key in ("GITHUB_TOKEN", "GH_TOKEN"):
        val = os.environ.get(key, "").strip()
        if val:
            return val
    secrets = Path.home() / ".sina" / "secrets.env"
    if secrets.is_file():
        for line in secrets.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            if k.strip() in ("GITHUB_TOKEN", "GH_TOKEN") and v.strip():
                return v.strip().strip('"').strip("'")
    return ""


def _api(method: str, path: str, *, token: str, body: dict | None = None) -> dict[str, Any]:
    url = f"{API}{path}"
    data = None
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(err_body)
        except json.JSONDecodeError:
            parsed = {"message": err_body[:300]}
        return {"ok": False, "http_status": exc.code, "error": parsed}


def list_workflow_runs(*, repo: str, workflow_file: str, token: str, per_page: int = 5) -> dict[str, Any]:
    wf = workflow_file.replace(".github/workflows/", "")
    path = f"/repos/{repo}/actions/workflows/{wf}/runs?per_page={per_page}"
    return _api("GET", path, token=token)


def dispatch_workflow(*, repo: str, workflow_file: str, ref: str, token: str) -> dict[str, Any]:
    wf = workflow_file.replace(".github/workflows/", "")
    path = f"/repos/{repo}/actions/workflows/{wf}/dispatches"
    out = _api("POST", path, token=token, body={"ref": ref})
    if out.get("error"):
        return {"ok": False, **out}
    return {"ok": True, "dispatched": True, "workflow": wf, "ref": ref}


def wait_for_run(
    *,
    repo: str,
    workflow_file: str,
    token: str,
    after_unix: float,
    timeout_s: int = 900,
    poll_s: int = 15,
) -> dict[str, Any]:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        runs = list_workflow_runs(repo=repo, workflow_file=workflow_file, token=token, per_page=5)
        for run in runs.get("workflow_runs") or []:
            created_raw = str(run.get("created_at") or "")
            try:
                created_dt = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
                created_unix = created_dt.timestamp()
            except ValueError:
                continue
            if created_unix < after_unix - 10:
                continue
            if run.get("status") == "completed":
                return {
                    "ok": True,
                    "run_id": run.get("id"),
                    "conclusion": run.get("conclusion"),
                    "html_url": run.get("html_url"),
                    "head_sha": run.get("head_sha"),
                    "status": run.get("status"),
                }
        time.sleep(poll_s)
    return {"ok": False, "error": "timeout_waiting_for_workflow_run"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=DEFAULT_REPO)
    ap.add_argument("--workflow", default="external-verify.yml")
    ap.add_argument("--ref", default="main")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--dispatch", action="store_true")
    ap.add_argument("--wait", action="store_true", help="After dispatch, poll until complete")
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    token = _load_token()
    if not token:
        out = {"ok": False, "error": "missing_GITHUB_TOKEN"}
        print(json.dumps(out, indent=2) if args.json else out["error"])
        return 1

    if args.dispatch:
        t0 = time.time()
        disp = dispatch_workflow(repo=args.repo, workflow_file=args.workflow, ref=args.ref, token=token)
        if not disp.get("ok"):
            print(json.dumps(disp, indent=2) if args.json else json.dumps(disp))
            return 1
        if args.wait:
            waited = wait_for_run(
                repo=args.repo,
                workflow_file=args.workflow,
                token=token,
                after_unix=t0,
            )
            out = {"dispatch": disp, "run": waited}
            print(json.dumps(out, indent=2) if args.json else json.dumps(out))
            return 0 if waited.get("ok") and waited.get("conclusion") == "success" else 1
        print(json.dumps(disp, indent=2) if args.json else json.dumps(disp))
        return 0

    runs = list_workflow_runs(
        repo=args.repo, workflow_file=args.workflow, token=token, per_page=args.limit
    )
    if args.json:
        print(json.dumps(runs, indent=2))
    else:
        for run in (runs.get("workflow_runs") or [])[: args.limit]:
            print(
                f"{run.get('id')} {run.get('status')} {run.get('conclusion')} "
                f"{run.get('html_url')} {str(run.get('head_sha') or '')[:8]}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
