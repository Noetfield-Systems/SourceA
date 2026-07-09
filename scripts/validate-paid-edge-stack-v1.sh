#!/usr/bin/env bash
# validate-paid-edge-stack-v1.sh — CF Workers Paid + UptimeRobot SSOT
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

python3 - "$ROOT" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
stack = json.loads((root / "data/sourcea-paid-edge-stack-v1.json").read_text())
tool = json.loads((root / "data/tool-pick-two-phase-v1.json").read_text())
mon = json.loads((root / "data/noos-external-monitors-v1.json").read_text())
dispatch = json.loads((root / "data/loop-specialist-cron-dispatch-v1.json").read_text())

if stack.get("cloudflare_workers_paid", {}).get("status") != "active":
    raise SystemExit("CF Workers Paid must be active in sourcea-paid-edge-stack-v1.json")

phase2 = tool.get("phase_2_affordable_ai", {}).get("tools", [])
cf = next((t for t in phase2 if t.get("id") == "cloudflare_paid_workers"), None)
if not cf or cf.get("status") != "active":
    raise SystemExit("tool-pick cloudflare_paid_workers must be active")

row15 = next((r for r in dispatch.get("crons", []) if r.get("cron") == "*/15 * * * *"), None)
if not row15 or not row15.get("parallel_jobs"):
    raise SystemExit("*/15 cron must set parallel_jobs true for paid acceleration")

urls = {m["url"] for m in mon.get("monitors", []) if m.get("url")}
need = "sourcea-loop-specialist-tick-v1.sina-kazemnezhad-ca.workers.dev/health"
if not any(need in u for u in urls):
    raise SystemExit("noos-external-monitors missing loop-specialist health URL")

if "POST /loop" not in mon.get("one_law", ""):
    raise SystemExit("uptimerobot one_law must forbid POST /loop")

print("OK: validate-paid-edge-stack-v1 — CF Paid active · parallel */15 · monitors wired")
PY

echo "PASS: validate-paid-edge-stack-v1"
