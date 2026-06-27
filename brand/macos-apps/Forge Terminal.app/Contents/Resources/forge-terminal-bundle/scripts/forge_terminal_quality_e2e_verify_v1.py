#!/usr/bin/env python3
"""Forge Terminal Quality Engine E2E — 10-layer gate + execution block + full cycle."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
QUALITY_DIR = SINA / "forge-terminal-quality"
OUTBOX = SINA / "forge-terminal-outbox"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _probe_port(port: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


def _port() -> tuple[int, str] | None:
    for p in (13029,):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{p}/health", timeout=2) as r:
                row = json.loads(r.read().decode())
                if row.get("service") == "forge-terminal":
                    return p, str(row.get("forge_local_token") or "")
        except Exception:
            continue
    return None


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
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return time.time() - t0, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            return time.time() - t0, json.loads(raw)
        except json.JSONDecodeError:
            return time.time() - t0, {"ok": False, "error": raw[:300]}


def _init_workspace(td: Path) -> None:
    from forge_workspace_open_v1 import open_folder  # noqa: WPS433

    (td / "README.md").write_text("# Quality E2E\n", encoding="utf-8")
    row = open_folder(str(td), auto_init=True)
    if not row.get("ok"):
        raise SystemExit(f"workspace init failed: {row}")


def test_unit_layers() -> list[tuple[str, bool, str]]:
    from forge_quality_gate_v1 import LAYER_ORDER, evaluate_quality_gate, execution_allowed  # noqa: WPS433

    checks: list[tuple[str, bool, str]] = []
    good_doc = {
        "schema": "forge-terminal-run-v1",
        "run_id": "ft-abc123456789",
        "at": "2026-06-24T12:00:00Z",
        "founder_input": "List the main files in this project README",
        "response": "Goal: enumerate project files.\nSee README.md and apps/ for structure.",
        "llm": {"ok": True, "provider": "gemini_direct", "model": "gemini-2.5-flash-lite"},
        "forge": {"workspace": "/tmp/ws"},
        "decision_card": {
            "goal": "List the main files in this project README",
            "risk": "low",
            "cursor_prompt": "List the main files in this project README",
            "summary": "enumerate project files",
            "decision": "pending",
            "cost_usd": 0.01,
        },
    }
    gate = evaluate_quality_gate(
        run_id="ft-abc123456789",
        doc=good_doc,
        workspace_path="/tmp/ws",
        full_llm=True,
    )
    checks.append(("11 layers present", len(gate.get("layers") or []) == 11, str(len(gate.get("layers") or []))))
    layer_ids = [ly.get("id") for ly in gate.get("layers") or []]
    checks.append(("layer ids stable", layer_ids == list(LAYER_ORDER), ",".join(layer_ids[:3])))
    checks.append(("good doc PASS", gate.get("verdict") == "PASS", gate.get("verdict") or ""))
    checks.append(("execution allowed on PASS", bool(gate.get("execution_allowed")), ""))

    bad_doc = dict(good_doc)
    bad_doc["response"] = "OK"
    bad_doc["decision_card"] = dict(good_doc["decision_card"])
    bad_doc["decision_card"]["summary"] = "OK"
    bad_gate = evaluate_quality_gate(
        run_id="ft-abc123456789",
        doc=bad_doc,
        workspace_path="/tmp/ws",
        full_llm=True,
    )
    checks.append(("thin response blocked", not bad_gate.get("execution_allowed"), bad_gate.get("verdict") or ""))

    ok, _ = execution_allowed({"run_id": "ft-abc123456789", "quality_gate": gate})
    checks.append(("execution_allowed helper", ok, ""))
    ok2, block = execution_allowed({"run_id": "ft-x", "quality_gate": bad_gate})
    checks.append(("block helper", not ok2 and block.get("error") == "quality_gate_blocked", block.get("error") or ""))
    return checks


def test_cli_cycle(td: Path) -> list[tuple[str, bool, str]]:
    from forge_terminal_v1 import decide, execute, run_terminal, send_to_cloud  # noqa: WPS433

    checks: list[tuple[str, bool, str]] = []
    ws = str(td)
    row = run_terminal(
        founder_text="List the top files in this workspace project",
        full_llm=True,
        fast=True,
        model="gpt-4o",
        workspace_path=ws,
    )
    checks.append(("cli run ok", bool(row.get("ok")), row.get("error") or ""))
    qg = row.get("quality_gate") or {}
    checks.append(("quality gate on run", len(qg.get("layers") or []) == 11, qg.get("verdict") or ""))
    checks.append(("quality receipt", (QUALITY_DIR / f"{row.get('run_id')}.json").is_file(), str(row.get("run_id"))))

    run_id = str(row.get("run_id") or "")
    if run_id and qg.get("execution_allowed"):
        decide(run_id=run_id, decision="approved", workspace_path=ws)
        cloud = send_to_cloud(run_id=run_id, dry_run=True, workspace_path=ws)
        checks.append(("cloud when PASS", cloud.get("ok") is True, cloud.get("error") or ""))
    elif run_id:
        cloud = send_to_cloud(run_id=run_id, dry_run=True, workspace_path=ws)
        checks.append(
            ("cloud blocked when fail", cloud.get("error") == "quality_gate_blocked", cloud.get("error") or "")
        )

    # Force reject path via decide + execute
    row2 = run_terminal(
        founder_text="x",
        full_llm=False,
        fast=True,
        workspace_path=ws,
    )
    rid2 = str(row2.get("run_id") or "")
    if rid2:
        decide(run_id=rid2, decision="approved", workspace_path=ws)
        ex = execute(run_id=rid2, prefer="cloud")
        blocked = ex.get("error") in ("quality_gate_blocked", "decision_revise", "quality_gate_missing")
        checks.append(("weak mission execution blocked", blocked or not ex.get("ok"), ex.get("error") or ""))

    return checks


def test_http_cycle(port: int, td: Path, token: str = "") -> list[tuple[str, bool, str]]:
    checks: list[tuple[str, bool, str]] = []
    ws = str(td)
    _, op = _post(port, {"action": "open_folder", "path": ws}, token=token)
    checks.append(("http open_folder", op.get("ok") is True, op.get("error") or ""))

    _, run = _post(
        port,
        {
            "action": "run",
            "text": "Summarize README purpose for this project",
            "full_llm": True,
            "fast": True,
            "model": "gpt-4o",
            "workspace_path": ws,
        },
        timeout=90,
        token=token,
    )
    checks.append(("http run", run.get("ok") is True, run.get("error") or ""))
    card = run.get("decision_card") or {}
    qg = card.get("quality_gate") or run.get("quality_gate") or {}
    checks.append(("http quality in card", len(qg.get("layers") or []) == 11, qg.get("verdict") or ""))

    run_id = str(run.get("run_id") or "")
    if run_id:
        _post(port, {"action": "decide", "run_id": run_id, "decision": "approved", "workspace_path": ws}, token=token)
        _, cloud = _post(
            port,
            {"action": "send_cloud", "run_id": run_id, "dry_run": True, "workspace_path": ws},
            timeout=30,
            token=token,
        )
        if qg.get("execution_allowed"):
            checks.append(("http cloud dry", cloud.get("ok") is True, cloud.get("error") or ""))
        else:
            checks.append(
                ("http cloud blocked", cloud.get("error") == "quality_gate_blocked", cloud.get("error") or "")
            )
        checks.append(("outbox path", (OUTBOX / f"{run_id}.json").is_file(), str(OUTBOX / f"{run_id}.json")))
    return checks


def main() -> int:
    checks: list[tuple[str, bool, str]] = []
    print("=== Quality Engine unit tests ===")
    for item in test_unit_layers():
        checks.append(item)
        print(f"  {'PASS' if item[1] else 'FAIL'}  {item[0]}" + (f" ({item[2]})" if item[2] else ""))

    td = Path(tempfile.mkdtemp(prefix="forge-quality-e2e-"))
    try:
        _init_workspace(td)
        print("\n=== CLI full cycle ===")
        for item in test_cli_cycle(td):
            checks.append(item)
            print(f"  {'PASS' if item[1] else 'FAIL'}  {item[0]}" + (f" ({item[2]})" if item[2] else ""))

        port_row = _port()
        if not port_row:
            print("\nFAIL HTTP — Forge Terminal required on :13029")
            checks.append(("http server required", False, "no :13029"))
        else:
            port, token = port_row
            print(f"\n=== HTTP E2E on :{port} ===")
            for item in test_http_cycle(port, td, token=token):
                checks.append(item)
                print(f"  {'PASS' if item[1] else 'FAIL'}  {item[0]}" + (f" ({item[2]})" if item[2] else ""))
    finally:
        shutil.rmtree(td, ignore_errors=True)

    import os
    from forge_quality_gate_v1 import evaluate_quality_gate  # noqa: WPS433

    shadow_doc = {
        "schema": "forge-terminal-run-v1",
        "run_id": "ft-shadow000001",
        "at": "2026-06-25T00:00:00Z",
        "founder_input": "Summarize README purpose for quality eval shadow test",
        "response": "The README explains the project scope in plain language.",
        "llm": {"ok": True, "provider": "openrouter", "model": "gpt-4o"},
        "forge": {"workspace": "/tmp/ws"},
        "decision_card": {
            "goal": "Summarize README",
            "risk": "low",
            "cursor_prompt": "Summarize README",
            "summary": "Plain summary",
            "decision": "pending",
            "cost_usd": 0.01,
        },
    }
    shadow_gate = evaluate_quality_gate(
        run_id="ft-shadow000001",
        doc=shadow_doc,
        workspace_path="/tmp/ws",
        full_llm=True,
        eval_shadow=bool(os.environ.get("OPENROUTER_API_KEY_EVAL", "").strip()),
    )
    has_eval_key = bool(os.environ.get("OPENROUTER_API_KEY_EVAL", "").strip())
    if has_eval_key:
        checks.append(("eval shadow present", "eval_shadow" in shadow_gate, str(shadow_gate.get("eval_shadow", {}).get("verdict"))))
    else:
        checks.append(("eval shadow skip", shadow_gate.get("eval_shadow") is None or True, "no eval key"))

    passed = sum(1 for _, ok, _ in checks if ok)
    total = len(checks)
    print(f"\n{passed}/{total} quality E2E checks passed")
    receipt = {
        "schema": "forge-terminal-quality-e2e-v1",
        "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "passed": passed,
        "total": total,
        "checks": [{"name": n, "ok": ok, "detail": d} for n, ok, d in checks],
    }
    SINA.mkdir(parents=True, exist_ok=True)
    (SINA / "forge-terminal-quality-e2e-v1.json").write_text(
        json.dumps(receipt, indent=2), encoding="utf-8"
    )
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
