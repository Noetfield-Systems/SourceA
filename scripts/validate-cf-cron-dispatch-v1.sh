#!/usr/bin/env bash
# validate-cf-cron-dispatch-v1.sh — GHA schedules retired; CF dispatch table owns crons
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: cf-cron-dispatch — $*" >&2; exit 1; }

SSOT="$ROOT/data/loop-specialist-cron-dispatch-v1.json"
WRANGLER="$ROOT/cloud/workers/loop-specialist-tick-v1/wrangler.toml"
BUNDLE="$ROOT/cloud/workers/loop-specialist-tick-v1/src/dispatch-table.json"
HTTP="$ROOT/scripts/fbe_cloud_worker_http_v1.py"

[[ -f "$SSOT" ]] || fail "missing SSOT $SSOT"
[[ -f "$WRANGLER" ]] || fail "missing wrangler.toml"
[[ -f "$BUNDLE" ]] || fail "missing dispatch-table.json (copy from SSOT before deploy)"
[[ -f "$HTTP" ]] || fail "missing fbe_cloud_worker_http_v1.py"

python3 - "$SSOT" "$WRANGLER" "$BUNDLE" "$HTTP" <<'PY'
import json, re, sys
from pathlib import Path

ssot, wrangler, bundle, http = map(Path, sys.argv[1:5])
d = json.loads(ssot.read_text())
b = json.loads(bundle.read_text())
if d.get("schema") != "loop-specialist-cron-dispatch-v1":
    raise SystemExit("bad SSOT schema")
if d != b:
    raise SystemExit("dispatch-table.json out of sync with data/loop-specialist-cron-dispatch-v1.json")

crons = [row["cron"] for row in d.get("crons", [])]
toml = wrangler.read_text()
m = re.search(r'crons\s*=\s*\[(.*?)\]', toml, re.S)
if not m:
    raise SystemExit("wrangler.toml missing crons block")
toml_crons = re.findall(r'"([^"]+)"', m.group(1))
wrangler_cron = d.get("wrangler_trigger_cron", "*/15 * * * *")
if toml_crons != [wrangler_cron]:
    raise SystemExit(f"wrangler must have single trigger {wrangler_cron!r}, got {toml_crons}")

paths = set()
for row in d.get("crons", []):
    for job in row.get("jobs", []):
        if job.get("kind") == "railway":
            paths.add(job["path"])

http_text = http.read_text()
for path in sorted(paths):
    if path not in http_text:
        raise SystemExit(f"missing FBE route for {path}")

retired = [
    "gmail-sweep-hourly-v1.yml",
    "ops-heartbeat-daily-v1.yml",
    "kaizen-nightly-v1.yml",
    "repo-health-daily-v1.yml",
    "security-sweep-weekly-v1.yml",
    "determinism-gate.yml",
]
for name in retired:
    wf = ssot.parent.parent / ".github" / "workflows" / name
    text = wf.read_text()
    if re.search(r'^\s*schedule\s*:', text, re.M):
        raise SystemExit(f"{name} still has schedule: block")

print(f"OK: {len(crons)} crons · {len(paths)} railway paths · GHA schedules retired")
PY

echo "OK: validate-cf-cron-dispatch-v1"
