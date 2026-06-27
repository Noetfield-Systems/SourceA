#!/usr/bin/env python3
"""Living system chain validator — light E2E probes for 24/7 agentic control plane."""
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SSOT = ROOT / "data/living-system-chain-registry-v1.json"
SSOT_CLOUD = ROOT / "data/living-system-chain-registry-cloud-v1.json"
RECEIPT = SINA / "living-system-chain-validate-receipt-v1.json"
HUB_PORT = int(os.environ.get("SINA_COMMAND_PORT", "13020"))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _expand(path: str) -> Path:
    return Path(os.path.expanduser(path))


def _http_probe(url: str, *, timeout: float = 12.0) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "SourceA-living-system-chain-validate/1.0", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            body = json.loads(raw) if raw.strip() else {}
            return {"ok": resp.status == 200 and bool(body.get("ok", True)), "status": resp.status, "body": body}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "url": url}


def _cloud_queue_ssot(*, timeout: float = 12.0) -> dict[str, Any]:
    """Cloud queue head — Railway only (no Mac :13020/:13027 polling)."""
    base = os.environ.get("FBE_CLOUD_WORKER_URL", "https://sourcea-fbe-runner-production.up.railway.app").rstrip("/")
    row = _http_probe(f"{base}/api/cloud-forge-run/queue/v1", timeout=timeout)
    if not row.get("ok"):
        return {"ok": False, "error": row.get("error"), "queue_head": None}
    body = row.get("body") or {}
    auto = (SINA / "cloud-forge-run-auto-proceed-v1.flag").is_file()
    return {
        "ok": True,
        "queue_head": body.get("cloud_forge_run_head"),
        "last_completed": body.get("cloud_forge_run_last_completed"),
        "pipe": "LIVE",
        "auto_proceed": auto,
        "source": "cloud:railway_queue_v1",
    }


def _hub_queue_head() -> dict[str, Any]:
    return _cloud_queue_ssot()


def _extract_head(source_url: str, field: str) -> str | None:
    row = _http_probe(source_url, timeout=20.0)
    if not row.get("ok"):
        return None
    body = row.get("body") or {}
    if field == "queue_head":
        sit = body.get("situation") or {}
        return sit.get("queue_head") or (body.get("cloud_workers_live") or {}).get("queue_head")
    if field == "cloud_forge_run_head":
        return body.get("cloud_forge_run_head")
    return body.get(field)


def _hub_queue_fast() -> dict[str, Any]:
    """Disk-first queue head — sub-second."""
    phase_path = SINA / "phase-observed-v1.json"
    if phase_path.is_file():
        try:
            phase = json.loads(phase_path.read_text(encoding="utf-8"))
            head = phase.get("cloud_forge_run_head") or phase.get("queue_head")
            if head:
                auto = (SINA / "cloud-forge-run-auto-proceed-v1.flag").is_file()
                return {
                    "ok": True,
                    "queue_head": head,
                    "last_completed": phase.get("cloud_forge_run_last_completed"),
                    "pipe": "LIVE",
                    "auto_proceed": auto,
                    "source": "disk:phase-observed-v1.json",
                }
        except (OSError, json.JSONDecodeError):
            pass
    return _cloud_queue_ssot(timeout=5.0)


def validate_chains_fast(*, write: bool = True) -> dict[str, Any]:
    """Parallel probes + disk queue — target under 3s."""
    ssot = _read(SSOT)
    hub = _hub_queue_fast()
    hub_head = hub.get("queue_head")
    chains_cfg = ssot.get("chains") or []
    chains_out: list[dict[str, Any]] = []
    critical_fail = 0

    def _probe_one(ch: dict[str, Any]) -> dict[str, Any]:
        cid = str(ch.get("id") or "")
        tier = str(ch.get("tier") or "optional")
        probe = ch.get("probe") or {}
        row: dict[str, Any] = {"id": cid, "label": ch.get("label"), "tier": tier, "ok": False}
        ptype = probe.get("type")
        if ptype == "http":
            pr = _http_probe(str(probe.get("url") or ""), timeout=5.0)
            row["ok"] = bool(pr.get("ok"))
            if not row["ok"]:
                row["error"] = pr.get("error")
            body = pr.get("body") or {}
            if cid == "railway_cloud_queue":
                row["queue_head"] = body.get("cloud_forge_run_head")
            if cid in ("cloud_workers_app", "n8n_integration_app"):
                sit = body.get("situation") or {}
                row["queue_head"] = sit.get("queue_head") or (body.get("cloud_workers_live") or {}).get("queue_head")
        elif ptype == "file":
            path = _expand(str(probe.get("path") or ""))
            row["ok"] = path.is_file()
            if not row["ok"]:
                row["error"] = "missing_flag"
        if hub_head and row.get("queue_head") and row["queue_head"] != hub_head:
            row["ok"] = False
            row["error"] = f"head_divergence hub={hub_head} local={row['queue_head']}"
        elif hub_head and cid == "railway_cloud_queue" and row.get("queue_head") and row["queue_head"] != hub_head:
            row["ok"] = False
            row["error"] = f"railway_divergence hub={hub_head}"
        return row

    with ThreadPoolExecutor(max_workers=7) as pool:
        futs = {pool.submit(_probe_one, ch): ch for ch in chains_cfg}
        for fut in as_completed(futs):
            row = fut.result()
            if not row.get("ok") and row.get("tier") == "critical":
                critical_fail += 1
            chains_out.append(row)
    chains_out.sort(key=lambda r: str(r.get("id") or ""))

    flag_path = _expand(str(ssot.get("autopilot_flag") or "~/.sina/cloud-forge-run-auto-proceed-v1.flag"))
    receipt = {
        "schema": "living-system-chain-validate-receipt-v1",
        "mode": "fast",
        "at": _now(),
        "ok": critical_fail == 0,
        "critical_fail": critical_fail,
        "hub_queue": hub,
        "autopilot_armed": bool(hub.get("auto_proceed")) and flag_path.is_file(),
        "chains": chains_out,
        "summary_line": (
            f"Chains {'PASS' if critical_fail == 0 else 'FAIL'} · hub head {hub_head or '—'} · "
            f"{sum(1 for c in chains_out if c.get('ok'))}/{len(chains_out)} links up (fast)"
        ),
        "ssot": str(SSOT.relative_to(ROOT)),
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def validate_chains(*, write: bool = True) -> dict[str, Any]:
    ssot = _read(SSOT)
    hub = _hub_queue_head()
    hub_head = hub.get("queue_head")
    chains_out: list[dict[str, Any]] = []
    critical_fail = 0

    for ch in ssot.get("chains") or []:
        cid = str(ch.get("id") or "")
        tier = str(ch.get("tier") or "optional")
        probe = ch.get("probe") or {}
        row: dict[str, Any] = {"id": cid, "label": ch.get("label"), "tier": tier, "ok": False}

        ptype = probe.get("type")
        if ptype == "http":
            pr = _http_probe(str(probe.get("url") or ""))
            row["ok"] = bool(pr.get("ok"))
            row["probe"] = {"type": "http", "url": probe.get("url"), "status": pr.get("status")}
            if not row["ok"]:
                row["error"] = pr.get("error")
            body = pr.get("body") or {}
            if cid == "railway_cloud_queue":
                row["queue_head"] = body.get("cloud_forge_run_head")
            if cid == "cloud_workers_app" and body.get("situation"):
                row["queue_head"] = (body.get("situation") or {}).get("queue_head")
            if cid == "n8n_integration_app":
                cw = body.get("cloud_workers_live") or {}
                row["queue_head"] = cw.get("queue_head")
                row["hub_aligned"] = bool(hub_head and cw.get("queue_head") == hub_head)
        elif ptype == "file":
            path = _expand(str(probe.get("path") or ""))
            row["ok"] = path.is_file()
            row["probe"] = {"type": "file", "path": str(path)}
            if not row["ok"]:
                row["error"] = "missing_flag"
        else:
            row["error"] = "unknown_probe_type"

        align_field = ch.get("align_field")
        align_source = ch.get("align_source")
        if align_field and align_source and hub_head:
            remote_head = _extract_head(str(align_source), str(align_field))
            row["align_field"] = align_field
            row["remote_head"] = remote_head
            row["hub_head"] = hub_head
            row["aligned"] = remote_head == hub_head
            if remote_head and remote_head != hub_head:
                row["ok"] = False
                row["error"] = f"head_divergence hub={hub_head} remote={remote_head}"

        if not row.get("ok") and tier == "critical":
            critical_fail += 1
        chains_out.append(row)

    autopilot = bool(hub.get("auto_proceed"))
    flag_path = _expand(str(ssot.get("autopilot_flag") or "~/.sina/cloud-forge-run-auto-proceed-v1.flag"))
    receipt = {
        "schema": "living-system-chain-validate-receipt-v1",
        "at": _now(),
        "ok": critical_fail == 0,
        "critical_fail": critical_fail,
        "hub_queue": hub,
        "autopilot_armed": autopilot and flag_path.is_file(),
        "chains": chains_out,
        "summary_line": (
            f"Chains {'PASS' if critical_fail == 0 else 'FAIL'} · hub head {hub_head or '—'} · "
            f"{sum(1 for c in chains_out if c.get('ok'))}/{len(chains_out)} links up"
        ),
        "for_founder": {
            "show_this": (
                f"Living system {'LIVE' if critical_fail == 0 else 'DEGRADED'} · queue {hub_head or '—'} · "
                f"autopilot {'ARMED' if autopilot else 'OFF'}"
            )
        },
        "ssot": str(SSOT.relative_to(ROOT)),
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def validate_chains_cloud(*, write: bool = False) -> dict[str, Any]:
    """Server-side PROVE — cloud-reachable chains only (Railway headless)."""
    ssot = _read(SSOT_CLOUD)
    port = int(os.environ.get("PORT", "8080"))
    self_base = (os.environ.get("FBE_SELF_URL") or f"http://127.0.0.1:{port}").rstrip("/")
    try:
        from fbe.lib.cloud_forge_run_queue_v1 import read_head  # noqa: WPS433

        hub = {
            "ok": True,
            "queue_head": read_head().get("cloud_forge_run_head"),
            "source": "cloud:phase-observed",
        }
    except Exception as exc:
        hub = {"ok": False, "error": str(exc)[:120], "queue_head": None}
    hub_head = hub.get("queue_head")
    chains_out: list[dict[str, Any]] = []
    critical_fail = 0

    for ch in ssot.get("chains") or []:
        cid = str(ch.get("id") or "")
        tier = str(ch.get("tier") or "optional")
        probe = ch.get("probe") or {}
        row: dict[str, Any] = {"id": cid, "label": ch.get("label"), "tier": tier, "ok": False}
        ptype = probe.get("type")
        if ptype == "http":
            if cid == "railway_cloud_queue" and hub.get("ok"):
                row["ok"] = True
                row["queue_head"] = hub_head
                row["probe_mode"] = "in_process_read_head"
            elif cid == "railway_fbe_health" and _is_cloud_headless():
                row["ok"] = True
                row["probe_mode"] = "in_process_alive"
            elif probe.get("env_url") == "FBE_SELF_URL" and _is_cloud_headless():
                row["ok"] = True
                row["probe_mode"] = "in_process_no_recursive_http"
                if cid == "railway_cloud_queue":
                    row["queue_head"] = hub_head
            else:
                url = str(probe.get("url") or "")
                pr = _http_probe(url, timeout=8.0)
                row["ok"] = bool(pr.get("ok"))
                if not row["ok"]:
                    row["error"] = pr.get("error")
                body = pr.get("body") or {}
                if cid == "railway_cloud_queue":
                    row["queue_head"] = body.get("cloud_forge_run_head")
        elif ptype == "env":
            key = str(probe.get("key") or "")
            val = str(os.environ.get(key, "")).lower()
            expect = str(probe.get("expect") or "true").lower()
            row["ok"] = val == expect
            if not row["ok"]:
                row["error"] = f"env:{key}!={expect}"
        if hub_head and row.get("queue_head") and row["queue_head"] != hub_head:
            row["ok"] = False
            row["error"] = f"head_divergence cloud={hub_head} probe={row['queue_head']}"
        if not row.get("ok") and tier == "critical":
            critical_fail += 1
        chains_out.append(row)

    receipt = {
        "schema": "living-system-chain-validate-receipt-v1",
        "mode": "cloud_fast",
        "at": _now(),
        "ok": critical_fail == 0,
        "critical_fail": critical_fail,
        "hub_queue": hub,
        "autopilot_armed": str(os.environ.get("CLOUD_FORGE_RUN_AUTO_PROCEED", "")).lower() == "true",
        "chains": chains_out,
        "chains_up": sum(1 for c in chains_out if c.get("ok")),
        "chains_total": len(chains_out),
        "summary_line": (
            f"Cloud chains {'PASS' if critical_fail == 0 else 'FAIL'} · head {hub_head or '—'} · "
            f"{sum(1 for c in chains_out if c.get('ok'))}/{len(chains_out)} up (server-side)"
        ),
        "ssot": str(SSOT_CLOUD.relative_to(ROOT)),
    }
    if write:
        cloud_receipt = Path("/app/receipts/cloud/living-system-chain-validate-receipt-v1.json")
        if cloud_receipt.parent.is_dir() or _is_cloud_headless():
            cloud_receipt.parent.mkdir(parents=True, exist_ok=True)
            cloud_receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def _is_cloud_headless() -> bool:
    return str(os.environ.get("FBE_MODE", "")).lower() == "headless" or os.environ.get("FBE_HOME", "").strip() == "/app"


def hub_slice(*, fast: bool = False) -> dict[str, Any]:
    """Light slice for Hub / Cloud Workers APIs."""
    row = validate_chains_fast(write=False) if fast else validate_chains(write=False)
    return {
        "ok": row.get("ok"),
        "schema": "living-system-chain-hub-slice-v1",
        "at": row.get("at"),
        "summary_line": row.get("summary_line"),
        "hub_queue": row.get("hub_queue"),
        "autopilot_armed": row.get("autopilot_armed"),
        "chains": row.get("chains"),
        "receipt": str(RECEIPT),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Living system chain validator v1")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--cloud", action="store_true", help="Server-side cloud-only PROVE (Railway)")
    ap.add_argument("--hub-slice", action="store_true")
    args = ap.parse_args()
    if args.hub_slice:
        out = hub_slice(fast=args.fast)
    elif args.cloud:
        out = validate_chains_cloud(write=not args.no_write)
    elif args.fast:
        out = validate_chains_fast(write=not args.no_write)
    else:
        out = validate_chains(write=not args.no_write)
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(out.get("summary_line") or out.get("for_founder", {}).get("show_this", "done"))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
