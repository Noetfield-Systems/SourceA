#!/usr/bin/env python3
"""Dispatch ready activation gates — hub/orchestrator must match orchestrator_dispatch_ready() (v1.1)."""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
HUB = "http://127.0.0.1:13020"

_HUB_PATHS = (
    "/api/dispatch-policy-v1",
    "/api/runtime-orchestrator-v1",
    "/api/graph-executor-v1",
)


def _expected_ready() -> tuple[bool, list[str]]:
    from runtime.dispatch_policy.policy_engine import orchestrator_dispatch_ready  # noqa: WPS433

    return orchestrator_dispatch_ready()


def assert_strategic_synthesis_sync() -> str | None:
    try:
        from runtime.dispatch_policy.policy_engine import orchestrator_dispatch_ready_payload  # noqa: WPS433
        from strategic_synthesis_hub import strategic_synthesis_payload  # noqa: WPS433

        orch = orchestrator_dispatch_ready_payload()
        row = strategic_synthesis_payload()
        gates = row.get("machine_gates") or {}
        expected = bool(orch.get("dispatch_ready"))
        if gates.get("dispatch_ready") is not expected:
            return f"machine_gates.dispatch_ready={gates.get('dispatch_ready')!r} expected {expected!r}"
        bn = str(row.get("bottleneck") or "")
        if expected and "dispatch_ready=false" in bn.replace(" ", ""):
            return f"strategic_synthesis bottleneck stale false while ready: {bn!r}"
        if not expected and "dispatch_ready=true" in bn.replace(" ", ""):
            return f"strategic_synthesis bottleneck claims true while blocked: {bn!r}"
    except Exception as exc:
        return f"strategic_synthesis_hub: {exc}"
    return None


def assert_hub_apis_match() -> list[str]:
    from runtime.dispatch_policy.policy_engine import orchestrator_dispatch_ready_payload  # noqa: WPS433

    expected = orchestrator_dispatch_ready_payload()
    exp_ready = bool(expected.get("dispatch_ready"))
    errors: list[str] = []
    for path in _HUB_PATHS:
        try:
            with urllib.request.urlopen(f"{HUB}{path}", timeout=60) as resp:
                data = json.loads(resp.read().decode())
        except Exception as exc:
            errors.append(f"{path}: unreachable ({exc})")
            continue
        if "dispatch_ready" not in data:
            continue
        if path == "/api/graph-executor-v1":
            if bool(data.get("dispatch_ready")) is not False:
                errors.append(f"{path}: dispatch_ready must stay false until founder spine Action")
            if bool(data.get("orchestrator_dispatch_ready")) != exp_ready:
                errors.append(
                    f"{path}: orchestrator_dispatch_ready={data.get('orchestrator_dispatch_ready')!r} "
                    f"expected {exp_ready!r} blockers={expected.get('dispatch_ready_blockers')}"
                )
            continue
        if bool(data.get("dispatch_ready")) != exp_ready:
            errors.append(
                f"{path}: dispatch_ready={data.get('dispatch_ready')!r} expected {exp_ready!r} "
                f"blockers={expected.get('dispatch_ready_blockers')}"
            )
    return errors


def assert_graph_executor_clamp() -> str | None:
    try:
        from runtime.graph_executor.api import _clamp_founder_law  # noqa: WPS433
        from runtime.dispatch_policy.policy_engine import orchestrator_dispatch_ready_payload  # noqa: WPS433

        orch = orchestrator_dispatch_ready_payload()
        tampered = {"dispatch_ready": not orch["dispatch_ready"], "auto_dispatch": True, "ok": True}
        fixed = _clamp_founder_law(tampered)
        if fixed.get("dispatch_ready") is not False:
            return "graph_executor _clamp_founder_law dispatch_ready must be False at hub"
        if fixed.get("founder_confirm_required") is not True:
            return "graph_executor _clamp_founder_law failed founder_confirm_required"
        if fixed.get("auto_dispatch") is not False:
            return "graph_executor _clamp_founder_law failed auto_dispatch"
    except Exception as exc:
        return f"graph_executor hub clamp: {exc}"
    return None


def assert_orchestrator_top_level() -> str | None:
    try:
        from runtime.orchestrator.orchestrator_engine import run_runtime_orchestration  # noqa: WPS433
        from runtime.dispatch_policy.policy_engine import orchestrator_dispatch_ready  # noqa: WPS433

        ready, blockers, _ = orchestrator_dispatch_ready()
        orch = run_runtime_orchestration(goal_tool_id="pos-run", task_id="dispatch-ready-lock-check")
        if bool(orch.get("dispatch_ready")) != ready:
            return f"orchestrator dispatch_ready={orch.get('dispatch_ready')!r} expected {ready!r}"
        if ready and orch.get("instruction", {}).get("action") == "dispatch_blocked":
            return "orchestrator ready but instruction still dispatch_blocked"
        dec = orch.get("dispatch_decision") or {}
        if dec.get("dry_run") is not True:
            return "dispatch_decision must stay dry_run=true for task simulation"
        if list(orch.get("dispatch_ready_blockers") or []) != blockers:
            return "orchestrator blockers drift from SSOT"
    except Exception as exc:
        return f"orchestrator top-level: {exc}"
    return None


def assert_spine_bridge_sync() -> str | None:
    try:
        from runtime.graph_executor.spine_bridge import build_spine_bridge  # noqa: WPS433
        from runtime.dispatch_policy.policy_engine import orchestrator_dispatch_ready  # noqa: WPS433

        ready, blockers, _ = orchestrator_dispatch_ready()
        bridge = build_spine_bridge()
        if bridge.get("ok") and bridge.get("dispatch_ready") is not False:
            return "spine_bridge dispatch_ready must be False at hub"
        if bridge.get("ok") and bool(bridge.get("orchestrator_dispatch_ready")) != ready:
            return (
                f"spine_bridge orchestrator_dispatch_ready="
                f"{bridge.get('orchestrator_dispatch_ready')!r} expected {ready!r}"
            )
        if bridge.get("ok") and list(bridge.get("dispatch_ready_blockers") or []) != blockers:
            return "spine_bridge blockers drift"
        if bridge.get("ok") and not bridge.get("founder_confirm_required"):
            return "spine_bridge must set founder_confirm_required=True"
        if bridge.get("ok") and bridge.get("auto_dispatch"):
            return "spine_bridge auto_dispatch must be false"
    except Exception as exc:
        return f"spine_bridge: {exc}"
    return None


def run_validate() -> tuple[bool, list[str]]:
    errors: list[str] = []
    ready, blockers, _ = _expected_ready()
    err = assert_strategic_synthesis_sync()
    if err:
        errors.append(err)
    err = assert_graph_executor_clamp()
    if err:
        errors.append(err)
    err = assert_orchestrator_top_level()
    if err:
        errors.append(err)
    err = assert_spine_bridge_sync()
    if err:
        errors.append(err)
    errors.extend(assert_hub_apis_match())
    return (not errors, errors)


def main() -> int:
    ok, errors = run_validate()
    ready, blockers, _ = _expected_ready()
    if ok:
        print(
            f"OK: validate-dispatch-ready-lock-v1 · dispatch_ready={ready} "
            f"blockers={len(blockers)} · hub synced"
        )
        return 0
    for e in errors:
        print(f"FAIL: {e}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
