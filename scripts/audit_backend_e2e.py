#!/usr/bin/env python3
"""Backend E2E — hub APIs, intelligence circle, agent loop, workspaces."""
from __future__ import annotations

import fcntl
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE_A / "scripts"))

HUB = "http://127.0.0.1:13020"
WORKER = "http://127.0.0.1:13030"
WORKER_SERVE = SOURCE_A / "scripts" / "serve-hub-rebuild-worker.sh"
WORKER_LOCK = Path.home() / ".sina" / "hub-rebuild-worker-v1.lock"
E2E_LOCK = Path.home() / ".sina" / ".backend-e2e.lock"
REFRESH_E2E_BUDGET_SEC = 360  # sa-0853 — Super Fast Hub light default; full rebuild poll cap


def _http(method: str, path: str, body: dict | None = None, *, timeout: int = 120) -> tuple[int, dict]:
    data = json.dumps(body or {}).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        f"{HUB}{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if data else {},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, {"error": raw[:500]}


def _require(errors: list[str], cond: bool, msg: str) -> None:
    if not cond:
        errors.append(msg)


def _require_intelligence_circle(
    errors: list[str],
    data: dict,
    *,
    label: str,
    expect_empty_chat: bool | None = None,
) -> None:
    """Harden intelligence_circle payload shape — chat_messages list + scope (sa-0216)."""
    _require(errors, data.get("ok") is not False, f"{label}: ok false — {data.get('error')}")
    _require(errors, data.get("scope") == "live_agents_only", f"{label}: scope mismatch")
    msgs = data.get("chat_messages")
    _require(errors, isinstance(msgs, list), f"{label}: chat_messages not list")
    _require(errors, "live_agents" in data and isinstance(data.get("live_agents"), list), f"{label}: live_agents missing")
    _require(errors, bool(data.get("selected_live_agent")), f"{label}: selected_live_agent missing")
    if expect_empty_chat is True:
        _require(errors, len(msgs) == 0, f"{label}: chat_messages not empty ({len(msgs)})")
    elif expect_empty_chat is False and msgs:
        for i, row in enumerate(msgs[:3]):
            _require(errors, isinstance(row, dict), f"{label}: chat_messages[{i}] not object")
            _require(errors, row.get("role") in ("user", "assistant", "system"), f"{label}: chat_messages[{i}] role invalid")


def _hub_health_ok(*, timeout: int = 8) -> bool:
    code, health = _http("GET", "/health", timeout=timeout)
    return code == 200 and bool(health.get("ok"))


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


def _ensure_worker_before_e2e(errors: list[str]) -> None:
    if _worker_health_ok():
        print("OK: rebuild worker health on :13030 before E2E")
        return
    if not WORKER_SERVE.is_file():
        errors.append("serve-hub-rebuild-worker.sh missing")
        return
    try:
        subprocess.run(
            ["bash", str(WORKER_SERVE)],
            cwd=str(SOURCE_A),
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        errors.append("serve-hub-rebuild-worker.sh timed out before E2E")
        return
    if _worker_health_ok():
        print("OK: serve-hub-rebuild-worker.sh brought worker up before E2E")
        return
    errors.append("rebuild worker :13030 still down after serve-hub-rebuild-worker.sh")


def _ensure_hub_before_e2e(errors: list[str]) -> None:
    """Run serve-sina-command.sh when :13020 /health is down (sa-0214)."""
    if _hub_health_ok():
        print("OK: hub health on :13020 before E2E (sa-0214)")
    else:
        serve = SOURCE_A / "scripts" / "serve-sina-command.sh"
        if not serve.is_file():
            errors.append("serve-sina-command.sh missing")
            return
        try:
            proc = subprocess.run(
                ["bash", str(serve)],
                cwd=str(SOURCE_A),
                capture_output=True,
                text=True,
                timeout=90,
            )
        except subprocess.TimeoutExpired:
            errors.append("serve-sina-command.sh timed out before E2E")
            return
        if _hub_health_ok():
            print("OK: serve-sina-command.sh brought hub up before E2E (sa-0214)")
        else:
            tail = ((proc.stdout or "") + (proc.stderr or "")).strip()[-400:]
            errors.append(f"hub health after serve-sina-command.sh: exit {proc.returncode} — {tail}")
            return
    _ensure_worker_before_e2e(errors)


def _e2e_force_enabled() -> bool:
    import os

    return os.environ.get("SINA_E2E_FORCE", "").strip().lower() in ("1", "true", "yes")


def main() -> int:
    if not _e2e_force_enabled():
        print(
            "OK: backend E2E CANCELLED — founder directive 2026-06-10 "
            "(Phase 10 regate off; hub light migration next). "
            "Set SINA_E2E_FORCE=1 to run."
        )
        return 0
    errors: list[str] = []
    E2E_LOCK.parent.mkdir(parents=True, exist_ok=True)
    lock_fh = E2E_LOCK.open("w", encoding="utf-8")
    try:
        fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX)
    except OSError:
        lock_fh.close()
        print("BACKEND E2E FAILED:")
        print("  - another backend E2E audit is already running")
        return 1

    try:
        return _run_audit(errors)
    finally:
        try:
            fcntl.flock(lock_fh.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        lock_fh.close()


def _run_audit(errors: list[str]) -> int:
    _ensure_hub_before_e2e(errors)
    if errors:
        print("BACKEND E2E FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    code, health = _http("GET", "/health")
    _require(errors, code == 200 and health.get("ok"), f"health: {code} {health}")

    get_paths = [
        "/api/intelligence-circle",
        "/api/agent-loop",
        "/api/agent-workspaces",
        "/api/prompt-queue",
        "/api/prompt-direction",
        "/api/advisor/chat",
        "/api/semej",
        "/api/agent-review",
        "/api/audit-backlog",
        "/api/founder/actions",
        "/api/apps",
        "/api/notes",
        "/api/commitments",
        "/api/hub-essentials",
        "/api/important-docs",
        "/api/strategic-synthesis-v1",
        "/api/eval-packet-v1b",
        "/api/dispatch-policy-v1",
        "/api/graph-executor-v1",
        "/api/event-bus-v1",
        "/api/incident-room",
        "/api/conflict-room",
        "/api/workspace-mirror?agent_id=trustfield",
        "/api/workspace-vault?agent_id=trustfield",
    ]
    for p in get_paths:
        code, data = _http("GET", p)
        _require(errors, code == 200, f"GET {p}: HTTP {code}")
        if p == "/api/intelligence-circle":
            _require_intelligence_circle(errors, data, label="GET /api/intelligence-circle")
        if p == "/api/agent-loop":
            ws = data.get("loop_workspaces") or []
            _require(errors, len(ws) == 7, f"agent-loop workspaces: {len(ws)}")
        if p == "/api/agent-workspaces":
            _require(errors, len(data.get("workspaces") or []) == 7, "agent-workspaces count")
        if p == "/api/hub-essentials":
            _require(errors, data.get("ok"), "hub-essentials not ok")
            cov = data.get("nav_coverage") or {}
            _require(errors, cov.get("complete"), f"hub-essentials nav gaps: {cov.get('missing_nav_tabs')}")
            _require(errors, (data.get("pillar_count") or 0) >= 6, "hub-essentials pillar_count")
        if p == "/api/important-docs":
            _require(errors, data.get("ok"), "important-docs not ok")
            _require(errors, "sections" in data, "important-docs missing sections")
        if p == "/api/strategic-synthesis-v1":
            _require(errors, data.get("ok"), "strategic-synthesis not ok")
            _require(errors, data.get("strategic_goals"), "strategic-synthesis missing goals")
            _require(errors, data.get("next_plans"), "strategic-synthesis missing next_plans")
        if p == "/api/eval-packet-v1b":
            _require(errors, data.get("schema") == "eval-packet-v1b", "eval-1b schema")
            _require(errors, data.get("packet_win_pct") is not None, "eval-1b missing win pct")
        if p == "/api/dispatch-policy-v1":
            _require(errors, data.get("ok"), "dispatch-policy not ok")
            _require(errors, data.get("classes"), "dispatch-policy missing classes")
        if p == "/api/graph-executor-v1":
            _require(errors, data.get("ok"), "graph-executor not ok")
            _require(errors, "policy_class" in data, "graph-executor missing policy_class")
            _require(errors, "spine_bridge_ready" in data, "graph-executor missing spine_bridge_ready")
        if p == "/api/event-bus-v1":
            _require(errors, data.get("schema") == "event-bus-v1", "event-bus schema")
            _require(errors, isinstance(data.get("recent_topics"), list), "event-bus recent_topics")
        if p.startswith("/api/workspace-mirror"):
            _require(errors, data.get("ok") and data.get("schema", "").startswith("workspace_mirror"), "workspace-mirror invalid")
            _require(errors, "mission" in data and "stats" in data, "workspace-mirror missing sections")
        if p.startswith("/api/workspace-vault"):
            _require(errors, data.get("ok"), "workspace-vault not ok")
        if p == "/api/personal-db":
            _require(errors, data.get("ok"), "personal-db not ok")
            _require(errors, "layer_legend" in data, "personal-db missing layer_legend")

    code, inc_post = _http(
        "POST",
        "/api/incident-room",
        {
            "action": "submit_weekly",
            "agent_id": "trustfield",
            "title": "audit-e2e weekly test",
            "what_happened": "Backend e2e dry-run incident share for hub verification only.",
            "lesson": "Always use Incident Room UI for real lessons.",
        },
    )
    _require(
        errors,
        code in (200, 202) and inc_post.get("ok"),
        f"incident submit_weekly: {inc_post.get('error')}",
    )

    code, sb = _http("POST", "/api/agent-scoreboard", {"action": "list"})
    _require(errors, code == 200 and sb.get("ok"), f"agent-scoreboard list: {sb.get('error')}")
    _require(errors, sb.get("agent_count") == 7, f"scoreboard agent_count: {sb.get('agent_count')}")
    _require(errors, "fleet_auto_green_count" in sb, "scoreboard missing fleet_auto_green_count")
    print("OK: audit_backend_e2e agent-scoreboard POST list (sa-0320)")

    # Intelligence circle POST flow
    code, cleared = _http(
        "POST",
        "/api/intelligence-circle",
        {"action": "clear_session", "agent_id": "cursor_maintainer"},
    )
    _require(errors, code == 200 and cleared.get("ok"), f"clear_session: {cleared.get('error')}")
    msgs = cleared.get("chat_messages") or []
    comms = cleared.get("comms") or []
    _require(errors, len(msgs) == 0, f"clear_session chat_messages: {len(msgs)}")
    _require(errors, len(comms) == 0, f"clear_session comms: {len(comms)}")

    code, st = _http("POST", "/api/intelligence-circle", {"action": "status"})
    _require(errors, code == 200 and len(st.get("chat_messages") or []) == 0, "status after clear not empty")

    # Dry-run chat only — never inject Cursor or spam comms during panel builds.
    code, sent = _http(
        "POST",
        "/api/intelligence-circle",
        {
            "action": "chat",
            "message": "audit-dry-run-no-cursor",
            "agent_id": "cursor_maintainer",
            "topic": "general",
            "inject_cursor": False,
        },
    )
    _require(errors, code == 200, f"chat HTTP {code}")
    _require(errors, sent.get("ok") is not False, f"chat failed: {sent.get('error')}")
    _require(errors, sent.get("inject_skipped"), "chat must not inject Cursor")

    code, cleared2 = _http(
        "POST",
        "/api/intelligence-circle",
        {"action": "clear_session", "agent_id": "cursor_maintainer"},
    )
    _require(errors, len(cleared2.get("chat_messages") or []) == 0, "second clear: chat not empty")
    _require(errors, len(cleared2.get("comms") or []) == 0, "second clear: comms not empty")

    code, ping = _http("POST", "/api/intelligence-circle", {"action": "ping"})
    _require(errors, code == 200 and ping.get("ok") is not False, f"ping: {ping.get('error')}")

    _http(
        "POST",
        "/api/intelligence-circle",
        {"action": "set_agent_enabled", "agent_id": "openrouter", "enabled": False},
    )
    code, sel_def = _http("POST", "/api/intelligence-circle", {"action": "select_agent"})
    _require(
        errors,
        code == 200 and sel_def.get("selected_live_agent") == "cursor_maintainer",
        f"select_agent default: {sel_def.get('selected_live_agent')}",
    )

    # Direct module vs HTTP
    from intelligence_circle import circle_payload, handle_circle_action, _load_config  # noqa: E402

    direct = handle_circle_action({"action": "status"})
    _require(errors, direct.get("scope") == "live_agents_only", "direct status scope")
    cfg = _load_config()
    _require(
        errors,
        "cursor_maintainer" in (cfg.get("chat_cleared_at") or {}),
        "config missing chat_cleared_at.cursor_maintainer",
    )

    # Agent loop packs: disk SSOT first (stable), HTTP smoke second (sa-0216 flake guard)
    from agent_workspace_registry import AGENT_WORKSPACES  # noqa: E402
    from loop_seeds import _pack_seeds_payload  # noqa: E402

    for spec in AGENT_WORKSPACES:
        aid = spec["id"]
        pid = spec.get("pack_id")
        if pid:
            pd = _pack_seeds_payload(pid)
            disk_n = len((pd or {}).get("seed_suggestions") or [])
            _require(errors, disk_n == 10, f"{aid}: disk pack expected 10 seeds, got {disk_n}")
        else:
            pd = None

    def _http_seed_counts(aid: str) -> tuple[int, int]:
        code, sel = _http("POST", "/api/agent-loop", {"action": "select_workspace", "workspace_id": aid})
        if code not in (200, 202) or not sel.get("ok"):
            return -1, -1
        if code == 200:
            al = (sel.get("data") or {}).get("agent_loop") or {}
            n = len(al.get("seed_suggestions") or [])
            row = next((w for w in (al.get("loop_workspaces") or []) if w.get("id") == aid), None)
            row_n = len((row or {}).get("pack_suggestions") or [])
            return n, row_n
        for _ in range(20):
            time.sleep(0.5)
            gcode, al = _http("GET", "/api/agent-loop")
            if gcode != 200:
                continue
            n = len(al.get("seed_suggestions") or [])
            row = next((w for w in (al.get("loop_workspaces") or []) if w.get("id") == aid), None)
            row_n = len((row or {}).get("pack_suggestions") or [])
            if n > 0 or row_n > 0:
                return n, row_n
        return 0, 0

    smoke_id = "trustfield"
    spec = next(s for s in AGENT_WORKSPACES if s["id"] == smoke_id)
    n, row_n = -1, -1
    for attempt in range(3):
        n, row_n = _http_seed_counts(smoke_id)
        pid = spec.get("pack_id")
        if pid and n == 10 and row_n == 10:
            break
        if not pid and n == 0 and row_n == 0:
            break
        time.sleep(0.75 * (attempt + 1))
    if spec.get("pack_id"):
        _require(errors, n == 10, f"{smoke_id}: HTTP expected 10 seed_suggestions, got {n}")
        _require(errors, row_n == 10, f"{smoke_id}: HTTP expected 10 pack_suggestions, got {row_n}")

    _http("POST", "/api/agent-loop", {"action": "select_workspace", "workspace_id": "trustfield"})

    # Light refresh — Super Fast Hub default (sa-0853); full async 202 still accepted when queued
    code, sync_before = _http("GET", "/api/hub-sync", timeout=10)
    gid_before = int((sync_before or {}).get("generation_id", 0)) if code == 200 else 0

    t0 = time.time()
    code, ref = _http("POST", "/refresh", {"mode": "light"}, timeout=30)
    elapsed = time.time() - t0
    _require(
        errors,
        elapsed <= REFRESH_E2E_BUDGET_SEC,
        f"/refresh total time {elapsed:.1f}s > {REFRESH_E2E_BUDGET_SEC}s (sa-0853)",
    )
    _require(
        errors,
        ref.get("ok") and code in (200, 202),
        f"/refresh light: HTTP {code} {ref}",
    )

    gid_after = gid_before
    deadline = t0 + REFRESH_E2E_BUDGET_SEC
    while time.time() < deadline:
        code, sync = _http("GET", "/api/hub-sync", timeout=10)
        if code == 200:
            gid_after = int(sync.get("generation_id", 0))
            if gid_after > gid_before:
                break
        time.sleep(0.5)
    _require(
        errors,
        gid_after > gid_before,
        f"generation_id after /refresh: {gid_before}→{gid_after}",
    )
    print(
        f"OK: audit_backend_e2e refresh mode={ref.get('mode', 'light')} "
        f"{elapsed:.2f}s · generation_id {gid_before} → {gid_after} (sa-0853)"
    )

    code, ic_get = _http("GET", "/api/intelligence-circle")
    _require(errors, code == 200, f"GET intelligence-circle after async refresh: HTTP {code}")
    _require_intelligence_circle(errors, ic_get, label="GET after async /refresh")
    print("OK: audit_backend_e2e async refresh + intelligence_circle GET (sa-0216)")

    # Stale hub process may write full payload to shell on POST /refresh — heal from disk (sa-0016).
    try:
        from sina_command_lib import heal_command_data_shell_from_disk  # noqa: WPS433

        heal_ok, heal_msg = heal_command_data_shell_from_disk(force=True)
        _require(errors, heal_ok, f"heal_command_data_shell after /refresh: {heal_msg}")
        if heal_ok:
            print(f"OK: audit_backend_e2e shell heal after /refresh · {heal_msg}")
    except Exception as exc:
        _require(errors, False, f"heal_command_data_shell after /refresh: {exc}")

    if _worker_health_ok():
        print("OK: worker-health on :13030")
    else:
        _require(errors, False, "worker-health: :13030/health failed")

    if WORKER_LOCK.exists():
        print("OK: worker lock present")
    else:
        _require(errors, False, "worker lock missing (secondary signal)")

    if errors:
        print("BACKEND E2E FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("OK: backend E2E · hub APIs · live agents · agent loop · async refresh · worker-health")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
