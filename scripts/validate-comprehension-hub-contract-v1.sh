#!/usr/bin/env bash
# validate-comprehension-hub-contract-v1.sh — hub slim route contract (hub :13020 must be up)
set -euo pipefail
cd "$(dirname "$0")/.."

HUB="${SINA_COMMAND_URL:-http://127.0.0.1:13020}"
HUB="${HUB%/}"

if ! curl -sf "${HUB}/health" >/dev/null 2>&1; then
  echo "SKIP: hub not up at ${HUB} — start serve-sina-command for hub contract"
  exit 0
fi

python3 <<PY
import json
import urllib.error
import urllib.request
from pathlib import Path

hub = "${HUB}"
golden = json.loads(Path("data/comprehension-golden-v1.json").read_text())
parrot = ""
for case in golden.get("cases") or []:
    if case.get("id") == "golden-002":
        parrot = str(case.get("draft") or "")
        break
assert parrot, "missing golden-002"


def post(draft: str, founder: str, job_id: str) -> tuple[int, dict]:
    body = {
        "job_id": job_id,
        "factory_id": "comprehension-loop-factory-v1",
        "bay_slug": "comprehension-loop-bay",
        "tenant": "sourcea",
        "execution_mode": "CLOUD_ONLY",
        "draft": draft,
        "founder_message": founder,
    }
    req = urllib.request.Request(
        f"{hub}/api/comprehension-loop/v1",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.getcode(), json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode())


good = (
    "You asked why email stays off. WitnessBC still shows old journalism on the live site, "
    "so outbound email stays blocked until prod DNS switches. TrustField and Noetfield load fine."
)
status, row = post(good, "why defer", "hub-contract-accept")
print(f"OK: hub ACCEPT HTTP {status}")
assert status == 200, row
assert row.get("verdict") == "ACCEPT", row
assert row.get("config_version"), row
assert isinstance(row.get("attempts"), list), row

status2, row2 = post(parrot, "why", "hub-contract-block")
print(f"OK: hub BLOCKED HTTP {status2}")
assert status2 == 200, row2
assert row2.get("verdict") == "BLOCKED", row2
assert row2.get("for_founder", {}).get("blocked"), row2
PY

echo "PASS: validate-comprehension-hub-contract-v1"
