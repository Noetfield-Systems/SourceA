#!/usr/bin/env python3
"""Critic verification — Forge Terminal V1 five-check suite."""
from __future__ import annotations

import json
import sys
import tempfile
import time
import urllib.error
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
    raise SystemExit("Start Forge Terminal.app on :13029")


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
            raw = resp.read().decode("utf-8")
            return time.time() - t0, json.loads(raw)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            return time.time() - t0, json.loads(raw)
        except json.JSONDecodeError:
            return time.time() - t0, {"ok": False, "error": raw[:300]}


def main() -> int:
    port, token = _port_token()
    print(f"API port: {port}\n")

    td = Path(tempfile.mkdtemp(prefix="forge-critic-"))
    (td / "README.md").write_text("# critic e2e\n", encoding="utf-8")
    ws = str(td)
    _, op = _post(port, {"action": "open_folder", "path": ws}, token=token)
    if not op.get("ok"):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
        from forge_workspace_open_v1 import open_folder  # noqa: WPS433

        open_folder(ws, auto_init=True)

    run_body = {
        "action": "run",
        "text": "Design a trust brief MVP for Noetfield",
        "full_llm": True,
        "fast": True,
        "model": "gpt-4o",
        "workspace_path": ws,
    }

    print("=== 1. LLM real call ===")
    elapsed, run1 = _post(port, run_body, token=token, timeout=90)
    llm = run1.get("llm") or {}
    provider = llm.get("provider")
    model = llm.get("model")
    skipped = llm.get("skipped")
    print(f"  elapsed: {elapsed:.2f}s")
    print(f"  ok: {run1.get('ok')}  provider: {provider}  model: {model}  skipped: {skipped}")
    print(f"  response_chars: {len(run1.get('response') or '')}")
    llm_real = bool(run1.get("ok") and provider and provider not in ("forge_only",))
    if llm_real:
        print("  VERDICT: PASS — real LLM call")
    else:
        print("  VERDICT: FAIL — " + str(run1.get("error") or run1.get("message") or "no provider"))

    run_id = run1.get("run_id") or ""
    print(f"  run_id: {run_id}\n")

    print("=== 2. Decision Card gates execution ===")
    _, run2 = _post(
        port,
        {"action": "run", "text": "reject gate test", "full_llm": False, "fast": True, "workspace_path": ws},
        token=token,
    )
    rid2 = run2.get("run_id") or ""
    _, dec = _post(port, {"action": "decide", "run_id": rid2, "decision": "rejected"}, token=token)
    print(f"  reject ok: {dec.get('ok')}  decision: {(dec.get('decision_card') or {}).get('decision')}")
    _, cloud_after_reject = _post(port, {"action": "send_cloud", "run_id": rid2}, token=token)
    _, exec_after_reject = _post(port, {"action": "execute", "run_id": rid2, "prefer": "cloud"}, token=token)
    blocked = cloud_after_reject.get("error") in ("decision_rejected", "quality_gate_blocked") or (
        not cloud_after_reject.get("ok") and cloud_after_reject.get("error")
    )
    print(f"  send_cloud after reject: ok={cloud_after_reject.get('ok')} error={cloud_after_reject.get('error')}")
    print(f"  execute after reject: ok={exec_after_reject.get('ok')} error={exec_after_reject.get('error')}")
    print(f"  VERDICT: {'PASS' if blocked else 'FAIL — decision cosmetic'}\n")

    print("=== 3–5. Full cycle (Noetfield intake) ===")
    cycle_start = time.time()
    mission = "Create intake workflow for Noetfield Trust Brief pilot"
    elapsed_run, run3 = _post(
        port,
        {
            "action": "run",
            "text": mission,
            "full_llm": True,
            "fast": True,
            "model": "gpt-4o",
            "workspace_path": ws,
        },
        token=token,
        timeout=90,
    )
    rid3 = run3.get("run_id") or ""
    has_card = bool(run3.get("decision_card"))
    qg3 = (run3.get("quality_gate") or (run3.get("decision_card") or {}).get("quality_gate") or {})
    print(f"  [1] decision card: {'yes' if has_card else 'NO'}  run_id={rid3}  run_time={elapsed_run:.1f}s")

    _, approve = _post(port, {"action": "decide", "run_id": rid3, "decision": "approved"}, token=token)
    print(f"  [2] approve: ok={approve.get('ok')}")

    outbox_before = set(OUTBOX.glob("*.json")) if OUTBOX.is_dir() else set()
    cloud_ok = False
    if qg3.get("execution_allowed"):
        _, cloud = _post(port, {"action": "send_cloud", "run_id": rid3, "dry_run": True}, token=token, timeout=30)
        cloud_ok = cloud.get("ok") is True
        print(f"  [3] cloud (dry_run): ok={cloud.get('ok')} error={cloud.get('error')}")
    else:
        print(f"  [3] cloud skipped — quality {qg3.get('verdict')}")

    _, poll = _post(port, {"action": "poll_outbox", "run_id": rid3}, token=token)
    outbox_row = poll.get("outbox") or {}
    outbox_path = OUTBOX / f"{rid3}.json"
    payload = outbox_row.get("payload") or {}
    print(f"  [4] outbox file: {outbox_path} exists={outbox_path.is_file()}")
    print(f"      payload keys: {list(payload.keys()) if payload else 'empty'}")
    print(f"      run_id in outbox: {outbox_row.get('run_id')}")

    cycle_elapsed = time.time() - cycle_start
    print(f"  [5] total cycle: {cycle_elapsed:.1f}s")

    checks = [
        llm_real,
        blocked,
        has_card,
        approve.get("ok"),
        cloud_ok or not qg3.get("execution_allowed"),
        outbox_path.is_file() and bool(outbox_row.get("run_id")) if qg3.get("execution_allowed") else True,
        cycle_elapsed < 60,
    ]
    labels = ["llm_real", "reject_blocks", "decision_card", "approve", "cloud_execute", "outbox_writeback", "under_60s"]
    print("\n=== Summary ===")
    for label, ok in zip(labels, checks):
        print(f"  {'PASS' if ok else 'FAIL'}  {label}")

    print("\n=== Architecture scope (V1 = compose/route/display) ===")
    print(f"  freeze_active: {(run3.get('orchestration') or {}).get('freeze_active')}")
    print(f"  execution_plane default: {(run3.get('decision_card') or {}).get('execution_plane')}")
    gate = (run3.get("llm") or {}).get("gate") or {}
    print(f"  llm gate mode: {gate.get('mode')} bypass_tier: {gate.get('bypass_tier_routing')}")

    core = checks[:5]
    passed = sum(1 for c in core if c)
    print(f"\n{passed}/5 critic checks passed")
    receipt = {
        "schema": "forge-terminal-critic-verify-v1",
        "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "port": port,
        "checks": dict(zip(labels, checks)),
        "run_ids": {"llm_test": run_id, "reject_test": rid2, "full_cycle": rid3},
    }
    SINA.mkdir(parents=True, exist_ok=True)
    (SINA / "forge-terminal-critic-verify-v1.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    import shutil

    shutil.rmtree(td, ignore_errors=True)
    return 0 if passed == 5 else 1


if __name__ == "__main__":
    sys.exit(main())
