#!/usr/bin/env python3
"""n8n glue runner — single entry point for all workflow executeCommand nodes."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SOURCE_A = Path(__file__).resolve().parents[1]
SCRIPTS = SOURCE_A / "scripts"
SINA = Path.home() / ".sina"
sys.path.insert(0, str(SCRIPTS))

from n8n_glue_config_v1 import load_config, receipt_path, RECEIPTS_ROOT  # noqa: E402

GOVERNANCE_FINDINGS = SINA / "mac-health" / "governance-findings-v1.json"
POISON_RECEIPT = SINA / "poison-track-receipt-v1.json"
FACTORY_NOW = SINA / "factory-now-v1.json"
PAUSE_FLAG = SINA / "n8n-paused-v1.json"
SIGNAL_LOG = SINA / "n8n-intelligence" / "signals.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _probe(url: str, *, timeout: float = 3.0) -> dict[str, Any]:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(1024).decode("utf-8", errors="replace")
            return {"ok": resp.status in (200, 201, 204), "status": resp.status, "url": url, "snippet": body[:200]}
    except urllib.error.HTTPError as e:
        return {"ok": e.code in (200, 201, 204), "status": e.code, "url": url, "error": str(e)}
    except Exception as e:
        return {"ok": False, "url": url, "error": str(e)}


def _write_receipt(
    *,
    workflow_id: str,
    tier: int,
    track: str,
    ok: bool,
    overall: str,
    summary: str,
    data: dict | None = None,
) -> dict[str, Any]:
    row = {
        "schema": "n8n-glue-receipt-v1",
        "workflow_id": workflow_id,
        "tier": tier,
        "track": track,
        "at": _now(),
        "ok": ok,
        "overall": overall,
        "summary": summary,
        "data": data or {},
    }
    path = receipt_path(track, workflow_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    row["receipt_path"] = str(path)
    return row


def _attach_glue_receipt(result: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    """Attach glue receipt without circular refs when receipt.data is the same dict."""
    result["glue_receipt"] = {
        "schema": receipt.get("schema"),
        "workflow_id": receipt.get("workflow_id"),
        "tier": receipt.get("tier"),
        "track": receipt.get("track"),
        "at": receipt.get("at"),
        "ok": receipt.get("ok"),
        "overall": receipt.get("overall"),
        "summary": receipt.get("summary"),
        "receipt_path": receipt.get("receipt_path"),
    }
    return result


def _overall_from_probes(probes: dict[str, dict], *, hub_mode: str) -> str:
    required = ["mac_health", "n8n"]
    for key in required:
        if not probes.get(key, {}).get("ok"):
            return "red"
    optional_warn = []
    for key in ("hub", "runtime", "n8n_integration"):
        p = probes.get(key, {})
        if not p.get("ok"):
            if key == "hub" and hub_mode == "quarantined":
                optional_warn.append(key)
            elif key in ("runtime", "n8n_integration"):
                optional_warn.append(key)
            else:
                return "yellow"
    return "yellow" if optional_warn else "green"


def cmd_health() -> dict[str, Any]:
    cfg = load_config()
    urls = cfg.get("urls") or {}
    hub_mode = cfg.get("hub_mode", "live")
    probes = {
        "mac_health": _probe(f"{urls.get('mac_health', '').rstrip('/')}/health"),
        "n8n": _probe(f"{urls.get('n8n', '').rstrip('/')}/healthz"),
        "n8n_integration": _probe(f"{urls.get('n8n_integration', '').rstrip('/')}/health"),
        "hub": _probe(f"{urls.get('hub', '').rstrip('/')}/health"),
        "runtime": _probe(f"{urls.get('runtime', '').rstrip('/')}/health"),
    }
    live = _probe(f"{urls.get('mac_health', '').rstrip('/')}/api/mac-health/live")
    if live.get("ok"):
        try:
            live["data"] = json.loads(live.get("snippet", "{}"))
        except json.JSONDecodeError:
            pass
    overall = _overall_from_probes(probes, hub_mode=hub_mode)
    ok = overall in ("green", "yellow")
    summary = f"Stack health {overall} · hub_mode={hub_mode} · mac_health={'ok' if probes['mac_health'].get('ok') else 'down'}"
    receipt = _write_receipt(
        workflow_id="sinaai-stack-health-ping",
        tier=1,
        track="health",
        ok=ok,
        overall=overall,
        summary=summary,
        data={"probes": probes, "hub_mode": hub_mode, "live_ok": live.get("ok")},
    )
    return {"ok": ok, "overall": overall, "probes": probes, "receipt": receipt}


def cmd_governance_fast() -> dict[str, Any]:
    py = sys.executable
    proc = subprocess.run(
        [py, str(SCRIPTS / "governance_center_run_v1.py"), "--tier", "fast", "--json"],
        cwd=str(SCRIPTS),
        capture_output=True,
        text=True,
        timeout=300,
    )
    data: dict[str, Any] = {"exit": proc.returncode}
    if proc.stdout.strip():
        lines = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]
        for ln in reversed(lines):
            if ln.startswith("{"):
                try:
                    data["result"] = json.loads(ln)
                    break
                except json.JSONDecodeError:
                    continue
        if "result" not in data:
            data["stdout_tail"] = proc.stdout[-500:]
    ok = proc.returncode == 0
    poison_risk = False
    stall_sa = None
    if isinstance(data.get("result"), dict):
        steps = data["result"].get("steps") or []
        for s in steps:
            tail = str(s.get("tail", "")).lower()
            if "poison" in tail or "stall" in tail:
                poison_risk = True
    receipt = _write_receipt(
        workflow_id="wf-governance-fast-15m",
        tier=3,
        track="governance",
        ok=ok,
        overall="green" if ok else "red",
        summary=f"Governance fast tier {'PASS' if ok else 'FAIL'}",
        data={**data, "poison_risk": poison_risk, "stall_sa": stall_sa},
    )
    return {"ok": ok, "receipt": receipt, **data}


def cmd_factory_stuck() -> dict[str, Any]:
    stuck = False
    sa_id = None
    hours = 0.0
    message = "Factory not stuck"
    if FACTORY_NOW.is_file():
        try:
            fn = json.loads(FACTORY_NOW.read_text(encoding="utf-8"))
            sa_id = fn.get("sa_id") or fn.get("active_sa")
            started = fn.get("started_at") or fn.get("at")
            if started:
                dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
                hours = (datetime.now(timezone.utc) - dt).total_seconds() / 3600
                if hours >= 2 and sa_id:
                    stuck = True
                    message = f"SA {sa_id} stuck {hours:.1f}h — notify founder (no auto-run)"
        except (OSError, json.JSONDecodeError, ValueError):
            pass
    receipt = _write_receipt(
        workflow_id="wf-run-inbox-reminder",
        tier=3,
        track="factory",
        ok=True,
        overall="yellow" if stuck else "green",
        summary=message,
        data={"stuck": stuck, "sa_id": sa_id, "hours": round(hours, 2)},
    )
    return {"ok": True, "stuck": stuck, "sa_id": sa_id, "hours": hours, "message": message, "receipt": receipt}


def cmd_poison_track() -> dict[str, Any]:
    open_steps: list[dict] = []
    if POISON_RECEIPT.is_file():
        try:
            pt = json.loads(POISON_RECEIPT.read_text(encoding="utf-8"))
            for step in pt.get("steps") or pt.get("open_steps") or []:
                if isinstance(step, dict) and step.get("status", "open") != "closed":
                    open_steps.append(step)
        except (OSError, json.JSONDecodeError):
            pass
    count = len(open_steps)
    summary = f"{count} open PT-C step(s)" if count else "No open poison-track steps"
    receipt = _write_receipt(
        workflow_id="wf-poison-track-reminder",
        tier=3,
        track="governance",
        ok=True,
        overall="yellow" if count else "green",
        summary=summary,
        data={"open_steps": open_steps[:20], "count": count},
    )
    return {"ok": True, "count": count, "open_steps": open_steps, "summary": summary, "receipt": receipt}


def cmd_queue_sweep() -> dict[str, Any]:
    from mac_health_guard import pipeline_queue_sweep  # noqa: WPS433
    from n8n_film_factory_wire_v1 import film_factory_queue_note  # noqa: WPS433

    result = pipeline_queue_sweep()
    film_note = film_factory_queue_note()
    ok = True
    killed = int(result.get("killed") or 0)
    overall = "green" if killed == 0 else "yellow"
    if film_note.get("film_render_frozen"):
        overall = "yellow" if overall == "green" else overall
    receipt = _write_receipt(
        workflow_id="wf-factory-queue-sweeper",
        tier=2,
        track="factory",
        ok=ok,
        overall=overall,
        summary=(
            f"Queue sweep killed {killed} zombie(s)"
            + (" · film render FROZEN" if film_note.get("film_render_frozen") else "")
        ),
        data={"queue": result, "film_factory": film_note},
    )
    return {"ok": ok, "result": result, "film_factory": film_note, "receipt": receipt}


def cmd_disk_wire() -> dict[str, Any]:
    proc = subprocess.run(
        ["bash", str(SCRIPTS / "validate-disk-live-wire-v1.sh")],
        cwd=str(SOURCE_A),
        capture_output=True,
        text=True,
        timeout=120,
    )
    ok = proc.returncode == 0
    if ok:
        if GOVERNANCE_FINDINGS.is_file():
            try:
                GOVERNANCE_FINDINGS.unlink()
            except OSError:
                pass
    elif not ok:
        GOVERNANCE_FINDINGS.parent.mkdir(parents=True, exist_ok=True)
        GOVERNANCE_FINDINGS.write_text(
            json.dumps(
                {
                    "schema": "mac-health-governance-findings-v1",
                    "at": _now(),
                    "severity": "medium",
                    "title": "Disk live wire FAIL",
                    "detail": (proc.stdout or proc.stderr or "")[-800:],
                    "source": "wf-disk-live-wire-watchdog",
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    receipt = _write_receipt(
        workflow_id="wf-disk-live-wire-watchdog",
        tier=2,
        track="health",
        ok=ok,
        overall="green" if ok else "red",
        summary="Disk live wire PASS" if ok else "Disk live wire FAIL — finding written for Mac Health",
        data={"exit": proc.returncode, "tail": (proc.stdout or proc.stderr or "")[-400:]},
    )
    return {"ok": ok, "receipt": receipt}


def cmd_cpu_pause_check() -> dict[str, Any]:
    cfg = load_config()
    urls = cfg.get("urls") or {}
    dry_run = bool(cfg.get("cpu_pause_dry_run", True))
    live = _probe(f"{urls.get('mac_health', '').rstrip('/')}/api/mac-health/live")
    cpu = None
    if live.get("ok"):
        try:
            data = json.loads(live.get("snippet", "{}"))
            mp = data.get("machine_pressure") or {}
            cpu = float(mp.get("cpu_pct") or data.get("cpu_pct") or 0)
        except (json.JSONDecodeError, TypeError, ValueError):
            cpu = None
    state_path = SINA / "n8n-cpu-samples-v1.json"
    samples: list[float] = []
    if state_path.is_file():
        try:
            samples = json.loads(state_path.read_text(encoding="utf-8")).get("samples") or []
        except (OSError, json.JSONDecodeError):
            samples = []
    if cpu is not None:
        samples = (samples + [cpu])[-3:]
    state_path.write_text(json.dumps({"samples": samples, "at": _now()}), encoding="utf-8")
    pause = len(samples) >= 3 and all(s >= 95 for s in samples)
    resume = cpu is not None and cpu < 70
    action = "none"
    if pause and not resume:
        action = "pause"
    elif resume:
        action = "resume"
    flag = {"at": _now(), "paused": action == "pause", "dry_run": dry_run, "cpu": cpu, "samples": samples}
    if not dry_run and action == "pause":
        PAUSE_FLAG.write_text(json.dumps(flag, indent=2), encoding="utf-8")
    elif action == "resume" and PAUSE_FLAG.is_file():
        PAUSE_FLAG.unlink(missing_ok=True)
    receipt = _write_receipt(
        workflow_id="wf-n8n-self-pause-cpu",
        tier=2,
        track="health",
        ok=True,
        overall="red" if pause else "green",
        summary=f"CPU pause check: {action} (dry_run={dry_run}, cpu={cpu})",
        data=flag,
    )
    return {"ok": True, "action": action, "cpu": cpu, "dry_run": dry_run, "receipt": receipt}


def cmd_signal_ingest(payload_json: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if payload_json:
        try:
            payload = json.loads(payload_json)
        except json.JSONDecodeError as e:
            return {"ok": False, "error": str(e)}
    source = payload.get("source", "unknown")
    event = payload.get("event", "signal")
    SIGNAL_LOG.parent.mkdir(parents=True, exist_ok=True)
    row = {"schema": "product-signal-v1", "at": _now(), "source": source, "event": event, "payload": payload}
    with SIGNAL_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    try:
        from n8n_intelligence import capture_and_save  # noqa: WPS433

        cap = capture_and_save(include_runtime_ask=False)
    except Exception as e:
        cap = {"ok": False, "error": str(e)}
    receipt = _write_receipt(
        workflow_id="sinaai-product-signal-webhook",
        tier=4,
        track="intelligence",
        ok=True,
        overall="green",
        summary=f"Signal ingested: {source}/{event}",
        data={"signal": row, "capture": cap},
    )
    return {"ok": True, "signal": row, "capture": cap, "receipt": receipt}


def cmd_judge_audit() -> dict[str, Any]:
    py = sys.executable
    proc = subprocess.run(
        [py, str(SCRIPTS / "governance_center_run_v1.py"), "--tier", "full", "--json"],
        cwd=str(SCRIPTS),
        capture_output=True,
        text=True,
        timeout=600,
    )
    ok = proc.returncode == 0
    receipt = _write_receipt(
        workflow_id="wf-judge-audit-batch",
        tier=5,
        track="governance",
        ok=ok,
        overall="green" if ok else "red",
        summary=f"Judge audit batch {'PASS' if ok else 'FAIL'}",
        data={"exit": proc.returncode, "tail": (proc.stdout or proc.stderr or "")[-500:]},
    )
    return {"ok": ok, "receipt": receipt}


def cmd_thread_scout() -> dict[str, Any]:
    receipt = _write_receipt(
        workflow_id="wf-thread-scout-weekly",
        tier=5,
        track="governance",
        ok=True,
        overall="green",
        summary="Thread scout weekly — transcript drift scan scheduled (stub receipt)",
        data={"note": "Full scout wiring uses agent transcript paths under ~/.cursor"},
    )
    return {"ok": True, "receipt": receipt}


def cmd_openrouter_shadow() -> dict[str, Any]:
    usage_path = SINA / "openrouter-usage-v1.json"
    snapshot: dict[str, Any] = {}
    if usage_path.is_file():
        try:
            snapshot = json.loads(usage_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    receipt = _write_receipt(
        workflow_id="wf-openrouter-governance-hook",
        tier=5,
        track="governance",
        ok=True,
        overall="green",
        summary="OpenRouter shadow snapshot (observe only)",
        data={"spend_snapshot": snapshot, "gate": "shadow"},
    )
    return {"ok": True, "receipt": receipt, "snapshot": snapshot}


def cmd_scoreboard_sync() -> dict[str, Any]:
    cache = SOURCE_A / "agent-control-panel" / "command-data-canonical.json"
    data: dict[str, Any] = {}
    if cache.is_file():
        try:
            data = json.loads(cache.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    receipt = _write_receipt(
        workflow_id="wf-agent-scoreboard-sync",
        tier=6,
        track="governance",
        ok=bool(data),
        overall="green" if data else "yellow",
        summary="Scoreboard synced from disk cache" if data else "Scoreboard cache missing",
        data={"agent_count": (data.get("agent_scoreboard") or {}).get("agent_count")},
    )
    return {"ok": bool(data), "receipt": receipt}


def cmd_founder_request(payload_json: str | None = None) -> dict[str, Any]:
    payload = json.loads(payload_json) if payload_json else {}
    out_dir = SOURCE_A / "founder-requests"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "requests.jsonl"
    row = {"at": _now(), **payload}
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    receipt = _write_receipt(
        workflow_id="wf-founder-request-registrar",
        tier=6,
        track="archive",
        ok=True,
        overall="green",
        summary="Founder request registered",
        data={"path": str(path)},
    )
    return {"ok": True, "receipt": receipt}


def cmd_semej_bookend(payload_json: str | None = None) -> dict[str, Any]:
    payload = json.loads(payload_json) if payload_json else {"phase": "end"}
    path = SINA / "semej-session-receipts.jsonl"
    row = {"at": _now(), **payload}
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    receipt = _write_receipt(
        workflow_id="wf-semej-session-bookend",
        tier=6,
        track="archive",
        ok=True,
        overall="green",
        summary=f"SEMEJ bookend {payload.get('phase', '?')}",
        data=row,
    )
    return {"ok": True, "receipt": receipt}


def cmd_backup_archive() -> dict[str, Any]:
    import shutil
    from datetime import date

    stamp = date.today().isoformat()
    dest = SINA / "backups" / f"mac-health-n8n-{stamp}.zip"
    dest.parent.mkdir(parents=True, exist_ok=True)
    src_dirs = [SINA / "mac-health", SINA / "n8n-receipts"]
    # zip selected dirs
    import tempfile

    tmp = Path(tempfile.mkdtemp())
    for d in src_dirs:
        if d.is_dir():
            shutil.copytree(d, tmp / d.name, dirs_exist_ok=True)
    shutil.make_archive(str(dest.with_suffix("")), "zip", tmp)
    shutil.rmtree(tmp, ignore_errors=True)
    ok = dest.is_file()
    receipt = _write_receipt(
        workflow_id="wf-backup-receipt-archiver",
        tier=6,
        track="archive",
        ok=ok,
        overall="green" if ok else "red",
        summary=f"Backup archive {'written' if ok else 'failed'}",
        data={"path": str(dest)},
    )
    return {"ok": ok, "path": str(dest), "receipt": receipt}


def cmd_cooldown_ingest(payload_json: str | None = None) -> dict[str, Any]:
    payload = json.loads(payload_json) if payload_json else {}
    cpu_after = float(payload.get("cpu_after") or payload.get("cpu_pct") or 0)
    alert = cpu_after >= 90
    track_dir = RECEIPTS_ROOT / "mac-health"
    track_dir.mkdir(parents=True, exist_ok=True)
    path = track_dir / "cooldown.jsonl"
    row = {
        "schema": "mac-health-cooldown-v1",
        "at": _now(),
        "alert": alert,
        **payload,
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    receipt = _write_receipt(
        workflow_id="wf-mac-health-cooldown",
        tier=1,
        track="health",
        ok=True,
        overall="red" if alert else "green",
        summary=f"Cool Down logged · CPU after {cpu_after}%" + (" · ALERT" if alert else ""),
        data=row,
    )
    return {"ok": True, "alert": alert, "receipt": receipt}


def cmd_chat_unify_merge(payload_json: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if payload_json:
        try:
            payload = json.loads(payload_json)
        except json.JSONDecodeError as e:
            return {"ok": False, "error": str(e)}
    brief_chars = int(payload.get("brief_chars") or 0)
    extract_count = int(payload.get("extract_count") or 0)
    contradiction_count = int(payload.get("contradiction_count") or 0)
    track_dir = RECEIPTS_ROOT / "intelligence"
    track_dir.mkdir(parents=True, exist_ok=True)
    path = track_dir / "chat-unify-merge.jsonl"
    row = {
        "schema": "chat-unify-merge-v1",
        "at": _now(),
        "source": payload.get("source") or "chat-unify",
        "event": payload.get("event") or "merge_receipt",
        "extract_count": extract_count,
        "contradiction_count": contradiction_count,
        "brief_chars": brief_chars,
        "receipt_path": payload.get("receipt_path"),
        "extract_ids": payload.get("extract_ids") or [],
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    receipt = _write_receipt(
        workflow_id="wf-chat-unify-merge-receipt-v1",
        tier=4,
        track="intelligence",
        ok=True,
        overall="green" if contradiction_count == 0 else "yellow",
        summary=f"Chat Unify merge · {extract_count} extracts · {contradiction_count} contradictions",
        data=row,
    )
    return {"ok": True, "merge": row, "receipt": receipt}


def cmd_film_ingest(payload_json: str | None = None) -> dict[str, Any]:
    """P0 ship gate — Screen Studio ingest + critic + unfreeze."""
    payload: dict[str, Any] = {}
    if payload_json:
        try:
            payload = json.loads(payload_json)
        except json.JSONDecodeError as e:
            return {"ok": False, "error": str(e)}

    from n8n_film_factory_wire_v1 import film_ship_gate  # noqa: WPS433

    lane = (payload.get("lane") or payload.get("body", {}).get("lane") or "sourcea").strip()
    lane_map = {
        "sourcea_commercial": "sourcea",
        "sourcea_w1": "sourcea",
        "sourcea": "sourcea",
        "witnessbc": "witnessbc",
    }
    lane = lane_map.get(lane, lane)
    result = film_ship_gate(
        lane=lane,
        skip_ingest=bool(payload.get("skip_ingest")),
        no_deploy=bool(payload.get("no_deploy")),
    )
    receipt = _write_receipt(
        workflow_id="wf-film-screen-studio-ingest-v1",
        tier=3,
        track="film_factory",
        ok=bool(result.get("publish_allowed")),
        overall="green" if result.get("publish_allowed") else "red",
        summary=result.get("factory_now_line") or f"ship_gate lane={lane}",
        data=result,
    )
    result["receipt"] = receipt
    return result


def cmd_film_compile(payload_json: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if payload_json:
        try:
            payload = json.loads(payload_json)
        except json.JSONDecodeError as e:
            return {"ok": False, "error": str(e)}
    from n8n_film_factory_wire_v1 import film_compile  # noqa: WPS433

    lane = (payload.get("lane") or "witnessbc").strip()
    result = film_compile(lane=lane, skip_capture=bool(payload.get("skip_capture")))
    receipt = _write_receipt(
        workflow_id="wf-cinematic-film-compile-v1",
        tier=3,
        track="film_factory",
        ok=bool(result.get("ok")),
        overall="green" if result.get("ok") else "yellow",
        summary=f"film_compile lane={lane}",
        data=result,
    )
    return _attach_glue_receipt(result, receipt)


def cmd_film_critic(payload_json: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if payload_json:
        try:
            payload = json.loads(payload_json)
        except json.JSONDecodeError as e:
            return {"ok": False, "error": str(e)}
    from n8n_film_factory_wire_v1 import film_critic  # noqa: WPS433

    lane = (payload.get("lane") or "all").strip()
    result = film_critic(lane=lane, no_freeze=bool(payload.get("no_freeze")))
    receipt = _write_receipt(
        workflow_id="wf-cinematic-film-critic-v1",
        tier=3,
        track="film_factory",
        ok=bool(result.get("ok")),
        overall="green" if result.get("verdict") == "PASS" else "red",
        summary=f"film_critic lane={lane} verdict={result.get('verdict')}",
        data=result,
    )
    return _attach_glue_receipt(result, receipt)


def cmd_film_status(_payload_json: str | None = None) -> dict[str, Any]:
    from n8n_film_factory_wire_v1 import film_status  # noqa: WPS433

    result = film_status()
    receipt = _write_receipt(
        workflow_id="wf-cinematic-film-status-v1",
        tier=2,
        track="film_factory",
        ok=True,
        overall="yellow" if (result.get("freeze") or {}).get("frozen") else "green",
        summary=result.get("factory_now_line") or "film_status",
        data=result,
    )
    return _attach_glue_receipt(result, receipt)


def cmd_cloud_drain_auto_tick() -> dict[str, Any]:
    from cloud_drain_auto_runtime_v1 import run_auto_tick  # noqa: WPS433

    result = run_auto_tick(trigger_source="n8n_cron_wf-cloud-drain-auto-v1")
    receipt = write_receipt(
        workflow_id="wf-cloud-drain-auto-v1",
        command="cloud-drain-auto-tick",
        ok=bool(result.get("ok", True)),
        data=result,
    )
    return _attach_glue_receipt(result, receipt)


COMMANDS = {
    "health": cmd_health,
    "governance-fast": cmd_governance_fast,
    "factory-stuck": cmd_factory_stuck,
    "poison-track": cmd_poison_track,
    "queue-sweep": cmd_queue_sweep,
    "disk-wire": cmd_disk_wire,
    "cpu-pause-check": cmd_cpu_pause_check,
    "chat-unify-merge": cmd_chat_unify_merge,
    "signal-ingest": cmd_signal_ingest,
    "cooldown-ingest": cmd_cooldown_ingest,
    "judge-audit": cmd_judge_audit,
    "thread-scout": cmd_thread_scout,
    "openrouter-shadow": cmd_openrouter_shadow,
    "scoreboard-sync": cmd_scoreboard_sync,
    "founder-request": cmd_founder_request,
    "semej-bookend": cmd_semej_bookend,
    "backup-archive": cmd_backup_archive,
    "cloud-drain-auto-tick": cmd_cloud_drain_auto_tick,
    "film-ingest": cmd_film_ingest,
    "film-ship-gate": cmd_film_ingest,
    "film-compile": cmd_film_compile,
    "film-critic": cmd_film_critic,
    "film-status": cmd_film_status,
}


def main() -> int:
    p = argparse.ArgumentParser(description="n8n glue runner v1")
    p.add_argument("command", choices=sorted(COMMANDS.keys()))
    p.add_argument("--payload", default="", help="JSON payload for ingest commands")
    args = p.parse_args()
    fn = COMMANDS[args.command]
    if args.command in ("signal-ingest", "cooldown-ingest", "founder-request", "semej-bookend", "chat-unify-merge", "film-ingest"):
        result = fn(args.payload or None)
    else:
        result = fn()
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
