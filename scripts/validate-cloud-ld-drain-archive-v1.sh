#!/usr/bin/env bash
# validate-cloud-ld-drain-archive-v1.sh — disk-only CLOUD-LD-001..010 archive receipts
set -euo pipefail
cd "$(dirname "$0")/.."

python3 <<'PY'
import json
from pathlib import Path

ROOT = Path(".")
dispatch_dir = ROOT / "receipts" / "cloud-dispatch"
found: dict[str, dict] = {}
required_workstreams = {"ws-ux", "ws-pricing", "ws-run", "ws-onboard", "ws-integrate"}

for path in sorted(dispatch_dir.glob("cloud-dispatch-*.json")):
    try:
        row = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        continue
    pid = str(row.get("plan_id") or "")
    if not pid.startswith("CLOUD-LD-"):
        continue
    prev = found.get(pid)
    if prev is None:
        found[pid] = row
        continue
    prev_at = str(prev.get("at") or "")
    row_at = str(row.get("at") or "")
    if row_at >= prev_at:
        found[pid] = row

missing = []
failed = []
quality = []

for n in range(1, 11):
    pid = f"CLOUD-LD-{n:03d}"
    row = found.get(pid)
    if not row:
        missing.append(pid)
        continue
    if not row.get("ok"):
        failed.append(pid)
        continue

    source_url = str(row.get("source_url") or "")
    if "launchdarkly.com" not in source_url:
        quality.append(f"{pid}: source_url missing launchdarkly.com")
    if int(row.get("http_status") or 0) != 200:
        quality.append(f"{pid}: http_status != 200")
    if int(row.get("bytes_fetched") or 0) <= 1000:
        quality.append(f"{pid}: bytes_fetched <= 1000")
    snippets = row.get("evidence_snippets") or []
    if len(snippets) < 3:
        quality.append(f"{pid}: evidence_snippets < 3")

seen_workstreams = {
    str(row.get("workstream") or "")
    for row in found.values()
    if row.get("ok")
}
missing_ws = sorted(required_workstreams - seen_workstreams)

if missing:
    raise SystemExit(f"FAIL missing receipts: {', '.join(missing)}")
if failed:
    raise SystemExit(f"FAIL not ok: {', '.join(failed)}")
if quality:
    raise SystemExit("FAIL evidence quality:\n  " + "\n  ".join(quality))
if missing_ws:
    raise SystemExit(f"FAIL missing workstreams across CLOUD-LD-001..010: {', '.join(missing_ws)}")

print("OK: CLOUD-LD-001..010 archive receipts with evidence + workstreams", len(found))
PY

echo "PASS: validate-cloud-ld-drain-archive-v1"
