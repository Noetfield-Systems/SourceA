#!/usr/bin/env python3
"""SourceA pipeline node graph runner — parallel tiers like n8n, receipts logged.

Law: SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md (n8n = external glue only)
Graph SSOT: data/sourcea_pipeline_node_graph_v1.json
Receipt: ~/.sina/pipeline-node-graph-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
DATA = ROOT / "data"
SINA = Path.home() / ".sina"
GRAPH_PATH = DATA / "sourcea_pipeline_node_graph_v1.json"
RECEIPT_PATH = SINA / "pipeline-node-graph-receipt-v1.json"
PY = sys.executable


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _hub_up() -> bool:
    try:
        subprocess.check_output(
            ["curl", "-sf", "--max-time", "2", "http://127.0.0.1:13020/health"],
            stderr=subprocess.DEVNULL,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _panic_active() -> bool:
    return (SINA / "mac-health-emergency-active-v1.flag").is_file()


def _should_skip(node: dict) -> tuple[bool, str]:
    cond = node.get("skip_if") or ""
    if cond == "hub_down" and not _hub_up():
        return True, "hub_down"
    if cond == "panic_active" and _panic_active():
        return True, "panic_active"
    return False, ""


def _run_node(node: dict, *, dry_run: bool = False) -> dict:
    nid = str(node.get("id") or "unknown")
    label = str(node.get("label") or nid)
    skip, reason = _should_skip(node)
    if skip:
        return {
            "id": nid,
            "label": label,
            "ok": True,
            "skipped": True,
            "skip_reason": reason,
            "elapsed_sec": 0.0,
        }
    cmd = node.get("cmd") or []
    if not cmd:
        return {"id": nid, "label": label, "ok": False, "error": "empty cmd"}
    if dry_run:
        return {"id": nid, "label": label, "ok": True, "dry_run": True, "cmd": cmd}

    t0 = time.monotonic()
    try:
        if cmd[0] == "python3":
            cmd = [PY, *cmd[1:]]
        out = subprocess.check_output(
            cmd,
            cwd=str(ROOT),
            stderr=subprocess.STDOUT,
            text=True,
            timeout=int(node.get("timeout_sec") or 120),
        )
        code = 0
    except subprocess.CalledProcessError as e:
        out = e.output or ""
        code = e.returncode
    except subprocess.TimeoutExpired as e:
        out = (e.output or "") + "\nTIMEOUT"
        code = 124

    elapsed = round(time.monotonic() - t0, 2)
    ok = code == 0
    row: dict[str, Any] = {
        "id": nid,
        "label": label,
        "ok": ok,
        "exit": code,
        "elapsed_sec": elapsed,
        "required": bool(node.get("required")),
        "plane": node.get("plane") or "INTERNAL",
    }
    if not ok:
        row["tail"] = out.strip()[-400:]
    receipt = node.get("receipt")
    if receipt:
        rp = Path(str(receipt).replace("~", str(Path.home())))
        row["receipt_exists"] = rp.is_file()
    return row


def run_graph(
    *,
    tier_filter: str | None = None,
    dry_run: bool = False,
    max_workers: int = 4,
) -> dict:
    graph = _read_json(GRAPH_PATH)
    if graph.get("schema") != "sourcea-pipeline-node-graph-v1":
        return {"ok": False, "error": f"missing or bad graph at {GRAPH_PATH}"}

    t0 = time.monotonic()
    tier_rows: list[dict] = []
    ok = True

    for tier in graph.get("tiers") or []:
        tid = str(tier.get("id") or "")
        if tier_filter and tid != tier_filter:
            continue
        nodes = tier.get("nodes") or []
        parallel = bool(tier.get("parallel", True))
        budget = int(tier.get("budget_sec") or 90)
        tier_t0 = time.monotonic()

        node_results: list[dict] = []
        if parallel and len(nodes) > 1 and not dry_run:
            with ThreadPoolExecutor(max_workers=min(max_workers, len(nodes))) as pool:
                futs = {pool.submit(_run_node, n, dry_run=dry_run): n for n in nodes}
                for fut in as_completed(futs, timeout=budget + 5):
                    node_results.append(fut.result())
        else:
            for n in nodes:
                node_results.append(_run_node(n, dry_run=dry_run))

        tier_elapsed = round(time.monotonic() - tier_t0, 2)
        tier_ok = all(
            r.get("ok") or r.get("skipped")
            for r in node_results
            if not (r.get("required") and not r.get("ok"))
        )
        for r in node_results:
            if r.get("required") and not r.get("ok") and not r.get("skipped"):
                tier_ok = False
                break
        ok = ok and tier_ok
        tier_rows.append(
            {
                "tier": tid,
                "parallel": parallel,
                "ok": tier_ok,
                "elapsed_sec": tier_elapsed,
                "within_budget": tier_elapsed <= budget,
                "nodes": node_results,
            }
        )

    elapsed = round(time.monotonic() - t0, 2)
    live = _read_json(SINA / "agent-live-surfaces-v1.json")
    hub_up = _hub_up()
    degraded_nodes = [
        r.get("id")
        for tr in tier_rows
        for r in tr.get("nodes") or []
        if r.get("skipped") and r.get("skip_reason") == "hub_down"
    ]
    required_fail = any(
        r.get("required") and not r.get("ok") and not r.get("skipped")
        for tr in tier_rows
        for r in tr.get("nodes") or []
    )
    receipt = {
        "schema": "pipeline-node-graph-receipt-v1",
        "ok": ok and not required_fail,
        "degraded": bool(degraded_nodes) and not required_fail,
        "degraded_reason": "hub_down" if degraded_nodes and not hub_up else "",
        "at": _now(),
        "elapsed_sec": elapsed,
        "graph": str(GRAPH_PATH.relative_to(ROOT)),
        "queue_sa": (live.get("factory_now") or {}).get("queue_sa") if isinstance(live.get("factory_now"), dict) else live.get("queue_sa"),
        "factory_now_line": live.get("factory_now_line") or "",
        "hub_up": hub_up,
        "degraded_nodes": degraded_nodes,
        "tiers": tier_rows,
        "n8n_note": "External workflows via workflow_manifest.json — not SSOT for law",
    }
    if not dry_run:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


SESSION_TIERS = (
    "T0_safety",
    "T1_truth_parallel",
    "T2_fleet_parallel",
    "T3_proof_parallel",
)


def run_session_tiers(*, dry_run: bool = False) -> dict:
    """N03 — run session graph tiers T0→T3 (excludes LAT orient)."""
    combined: list[dict] = []
    ok = True
    degraded = False
    t0 = time.monotonic()
    for tid in SESSION_TIERS:
        row = run_graph(tier_filter=tid, dry_run=dry_run)
        if not row.get("ok"):
            ok = False
        if row.get("degraded"):
            degraded = True
        combined.append({"tier": tid, "ok": row.get("ok"), "degraded": row.get("degraded")})
    elapsed = round(time.monotonic() - t0, 2)
    final = _read_json(RECEIPT_PATH) if not dry_run else {}
    if final:
        final["session_tiers"] = combined
        final["session_elapsed_sec"] = elapsed
        final["session_ok"] = ok
        RECEIPT_PATH.write_text(json.dumps(final, indent=2) + "\n", encoding="utf-8")
    return {
        "ok": ok,
        "degraded": degraded or bool(final.get("degraded")),
        "elapsed_sec": elapsed,
        "tiers": combined,
        "receipt": str(RECEIPT_PATH),
        "graph_receipt": final,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Run SourceA pipeline node graph (parallel tiers)")
    ap.add_argument("--tier", help="Run single tier id only")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    row = run_graph(tier_filter=args.tier, dry_run=args.dry_run, max_workers=args.workers)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"ok={row.get('ok')} elapsed={row.get('elapsed_sec')}s receipt={RECEIPT_PATH}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
