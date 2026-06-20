#!/usr/bin/env python3
"""
Light E2E gate — SourceA hub.
No blocking /refresh. Completes in < 30s.
Includes four-rule static proof.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUB = "http://127.0.0.1:13020"
WORKER = "http://127.0.0.1:13030"
REFRESH_E2E_BUDGET_SEC = 360  # sa-0853
FAIL: list[str] = []
SERVE_SCRIPT = ROOT / "scripts" / "serve-sina-command.sh"
WORKER_SERVE = ROOT / "scripts" / "serve-hub-rebuild-worker.sh"


def _hub_health_ok(*, timeout: int = 8) -> bool:
    try:
        with urllib.request.urlopen(f"{HUB}/health", timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
            return r.status == 200 and bool(data.get("ok"))
    except Exception:
        return False


def _worker_health_ok(*, timeout: int = 5) -> bool:
    try:
        with urllib.request.urlopen(f"{WORKER}/health", timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
            return (
                r.status == 200
                and bool(data.get("ok"))
                and data.get("service") == "hub-rebuild-worker"
            )
    except Exception:
        return False


def _ensure_worker_via_serve() -> None:
    if _worker_health_ok():
        print("OK: rebuild worker health on :13030 before light E2E")
        return
    if not WORKER_SERVE.is_file():
        FAIL.append("ERROR   worker preflight: serve-hub-rebuild-worker.sh missing")
        return
    try:
        subprocess.run(
            ["bash", str(WORKER_SERVE)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        FAIL.append("ERROR   worker preflight: serve-hub-rebuild-worker.sh timed out")
        return
    if _worker_health_ok():
        print("OK: serve-hub-rebuild-worker.sh brought worker up before light E2E")
    else:
        FAIL.append("ERROR   worker preflight: :13030 still down after serve")


def _ensure_hub_via_serve() -> None:
    if _hub_health_ok():
        print("OK: hub health on :13020 before light E2E")
    elif not SERVE_SCRIPT.is_file():
        FAIL.append("ERROR   hub preflight: serve-sina-command.sh missing")
        return
    else:
        try:
            subprocess.run(
                ["bash", str(SERVE_SCRIPT)],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=90,
            )
        except subprocess.TimeoutExpired:
            FAIL.append("ERROR   hub preflight: serve-sina-command.sh timed out")
            return
        if _hub_health_ok():
            print("OK: serve-sina-command.sh brought hub up before light E2E")
        else:
            FAIL.append("ERROR   hub preflight: :13020 still down after serve")
            return
    _ensure_worker_via_serve()


def chk(
    name: str,
    method: str,
    path: str,
    body: dict | None = None,
    *,
    max_ms: int = 2000,
    expect: int = 200,
) -> None:
    t0 = time.time()
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        f"{HUB}{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if data else {},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            ms = int((time.time() - t0) * 1000)
            json.loads(r.read())
            if r.status != expect:
                FAIL.append(f"STATUS  {name}: got {r.status}, want {expect}")
            elif ms > max_ms:
                FAIL.append(f"SLOW    {name}: {ms}ms > {max_ms}ms limit")
            else:
                print(f"PASS    {name} ({ms}ms)")
    except Exception as e:
        FAIL.append(f"ERROR   {name}: {e}")


def main() -> int:
    _ensure_hub_via_serve()
    if any(
        f.startswith("ERROR   hub preflight") or f.startswith("ERROR   worker preflight")
        for f in FAIL
    ):
        for f in FAIL:
            print(" ", f)
        return 1

    chk("health", "GET", "/health", max_ms=500)
    chk("hub-sync", "GET", "/api/hub-sync", max_ms=800)
    chk("agent-loop", "GET", "/api/agent-loop", max_ms=5000)
    chk("ic-get", "GET", "/api/intelligence-circle", max_ms=3000)
    chk("prompt-queue", "GET", "/api/prompt-queue", max_ms=3000)
    chk(
        "clear-session",
        "POST",
        "/api/intelligence-circle",
        body={"action": "clear_session"},
        max_ms=5000,
    )

    gid_before = 0
    try:
        with urllib.request.urlopen(f"{HUB}/api/hub-sync", timeout=5) as r:
            gid_before = int(json.loads(r.read().decode("utf-8")).get("generation_id", 0))
    except Exception as e:
        FAIL.append(f"ERROR   generation_id baseline: {e}")

    chk(
        "refresh-light",
        "POST",
        "/refresh",
        body={"mode": "light"},
        max_ms=10000,
        expect=200,
    )

    gid_after = gid_before
    for _ in range(60):
        try:
            with urllib.request.urlopen(f"{HUB}/api/hub-sync", timeout=5) as r:
                gid_after = int(json.loads(r.read().decode("utf-8")).get("generation_id", 0))
            if gid_after > gid_before:
                break
        except Exception:
            pass
        time.sleep(0.5)

    if gid_after > gid_before:
        print(f"PASS    generation_id incremented {gid_before} → {gid_after}")
    else:
        FAIL.append(
            f"FAIL    generation_id did not increment after /refresh "
            f"(before={gid_before}, after={gid_after})"
        )

    shell_path = ROOT / "agent-control-panel" / "command-data-shell.json"
    try:
        shell = json.loads(shell_path.read_text(encoding="utf-8"))
        if "generation_id" not in shell:
            FAIL.append("FAIL    generation_id missing from command-data-shell.json")
        else:
            print(f"PASS    shell generation_id={shell['generation_id']}")
    except Exception as e:
        FAIL.append(f"ERROR   shell generation_id check: {e}")

    truth = Path.home() / ".sina" / "run-inbox-disk-truth-v1.json"
    if truth.exists():
        t = json.loads(truth.read_text(encoding="utf-8"))
        sa = t.get("queue", {}).get("sa_id", "MISSING")
        if sa.startswith("sa-"):
            print(f"PASS    queue.sa_id={sa}")
        else:
            FAIL.append(f"FAIL    queue.sa_id unexpected: {sa}")
    else:
        FAIL.append("FAIL    run-inbox-disk-truth-v1.json missing")

    t0 = time.time()
    try:
        with urllib.request.urlopen(f"{WORKER}/health", timeout=5) as r:
            ms = int((time.time() - t0) * 1000)
            wd = json.loads(r.read().decode("utf-8"))
            if r.status == 200 and wd.get("ok") and wd.get("service") == "hub-rebuild-worker":
                if ms > 500:
                    FAIL.append(f"SLOW    worker-health: {ms}ms > 500ms limit")
                else:
                    print(f"PASS    worker-health ({ms}ms)")
            else:
                FAIL.append(f"FAIL    worker-health: unexpected response {wd}")
    except Exception as e:
        FAIL.append(f"ERROR   worker-health: {e}")

    wl = Path.home() / ".sina" / "hub-rebuild-worker-v1.lock"
    if wl.exists():
        print("PASS    worker lock present")
    else:
        FAIL.append("FAIL    worker lock missing (secondary signal)")

    server_py = (ROOT / "scripts" / "sina-command-server.py").read_text(encoding="utf-8")
    get_block = server_py.split("def do_POST", 1)[0]
    violations = [
        line
        for line in get_block.splitlines()
        if any(
            tok in line
            for tok in (
                "build_payload(",
                "write_panel_outputs(",
                "hub_after_mutation(",
                "run_refresh_pipeline(",
            )
        )
        and not line.strip().startswith("#")
        and "def " not in line
        and '"""' not in line
        and "'''" not in line
    ]
    if violations:
        FAIL.append(f"FAIL    four-rule violations: {len(violations)} line(s)")
        for v in violations:
            print(f"  VIOLATION: {v}")
    else:
        print("PASS    four request-thread rules satisfied")

    if FAIL:
        print("\nFAILURES:")
        for f in FAIL:
            print(" ", f)
        return 1

    print("\nPASS    all light E2E checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
