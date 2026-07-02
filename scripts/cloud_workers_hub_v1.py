#!/usr/bin/env python3
"""Cloud Workers — founder command center (dispatch · proceed · plans · inbox · events · CLI).

Law: Founder manages cloud deploy and motor — Hub wires status + triggers only.
Agents MUST NOT auto-run deploy_fbe_railway_v1.py unless founder explicitly asks.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
DRAIN = ROOT / "data" / "secondary-cloud-forge-run-next-100-v1.json"  # legacy fallback name only


def _active_drain_path() -> Path:
    import sys

    sys.path.insert(0, str(SCRIPTS))
    from cloud_forge_run_queue_path_v1 import active_drain_path  # noqa: WPS433

    return active_drain_path()
SSOT = ROOT / "data/cloud-workers-control-plane-v1.json"
DEPLOY_SCRIPT = ROOT / "scripts/deploy_fbe_railway_v1.py"
FOUNDER_DEPLOY_CMD = "cd ~/Desktop/SourceA && python3 scripts/deploy_fbe_railway_v1.py"
EVENT_LOG = SINA / "cloud-workers-event-log-v1.json"
HUB_RECEIPT = SINA / "hub-cloud-forge-run-proceed-receipt-v1.json"
PHASE_OBS = SINA / "phase-observed-v1.json"
WORKER_INBOX = SINA / "worker-prompt-inbox-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_json(path: Path, doc: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def founder_deploy_card(*, reason: str = "") -> dict[str, Any]:
    return {
        "founder_runs_this": FOUNDER_DEPLOY_CMD,
        "deploy_script": str(DEPLOY_SCRIPT.relative_to(ROOT)),
        "why": reason or "Push latest FBE image to Railway so Proceed/Dispatch work on cloud.",
        "agent_rule": "Agents do not run deploy — founder runs the command above, then Hub Proceed.",
        "after_deploy": "Worker Hub → Cloud Workers → Refresh status → Proceed next task",
    }


def classify_cloud_result(row: dict[str, Any] | None) -> dict[str, Any]:
    """Plain-English failure class for founder — pipe vs motor vs stale."""
    row = row or {}
    blob = json.dumps(row, default=str)
    if any(x in blob for x in ("hub_cloud_forge_run_proceed", "No module named", "ModuleNotFoundError")):
        return {
            "failure_class": "stale_image",
            "pipe_live": False,
            "label": "STALE IMAGE",
            "color": "amber",
            "show_this": "Railway image missing proceed/FORGE modules — you deploy, then retry.",
            "founder_action": "deploy_railway_then_retry",
        }
    if row.get("error") in ("no_url", "cloud_proxy_error"):
        return {
            "failure_class": "connectivity",
            "pipe_live": False,
            "label": "PIPE DOWN",
            "color": "red",
            "show_this": "Cannot reach Railway cloud worker — check URL and network.",
            "founder_action": "check_cloud_url",
        }
    if row.get("error") == "cloud_proxy_http_error" and row.get("status") in (502, 503, 504):
        return {
            "failure_class": "motor_timeout",
            "pipe_live": True,
            "label": "MOTOR TIMEOUT",
            "color": "amber",
            "show_this": (
                "Pipe LIVE · Railway edge timed out during FORGE motor — "
                "cron uses evidence slice on T3/free; tap Proceed or wait for next tick."
            ),
            "founder_action": "auto_tick_or_evidence_slice",
            "plan_id": str(row.get("plan_id") or ""),
            "maps_registry": str(row.get("maps_registry") or ""),
        }
    if row.get("ok"):
        if row.get("dry_run") or (row.get("details") or {}).get("dry_run"):
            return {
                "failure_class": "dry_run_ok",
                "pipe_live": True,
                "label": "DRY RUN OK",
                "color": "green",
                "show_this": "Dry-run preview OK — pipe live, no full motor executed.",
                "founder_action": "proceed_full_motor_when_ready",
            }
        return {
            "failure_class": "pass",
            "pipe_live": True,
            "label": "PASS",
            "color": "green",
            "show_this": "Cloud proceed PASS — motor completed on Railway.",
            "founder_action": "none",
        }
    # End-of-patch success — Railway may still return HTTP 422 until image deploy catches up
    details = row.get("details") if isinstance(row.get("details"), dict) else {}
    inner_early = details or row
    decision = str(row.get("decision") or inner_early.get("decision") or "")
    pack_early = inner_early.get("pack") or row.get("pack") or {}
    if decision in ("drain_complete", "batch_complete") or (
        pack_early.get("idle_batch") and pack_early.get("registry_exhausted")
    ):
        last = str(
            inner_early.get("last_completed")
            or pack_early.get("last_completed")
            or inner_early.get("plan_id")
            or row.get("plan_id")
            or ""
        )
        return {
            "failure_class": "pass",
            "pipe_live": True,
            "label": "PATCH COMPLETE",
            "color": "green",
            "show_this": (
                f"Cloud forge patch COMPLETE — {last or 'queue head'} · "
                "registry exhausted · no more CLOUD-SEC rows to ship"
            ),
            "founder_action": "none",
        }
    # Motor / task failure — pipe often still live
    inner = inner_early
    forge = inner.get("forge_dispatch") or row.get("forge_dispatch") or {}
    plan_id = str(inner.get("plan_id") or row.get("plan_id") or "")
    registry = str(inner.get("maps_registry") or row.get("maps_registry") or "")
    motor_ok = inner.get("motor_ok")
    status = row.get("status")
    if row.get("failure_class") == "skeleton_blocked" or inner.get("failure_class") == "skeleton_blocked":
        return {
            "failure_class": "skeleton_blocked",
            "pipe_live": True,
            "label": "SKELETON BLOCKED",
            "color": "amber",
            "show_this": (
                f"Pipe LIVE · FORGE skeleton blocked on {registry or plan_id} — "
                "redeploy FBE runner image (dockerfile gate on cloud)."
            ),
            "founder_action": "deploy_railway_then_retry",
            "plan_id": plan_id,
            "maps_registry": registry,
        }
    run_result = forge.get("run_result") or inner.get("run_result") or {}
    skel = forge.get("skeleton") or {}
    if not run_result and skel.get("dockerfile") is False:
        return {
            "failure_class": "skeleton_blocked",
            "pipe_live": True,
            "label": "SKELETON BLOCKED",
            "color": "amber",
            "show_this": (
                f"Pipe LIVE · FORGE never started on {registry or plan_id} — "
                "skeleton gate failed (redeploy FBE runner)."
            ),
            "founder_action": "deploy_railway_then_retry",
            "plan_id": plan_id,
            "maps_registry": registry,
        }
    if status == 422 or motor_ok is False or (forge and not forge.get("ok")):
        gate_row = inner if inner.get("schema") == "cloud-auto-runtime-single-cycle-gate-v1" else row
        if (
            gate_row.get("schema") == "cloud-auto-runtime-single-cycle-gate-v1"
            or gate_row.get("decision") == "halt_single_cycle"
            or gate_row.get("decision") == "pack_in_progress_skip"
        ):
            reason = str(gate_row.get("reason") or gate_row.get("halt_reason") or "gate_halt")
            ff = gate_row.get("for_founder") or {}
            show = ff.get("show_this") if isinstance(ff, dict) else str(ff)
            return {
                "failure_class": "pack_gate_halt",
                "pipe_live": True,
                "label": "GATE HALT",
                "color": "amber",
                "show_this": show or f"Cloud Forge Run gate halted ({reason}) — retry Proceed or wait for cron",
                "founder_action": "retry_proceed_or_wait_cron",
                "plan_id": plan_id,
                "maps_registry": registry,
                "gate_reason": reason,
            }
        pid = plan_id or str(inner.get("resolved", {}).get("task_id") or "")
        plan = _plan_by_id(pid) if pid.startswith("CLOUD-SEC-") else None
        mock = is_mock_plan(plan)
        return {
            "failure_class": "motor_failed",
            "pipe_live": True,
            "label": "MOTOR FAIL",
            "color": "amber",
            "show_this": (
                f"Pipe LIVE · FORGE motor FAIL on {registry or plan_id}"
                + (" (scaffold row — skip or auto-pass)" if mock else "")
                + " — task execution on Railway, not Hub connectivity."
            ),
            "founder_action": "skip_head_or_auto_tick" if mock else "skip_head_or_check_railway_logs",
            "plan_id": plan_id,
            "maps_registry": registry,
            "head_is_mock": mock,
            "railway_logs_hint": "railway logs (fbe-runner service) or Cloud Workers → Skip head",
        }
    err = row.get("error") or row.get("message") or inner.get("message") or "cloud_failed"
    return {
        "failure_class": "unknown",
        "pipe_live": bool(row.get("proxied")),
        "label": "FAIL",
        "color": "red",
        "show_this": f"Cloud error: {err}",
        "founder_action": "check_receipt",
    }


def _cloud_error_founder_hint(cloud_row: dict[str, Any]) -> dict[str, Any]:
    inner = cloud_row.get("details") if isinstance(cloud_row.get("details"), dict) else cloud_row
    if inner.get("forge_dispatch") or inner.get("motor_ok") is not None:
        cloud_row = {**cloud_row, **inner}
    classified = classify_cloud_result(cloud_row)
    out: dict[str, Any] = {
        "show_this": classified["show_this"],
        "failure_class": classified["failure_class"],
        "pipe_live": classified.get("pipe_live"),
        "founder_action": classified.get("founder_action"),
        "label": classified.get("label"),
    }
    if classified["failure_class"] == "stale_image":
        out["cloud_stale"] = True
        out.update(founder_deploy_card(reason="Railway image missing hub_cloud_forge_run_proceed_v1.py"))
    else:
        out["cloud_stale"] = False
        out["receipt"] = str(HUB_RECEIPT)
    if classified.get("railway_logs_hint"):
        out["railway_logs_hint"] = classified["railway_logs_hint"]
    return out


def append_event(kind: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    doc = _read(EVENT_LOG)
    if doc.get("schema") != "cloud-workers-event-log-v1":
        doc = {"schema": "cloud-workers-event-log-v1", "events": []}
    events = list(doc.get("events") or [])
    entry = {"at": _now(), "kind": kind, **(payload or {})}
    events.insert(0, entry)
    doc["events"] = events[:200]
    doc["updated_at"] = _now()
    _write_json(EVENT_LOG, doc)
    return entry


def event_timeline(*, limit: int = 40) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    log = _read(EVENT_LOG)
    for e in list(log.get("events") or [])[:limit]:
        rows.append(
            {
                "source": "event_log",
                "at": e.get("at"),
                "kind": e.get("kind"),
                "ok": e.get("ok"),
                "plan_id": e.get("plan_id"),
                "maps_registry": e.get("maps_registry"),
                "line": e.get("line") or e.get("show_this") or e.get("kind"),
                "failure_class": e.get("failure_class"),
            }
        )
    hub = _read(HUB_RECEIPT)
    if hub.get("at"):
        cloud = hub.get("cloud") or {}
        classified = classify_cloud_result(cloud if cloud.get("details") else hub)
        rows.insert(
            0,
            {
                "source": "hub_proceed_receipt",
                "at": hub.get("at"),
                "kind": "proceed",
                "ok": hub.get("ok"),
                "plan_id": hub.get("plan_id"),
                "maps_registry": hub.get("maps_registry"),
                "line": hub.get("hub_proceed_line"),
                "failure_class": classified.get("failure_class"),
            },
        )
    receipts_dir = ROOT / "receipts"
    if receipts_dir.is_dir():
        for p in sorted(receipts_dir.glob("cloud-sec-*-receipt-v1.json"), reverse=True)[:15]:
            doc = _read(p)
            if not doc.get("at"):
                continue
            rows.append(
                {
                    "source": str(p.relative_to(ROOT)),
                    "at": doc.get("at"),
                    "kind": "cloud_sec_receipt",
                    "ok": doc.get("ok"),
                    "plan_id": doc.get("id"),
                    "maps_registry": doc.get("maps_registry"),
                    "line": (doc.get("evidence") or doc.get("title") or "")[:100],
                    "failure_class": "pass" if doc.get("ok") else "motor_failed",
                }
            )
    rows.sort(key=lambda r: str(r.get("at") or ""), reverse=True)
    seen: set[str] = set()
    out: list[dict] = []
    for r in rows:
        key = f"{r.get('at')}|{r.get('kind')}|{r.get('plan_id')}"
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
        if len(out) >= limit:
            break
    return out


def _last_cloud_plan_id() -> str:
    ids = [str(p.get("id") or "") for p in _cloud_plans()]
    return ids[-1] if ids else ""


def queue_batch_complete(*, head: str, last_done: str) -> bool:
    """True when the 100-plan Cloud Forge Run batch finished (head == last row done)."""
    last_id = _last_cloud_plan_id()
    return bool(head and last_done and head == last_done and head == last_id)


def _plan_status(plan_id: str, *, head: str, last_done: str, last_fail: str) -> str:
    if queue_batch_complete(head=head, last_done=last_done) and plan_id == head:
        return "batch_complete"
    if plan_id == head:
        return "head"
    if plan_id == last_fail and plan_id == head:
        return "failed_head"
    if plan_id == last_done:
        return "last_completed"
    m = re.match(r"CLOUD-SEC-(\d+)", plan_id)
    hm = re.match(r"CLOUD-SEC-(\d+)", head) if head else None
    dm = re.match(r"CLOUD-SEC-(\d+)", last_done) if last_done else None
    if m and dm and int(m.group(1)) <= int(dm.group(1)):
        return "completed"
    if m and hm and int(m.group(1)) < int(hm.group(1)):
        return "completed"
    return "pending"


def _fetch_cf_queue(*, timeout_s: float = 12.0) -> dict[str, Any]:
    """Mac may read CF /queue proxy — never Cloud Forge Run HTTP."""
    import urllib.error
    import urllib.request

    ssot = _read(ROOT / "data/cloud-auto-runtime-v1.json")
    cf = (ssot.get("cloudflare_worker") or {}).get("url") or ""
    cf_base = str(cf or "https://sourcea-cloud-auto-runtime-tick-v1.sina-kazemnezhad-ca.workers.dev").rstrip("/")
    url = f"{cf_base}/queue"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            row = json.loads(resp.read().decode("utf-8"))
            if isinstance(row, dict) and row.get("cloud_forge_run_head"):
                return row
            return {"ok": False, "error": "invalid_cf_queue", "url": url}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "error": f"cf_http_{exc.code}", "url": url}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:120], "url": url}


def _sync_cloud_queue_to_mac() -> dict[str, Any]:
    """Pull live queue from CF proxy when Mac phase diverges from cloud."""
    phase = _read(PHASE_OBS)
    local_head = str(phase.get("cloud_forge_run_head") or "")
    local_batch = int(phase.get("batch_id") or 0)
    live = _fetch_cf_queue()
    if not live.get("cloud_forge_run_head"):
        return {
            "ok": True,
            "skipped": "cf_fetch_failed",
            "head": local_head,
            "batch_id": phase.get("batch_id"),
            "cf_error": live.get("error"),
        }
    cloud_head = str(live.get("cloud_forge_run_head") or "")
    observed = live.get("observed") if isinstance(live.get("observed"), dict) else {}
    cloud_batch = int(observed.get("batch_id") or 0)
    diverged = bool(local_head and cloud_head != local_head) or (
        cloud_batch and local_batch and cloud_batch != local_batch
    )
    if not diverged and local_head == cloud_head:
        return {
            "ok": True,
            "synced": False,
            "head": local_head,
            "batch_id": phase.get("batch_id"),
            "reason": "already_current",
        }
    synced = apply_live_queue(live)
    synced["synced"] = True
    synced["source"] = "cf_queue_auto"
    return synced


def _mac_observe_block(action: str) -> dict[str, Any]:
    cf = _read(ROOT / "data/cloud-auto-runtime-v1.json").get("cloudflare_worker") or {}
    cf_base = str(cf.get("url") or "https://sourcea-cloud-auto-runtime-tick-v1.sina-kazemnezhad-ca.workers.dev").rstrip("/")
    return {
        "ok": False,
        "error": "mac_observe_only",
        "schema": "mac-cloud-observe-only-v1",
        "action": action,
        "execution_plane": "mac_control_panel",
        "motor_blocked": True,
        "for_founder": {
            "show_this": (
                f"Mac does not {action} on Railway motor — CF cron */10 runs full_pack×100. "
                "Deploy/dispatch still works: Hub → cloud-worker · loop-specialist · forge run."
            ),
        },
        "cf_tick_url": f"{cf_base}/tick",
        "cf_queue_url": f"{cf_base}/queue",
        "cf_observer_url": f"{cf_base}/observer-json",
        "mac_dispatch_hint": "python3 scripts/mac_cloud_deploy_dispatch_v1.py --target dispatch --plan-id MAC-CTL-002",
    }


def trigger_cf_full_pack(*, force: bool = False) -> dict[str, Any]:
    """Mac-safe: trigger Cloudflare cron worker tick (not direct Railway motor)."""
    ssot = _read(ROOT / "data/cloud-auto-runtime-v1.json")
    cf = ssot.get("cloudflare_worker") or {}
    cf_base = str(cf.get("url") or "https://sourcea-cloud-auto-runtime-tick-v1.sina-kazemnezhad-ca.workers.dev").rstrip("/")
    tick_url = f"{cf_base}/tick"
    payload = {
        "proceed": True,
        "full_pack": bool(ssot.get("full_pack", True)),
        "max_advance": int(ssot.get("max_advance_per_tick") or 100),
        "trigger_source": "mac_hub_trigger_cf",
        "force": bool(force),
    }
    import urllib.error
    import urllib.request

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
    }
    req = urllib.request.Request(
        tick_url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    row: dict[str, Any] = {}
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8")
            row = json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as exc:
        try:
            row = json.loads(exc.read().decode("utf-8"))
        except Exception:
            row = {"ok": False, "error": "cf_tick_http_error", "status": exc.code, "message": str(exc)}
        # Cloudflare edge sometimes blocks urllib — curl fallback (INCIDENT-042).
        if exc.code == 403:
            try:
                import subprocess

                proc = subprocess.run(
                    [
                        "curl",
                        "-sfS",
                        "--max-time",
                        "120",
                        "-X",
                        "POST",
                        tick_url,
                        "-H",
                        "Content-Type: application/json",
                        "-d",
                        json.dumps(payload),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=125,
                )
                if proc.stdout.strip():
                    row = json.loads(proc.stdout)
            except Exception as curl_exc:
                row.setdefault("curl_fallback_error", str(curl_exc)[:120])
    except Exception as exc:
        row = {"ok": False, "error": "cf_tick_failed", "message": str(exc)[:200]}

    out = {
        "ok": bool(row.get("ok")),
        "schema": "mac-cf-trigger-tick-v1",
        "at": _now(),
        "execution_plane": "mac_control_panel",
        "tick_url": tick_url,
        "payload": payload,
        "cf_response": row,
        "for_founder": {
            "show_this": (
                "CF full-pack tick triggered from Mac — motor runs on cloud, not Mac body. "
                f"Observer: {cf_base}/observer-json"
            ),
        },
    }
    append_event("trigger_cf_tick", {"ok": out.get("ok"), "line": json.dumps(row)[:200]})
    return out


def apply_live_queue(cloud_row: dict[str, Any]) -> dict[str, Any]:
    """Sync Mac phase + active batch file pointer from browser-fetched live queue (CF proxy)."""
    if not isinstance(cloud_row, dict) or not cloud_row.get("cloud_forge_run_head"):
        return {"ok": False, "error": "invalid_live_queue"}
    observed = cloud_row.get("observed") if isinstance(cloud_row.get("observed"), dict) else {}
    batch_id = observed.get("batch_id")
    head = str(cloud_row.get("cloud_forge_run_head") or "")
    last = cloud_row.get("cloud_forge_run_last_completed")
    phase = _read(PHASE_OBS)
    phase.update(
        {
            "schema": "phase-observed-v1",
            "cloud_forge_run_head": head,
            "cloud_forge_run_last_completed": last,
            "queue_batch_complete": cloud_row.get("queue_batch_complete", False),
            "batch_id": int(batch_id) if batch_id is not None else phase.get("batch_id"),
            "rebuilt_at": _now(),
            "rebuilt_by": "cloud_workers_hub_v1.apply_live_queue",
            "synced_from_cloud": True,
            "sync_source": "cf_queue_proxy",
            "skip_reason": observed.get("skip_reason"),
            "rebuilt_by_cloud": observed.get("rebuilt_by"),
        }
    )
    _write_json(PHASE_OBS, phase)
    wired: dict[str, Any] = {"ok": True, "skipped": True}
    if batch_id is not None:
        ptr = _read(ROOT / "data/cloud-forge-run-queue-active-v1.json")
        active_batch = int(ptr.get("batch_id") or 0)
        if active_batch != int(batch_id):
            try:
                import sys

                sys.path.insert(0, str(SCRIPTS))
                from cloud_forge_run_wire_batch_chain_v1 import wire  # noqa: WPS433

                wired = wire(active_batch_id=int(batch_id))
            except Exception as exc:
                wired = {"ok": False, "error": str(exc)[:120]}
        else:
            wired = {"ok": True, "skipped": True, "reason": "pointer_already_batch"}
    return {
        "ok": True,
        "schema": "cloud-forge-run-live-sync-v1",
        "at": _now(),
        "head": head,
        "last_completed": last,
        "batch_id": batch_id,
        "wire": wired,
        "for_founder": {"show_this": f"Live sync · head {head} · batch {batch_id}"},
    }


def chain_status() -> dict[str, Any]:
    """Local receipts only — honest chain picture without Mac→Railway HTTP."""
    deploy = _read(SINA / "fbe-cloud-deploy-receipt-v1.json")
    phase = _read(PHASE_OBS)
    tick = _read(SINA / "cloud-auto-runtime-tick-receipt-v1.json")
    hub = _read(HUB_RECEIPT)
    ssot = _read(ROOT / "data/cloud-auto-runtime-v1.json")
    cf = ssot.get("cloudflare_worker") or {}
    cp = _read(ROOT / "data/cloud-workers-control-plane-v1.json")
    url = str(deploy.get("worker_url") or deploy.get("url") or "")
    health = deploy.get("health") if isinstance(deploy.get("health"), dict) else {}
    health_ok = bool(deploy.get("ok")) and bool(health.get("ok"))
    cf_base = str(cf.get("url") or "https://sourcea-cloud-auto-runtime-tick-v1.sina-kazemnezhad-ca.workers.dev").rstrip("/")
    return {
        "ok": health_ok,
        "schema": "cloud-workers-chain-status-v1",
        "at": _now(),
        "execution_plane": "mac_control_dispatch",
        "mac_never_commands_railway_motor": True,
        "mac_control_dispatch_allowed": True,
        "railway": {
            "url": url,
            "deploy_at": deploy.get("at"),
            "health_ok": health_ok,
            "health": health,
            "queue_url": f"{url.rstrip('/')}/api/cloud-forge-run/queue/v1" if url else None,
            "observer_url": f"{url.rstrip('/')}/api/cloud-forge-run/observer/v1" if url else None,
        },
        "cf_cron": {
            "url": cf_base,
            "cron": cf.get("cron") or ssot.get("cron") or "*/10 * * * *",
            "health_url": f"{cf_base}/health",
            "tick_url": f"{cf_base}/tick",
            "queue_proxy_url": f"{cf_base}/queue",
            "observer_proxy_url": f"{cf_base}/observer-json",
        },
        "pattern": {
            "full_pack": True,
            "max_advance_per_tick": ssot.get("max_advance_per_tick") or 100,
            "scheduler": "cloudflare_cron_only",
        },
        "queue_local": {
            "head": phase.get("cloud_forge_run_head"),
            "last_completed": phase.get("cloud_forge_run_last_completed"),
            "batch_id": phase.get("batch_id"),
            "queue_batch_complete": phase.get("queue_batch_complete"),
            "synced_from_cloud": phase.get("synced_from_cloud"),
        },
        "active_batch": cp.get("active_batch"),
        "last_mac_tick": {
            "at": tick.get("at"),
            "decision": tick.get("decision"),
            "local_head": tick.get("local_head"),
        },
        "last_hub_receipt": {
            "at": hub.get("at"),
            "ok": hub.get("ok"),
            "error": hub.get("error"),
            "ignored_on_mac": hub.get("error") == "mac_observe_only",
        },
        "for_founder": {
            "show_this": (
                f"Chain · Railway deploy {'PASS' if health_ok else 'FAIL'} · "
                f"CF cron {cf.get('cron') or '*/10 * * * *'} · "
                f"local head {phase.get('cloud_forge_run_head') or '—'} · "
                "Mac dispatch OK · motor = CF cron only"
            ),
        },
    }


def _proxy_queue_action(action: str, *, reason: str = "", max_skips: int = 12) -> dict[str, Any]:
    return _mac_observe_block(action)


def plans_organized(*, limit_cloud: int = 30, limit_mac: int = 10) -> dict[str, Any]:
    _sync_cloud_queue_to_mac()
    drain = _read(_active_drain_path())
    all_plans = list(drain.get("plans") or [])
    obs = _read(PHASE_OBS)
    head = str(obs.get("cloud_forge_run_head") or "")
    last_done = str(obs.get("cloud_forge_run_last_completed") or "")
    hub = _read(HUB_RECEIPT)
    last_fail = str(hub.get("plan_id") or "") if hub.get("ok") is False else ""

    mac_rows: list[dict] = []
    cloud_rows: list[dict] = []
    for p in all_plans:
        pid = str(p.get("id") or "")
        plane = str(p.get("plane") or "")
        row = {
            "id": pid,
            "n": p.get("n"),
            "plane": plane,
            "maps_registry": p.get("maps_registry"),
            "title": p.get("cloud_action") or p.get("title"),
            "tier": p.get("tier"),
            "competitor": p.get("competitor"),
            "workstream": p.get("workstream"),
            "cost_tier": p.get("cost_tier"),
            "mac_role": p.get("mac_role"),
        }
        if plane == "mac_control" or pid.startswith("MAC-CTL-"):
            mac_rows.append(row)
        elif pid.startswith("CLOUD-SEC-"):
            st = _plan_status(pid, head=head, last_done=last_done, last_fail=last_fail)
            row["status"] = st
            row["is_head"] = pid == head
            row["is_mock"] = is_mock_plan(p)
            cloud_rows.append(row)

    head_plan = _plan_by_id(head)
    batch_done = bool(obs.get("queue_batch_complete")) or queue_batch_complete(head=head, last_done=last_done)
    visible = cloud_rows[:limit_cloud]
    head_row = next((r for r in cloud_rows if r.get("id") == head), None)
    if head_row and not any(r.get("id") == head for r in visible):
        visible = [head_row] + [r for r in visible if r.get("id") != head][: max(0, limit_cloud - 1)]
    return {
        "summary": drain.get("summary") or {},
        "one_law": drain.get("one_law"),
        "queue_head": head,
        "last_completed": last_done,
        "queue_batch_complete": batch_done,
        "head_is_mock": False if batch_done else is_mock_plan(head_plan),
        "mac_control": mac_rows[:limit_mac],
        "cloud_forge": visible,
        "cloud_forge_total": len(cloud_rows),
        "counts": {
            "mac_control": len(mac_rows),
            "cloud_forge": len(cloud_rows),
            "completed_estimate": sum(1 for r in cloud_rows if r.get("status") == "completed"),
            "pending_estimate": sum(1 for r in cloud_rows if r.get("status") == "pending"),
        },
    }


def cloud_inbox(*, window: int = 8) -> dict[str, Any]:
    """Cloud queue inbox — what founder should act on next (not Cursor Worker RUN INBOX)."""
    organized = plans_organized(limit_cloud=window + 3)
    head = organized.get("queue_head") or ""
    cloud = organized.get("cloud_forge") or []
    head_row = next((r for r in cloud if r.get("id") == head), None)
    upcoming = [r for r in cloud if r.get("status") in ("head", "pending")][:window]
    worker = _read(WORKER_INBOX)
    hub = _read(HUB_RECEIPT)
    classified = classify_cloud_result((hub.get("cloud") or {}) if hub else {})

    items: list[dict[str, Any]] = []
    if head_row:
        items.append(
            {
                "priority": "P0",
                "id": head_row.get("id"),
                "maps_registry": head_row.get("maps_registry"),
                "title": head_row.get("title"),
                "status": head_row.get("status"),
                "action": "proceed_or_skip",
                "note": "Queue head — tap Proceed or Skip head if motor blocked",
            }
        )
    for r in upcoming:
        if r.get("id") == head:
            continue
        items.append(
            {
                "priority": "P1",
                "id": r.get("id"),
                "maps_registry": r.get("maps_registry"),
                "title": r.get("title"),
                "status": r.get("status"),
                "action": "dispatch_preview",
                "note": "Upcoming cloud row",
            }
        )

    return {
        "schema": "cloud-workers-inbox-v1",
        "at": _now(),
        "one_law": "Cloud inbox = CLOUD-SEC queue on Railway — NOT Cursor Worker RUN INBOX",
        "worker_inbox_note": {
            "pending": worker.get("pending"),
            "queue_exhausted": (worker.get("meta") or {}).get("queue_exhausted"),
            "path": str(WORKER_INBOX),
            "show_this": (
                "Worker RUN INBOX idle — cloud work lives in CLOUD-SEC queue below"
                if not worker.get("pending")
                else "Worker INBOX has pending — still use Cloud Workers for FORGE motor"
            ),
        },
        "last_proceed": {
            "ok": hub.get("ok"),
            "plan_id": hub.get("plan_id"),
            "maps_registry": hub.get("maps_registry"),
            "at": hub.get("at"),
            "failure_class": classified.get("failure_class"),
            "show_this": classified.get("show_this"),
        },
        "items": items,
    }


def cli_catalog() -> list[dict[str, str]]:
    base = "cd ~/Desktop/SourceA && python3 scripts/cloud_workers_hub_v1.py"
    return [
        {"id": "status", "label": "Full status JSON", "cmd": f"{base} --json"},
        {"id": "situation", "label": "Situation card", "cmd": f"{base} --action situation --json"},
        {"id": "probe", "label": "Probe Railway", "cmd": f"{base} --probe --json"},
        {"id": "dry_run_mac", "label": "Dry-run queue (Mac only)", "cmd": f"{base} --action dry_run --json"},
        {"id": "dry_run_cloud", "label": "Dry-run on cloud", "cmd": f"{base} --action proceed_dry_cloud --json"},
        {"id": "plans", "label": "Organized plans", "cmd": f"{base} --action plans --json"},
        {"id": "inbox", "label": "Cloud inbox", "cmd": f"{base} --action inbox --json"},
        {"id": "events", "label": "Event timeline", "cmd": f"{base} --action events --json"},
        {"id": "deploy", "label": "Deploy instructions", "cmd": f"{base} --action deploy_instructions --json"},
        {
            "id": "deploy_railway",
            "label": "YOU deploy Railway (founder only)",
            "cmd": FOUNDER_DEPLOY_CMD,
        },
        {
            "id": "trigger_cf_tick",
            "label": "Trigger CF full-pack tick (Mac-safe)",
            "cmd": f"{base} --action trigger_cf_tick --json",
        },
        {
            "id": "dispatch_mac",
            "label": "Dispatch plan via Hub (Mac OK)",
            "cmd": "python3 scripts/mac_cloud_deploy_dispatch_v1.py --target dispatch --plan-id MAC-CTL-002 --json",
        },
        {
            "id": "hub_status_curl",
            "label": "Cloud Workers GET",
            "cmd": "curl -s http://127.0.0.1:13027/api/cloud-workers/v1 | python3 -m json.tool",
        },
    ]


def situation_card() -> dict[str, Any]:
    chain = chain_status()
    probe = probe_cloud_worker()
    organized = plans_organized(limit_cloud=5)
    inbox = cloud_inbox(window=3)
    hub = _read(HUB_RECEIPT)
    head = str(organized.get("queue_head") or chain.get("queue_local", {}).get("head") or "")
    head_is_mock = bool(organized.get("head_is_mock"))
    batch_done = bool(organized.get("queue_batch_complete"))
    health_ok = bool(chain.get("ok"))
    pipe = "LIVE" if health_ok else "DOWN"
    hub_stale_fail = (
        hub.get("ok") is False
        and hub.get("error") != "mac_observe_only"
        and hub.get("at")
    )

    parts = [
        f"Pipe {pipe} · Mac dispatch OK · motor CF cron",
        (
            f"Batch COMPLETE · {organized.get('last_completed') or '—'}"
            if batch_done
            else f"Queue head {head or '—'}"
        ),
        f"CF cron {chain.get('cf_cron', {}).get('cron') or '*/10 * * * *'}",
    ]
    if hub_stale_fail:
        parts.append(f"Stale receipt FAIL (ignored) · {hub.get('error') or 'old proceed'}")

    return {
        "schema": "cloud-workers-situation-v1",
        "at": _now(),
        "pipe": pipe,
        "pipe_live": health_ok,
        "cloud_stale": not health_ok,
        "mac_motor_observe_only": True,
        "mac_control_dispatch_allowed": True,
        "cloud_worker_url": chain.get("railway", {}).get("url"),
        "cf_cron_url": chain.get("cf_cron", {}).get("url"),
        "queue_head": head,
        "last_completed": organized.get("last_completed"),
        "head_is_mock": head_is_mock,
        "queue_batch_complete": batch_done,
        "head_proceed_failed": False,
        "last_proceed": {
            "at": None if hub.get("error") == "mac_observe_only" else hub.get("at"),
            "ok": None if hub.get("error") == "mac_observe_only" else hub.get("ok"),
            "plan_id": None,
            "failure_class": None,
            "label": None,
        },
        "summary_line": " · ".join(parts),
        "for_founder": {
            "show_this": chain.get("for_founder", {}).get("show_this") or probe.get("for_founder", {}).get("show_this"),
        },
        "chain": chain,
        "inbox_headline": (inbox.get("items") or [{}])[0].get("title") if inbox.get("items") else "—",
        "deploy": founder_deploy_card(),
    }


def probe_cloud_worker() -> dict[str, Any]:
    deploy = _read(SINA / "fbe-cloud-deploy-receipt-v1.json")
    url = str(deploy.get("worker_url") or deploy.get("url") or "")
    health = deploy.get("health") if isinstance(deploy.get("health"), dict) else {}
    health_ok = bool(health.get("ok"))
    observer = f"{url.rstrip('/')}/api/cloud-forge-run/observer/v1" if url else ""
    return {
        "ok": health_ok,
        "schema": "cloud-workers-probe-v1",
        "at": _now(),
        "execution_plane": "mac_control_dispatch",
        "cloud_worker_url": url or None,
        "health": health,
        "deploy_at": deploy.get("at"),
        "modules_ok": bool(deploy.get("ok")),
        "cloud_stale": not health_ok,
        "observer_url": observer,
        "for_founder": {
            "show_this": (
                f"Mac dispatch OK · motor CF cron · last deploy {deploy.get('at') or '—'} · "
                f"health {'PASS' if health_ok else 'FAIL'} · proof {observer or 'deploy first'}"
            ),
            "pipe_live": health_ok,
        },
        "mac_motor_observe_only": True,
        "mac_control_dispatch_allowed": True,
    }


def plans_queue(*, limit: int = 25) -> list[dict[str, Any]]:
    return (plans_organized(limit_cloud=limit).get("cloud_forge") or [])[:limit]


def reports_recent(*, limit: int = 12) -> list[dict[str, Any]]:
    receipts_dir = ROOT / "receipts"
    rows: list[dict] = []
    if receipts_dir.is_dir():
        for p in sorted(receipts_dir.glob("cloud-sec-*-receipt-v1.json"), reverse=True)[:limit]:
            doc = _read(p)
            rows.append(
                {
                    "path": str(p.relative_to(ROOT)),
                    "id": doc.get("id"),
                    "ok": doc.get("ok"),
                    "at": doc.get("at"),
                    "evidence": (doc.get("evidence") or "")[:120],
                }
            )
    hub_rcpt = _read(HUB_RECEIPT)
    if hub_rcpt:
        rows.insert(
            0,
            {
                "path": str(HUB_RECEIPT),
                "id": hub_rcpt.get("plan_id"),
                "ok": hub_rcpt.get("ok"),
                "at": hub_rcpt.get("at"),
                "evidence": (hub_rcpt.get("hub_proceed_line") or "")[:120],
            },
        )
    return rows[:limit]


def _cloud_plans() -> list[dict[str, Any]]:
    drain = _read(_active_drain_path())
    return [p for p in (drain.get("plans") or []) if str(p.get("id", "")).startswith("CLOUD-SEC-")]


def _plan_by_id(plan_id: str) -> dict[str, Any] | None:
    return next((p for p in _cloud_plans() if str(p.get("id")) == plan_id), None)


def is_mock_plan(plan: dict[str, Any] | None) -> bool:
    if not plan:
        return False
    if plan.get("auto_pass") is True:
        return True
    if str(plan.get("drain_lane") or "") == "scaffold":
        return True
    blob = json.dumps(plan).lower()
    return "mock_only" in blob or "mock run-detail" in blob or "stub mock" in blob


def is_mock_at_head() -> bool:
    obs = _read(PHASE_OBS)
    head = str(obs.get("cloud_forge_run_head") or "")
    return is_mock_plan(_plan_by_id(head))


def skip_head(*, reason: str = "") -> dict[str, Any]:
    return _mac_observe_block("skip_head")


def skip_to_next_real(*, reason: str = "", max_skips: int = 12) -> dict[str, Any]:
    return _mac_observe_block("skip_to_next_real")


def auto_runtime_status() -> dict[str, Any]:
    ssot_path = ROOT / "data/cloud-auto-runtime-v1.json"
    ssot = _read(ssot_path) if ssot_path.is_file() else {}
    flag = SINA / "cloud-forge-run-auto-proceed-v1.flag"
    env_on = str(__import__("os").environ.get("CLOUD_FORGE_RUN_AUTO_PROCEED", "")).lower() in (
        "1",
        "true",
        "yes",
    )
    enabled = bool(ssot.get("enabled")) or flag.is_file() or env_on
    hub = _read(HUB_RECEIPT)
    tick_rcpt = _read(SINA / "cloud-auto-runtime-tick-receipt-v1.json")
    return {
        "ok": True,
        "schema": "cloud-auto-runtime-status-v1",
        "at": _now(),
        "auto_proceed_enabled": enabled,
        "flag_path": str(flag),
        "ssot": str(ssot_path.relative_to(ROOT)) if ssot_path.is_file() else "",
        "cron": ssot.get("cron") or "*/10 * * * *",
        "mac_observe_only": bool(ssot.get("mac_observe_only", True)),
        "scheduler": "cloudflare_cron",
        "head": str(_read(PHASE_OBS).get("cloud_forge_run_head") or ""),
        "head_is_mock": is_mock_at_head(),
        "last_proceed_ok": hub.get("ok"),
        "last_proceed_plan": hub.get("plan_id"),
        "last_auto_tick": tick_rcpt.get("at"),
        "last_auto_tick_ok": tick_rcpt.get("ok"),
    }


def payload() -> dict[str, Any]:
    import sys

    sys.path.insert(0, str(SCRIPTS))
    from hub_cloud_forge_run_proceed_v1 import hub_slice  # noqa: WPS433

    live_sync = _sync_cloud_queue_to_mac()
    probe = probe_cloud_worker()
    situation = situation_card()
    return {
        "ok": True,
        "schema": "cloud-workers-hub-v1",
        "at": _now(),
        "live_sync": live_sync,
        "one_law": "Founder manages cloud deploy + plans — Hub dispatches/triggers/reports only.",
        "ssot": str(SSOT.relative_to(ROOT)),
        "hub_apis": {
            "status": "GET /api/cloud-workers/v1",
            "probe": "POST {\"action\":\"probe\"}",
            "situation": "POST {\"action\":\"situation\"}",
            "plans": "POST {\"action\":\"plans\"}",
            "inbox": "POST {\"action\":\"inbox\"}",
            "events": "POST {\"action\":\"events\"}",
            "cli": "POST {\"action\":\"cli\"}",
            "dry_run_mac": "POST {\"action\":\"dry_run\"}",
            "dry_run_cloud": "POST {\"action\":\"proceed_dry_cloud\"}",
            "dispatch": "POST {\"action\":\"dispatch\",\"plan_id\":\"CLOUD-SEC-011\"}",
            "skip_head": "POST {\"action\":\"skip_head\",\"reason\":\"motor blocked\"}",
            "skip_to_next_real": "POST {\"action\":\"skip_to_next_real\"}",
            "sync_live_queue": "POST {\"action\":\"sync_live_queue\",\"queue\":{...}}",
            "chain_status": "POST {\"action\":\"chain_status\"}",
            "auto_tick": "POST {\"action\":\"auto_tick\"} (Mac observe only)",
            "auto_status": "POST {\"action\":\"auto_status\"}",
            "proceed": "POST {\"action\":\"proceed\",\"full_pack\":true,\"max_advance\":100}",
        },
        "situation": situation,
        "chain": chain_status(),
        "proceed_slice": hub_slice(),
        "probe": probe,
        "deploy": founder_deploy_card(),
        "plans": plans_organized(),
        "inbox": cloud_inbox(),
        "events": event_timeline(limit=20),
        "cli": cli_catalog(),
        "reports": reports_recent(),
        "auto_runtime": auto_runtime_status(),
        "living_system_chain": _living_system_chain_slice(),
        "for_founder": situation.get("for_founder") or probe.get("for_founder") or {"show_this": "Load Cloud Workers status."},
    }


def _living_system_chain_slice() -> dict[str, Any]:
    try:
        from living_system_chain_validate_v1 import hub_slice  # noqa: WPS433

        return hub_slice()
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200]}


def handle_action(body: dict[str, Any] | None) -> dict[str, Any]:
    import sys

    sys.path.insert(0, str(SCRIPTS))
    body = body or {}
    action = str(body.get("action") or "status").strip().lower()

    if action in ("status", "refresh", "payload"):
        return payload()

    if action == "situation":
        return {"ok": True, **situation_card()}

    if action == "plans":
        return {"ok": True, **plans_organized(limit_cloud=int(body.get("limit") or 50))}

    if action == "inbox":
        return {"ok": True, **cloud_inbox(window=int(body.get("window") or 8))}

    if action == "events":
        return {"ok": True, "events": event_timeline(limit=int(body.get("limit") or 40))}

    if action == "cli":
        return {"ok": True, "cli": cli_catalog(), "deploy": founder_deploy_card()}

    if action == "probe":
        row = probe_cloud_worker()
        row["plans"] = plans_queue(limit=10)
        row["chain"] = chain_status()
        return row

    if action == "chain_status":
        return chain_status()

    if action == "sync_live_queue":
        row = body.get("queue") if isinstance(body.get("queue"), dict) else body
        return apply_live_queue(row if isinstance(row, dict) else {})

    if action == "dry_run":
        from hub_cloud_forge_run_proceed_v1 import _resolve_next  # noqa: WPS433

        nxt = _resolve_next(
            plan_id=str(body.get("plan_id") or ""),
            maps_registry=str(body.get("maps_registry") or ""),
        )
        return {
            "ok": True,
            "schema": "cloud-workers-dry-run-v1",
            "at": _now(),
            "execution_plane": "mac_hub_resolve_only",
            "next": nxt,
            "for_founder": {
                "show_this": f"Mac dry-run — next queue row {nxt.get('task_id')} · {str(nxt.get('title', ''))[:80]}",
                "note": "No cloud motor — only resolves queue on Mac.",
            },
        }

    if action == "proceed_dry_cloud":
        from hub_cloud_forge_run_proceed_v1 import proceed_from_hub  # noqa: WPS433

        row = proceed_from_hub(
            {
                "dry_run": True,
                "full_motor": bool(body.get("full_motor", False)),
                "llm_provider": body.get("llm_provider") or "openrouter",
                "plan_id": body.get("plan_id"),
                "maps_registry": body.get("maps_registry"),
            }
        )
        classified = classify_cloud_result(row.get("cloud") or row)
        row["for_founder"] = row.get("for_founder") or classified
        row["failure_class"] = classified.get("failure_class")
        return row

    if action == "dispatch":
        plan_id = str(body.get("plan_id") or "").strip()
        if not plan_id:
            return {"ok": False, "error": "plan_id_required"}
        from fbe.lib.hub_cloud_proxy_v1 import proxy_to_cloud  # noqa: WPS433

        row = proxy_to_cloud(
            path="/api/cloud-worker/dispatch/v1",
            body={"plan_id": plan_id, "dry_run": bool(body.get("dry_run"))},
            timeout_s=120,
        )
        if not row.get("ok"):
            row["for_founder"] = _cloud_error_founder_hint(row)
        append_event("dispatch", {"ok": row.get("ok"), "plan_id": plan_id, "line": json.dumps(row)[:200]})
        return row

    if action == "skip_head":
        return skip_head(reason=str(body.get("reason") or "founder_skip"))

    if action == "skip_to_next_real":
        return skip_to_next_real(reason=str(body.get("reason") or "founder_skip_mock"))

    if action == "auto_status":
        return auto_runtime_status()

    if action == "auto_tick":
        from fbe.lib.mac_control_dispatch_v1 import (  # noqa: WPS433
            is_mac_control_plane,
            mac_deploy_bypass,
            upgrade_mac_motor_block,
        )

        if is_mac_control_plane() and not mac_deploy_bypass():
            return upgrade_mac_motor_block(
                _mac_observe_block("auto_tick"),
                cf_tick_row=trigger_cf_full_pack(force=bool(body.get("force"))),
                action="auto_tick",
            )
        from cloud_auto_runtime_v1 import run_auto_tick  # noqa: WPS433

        return run_auto_tick(
            force=bool(body.get("force")),
            llm_provider=str(body.get("llm_provider") or "openrouter"),
            trigger_source=str(body.get("trigger_source") or "hub_auto_tick"),
        )

    if action == "trigger_cf_tick":
        return trigger_cf_full_pack(force=bool(body.get("force")))

    if action == "glue_run":
        cmd = str(body.get("command") or "").strip()
        if not cmd:
            return {"ok": False, "error": "command_required"}
        from n8n_glue_runner_v1 import COMMANDS  # noqa: WPS433

        fn = COMMANDS.get(cmd)
        if not fn:
            return {"ok": False, "error": "unknown_glue_command", "command": cmd}
        payload = body.get("payload")
        if cmd in (
            "signal-ingest",
            "cooldown-ingest",
            "founder-request",
            "semej-bookend",
            "chat-unify-merge",
            "film-ingest",
        ):
            if isinstance(payload, dict):
                payload = json.dumps(payload)
            result = fn(payload if payload else None)
        else:
            result = fn()
        return {"ok": bool(result.get("ok", True)), "command": cmd, **result}

    if action == "proceed":
        from fbe.lib.mac_control_dispatch_v1 import upgrade_mac_motor_block  # noqa: WPS433
        from hub_cloud_forge_run_proceed_v1 import proceed_from_hub  # noqa: WPS433

        row = proceed_from_hub(body)
        if row.get("error") == "mac_observe_only":
            row = upgrade_mac_motor_block(
                row,
                cf_tick_row=trigger_cf_full_pack(force=bool(body.get("force"))),
                action="proceed",
            )
            row["ok"] = True
        return row

    if action == "deploy_instructions":
        return {"ok": True, "deploy": founder_deploy_card(reason=str(body.get("reason") or ""))}

    return {
        "ok": False,
        "error": "unknown_action",
        "allowed": [
            "status",
            "situation",
            "plans",
            "inbox",
            "events",
            "cli",
            "probe",
            "dry_run",
            "proceed_dry_cloud",
            "dispatch",
            "skip_head",
            "skip_to_next_real",
            "sync_live_queue",
            "chain_status",
            "auto_tick",
            "trigger_cf_tick",
            "auto_status",
            "glue_run",
            "proceed",
            "deploy_instructions",
        ],
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Cloud Workers founder hub v1")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--action", default="status")
    args = ap.parse_args()
    row = probe_cloud_worker() if args.probe else handle_action({"action": args.action})
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
