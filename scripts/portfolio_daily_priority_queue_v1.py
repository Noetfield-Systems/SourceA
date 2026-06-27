#!/usr/bin/env python3
"""Portfolio daily priority queue — P0/P1/P2 blockers for every report.

Law: data/portfolio-daily-priority-queue-v1.json
Receipt: ~/.sina/portfolio-daily-priority-queue-v1.json
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
SSOT = ROOT / "data" / "portfolio-daily-priority-queue-v1.json"
RECEIPT = SINA / "portfolio-daily-priority-queue-v1.json"
SURFACES = SINA / "agent-live-surfaces-v1.json"
SECRETS_DIR = Path.home() / ".sourcea-secrets"
TF_LADDER = Path.home() / "Desktop" / "TrustField Technologies" / "os" / "ladder_state.json"
VIRLUX_COPY = Path.home() / "Desktop" / "VIRLUX" / "packages" / "shared" / "src" / "public-copy.ts"
WBC_DEPLOY = ROOT / "witnessbc-site" / "dist" / "deploy" / "index.html"
ALL_PLAN_BACKLOG = ROOT / "data" / "all-remaining-plan-backlog-v1.json"
CLOUD_FORGE_ACTIVE_QUEUE = ROOT / "data" / "cloud-forge-run-queue-active-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _curl(url: str, *, timeout: float = 10.0) -> tuple[bool, str]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SourceA-priority-queue/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return True, resp.read().decode("utf-8", errors="replace")[:12000]
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, TimeoutError) as exc:
        return False, str(exc)[:120]


def _probe_wbc() -> dict:
    ok_prod, prod_html = _curl("https://www.witnessbc.com/")
    ok_disk = WBC_DEPLOY.is_file()
    disk_html = WBC_DEPLOY.read_text(encoding="utf-8", errors="replace") if ok_disk else ""
    def markers(html: str) -> dict:
        return {
            "dispatch": "AI policy at dispatch" in html or "policy at dispatch" in html,
            "brand_disambig": "brand-disambiguation" in html,
            "journalism": "Independent Public-interest Journalism" in html,
        }
    prod_m = markers(prod_html) if ok_prod else {}
    disk_m = markers(disk_html) if ok_disk else {}
    prod_pass = ok_prod and prod_m.get("dispatch") and prod_m.get("brand_disambig") and not prod_m.get("journalism")
    disk_pass = ok_disk and disk_m.get("dispatch") and disk_m.get("brand_disambig")
    return {
        "id": "wbc-prod",
        "status": "green" if prod_pass else ("yellow" if disk_pass else "red"),
        "prod_pass": prod_pass,
        "artifact_on_disk": disk_pass,
        "blocker": None if prod_pass else "DNS cutover + Stripe paste (founder)",
    }


def _probe_tf_ladder() -> dict:
    row = _read(TF_LADDER)
    steps = row.get("steps") or {}
    red_1_4 = [int(k) for k, v in steps.items() if str(v.get("status") or "").lower() == "red" and int(k) <= 4]
    blocked = bool(row.get("commercial_blocked")) or bool(red_1_4)
    return {
        "id": "tf-ladder",
        "status": "green" if not blocked else "red",
        "commercial_blocked": bool(row.get("commercial_blocked")),
        "steps_1_4_red": red_1_4,
        "blocker": None if not blocked else "TrustField agent — ui_build_and_verify.sh",
    }


def _probe_virlux_copy() -> dict:
    if not VIRLUX_COPY.is_file():
        return {"id": "virlux-copy", "status": "red", "blocker": "public-copy.ts missing"}
    text = VIRLUX_COPY.read_text(encoding="utf-8", errors="replace")
    bad = [
        "Cross-border B2B payments",
        "Send and receive global business payments",
    ]
    hits = [p for p in bad if p in text]
    positioning_ok = "Build agentic SaaS" in text or "Build Factory" in text
    return {
        "id": "virlux-copy",
        "status": "green" if not hits and positioning_ok else "red",
        "forbidden_hits": hits,
        "blocker": None if not hits else f"Remove: {hits[0]}",
    }


def _probe_supabase_secrets() -> dict:
    missing = []
    for name in ("portfolio-spine.env", "noetfield.env"):
        path = SECRETS_DIR / name
        if not path.is_file():
            missing.append(name)
            continue
        body = path.read_text(encoding="utf-8", errors="replace")
        if "YOUR_" in body or "SUPABASE_URL=\n" in body or re.search(r"SUPABASE_URL=\s*$", body, re.M):
            missing.append(f"{name}(placeholder)")
            continue
        anon_m = re.search(r"^SUPABASE_ANON_KEY=(.+)$", body, re.M)
        anon_val = (anon_m.group(1).strip() if anon_m else "")
        if not anon_val or not (anon_val.startswith("eyJ") or anon_val.startswith("sb_publishable_")):
            missing.append(f"{name}(no publishable/anon key)")
    return {
        "id": "supabase-secrets",
        "status": "green" if not missing else "red",
        "missing": missing,
        "blocker": None if not missing else "bash scripts/setup_supabase_secrets_mac_v1.sh",
    }


def _probe_vercel_token() -> dict:
    has = bool(__import__("os").environ.get("VERCEL_TOKEN"))
    vault = SINA / "secrets.env"
    if not has and vault.is_file():
        has = "VERCEL_TOKEN=" in vault.read_text(encoding="utf-8", errors="replace") and "VERCEL_TOKEN=\n" not in vault.read_text()
    return {
        "id": "virlux-vercel-token",
        "status": "green" if has else "yellow",
        "blocker": None if has else "Founder VERCEL_TOKEN for kazemnezhadsina144@gmail.com",
    }


def _probe_sourcea_dirty() -> dict:
    proc = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z"],
        cwd=str(ROOT),
        capture_output=True,
        text=False,
        timeout=15,
    )
    entries = (proc.stdout or b"").split(b"\0")
    items: list[tuple[str, str]] = []
    i = 0
    while i < len(entries):
        entry = entries[i]
        if not entry:
            i += 1
            continue
        status = entry[:2].decode("utf-8", errors="replace")
        path = entry[3:].decode("utf-8", errors="replace")
        if status.startswith(("R", "C")):
            i += 1
            if i < len(entries) and entries[i]:
                path = f"{path} -> {entries[i].decode('utf-8', errors='replace')}"
        items.append((status, path))
        i += 1
    n = len(items)
    top_dirs = collections.Counter(
        (path.split("/", 1)[0] if "/" in path else path) for _, path in items
    ).most_common(12)
    by_status = collections.Counter(status for status, _ in items).most_common()
    return {
        "id": "sourcea-commit",
        "status": "green" if n < 20 else ("yellow" if n < 80 else "red"),
        "dirty_count": n,
        "dirty_top_dirs": [{"path": path, "count": count} for path, count in top_dirs],
        "dirty_by_status": [{"status": status, "count": count} for status, count in by_status],
        "blocker": None if n < 20 else f"{n} uncommitted files",
    }


def _probe_all_plan_backlog() -> dict:
    backlog = _read(ALL_PLAN_BACKLOG)
    queue = _read(CLOUD_FORGE_ACTIVE_QUEUE)
    qrel = str(queue.get("queue_path") or "")
    qdoc = _read(ROOT / qrel) if qrel else {}
    items = [
        row
        for row in (qdoc.get("plans") or [])
        if str(row.get("id") or "").startswith("CLOUD-SEC-")
    ]
    total = int(backlog.get("total_remaining") or 0)
    active = len(items)
    phase_reset = queue.get("phase_reset") if isinstance(queue.get("phase_reset"), dict) else {}
    head = str(phase_reset.get("cloud_forge_run_head") or (items[0].get("id") if items else "") or "")
    rows_per_turn = int(queue.get("rows_per_turn") or 100)
    tasks_per_row = int(queue.get("tasks_per_row") or 100)
    ok = (
        total > 0
        and active == rows_per_turn == 100
        and tasks_per_row == 100
        and bool(head)
        and not queue.get("queue_batch_complete")
    )
    return {
        "id": "all-plan-backlog",
        "status": "green" if ok else "yellow",
        "backlog_total": total,
        "active_cloud_rows": active,
        "rows_per_turn": rows_per_turn,
        "tasks_per_row": tasks_per_row,
        "active_task_capacity": active * tasks_per_row,
        "batch_id": queue.get("batch_id"),
        "queue_path": qrel,
        "head": head,
        "remaining_after_window": max(0, total - (active * tasks_per_row)),
        "blocker": None if ok else "Run refill_cloud_forge_run_from_backlog_v1.py",
    }


def _compose_line(items: list[dict]) -> str:
    p0 = [i for i in items if i.get("status") != "green" and i["id"] in ("wbc-prod", "tf-ladder")]
    p1 = [i for i in items if i.get("status") != "green" and i["id"] in ("virlux-copy", "supabase-secrets")]
    parts = []
    if p0:
        parts.append("P0:" + ",".join(f"{i['id']}={i['status']}" for i in p0))
    if p1:
        parts.append("P1:" + ",".join(f"{i['id']}={i['status']}" for i in p1))
    open_n = sum(1 for i in items if i.get("status") != "green")
    if not parts:
        return f"portfolio-priority · CLEAR · {len(items)} checks green"
    return f"portfolio-priority · {open_n} open · {' · '.join(parts)}"


def run_assess(*, wire: bool = False) -> dict:
    ssot = _read(SSOT)
    probes = [
        _probe_wbc(),
        _probe_tf_ladder(),
        _probe_virlux_copy(),
        _probe_supabase_secrets(),
        _probe_vercel_token(),
        _probe_all_plan_backlog(),
        _probe_sourcea_dirty(),
    ]
    line = _compose_line(probes)
    all_p0_green = all(p.get("status") == "green" for p in probes if p["id"] in ("wbc-prod", "tf-ladder"))
    row = {
        "schema": "portfolio-daily-priority-queue-v1",
        "at": _now(),
        "ok": all_p0_green,
        "portfolio_priority_line": line,
        "bottom_line": ssot.get("bottom_line"),
        "items": probes,
        "ssot": str(SSOT.relative_to(ROOT)),
        "supabase_setup": "bash scripts/setup_supabase_secrets_mac_v1.sh",
    }
    if wire:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        surfaces = _read(SURFACES)
        surfaces["portfolio_priority_line"] = line
        surfaces["portfolio_priority"] = {"ok": all_p0_green, "at": row["at"], "receipt": str(RECEIPT)}
        SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--wire", action="store_true")
    args = ap.parse_args()
    row = run_assess(wire=args.wire)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("portfolio_priority_line") or row)
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
