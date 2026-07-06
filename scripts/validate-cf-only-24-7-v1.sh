#!/usr/bin/env bash
# validate-cf-only-24-7-v1.sh — zero GHA schedule: · CF motors own all crons
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: cf-only-24-7 — $*" >&2; exit 1; }

LAW="$ROOT/data/cf-only-24-7-execution-v1.json"
[[ -f "$LAW" ]] || fail "missing $LAW"

python3 - "$ROOT" "$LAW" <<'PY'
import json, re, sys
from pathlib import Path

root, law_path = Path(sys.argv[1]), Path(sys.argv[2])
law = json.loads(law_path.read_text())

# 1) No GHA schedule: anywhere
wf_dir = root / ".github" / "workflows"
for wf in sorted(wf_dir.glob("*.yml")) + sorted(wf_dir.glob("*.yaml")):
    text = wf.read_text()
    if re.search(r"^\s*schedule\s*:", text, re.M):
        raise SystemExit(f"GHA schedule forbidden: {wf.name} — use Cloudflare cron (data/cf-only-24-7-execution-v1.json)")

# 2) CF motors must have crons in wrangler
workers = root / "cloud" / "workers"
for motor in law.get("cf_motors", []):
    name = motor["worker"]
    hit = None
    for w in workers.glob("*/wrangler.toml"):
        if f'name = "{name}"' in w.read_text(encoding="utf-8"):
            hit = w
            break
    if not hit:
        raise SystemExit(f"wrangler.toml not found for motor {name}")
    if "crons" not in hit.read_text(encoding="utf-8"):
        raise SystemExit(f"motor {name} missing [triggers] crons in wrangler.toml")

# 3) Deprecated workers must not declare crons
for dep in law.get("deprecated_cf_workers_no_cron", []):
    w = root / "cloud" / "workers" / dep / "wrangler.toml"
    if w.is_file() and re.search(r"^\s*crons\s*=", w.read_text(), re.M):
        raise SystemExit(f"deprecated worker {dep} must not have wrangler crons — piggyback loop-specialist")

# 4) Dispatch SSOT must state GHA retired
dispatch = json.loads((root / "data/loop-specialist-cron-dispatch-v1.json").read_text())
if "forbidden" not in dispatch.get("one_law", "").lower() or "gha" not in dispatch.get("one_law", "").lower():
    raise SystemExit("loop-specialist-cron-dispatch one_law must forbid GHA schedules")

print("OK: validate-cf-only-24-7 — zero GHA schedules · CF motors armed · deprecated workers clean")
PY

bash "$ROOT/scripts/validate-cf-cron-dispatch-v1.sh"

echo "PASS: validate-cf-only-24-7-v1"
