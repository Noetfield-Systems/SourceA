#!/usr/bin/env python3
"""FBE pipeline node graph runner — parallel tiers, W0 dry-run."""
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
DATA = ROOT / "data"
SINA = Path.home() / ".sina"
GRAPH_PATH = DATA / "fbe_node_graph_v1.json"
RECEIPT_PATH = SINA / "fbe-pipeline-node-graph-receipt-v1.json"
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


def _run_node(node: dict, *, dry_run: bool = False) -> dict:
    nid = str(node.get("id") or "unknown")
    label = str(node.get("label") or nid)
    if not bool(node.get("required", True)) and dry_run:
        return {"id": nid, "label": label, "ok": True, "skipped": True, "reason": "not_required"}
    cmd = node.get("cmd") or []
    if not cmd:
        return {"id": nid, "label": label, "ok": False, "error": "empty cmd"}
    if dry_run:
        return {"id": nid, "label": label, "ok": True, "dry_run": True, "cmd": cmd, "required": bool(node.get("required", True))}

    t0 = time.monotonic()
    try:
        if cmd[0] == "python3":
            cmd = [PY, *cmd[1:]]
        out = subprocess.check_output(cmd, cwd=str(ROOT), stderr=subprocess.STDOUT, text=True, timeout=120)
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
        "required": bool(node.get("required", True)),
        "plane": node.get("plane") or "INTERNAL",
    }
    if not ok:
        row["tail"] = out.strip()[-400:]
    return row


def run_graph(*, tier_filter: str | None = None, dry_run: bool = False, max_workers: int = 4) -> dict:
    graph = _read_json(GRAPH_PATH)
    if graph.get("schema") != "fbe-node-graph-v1":
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
        tier_ok = True
        for r in node_results:
            if r.get("required") and not r.get("ok") and not r.get("skipped"):
                tier_ok = False
                break
        ok = ok and tier_ok
        tier_rows.append({
            "tier": tid,
            "parallel": parallel,
            "ok": tier_ok,
            "elapsed_sec": tier_elapsed,
            "within_budget": tier_elapsed <= budget,
            "nodes": node_results,
        })

    elapsed = round(time.monotonic() - t0, 2)
    receipt = {
        "schema": "fbe-pipeline-node-graph-receipt-v1",
        "ok": ok,
        "at": _now(),
        "elapsed_sec": elapsed,
        "graph": str(GRAPH_PATH.relative_to(ROOT)),
        "line_node_count": graph.get("line_node_count"),
        "deliveryMode": "prove_only",
        "tiers": tier_rows,
        "w0_note": "Dry-run or stub execution — cloud deferred W1",
    }
    if not dry_run:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="Run FBE pipeline node graph")
    ap.add_argument("--tier")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    row = run_graph(tier_filter=args.tier, dry_run=args.dry_run, max_workers=args.workers)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"ok={row.get('ok')} elapsed={row.get('elapsed_sec')}s")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
