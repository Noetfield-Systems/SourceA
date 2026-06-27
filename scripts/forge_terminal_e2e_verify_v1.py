#!/usr/bin/env python3
"""Forge Terminal E2E — open folder → scan → LLM → approve → cloud dry → outbox."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

SINA = Path.home() / ".sina"
OUTBOX = SINA / "forge-terminal-outbox"


def _port_token() -> tuple[int, str]:
    for p in (13029,):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{p}/health", timeout=2) as r:
                row = json.loads(r.read().decode())
            if row.get("service") == "forge-terminal":
                return p, str(row.get("forge_local_token") or "")
        except Exception:
            continue
    raise SystemExit("Start Forge Terminal.app on :13029 (service=forge-terminal)")


def _post(port: int, body: dict, token: str = "", timeout: float = 120) -> tuple[float, dict]:
    data = json.dumps(body).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["X-Forge-Token"] = token
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/api/forge-terminal/v1",
        data=data,
        headers=headers,
        method="POST",
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return time.time() - t0, json.loads(resp.read().decode())


def _get(port: int, path: str, timeout: float = 10) -> tuple[float, dict]:
    t0 = time.time()
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=timeout) as r:
        return time.time() - t0, json.loads(r.read().decode())


def main() -> int:
    port, token = _port_token()
    checks: list[tuple[str, bool, str]] = []

    _get(port, "/api/forge-terminal/v1?status=1&light=1")  # warm cache
    el, light = _get(port, "/api/forge-terminal/v1?status=1&light=1")
    checks.append(("status_light <0.5s", el < 0.5, f"{el:.3f}s"))
    checks.append(("status_light ok", light.get("ok") is True, ""))

    td = Path(tempfile.mkdtemp(prefix="forge-e2e-"))
    (td / "README.md").write_text("# E2E test project\n", encoding="utf-8")

    try:
        el, op = _post(port, {"action": "open_folder", "path": str(td)}, token=token)
        scan = op.get("scan") or {}
        checks.append(("open_folder", op.get("ok") is True, op.get("error") or ""))
        checks.append(("file_tree", len(scan.get("entries") or []) >= 1, str(len(scan.get("entries") or []))))

        el, snap = _post(port, {"action": "workspace_snapshot", "workspace_path": str(td)}, token=token)
        checks.append(("workspace_snapshot", snap.get("ok") is True, ""))

        el, run = _post(
            port,
            {
                "action": "run",
                "text": "List the top files in this project",
                "full_llm": True,
                "fast": True,
                "model": "gpt-4o",
                "workspace_path": str(td),
            },
            token=token,
        )
        llm = run.get("llm") or {}
        checks.append(
            ("llm_run", run.get("ok") and llm.get("provider") not in (None, "forge_only"), llm.get("provider") or "")
        )
        checks.append(("llm_under_15s", el < 15, f"{el:.1f}s"))
        qg = run.get("quality_gate") or (run.get("decision_card") or {}).get("quality_gate") or {}
        checks.append(("quality_gate", len(qg.get("layers") or []) == 11, qg.get("verdict") or ""))
        run_id = str(run.get("run_id") or "")

        _post(port, {"action": "decide", "run_id": run_id, "decision": "approved", "workspace_path": str(td)}, token=token)
        if qg.get("execution_allowed"):
            el, cloud = _post(
                port,
                {"action": "send_cloud", "run_id": run_id, "dry_run": True, "workspace_path": str(td)},
                token=token,
            )
            checks.append(("cloud_dry", cloud.get("ok") is True, cloud.get("error") or ""))
            ob = OUTBOX / f"{run_id}.json"
            checks.append(("outbox", ob.is_file(), str(ob)))
        else:
            el, cloud = _post(
                port,
                {"action": "send_cloud", "run_id": run_id, "dry_run": True, "workspace_path": str(td)},
                token=token,
            )
            checks.append(("cloud blocked", cloud.get("error") == "quality_gate_blocked", cloud.get("error") or ""))
    finally:
        shutil.rmtree(td, ignore_errors=True)

    print(f"Forge E2E on :{port}\n")
    passed = sum(1 for name, ok, detail in checks if ok)
    for name, ok, detail in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))
    print(f"\n{passed}/{len(checks)} passed")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
