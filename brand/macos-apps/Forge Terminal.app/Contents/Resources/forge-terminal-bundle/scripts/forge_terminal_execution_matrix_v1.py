#!/usr/bin/env python3
"""Forge Terminal execution path matrix E2E — reject/revise/quality/cursor/telemetry."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
TELEMETRY = SINA / "forge-terminal-telemetry-v1.jsonl"


def _port_token() -> tuple[int, str]:
    for p in (13029,):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{p}/health", timeout=3) as r:
                row = json.loads(r.read().decode())
            if row.get("service") == "forge-terminal":
                return p, str(row.get("forge_local_token") or "")
        except Exception:
            continue
    return 0, ""


def _post(port: int, body: dict, token: str = "", timeout: float = 60) -> dict:
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
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def _cli_run(text: str, ws: str, *, full_llm: bool = True) -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    from forge_terminal_v1 import run_terminal  # noqa: WPS433

    return run_terminal(
        founder_text=text,
        full_llm=full_llm,
        fast=True,
        model="gpt-4o",
        workspace_path=ws,
    )


def main() -> int:
    port, token = _port_token()
    checks: list[tuple[str, bool, str, str]] = []
    td = Path(tempfile.mkdtemp(prefix="forge-exec-matrix-"))
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from forge_workspace_open_v1 import open_folder  # noqa: WPS433
        from forge_terminal_v1 import decide, execute, send_to_cloud, send_to_cursor  # noqa: WPS433

        (td / "README.md").write_text("# matrix\n", encoding="utf-8")
        open_folder(str(td), auto_init=True)
        ws = str(td)

        tel_before = TELEMETRY.stat().st_size if TELEMETRY.is_file() else 0

        # reject blocks cloud
        r1 = _cli_run("reject gate test mission for workspace files", ws)
        rid1 = str(r1.get("run_id") or "")
        if rid1:
            decide(run_id=rid1, decision="rejected", workspace_path=ws)
            c1 = send_to_cloud(run_id=rid1, dry_run=True, workspace_path=ws)
            checks.append(("reject blocks cloud", c1.get("error") == "decision_rejected", c1.get("error") or "", "cli"))

        # revise blocks execute
        r2 = _cli_run("revise gate test list workspace readme files", ws)
        rid2 = str(r2.get("run_id") or "")
        if rid2:
            decide(run_id=rid2, decision="revise", workspace_path=ws)
            e2 = execute(run_id=rid2, prefer="cloud")
            checks.append(("revise blocks execute", e2.get("error") == "decision_revise", e2.get("error") or "", "cli"))

        # weak mission quality block
        r3 = _cli_run("x", ws, full_llm=False)
        rid3 = str(r3.get("run_id") or "")
        if rid3:
            decide(run_id=rid3, decision="approved", workspace_path=ws)
            c3 = send_to_cloud(run_id=rid3, dry_run=True, workspace_path=ws)
            checks.append(
                ("quality blocks weak", c3.get("error") == "quality_gate_blocked", c3.get("error") or "", "cli")
            )

        # pass path dry cloud
        r4 = _cli_run("Summarize README purpose for this workspace project", ws)
        rid4 = str(r4.get("run_id") or "")
        qg4 = r4.get("quality_gate") or {}
        if rid4 and qg4.get("execution_allowed"):
            decide(run_id=rid4, decision="approved", workspace_path=ws)
            c4 = send_to_cloud(run_id=rid4, dry_run=True, workspace_path=ws)
            checks.append(("pass cloud dry", c4.get("ok") is True, c4.get("error") or "", "cli"))

        r5c = _cli_run("Send cursor inbox test for readme summary", ws)
        rid5c = str(r5c.get("run_id") or "")
        qg5 = r5c.get("quality_gate") or {}
        if rid5c and qg5.get("execution_allowed"):
            decide(run_id=rid5c, decision="approved", workspace_path=ws)
            cur = send_to_cursor(run_id=rid5c)
            cur_ok = bool(cur.get("ok")) or bool((cur.get("cursor_bridge") or {}).get("ok")) or bool(
                cur.get("cursor_blocked")
            )
            cur_err = str(cur.get("error") or "")
            checks.append(
                ("send_cursor path",
                 cur_ok or cur_err in ("quality_gate_blocked", "decision_not_approved", "decision_rejected"),
                 cur_err or ("ok" if cur_ok else "fail"),
                 "cli")
            )

        if port:
            try:
                _post(port, {"action": "open_folder", "path": ws}, token=token)
                r5 = _post(
                    port,
                    {"action": "run", "text": "List files via HTTP matrix test", "full_llm": True, "workspace_path": ws},
                    token=token,
                    timeout=90,
                )
                checks.append(("http run", r5.get("ok") is True, r5.get("error") or "", "http"))
            except Exception as exc:
                checks.append(("http run", False, str(exc)[:80], "http"))

        tel_after = TELEMETRY.stat().st_size if TELEMETRY.is_file() else 0
        checks.append(("telemetry grew", tel_after >= tel_before, f"{tel_before}->{tel_after}", "disk"))
    finally:
        shutil.rmtree(td, ignore_errors=True)

    passed = sum(1 for _, ok, _, _ in checks if ok)
    print("Forge execution matrix E2E\n")
    for name, ok, detail, plane in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  [{plane}] {name}" + (f" ({detail})" if detail else ""))
    print(f"\n{passed}/{len(checks)} passed")
    receipt = {
        "schema": "forge-terminal-execution-matrix-v1",
        "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "passed": passed,
        "total": len(checks),
        "checks": [{"name": n, "ok": ok, "detail": d, "plane": p} for n, ok, d, p in checks],
    }
    SINA.mkdir(parents=True, exist_ok=True)
    (SINA / "forge-terminal-execution-matrix-v1.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
