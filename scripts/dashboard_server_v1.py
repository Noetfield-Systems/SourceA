#!/usr/bin/env python3
"""SourceA Dashboard Server — port 13021.

Serves the live dashboard and reads state directly from disk.
Works even when Hub (:13020) is down.

Usage:
    python3 scripts/dashboard_server_v1.py
    open http://127.0.0.1:13021
"""
from __future__ import annotations
import json, os, subprocess, sys, time, urllib.parse, urllib.request, urllib.error
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT   = Path(__file__).resolve().parents[1]
HOME   = Path.home()
SINA   = HOME / ".sina"
HUB    = "http://127.0.0.1:13020"
PORT   = 13021

KILL_FLAG       = SINA / "auto-run-disabled-v1.flag"
BATCH_LOCK      = SINA / "goal1-worker-batch-lock-v1.json"
QUEUE_STATE     = SINA / "healthy-queue-state-v1.json"
ORCH_STATE      = SINA / "healthy-drain-orchestrator-v1.json"
AGENT_LOG       = SINA / "claude-api-agent-v1.jsonl"
BATCH_LOG       = SINA / "goal1-worker-batch-latest.log"
QUEUE_FILE      = SINA / "healthy-queue-30-active.json"
QUEUE_REPO      = ROOT / "brain-os/plan-registry/sourcea-1000/prompts/healthy-queue-30-active.json"
REGISTRY        = ROOT / "brain-os/plan-registry/sourcea-1000/REGISTRY.json"
SCRIPTS         = ROOT / "scripts"
ACTIVE_NOW      = ROOT / "ACTIVE_NOW.md"
HEALTH_DIR      = SINA / "apple-health"
HEALTH_GOALS    = HEALTH_DIR / "goals.json"
HEALTH_SLEEP    = HEALTH_DIR / "sleep-signal-v1.json"
HEALTH_AUTO_ARM = HEALTH_DIR / "auto-arm-sleep-v1.flag"
SIDECAR_PID     = SINA / "sidecar-engines-watch-v1.pid"
SIDECAR_LOG     = SINA / "sidecar-engines-watch-v1.log"
SCOUT_DIR       = SINA / "sidecar" / "api-scout"
PREP_DIR        = SINA / "sidecar" / "cli-prep"
OVERNIGHT_PID   = SINA / "overnight-3engine-v1.pid"
OVERNIGHT_LOG   = SINA / "overnight-3engine-v1.log"

def _now(): return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def _read(p):
    try: return Path(p).read_text(encoding="utf-8")
    except: return ""
def _json(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except: return {}
def _pid_alive(pid):
    try: os.kill(int(pid), 0); return True
    except: return False

def hub_healthy():
    try:
        with urllib.request.urlopen(f"{HUB}/health", timeout=2) as r:
            return json.loads(r.read()).get("ok") is True
    except: return False

def hub_post(path, body={}):
    try:
        data = json.dumps(body).encode()
        req = urllib.request.Request(f"{HUB}{path}", data=data,
              headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e: return {"ok": False, "error": str(e)}

def get_active_now():
    """Parse ACTIVE_NOW.md for the 3 operating mode fields."""
    text = _read(ACTIVE_NOW)
    result = {
        "founder_mode": "founder_busy",
        "sleep_escalation": "off",
        "sprint": "",
        "sa_id": "",
        "blocker": "none",
    }
    for line in text.splitlines():
        l = line.strip()
        if l.startswith("**Current Founder Mode:**"):
            v = l.split("**Current Founder Mode:**")[-1].strip().strip("`").strip()
            result["founder_mode"] = v
        elif l.startswith("**Current Sleep Escalation:**"):
            v = l.split("**Current Sleep Escalation:**")[-1].strip().strip("`").strip()
            result["sleep_escalation"] = v
        elif l.startswith("**Current Sprint:**"):
            result["sprint"] = l.split("**Current Sprint:**")[-1].strip()
        elif l.startswith("**Current sa_id:**") or ("sa_id" in l and "sa-0" in l):
            import re
            m = re.search(r"sa-\d{4}", l)
            if m: result["sa_id"] = m.group(0)
        elif l.startswith("**Current Blocker:**"):
            result["blocker"] = l.split("**Current Blocker:**")[-1].strip()
    return result

def _log_age_sec(path: Path) -> float:
    """Seconds since a log file was last modified. 9999 if missing."""
    try: return time.time() - path.stat().st_mtime
    except: return 9999.0

def get_sidecar_status():
    """Return live/idle/off status for API scout and CLI prep lanes."""
    pid_alive = False
    if SIDECAR_PID.is_file():
        try: pid_alive = _pid_alive(int(SIDECAR_PID.read_text().strip()))
        except: pass
    log_age = _log_age_sec(SIDECAR_LOG)
    # Count sidecar output files written in last 15 min
    def recent_files(d: Path) -> int:
        if not d.is_dir(): return 0
        cutoff = time.time() - 900
        return sum(1 for f in d.glob("*.md") if f.stat().st_mtime > cutoff)
    scout_recent = recent_files(SCOUT_DIR)
    prep_recent  = recent_files(PREP_DIR)
    active = pid_alive or log_age < 600
    return {
        "pid_alive": pid_alive,
        "log_age_sec": int(log_age),
        "scout_recent": scout_recent,
        "prep_recent": prep_recent,
        "active": active,
    }

def get_overnight_status():
    """Return status of the overnight dispatcher loop."""
    pid_alive = False
    if OVERNIGHT_PID.is_file():
        try: pid_alive = _pid_alive(int(OVERNIGHT_PID.read_text().strip()))
        except: pass
    log_age = _log_age_sec(OVERNIGHT_LOG)
    paused = KILL_FLAG.is_file()
    return {
        "pid_alive": pid_alive,
        "log_age_sec": int(log_age),
        "active": pid_alive and not paused,
    }


def get_cli_live() -> bool:
    """True only when a Claude CLI agent subprocess is running right now."""
    for pat in ("claude_code_agent_v1.py", "claude -p You are SourceA Worker"):
        proc = subprocess.run(["pgrep", "-f", pat], capture_output=True, text=True)
        if (proc.stdout or "").strip():
            return True
    return False

def get_operating_mode(an: dict, sidecar: dict, overnight: dict) -> dict:
    """Derive the 3-mode label from locked source fields."""
    fm  = an.get("founder_mode", "founder_busy")
    slp = an.get("sleep_escalation", "off")

    if slp == "on" or overnight.get("active"):
        return {
            "mode": "sleep",
            "label": "OVERNIGHT",
            "sub": "Dispatcher running · Worker off",
            "color": "blue",
        }
    if fm == "founder_absent":
        return {
            "mode": "founder_absent",
            "label": "FOUNDER ABSENT",
            "sub": "API scout + CLI prep · no Worker",
            "color": "yellow",
        }
    # Default: founder_busy
    return {
        "mode": "founder_busy",
        "label": "FOUNDER BUSY",
        "sub": "Worker active · sidecars watching",
        "color": "green",
    }

def get_health_data() -> dict:
    """Read Apple Health state from ~/.sina/apple-health/ — no hub required."""
    goals_raw  = _json(HEALTH_GOALS)
    sleep_raw  = _json(HEALTH_SLEEP)
    goals = goals_raw.get("goals", [])
    sleep_state  = sleep_raw.get("state", "unknown")
    sleep_hours  = sleep_raw.get("sleep_hours")
    steps_today  = sleep_raw.get("steps_today")
    heart_rate   = sleep_raw.get("heart_rate")
    in_bed       = sleep_raw.get("in_bed")
    updated_at   = sleep_raw.get("updated_at") or goals_raw.get("updated_at")
    return {
        "ok": True,
        "sleep_state": sleep_state,          # "asleep" | "awake" | "unknown"
        "sleep_hours": sleep_hours,
        "steps_today": steps_today,
        "heart_rate":  heart_rate,
        "in_bed":      in_bed,
        "updated_at":  updated_at,
        "auto_arm":    HEALTH_AUTO_ARM.is_file(),
        "goals": [
            {
                "id":     g.get("id"),
                "title":  g.get("title"),
                "target": g.get("target"),
                "metric": g.get("metric"),
                "status": g.get("status", "active"),
            }
            for g in goals
        ],
    }

def get_batch_status():
    if not BATCH_LOCK.is_file(): return "idle"
    row = _json(BATCH_LOCK)
    pid = row.get("pid")
    if pid and _pid_alive(pid): return "running"
    return "stale"

def get_autorun_status():
    if KILL_FLAG.is_file(): return "paused"
    bs = get_batch_status()
    if bs == "running": return "running"
    if bs == "stale": return "stale"
    return "idle"

def get_queue_info():
    sys.path.insert(0, str(SCRIPTS))
    from healthy_queue_ssot_lib import healthy_queue_path, queue_items, load_healthy_queue  # noqa: WPS433

    q_state = _json(QUEUE_STATE)
    pos = int(q_state.get("next_pos") or 1)
    try:
        _, raw = load_healthy_queue()
        items = queue_items(raw)
        total = len(items)
        if pos < 1 or pos > total: pos = 1
        item = items[pos-1] if items else {}
        return {
            "pos": pos, "total": total,
            "sa_id": item.get("sa_id","?"),
            "role": item.get("queue_role","?"),
            "title": item.get("title",""),
            "pct": round((pos-1)/total*100) if total else 0
        }
    except: return {"pos": pos, "total": 30, "sa_id":"?", "role":"?", "title":"", "pct":0}

def get_registry_info():
    try:
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "goal-progress-v1.py"), "--json"],
            capture_output=True, text=True, timeout=8, cwd=str(ROOT)
        )
        if r.returncode == 0:
            data = json.loads(r.stdout)
            g1 = data.get("goal_1") or {}
            honest = int(g1.get("honest_done") or g1.get("done") or 0)
            return {
                "total": int(g1.get("total") or 1000),
                "done": honest,
                "honest_done": honest,
                "raw_done": int(g1.get("raw_done") or honest),
                "unproven_done": int(g1.get("unproven_done") or 0),
                "drift": bool(g1.get("drift")),
            }
    except:
        pass
    try:
        sys.path.insert(0, str(SCRIPTS))
        from registry_honest_lib_v1 import audit_registry_done  # noqa: WPS433

        a = audit_registry_done()
        return {
            "total": int(a.get("total") or 1000),
            "done": int(a.get("honest_done") or 0),
            "honest_done": int(a.get("honest_done") or 0),
            "raw_done": int(a.get("raw_done") or 0),
            "unproven_done": int(a.get("unproven_done") or 0),
            "drift": bool(a.get("drift")),
        }
    except Exception:
        return {"total": 1000, "done": 0, "honest_done": 0, "raw_done": 0, "unproven_done": 0, "drift": False}

def get_today_cost():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%dT")
    cost, turns = 0.0, 0
    for line in _read(AGENT_LOG).splitlines():
        try:
            row = json.loads(line)
            if row.get("event") == "AGENT_DONE" and (row.get("at","")).startswith(today):
                cost += float(row.get("cost_usd") or 0)
                turns += 1
        except: pass
    return {"cost": round(cost, 4), "turns": turns}

def get_log_tail(n=30):
    lines = _read(BATCH_LOG).splitlines()
    return lines[-n:] if len(lines) > n else lines

def get_latest_trace() -> dict:
    """Return the most recent execution trace from claude_code_agent_v1."""
    trace_dir = SINA / "exec-traces"
    if not trace_dir.is_dir():
        return {}
    traces = sorted(trace_dir.glob("*-trace.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not traces:
        return {}
    try:
        return json.loads(traces[0].read_text(encoding="utf-8"))
    except: return {}

def get_today_cost_all():
    """Billable turns only — cost_usd > 0 (CLI/API skip events excluded)."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%dT")
    cost, turns, skipped = 0.0, 0, 0
    billable_events = ("AGENT_DONE", "CC_AGENT_DONE", "CC_AGENT_BILLED")
    for log_path in [AGENT_LOG, SINA / "claude-code-agent-v1.jsonl"]:
        for line in _read(log_path).splitlines():
            try:
                row = json.loads(line)
                if row.get("event") not in billable_events or not (row.get("at", "")).startswith(today):
                    continue
                c = float(row.get("cost_usd") or 0)
                if c <= 0 or row.get("billed") is False:
                    skipped += 1
                    continue
                cost += c
                turns += 1
            except Exception:
                pass
    return {"cost": round(cost, 5), "turns": turns, "skipped_zero_cost": skipped}

def get_recent_receipts(n=10):
    """Read last N receipt files from receipts/ dir."""
    receipts_dir = ROOT / "receipts"
    if not receipts_dir.is_dir():
        return []
    files = sorted(receipts_dir.glob("sa-*-receipt.json"),
                   key=lambda p: p.stat().st_mtime, reverse=True)[:n]
    results = []
    for f in files:
        try:
            r = json.loads(f.read_text(encoding="utf-8"))
            results.append(r)
        except: pass
    return results

def get_recent_results(n=8):
    """Read last N result files from cc-agent-results/."""
    rdir = SINA / "cc-agent-results"
    if not rdir.is_dir():
        return []
    files = sorted(rdir.glob("sa-*-result.json"),
                   key=lambda p: p.stat().st_mtime, reverse=True)[:n]
    results = []
    for f in files:
        try:
            results.append(json.loads(f.read_text(encoding="utf-8")))
        except: pass
    return results

def get_apple_health_status():
    try:
        sys.path.insert(0, str(SCRIPTS))
        from apple_health_sleep_bridge_v1 import evaluate  # noqa: WPS433

        return evaluate()
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

def get_program_tracker():
    try:
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "program-1000-tracker-v1.py"), "--json"],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(ROOT),
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return json.loads(proc.stdout)
    except Exception:
        pass
    tracker_json = SINA / "PROGRAM_1000_TRACKER.json"
    if tracker_json.is_file():
        p = tracker_json
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"ok": False}


def get_current_recipe() -> dict:
    """3-file recipe for queue sa + last honest closed sa (monitor SSOT)."""
    q = get_queue_info()
    sa = str(q.get("sa_id") or "")
    role = str(q.get("role") or "?")
    try:
        reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
        plans = {p.get("id"): p for p in (reg.get("plans") or [])}
        pl = plans.get(sa) or {}
        title = pl.get("title") or q.get("title") or ""
        recipe_path = pl.get("path") or ""
        verify = pl.get("verify") or ""
        reg_st = pl.get("status") or "backlog"
    except Exception:
        title, recipe_path, verify, reg_st = "", "", "", "backlog"

    last_honest: dict = {}
    try:
        sys.path.insert(0, str(SCRIPTS))
        from registry_honest_lib_v1 import audit_registry_done  # noqa: WPS433

        audit = audit_registry_done()
        ids = audit.get("honest_done_ids") or []
        if ids:
            last_id = sorted(ids, key=lambda x: int(x.split("-")[1]))[-1]
            lp = plans.get(last_id) or {}
            rec_path = ROOT / "receipts" / f"{last_id}-receipt.json"
            rec = _json(rec_path) if rec_path.is_file() else {}
            last_honest = {
                "sa_id": last_id,
                "title": lp.get("title") or "",
                "recipe_path": lp.get("path") or "",
                "verify_recipe": lp.get("verify") or "",
                "registry_status": lp.get("status") or "",
                "receipt_status": rec.get("status") or "",
                "receipt_at": rec.get("at") or "",
                "receipt_evidence": rec.get("evidence") or "",
                "receipt_path": str(rec_path) if rec_path.is_file() else "",
                "honest": True,
            }
    except Exception:
        pass

    return {
        "current": {
            "sa_id": sa,
            "queue_pos": q.get("pos"),
            "queue_total": q.get("total"),
            "queue_role": role,
            "title": title,
            "recipe_path": recipe_path,
            "verify_recipe": verify,
            "registry_status": reg_st,
            "prompt_abs": str(ROOT / "brain-os/plan-registry/sourcea-1000" / recipe_path) if recipe_path else "",
        },
        "last_honest": last_honest,
        "law": "title + prompt .md + verify command — receipt required before done",
    }


def _matrix_summary_cached() -> dict:
    matrix_json = SINA / "PROGRAM_1000_STEP_MATRIX.json"
    if matrix_json.is_file():
        try:
            row = json.loads(matrix_json.read_text(encoding="utf-8"))
            return row.get("summary") or {}
        except Exception:
            pass
    return {}


def get_step_matrix(*, bucket: str = "", phase: str = "", q: str = "", limit: int = 50, offset: int = 0, refresh: bool = True):
    args = [sys.executable, str(SCRIPTS / "program-1000-step-matrix-v1.py"), "--json"]
    if refresh:
        args.append("--write")
    if bucket:
        args += ["--bucket", bucket]
    if phase:
        args += ["--phase", phase]
    if q:
        args += ["--q", q]
    args += ["--limit", str(limit), "--offset", str(offset)]
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=30, cwd=str(ROOT))
        if proc.returncode == 0 and proc.stdout.strip():
            return json.loads(proc.stdout)
    except Exception:
        pass
    matrix_json = SINA / "PROGRAM_1000_STEP_MATRIX.json"
    if matrix_json.is_file():
        try:
            row = json.loads(matrix_json.read_text(encoding="utf-8"))
            steps = row.get("steps") or []
            if bucket:
                steps = [s for s in steps if s.get("bucket") == bucket or s.get("proof_verdict") == bucket]
            if phase:
                steps = [s for s in steps if s.get("phase") == phase]
            if q:
                ql = q.lower()
                steps = [s for s in steps if ql in s.get("sa_id", "") or ql in (s.get("title") or "").lower()]
            total = len(steps)
            return {
                "ok": True,
                "updated_at": row.get("updated_at"),
                "summary": row.get("summary"),
                "total_filtered": total,
                "steps": steps[offset : offset + limit],
            }
        except Exception:
            pass
    return {"ok": False}


def get_full_status():
    hub_up   = hub_healthy()
    auto     = get_autorun_status()
    q        = get_queue_info()
    reg      = get_registry_info()
    today    = get_today_cost_all()
    orch     = _json(ORCH_STATE)
    orch_in  = orch.get("orchestrator") or orch
    lock     = _json(BATCH_LOCK)
    q_state  = _json(QUEUE_STATE)
    receipts = get_recent_receipts()
    results  = get_recent_results()
    an       = get_active_now()
    sidecar  = get_sidecar_status()
    overnight= get_overnight_status()
    op_mode  = get_operating_mode(an, sidecar, overnight)
    # enrich receipts with model from result files
    result_map = {r.get("sa_id"): r for r in results}
    for rec in receipts:
        sid = rec.get("sa_id")
        if sid in result_map:
            rec.setdefault("model", result_map[sid].get("model",""))
            rec.setdefault("cost_usd", result_map[sid].get("cost_usd", 0))
            rec.setdefault("tool_call_count", result_map[sid].get("tool_call_count", 0))
            rec.setdefault("elapsed", result_map[sid].get("elapsed", 0))
    pause_reason = None
    if KILL_FLAG.is_file():
        pause_reason = "autorun_kill_flag"
    elif auto == "stale":
        pause_reason = "batch_lock_stale"
    elif (an.get("founder_mode") or "founder_busy") == "founder_busy":
        pause_reason = "founder_busy_manual_worker"
    return {
        "ok": True, "at": _now(),
        "hub_up": hub_up,
        "autorun": auto,
        "worker_running": auto == "running",
        "pause_reason": pause_reason,
        "queue": q,
        "queue_state": q_state,
        "registry": reg,
        "today": today,
        "today_cost": today.get("cost", 0),
        "today_turns": today.get("turns", 0),
        "orch_status": orch_in.get("status","?"),
        "orch_turns": orch_in.get("turns_completed",0),
        "batch_pid": lock.get("pid"),
        "api_mode": bool(os.environ.get("ANTHROPIC_API_KEY","").strip()),
        "kill_flag": KILL_FLAG.is_file(),
        "recent_receipts": receipts,
        "recent_results": results,
        "active_now": an,
        "sidecar": sidecar,
        "overnight": overnight,
        "op_mode": op_mode,
        "cli_live": get_cli_live() and not KILL_FLAG.is_file(),
        "apple_health": get_apple_health_status(),
        "program_matrix_summary": _matrix_summary_cached(),
        "current_recipe": get_current_recipe(),
        "track_validate": get_track_validate(),
    }


def get_validator_list(*, filter_mode: str = "road", live: bool = True) -> dict:
    try:
        sys.path.insert(0, str(SCRIPTS))
        if live:
            try:
                from monitor_live_sync_v1 import sync_disk  # noqa: WPS433

                sync_disk(reason="api_validator_list")
            except Exception:
                pass
        import importlib.util

        spec = importlib.util.spec_from_file_location("validator_list", SCRIPTS / "validator_list_v1.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        data = mod.build_list(filter_mode=filter_mode)
        mod.write_audit_snapshot(data)
        try:
            from monitor_live_sync_v1 import load_pulse  # noqa: WPS433

            data["monitor_live"] = load_pulse()
        except Exception:
            data["monitor_live"] = {"schema": "monitor-live-v1", "law": "disk-wired"}
        data["disk_wired"] = True
        data["server_at"] = _now()
        return data
    except Exception as exc:
        return {"ok": False, "error": str(exc), "rows": [], "honest_done": 0, "total": 1000}


def get_monitor_pulse() -> dict:
    try:
        sys.path.insert(0, str(SCRIPTS))
        from monitor_live_sync_v1 import sync_disk  # noqa: WPS433

        return sync_disk(reason="api_pulse")
    except Exception as exc:
        return {"ok": False, "error": str(exc), "at": _now()}


def get_track_validate() -> dict:
    """Pending/unproven backlog + broker validation — monitor + Worker INBOX SSOT."""
    try:
        sys.path.insert(0, str(SCRIPTS))
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "track_validate",
            SCRIPTS / "track_validate_backlog_v1.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        snap = mod.load_snapshot(refresh_if_stale_sec=30)
        if not snap.get("rows"):
            snap = mod.build_list(filter_mode="road")
            mod.write_audit_snapshot(snap)
        return snap
    except Exception as exc:
        return {"ok": False, "error": str(exc), "backlog": {}, "broker_validation": {}}

def action_start_autorun(max_turns=30):
    hub_up = hub_healthy()
    if hub_up:
        r = hub_post("/api/goal1-autorun-start", {"max_turns": max_turns})
        if r.get("ok"):
            return {"ok": True, "method": "hub", "pid": r.get("pid"), **r}
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "goal1_unified_autorun_v1.py"), "start", "--max-turns", str(max_turns)],
        cwd=str(ROOT), capture_output=True, text=True, timeout=60,
    )
    try:
        row = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except json.JSONDecodeError:
        row = {"ok": False, "raw": proc.stdout, "stderr": proc.stderr}
    return {**row, "method": "direct", "ok": row.get("ok", proc.returncode == 0)}


def action_stop_autorun():
    hub_up = hub_healthy()
    if hub_up:
        r = hub_post("/api/goal1-autorun-stop", {})
        if r.get("ok"):
            return {"ok": True, "method": "hub", **r}
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "goal1_unified_autorun_v1.py"), "stop"],
        cwd=str(ROOT), capture_output=True, text=True, timeout=60,
    )
    try:
        row = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except json.JSONDecodeError:
        row = {"ok": False, "raw": proc.stdout, "stderr": proc.stderr}
    return {**row, "method": "direct", "ok": row.get("ok", proc.returncode == 0)}


def action_start_batch(size=5):
    hub_up = hub_healthy()
    if hub_up:
        r = hub_post("/api/run-goal1-batch", {"batch_size": size, "max_batches": 6})
        if r.get("ok"): return {"ok": True, "method": "hub", "pid": r.get("pid")}
    # Direct spawn
    env = {**os.environ, "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY",""),
           "SINA_WORKER_CHAT_RESUME_INJECT": "1"}
    log = SINA / "goal1-worker-batch-latest.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a") as fh:
        proc = subprocess.Popen(
            [sys.executable, str(SCRIPTS/"goal1_worker_batch_loop_v1.py"),
             "--batch-size", str(size), "--max-batches", "6"],
            cwd=str(ROOT), stdout=fh, stderr=subprocess.STDOUT,
            env=env, start_new_session=True)
    return {"ok": True, "method": "direct", "pid": proc.pid}

def action_emergency_stop():
    KILL_FLAG.parent.mkdir(parents=True, exist_ok=True)
    KILL_FLAG.touch()
    (SINA / "api-disabled-v1.flag").touch()
    (SINA / "cli-disabled-v1.flag").touch()
    if hub_healthy():
        hub_post("/api/emergency-stop", {})
    procs = ["goal1_worker_batch_loop","auto_run_worker_batch","healthy-drain-orchestrator",
             "claude_api_agent","brain_run_loop","sina-command-server"]
    killed = []
    for p in procs:
        r = subprocess.run(["pkill","-9","-f",p], capture_output=True)
        if r.returncode == 0: killed.append(p)
    return {"ok": True, "killed": killed, "kill_flag": True}

def action_toggle_autorun():
    if KILL_FLAG.is_file():
        KILL_FLAG.unlink()
        return {"ok": True, "autorun": "resumed"}
    else:
        KILL_FLAG.parent.mkdir(parents=True, exist_ok=True)
        KILL_FLAG.touch()
        return {"ok": True, "autorun": "paused"}

def action_restart_hub():
    subprocess.Popen(
        ["bash", str(SCRIPTS/"serve-sina-command.sh")],
        cwd=str(ROOT), start_new_session=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)
    return {"ok": hub_healthy(), "message": "Hub restart triggered"}

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SourceA Control</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0d0d0d;color:#e0e0e0;min-height:100vh;padding:20px 24px}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}
.logo{font-size:16px;font-weight:600;color:#fff;letter-spacing:-.3px}
.ticker{font-size:11px;color:#444}
.status-pill{display:inline-flex;align-items:center;gap:6px;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:500}
.pill-green{background:#0a2010;color:#4ade80;border:1px solid #1a4020}
.pill-yellow{background:#1a1200;color:#fbbf24;border:1px solid #3a2800}
.pill-red{background:#1a0505;color:#f87171;border:1px solid #3a0f0f}
.pill-gray{background:#1a1a1a;color:#666;border:1px solid #2a2a2a}
.pill-blue{background:#050f1a;color:#60a5fa;border:1px solid #0f2a3a}
.dot{width:7px;height:7px;border-radius:50%;background:currentColor;flex-shrink:0}
.dot-pulse{animation:pulse 1.8s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px}
.card{background:#161616;border:1px solid #222;border-radius:10px;padding:14px 16px}
.card-label{font-size:11px;color:#555;text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px}
.card-value{font-size:24px;font-weight:600;color:#fff;line-height:1}
.card-sub{font-size:11px;color:#555;margin-top:5px}
.bar{background:#1e1e1e;border-radius:4px;height:5px;margin:8px 0 3px;overflow:hidden}
.bar-fill{height:100%;border-radius:4px;transition:width .6s ease}
.bar-green{background:#22c55e}
.bar-blue{background:#3b82f6}
.section{background:#161616;border:1px solid #222;border-radius:10px;padding:16px;margin-bottom:12px}
.section-title{font-size:11px;color:#555;text-transform:uppercase;letter-spacing:.06em;margin-bottom:12px}
.row{display:flex;justify-content:space-between;align-items:center;padding:9px 0;border-bottom:1px solid #1c1c1c}
.row:last-child{border-bottom:none}
.row-name{font-size:13px;color:#ccc;font-weight:500}
.row-desc{font-size:11px;color:#444;margin-top:2px}
.controls{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:12px}
.btn{border:none;border-radius:8px;padding:11px 14px;font-size:13px;font-weight:500;cursor:pointer;transition:opacity .15s,transform .1s;width:100%}
.btn:active{transform:scale(.97)}
.btn:disabled{opacity:.35;cursor:not-allowed}
.btn-green{background:#22c55e;color:#000}
.btn-red{background:#dc2626;color:#fff}
.btn-gray{background:#2a2a2a;color:#ccc}
.btn-amber{background:#d97706;color:#000}
.btn-blue{background:#2563eb;color:#fff}
.log{background:#0a0a0a;border:1px solid #1e1e1e;border-radius:8px;padding:12px;font-family:'SF Mono','Fira Code',monospace;font-size:11px;color:#666;height:180px;overflow-y:auto;line-height:1.7}
.log p{margin:0}
.log-pass{color:#4ade80}
.log-fail{color:#f87171}
.log-run{color:#60a5fa}
.log-warn{color:#fbbf24}
.current{background:#0c140c;border:1px solid #1a2c1a;border-radius:8px;padding:12px 14px;margin-bottom:12px}
.cur-sa{font-size:14px;font-weight:600;color:#4ade80}
.cur-title{font-size:12px;color:#555;margin-top:4px;line-height:1.5}
.phase-row{display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid #1c1c1c}
.phase-row:last-child{border-bottom:none}
.phase-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0}
.phase-done{background:#22c55e}
.phase-prog{background:#f59e0b}
.phase-none{background:#333}
.phase-name{font-size:13px;color:#ccc;font-weight:500;flex:1}
.phase-desc{font-size:11px;color:#444;margin-top:2px}
.phase-badge{font-size:10px;padding:2px 8px;border-radius:10px;font-weight:500}
.pb-done{background:#0a2010;color:#22c55e}
.pb-prog{background:#1a1200;color:#f59e0b}
.pb-none{background:#1a1a1a;color:#555}
.toast{position:fixed;bottom:20px;right:20px;background:#1e1e1e;border:1px solid #333;color:#e0e0e0;padding:10px 16px;border-radius:8px;font-size:13px;z-index:999;transform:translateY(80px);transition:transform .3s;display:none}
.toast.show{display:block;transform:translateY(0)}
@media(max-width:640px){.grid4{grid-template-columns:repeat(2,1fr)}.controls{grid-template-columns:1fr 1fr}}
</style>
</head>
<body>

<div class="header">
  <div class="logo">SourceA Control</div>
  <div style="display:flex;align-items:center;gap:10px">
    <span class="status-pill pill-gray" id="hub-pill"><span class="dot"></span>Hub —</span>
    <span class="status-pill pill-gray" id="auto-pill"><span class="dot"></span>—</span>
    <a href="/monitor" style="font-size:11px;color:#60a5fa;text-decoration:none;border:1px solid #0f253a;background:#050f1a;padding:4px 10px;border-radius:6px;font-weight:500">⚡ Monitor →</a>
    <span class="ticker" id="tick">—</span>
  </div>
</div>

<!-- Metrics -->
<div class="grid4">
  <div class="card">
    <div class="card-label">Queue</div>
    <div class="card-value" id="m-q">—/—</div>
    <div class="bar"><div class="bar-fill bar-green" id="q-bar" style="width:0"></div></div>
    <div class="card-sub" id="m-q-sub">—</div>
  </div>
  <div class="card">
    <div class="card-label">Registry</div>
    <div class="card-value" id="m-reg">—</div>
    <div class="bar"><div class="bar-fill bar-blue" id="r-bar" style="width:0"></div></div>
    <div class="card-sub" id="m-reg-sub">—</div>
  </div>
  <div class="card">
    <div class="card-label">Today cost</div>
    <div class="card-value" id="m-cost">—</div>
    <div class="card-sub" id="m-turns">— turns</div>
  </div>
  <div class="card" id="mode-card">
    <div class="card-label">Mode</div>
    <div class="card-value" style="font-size:13px;padding-top:4px;line-height:1.3" id="m-mode">—</div>
    <div class="card-sub" id="m-mode-sub">—</div>
    <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap">
      <span class="status-pill pill-gray" id="lane-a" style="font-size:10px;padding:2px 8px">A Worker —</span>
      <span class="status-pill pill-gray" id="lane-b" style="font-size:10px;padding:2px 8px">B Scout —</span>
      <span class="status-pill pill-gray" id="lane-c" style="font-size:10px;padding:2px 8px">C Prep —</span>
      <span class="status-pill pill-gray" id="lane-d" style="font-size:10px;padding:2px 8px">D Overnight —</span>
    </div>
  </div>
</div>

<!-- Current task -->
<div class="current" id="cur-box">
  <div class="cur-sa" id="cur-sa">Connecting…</div>
  <div class="cur-title" id="cur-title"></div>
</div>

<!-- Controls -->
<div class="controls">
  <button class="btn btn-green" id="btn-start-autorun" onclick="startAutorun()">▶ START AUTO RUN</button>
  <button class="btn btn-red" id="btn-stop-autorun" onclick="stopAutorun()">⏹ STOP AUTO RUN</button>
  <span class="status-pill pill-red" id="freeze-banner" style="display:none;font-size:11px;padding:4px 10px">FREEZE — kill flag ON · tap Hub Safety · bounded ASF resume only</span>
  <button class="btn btn-gray" id="btn-toggle" onclick="toggleAutorun()">⏸ Pause autorun</button>
  <button class="btn btn-blue" onclick="restartHub()">↺ Restart hub</button>
  <button class="btn btn-gray" onclick="refreshNow()">↻ Refresh now</button>
  <button class="btn btn-red" onclick="emergencyStop()">🛑 Emergency stop</button>
</div>

<!-- System status -->
<div class="grid2">
  <div class="section">
    <div class="section-title">System layers</div>
    <div class="row">
      <div><div class="row-name">Hub :13020</div><div class="row-desc">Control server</div></div>
      <span class="status-pill pill-gray" id="l-hub">—</span>
    </div>
    <div class="row">
      <div><div class="row-name">Claude API agent</div><div class="row-desc">Headless Worker · no Cursor</div></div>
      <span class="status-pill pill-blue" id="l-api">API</span>
    </div>
    <div class="row">
      <div><div class="row-name">Autorun daemon</div><div class="row-desc">launchd · fires batches</div></div>
      <span class="status-pill pill-gray" id="l-auto">—</span>
    </div>
    <div class="row">
      <div><div class="row-name">Worker batch</div><div class="row-desc">5 turns per checkpoint</div></div>
      <span class="status-pill pill-gray" id="l-batch">—</span>
    </div>
    <div class="row">
      <div><div class="row-name">Telegram bot</div><div class="row-desc">/status /start /stop</div></div>
      <span class="status-pill pill-yellow" id="l-tg">setup needed</span>
    </div>
  </div>

  <div class="section">
    <div class="section-title">Roadmap phases</div>
    <div class="phase-row">
      <div class="phase-dot phase-done"></div>
      <div style="flex:1">
        <div class="phase-name">Phase A — Execution Spine</div>
        <div class="phase-desc">Queue · Workers · Validators · Receipts</div>
      </div>
      <span class="phase-badge pb-done">Done</span>
    </div>
    <div class="phase-row">
      <div class="phase-dot phase-prog"></div>
      <div style="flex:1">
        <div class="phase-name">Phase B — Execution Intelligence</div>
        <div class="phase-desc">Brain routing · broker · checkpoint</div>
      </div>
      <span class="phase-badge pb-prog">Active</span>
    </div>
    <div class="phase-row">
      <div class="phase-dot phase-prog"></div>
      <div style="flex:1">
        <div class="phase-name">Phase C — Runtime Stack</div>
        <div class="phase-desc">Claude API · Telegram · Railway cloud</div>
      </div>
      <span class="phase-badge pb-prog">In progress</span>
    </div>
    <div class="phase-row">
      <div class="phase-dot phase-none"></div>
      <div style="flex:1">
        <div class="phase-name">Phase D — Pre-LLM World Model</div>
        <div class="phase-desc">Proactive understanding before execution</div>
      </div>
      <span class="phase-badge pb-none">Not started</span>
    </div>
  </div>
</div>

<!-- Live log -->
<div class="section">
  <div class="section-title">Live batch log</div>
  <div class="log" id="log-box">
    <p class="log-run">Connecting to dashboard server…</p>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
let lastLog = [];

function toast(msg, ok=true) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = 'toast show';
  setTimeout(()=>el.className='toast', 2800);
}

function pill(id, text, cls) {
  const el = document.getElementById(id);
  if (!el) return;
  el.className = 'status-pill ' + cls;
  el.innerHTML = '<span class="dot' + (cls.includes('green') ? ' dot-pulse' : '') + '"></span>' + text;
}

function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function setBar(id, pct) {
  const el = document.getElementById(id);
  if (el) el.style.width = Math.min(100, Math.max(0, pct)) + '%';
}

async function refresh() {
  try {
    const st = await fetch('/api/status').then(r=>r.json());

    // Hub
    if (st.hub_up) {
      pill('hub-pill', 'Hub online', 'pill-green');
      pill('l-hub', 'online', 'pill-green');
    } else {
      pill('hub-pill', 'Hub offline', 'pill-red');
      pill('l-hub', 'offline', 'pill-red');
    }

    // Autorun
    const a = st.autorun;
    const btnT = document.getElementById('btn-toggle');
    if (a === 'running') {
      pill('auto-pill', 'Running', 'pill-green');
      pill('l-auto', 'running', 'pill-green');
      pill('l-batch', 'running · pid ' + (st.batch_pid||'?'), 'pill-green');
      if (btnT) { btnT.textContent = '⏸ Pause autorun'; btnT.className = 'btn btn-amber'; }
    } else if (a === 'paused') {
      pill('auto-pill', 'Paused', 'pill-yellow');
      pill('l-auto', 'paused', 'pill-yellow');
      pill('l-batch', 'paused', 'pill-yellow');
      if (btnT) { btnT.textContent = '▶ Resume autorun'; btnT.className = 'btn btn-green'; }
    } else if (a === 'stale') {
      pill('auto-pill', 'Stuck', 'pill-red');
      pill('l-batch', 'stuck — restart', 'pill-red');
    } else {
      pill('auto-pill', 'Idle', 'pill-gray');
      pill('l-batch', 'idle', 'pill-gray');
      if (btnT) { btnT.textContent = '⏸ Pause autorun'; btnT.className = 'btn btn-amber'; }
    }

    // Queue
    const q = st.queue || {};
    setText('m-q', (q.pos||'?') + '/' + (q.total||30));
    setText('m-q-sub', (q.role||'?') + ' · ' + (q.pct||0) + '% done');
    setBar('q-bar', q.pct||0);
    setText('cur-sa', (q.sa_id||'?') + ' · ' + (q.role||'?'));
    setText('cur-title', q.title||'');

    // Registry
    const r = st.registry || {};
    const done = r.honest_done != null ? r.honest_done : (r.done || 0);
    const total = r.total || 1000;
    const rpct = Math.round(done/total*100);
    const drift = r.drift ? ' · drift fixed' : '';
    setText('m-reg', done + '/' + total);
    setText('m-reg-sub', rpct + '% honest · ' + (total-done) + ' left' + drift);
    setBar('r-bar', rpct);

    // Cost
    const t = st.today || {};
    setText('m-cost', '$' + (t.cost||0).toFixed(3));
    setText('m-turns', (t.turns||0) + ' turns today');

    // Operating mode (3 states from ACTIVE_NOW)
    const om = st.op_mode || {};
    const sc = st.sidecar || {};
    const on = st.overnight || {};
    const modeColors = {green:'#4ade80', yellow:'#fbbf24', blue:'#60a5fa'};
    const modePills  = {green:'pill-green', yellow:'pill-yellow', blue:'pill-blue'};
    const mc = om.color || 'gray';
    const modeCard = document.getElementById('mode-card');
    if (modeCard) modeCard.style.borderColor = (modeColors[mc] || '#222') + '55';
    setText('m-mode', om.label || '—');
    const modeEl = document.getElementById('m-mode');
    if (modeEl) modeEl.style.color = modeColors[mc] || '#fff';
    setText('m-mode-sub', om.sub || '—');

    // Lane A — Worker (active when founder_busy)
    const laneAPill = om.mode === 'founder_busy' ? 'pill-green' : 'pill-gray';
    const laneAText = om.mode === 'founder_busy' ? 'A Worker ON' : 'A Worker OFF';
    pill('lane-a', laneAText, laneAPill);

    // Lane B — API Scout (active when sidecar running)
    const laneBPill = sc.active ? 'pill-blue' : 'pill-gray';
    const laneBText = sc.active ? 'B Scout ON' : 'B Scout OFF';
    pill('lane-b', laneBText, laneBPill);

    // Lane C — green only when CLI process running; yellow when sleep-armed; gray when paused
    const paused = st.kill_flag || !!st.pause_reason;
    const startBtn = document.getElementById('btn-start-autorun');
    const freezeBanner = document.getElementById('freeze-banner');
    if (startBtn) {
      if (st.kill_flag) {
        startBtn.disabled = true;
        startBtn.textContent = 'FREEZE — Cursor AUTO-RUN rejected';
        startBtn.className = 'btn btn-gray';
      } else {
        startBtn.disabled = false;
        startBtn.textContent = '▶ START AUTO RUN';
        startBtn.className = 'btn btn-green';
      }
    }
    if (freezeBanner) freezeBanner.style.display = st.kill_flag ? 'inline-block' : 'none';
    const cliOn = !!st.cli_live && !paused;
    const cliArmed = om.mode === 'sleep' && !paused && !cliOn;
    const scActive = sc.active;
    let laneCPill = 'pill-gray';
    let laneCText = 'C CLI OFF';
    if (cliOn) { laneCPill = 'pill-green'; laneCText = 'C CLI ACT'; }
    else if (cliArmed) { laneCPill = 'pill-yellow'; laneCText = 'C CLI ARMED'; }
    else if (scActive) { laneCPill = 'pill-blue'; laneCText = 'C Prep ON'; }
    pill('lane-c', laneCText, laneCPill);

    const dOn = !!(on.active) && !paused;
    pill('lane-d', dOn ? 'D Overnight ON' : 'D Overnight OFF', dOn ? 'pill-yellow' : 'pill-gray');

    // API key indicator (l-api row)
    if (st.api_mode) {
      pill('l-api', 'key set', 'pill-green');
    } else {
      pill('l-api', 'key missing', 'pill-red');
    }

    setText('tick', 'Updated ' + new Date().toLocaleTimeString());

  } catch(e) {
    setText('tick', 'Server error: ' + e.message);
  }

  // Log
  try {
    const log = await fetch('/api/log').then(r=>r.json());
    const box = document.getElementById('log-box');
    if (JSON.stringify(log) !== JSON.stringify(lastLog)) {
      lastLog = log;
      box.innerHTML = '';
      for (const line of log) {
        const p = document.createElement('p');
        let cls = '';
        if (line.includes('PASS') || line.includes('DONE')) cls = 'log-pass';
        else if (line.includes('FAIL') || line.includes('ERROR') || line.includes('error')) cls = 'log-fail';
        else if (line.includes('START') || line.includes('starting') || line.includes('Running')) cls = 'log-run';
        else if (line.includes('WARN') || line.includes('HALT')) cls = 'log-warn';
        p.className = cls;
        p.textContent = line;
        box.appendChild(p);
      }
      box.scrollTop = box.scrollHeight;
    }
  } catch(e) {}
}

async function startAutorun() {
  const st = await fetch('/api/status').then(r=>r.json()).catch(()=>({}));
  if (st.kill_flag) {
    toast('FREEZE — kill flag ON · Hub Safety · bounded ASF resume only', false);
    return;
  }
  if (!confirm('Start unified auto-run (up to 30 turns)?')) return;
  toast('Starting auto-run…');
  const r = await fetch('/api/goal1-autorun-start', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({max_turns: 30})}).then(r=>r.json());
  toast(r.ok ? '✓ Auto-run started (pid ' + (r.pid||'?') + ')' : '✗ ' + (r.error||r.message||'failed'), r.ok);
  setTimeout(refresh, 2000);
}

async function stopAutorun() {
  toast('Stopping auto-run…');
  const r = await fetch('/api/goal1-autorun-stop', {method:'POST'}).then(r=>r.json());
  toast(r.ok ? '✓ Auto-run stopped' : '✗ ' + (r.error||r.message||'failed'), r.ok);
  setTimeout(refresh, 1500);
}

async function emergencyStop() {
  if (!confirm('EMERGENCY STOP — kill all SourceA processes?')) return;
  const r = await fetch('/api/emergency-stop', {method:'POST'}).then(r=>r.json());
  toast(r.ok ? '🛑 Stopped · killed: ' + (r.killed||[]).join(', ') : '✗ Error');
  setTimeout(refresh, 1500);
}

async function toggleAutorun() {
  const r = await fetch('/api/toggle-autorun', {method:'POST'}).then(r=>r.json());
  toast(r.autorun === 'paused' ? '⏸ Autorun paused' : '▶ Autorun resumed');
  setTimeout(refresh, 500);
}

async function restartHub() {
  toast('Restarting Hub…');
  const r = await fetch('/api/restart-hub', {method:'POST'}).then(r=>r.json());
  toast(r.ok ? '✓ Hub online' : '✗ Hub restart failed — check terminal');
  setTimeout(refresh, 2000);
}

function refreshNow() { refresh(); toast('Refreshed'); }

refresh();
setInterval(refresh, 5000);
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass  # silence access log

    def _send(self, code, body, ct="application/json"):
        data = body.encode() if isinstance(body, str) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", len(data))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, DASHBOARD_HTML, "text/html; charset=utf-8")
        elif self.path in ("/monitor", "/monitor.html"):
            monitor_file = ROOT / "monitor.html"
            try:
                html = monitor_file.read_text(encoding="utf-8")
            except Exception:
                html = "<h1>monitor.html not found</h1>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return
        elif self.path == "/api/status":
            self._send(200, get_full_status())
        elif self.path == "/api/tracker":
            self._send(200, get_program_tracker())
        elif self.path in ("/api/monitor-pulse", "/api/monitor-live"):
            self._send(200, get_monitor_pulse())
        elif self.path == "/api/live-ongoing-prompts":
            try:
                sys.path.insert(0, str(SCRIPTS))
                from live_prompt_overrides_v1 import payload as live_payload  # noqa: WPS433

                self._send(200, live_payload())
            except Exception as exc:
                self._send(500, {"ok": False, "error": str(exc)})
        elif self.path.startswith("/api/validator-list"):
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            filt = (qs.get("filter") or ["road"])[0]
            if filt == "all":
                filt = "road"
            if filt not in ("road", "queue", "attention", "done"):
                filt = "road"
            live = (qs.get("live") or ["1"])[0] not in ("0", "false", "no")
            body = get_validator_list(filter_mode=filt, live=live)
            self.send_response(200)
            payload = json.dumps(body).encode()
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(payload))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.end_headers()
            self.wfile.write(payload)
            return
        elif self.path == "/api/track-validate":
            refresh = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("refresh", ["0"])[0]
            if refresh in ("1", "full"):
                try:
                    sys.path.insert(0, str(SCRIPTS))
                    import importlib.util

                    spec = importlib.util.spec_from_file_location(
                        "track_validate",
                        SCRIPTS / "track_validate_backlog_v1.py",
                    )
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)  # type: ignore[union-attr]
                    self._send(200, mod.write_snapshot(run_validators=refresh == "full"))
                except Exception as exc:
                    self._send(500, {"ok": False, "error": str(exc)})
            else:
                self._send(200, get_track_validate())
        elif self.path.startswith("/api/steps"):
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            def _q(key, default=""):
                v = qs.get(key)
                return (v[0] if v else default) or default
            limit = max(1, min(200, int(_q("limit", "50") or 50)))
            offset = max(0, int(_q("offset", "0") or 0))
            self._send(
                200,
                get_step_matrix(
                    bucket=_q("bucket"),
                    phase=_q("phase"),
                    q=_q("q"),
                    limit=limit,
                    offset=offset,
                    refresh=_q("refresh", "1") != "0",
                ),
            )
        elif self.path.startswith("/api/log"):
            self._send(200, get_log_tail(40))
        elif self.path == "/api/health":
            self._send(200, get_health_data())
        elif self.path == "/api/trace":
            self._send(200, get_latest_trace())
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}") if length else {}

        if self.path == "/api/goal1-autorun-start":
            r = action_start_autorun(int(body.get("max_turns", 30)))
            self._send(200, r)
        elif self.path == "/api/goal1-autorun-stop":
            r = action_stop_autorun()
            self._send(200, r)
        elif self.path == "/api/start-batch":
            r = action_start_batch(int(body.get("size", 5)))
            self._send(200, r)
        elif self.path == "/api/emergency-stop":
            r = action_emergency_stop()
            self._send(200, r)
        elif self.path == "/api/toggle-autorun":
            r = action_toggle_autorun()
            self._send(200, r)
        elif self.path == "/api/restart-hub":
            r = action_restart_hub()
            self._send(200, r)
        elif self.path in ("/api/live-prompt-overrides", "/api/live-ongoing-prompts"):
            try:
                sys.path.insert(0, str(SCRIPTS))
                from live_prompt_overrides_v1 import handle_action as live_override_action  # noqa: WPS433

                self._send(200, live_override_action(body))
            except Exception as exc:
                self._send(500, {"ok": False, "error": str(exc)})
        else:
            self._send(404, {"error": "not found"})

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def main():
    sys.path.insert(0, str(SCRIPTS))
    try:
        from monitor_live_sync_v1 import start_background  # noqa: WPS433

        start_background(interval_sec=5.0)
        print("Monitor disk sync: background 5s (no agent refresh required)")
    except Exception as exc:
        print(f"Monitor disk sync: warn {exc}")
    print(f"SourceA Dashboard → http://127.0.0.1:{PORT}")
    print("Ctrl+C to stop")
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()
