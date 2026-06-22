#!/usr/bin/env bash
# validate-cloud-comprehension-railway-v1.sh — post-deploy cloud probe (CI / deploy window only)
set -euo pipefail
cd "$(dirname "$0")/.."

export FBE_CLOUD_WORKER_URL="${FBE_CLOUD_WORKER_URL:-}"
python3 <<'PY'
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(".")
golden = json.loads((ROOT / "data/comprehension-golden-v1.json").read_text())
escalate_draft = golden.get("escalation_probe_draft") or ""
escalate_founder = golden.get("escalation_probe_founder_message") or "why defer"
parrot_draft = ""
for case in golden.get("cases") or []:
    if case.get("id") == "golden-002":
        parrot_draft = str(case.get("draft") or "")
        break
assert escalate_draft, "missing escalation_probe_draft"
assert parrot_draft, "missing golden-002 draft"

worker = os.environ.get("FBE_CLOUD_WORKER_URL", "").strip().rstrip("/")
if not worker:
    worker = str(json.loads((ROOT / "data/fbe_cloud_worker_config_v1.json").read_text()).get("worker_url") or "").rstrip("/")
assert worker, "worker_url missing"


def post_comprehension(job_id: str, draft: str, founder_message: str) -> tuple[int, dict]:
    body = {
        "job_id": job_id,
        "factory_id": "comprehension-loop-factory-v1",
        "bay_slug": "comprehension-loop-bay",
        "tenant": "sourcea",
        "execution_mode": "CLOUD_ONLY",
        "draft": draft,
        "founder_message": founder_message,
    }
    req = urllib.request.Request(
        f"{worker}/api/fbe/comprehension-loop/v1",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            status = resp.getcode()
            row = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        status = exc.code
        row = json.loads(exc.read().decode())
    return status, row


with urllib.request.urlopen(f"{worker}/health", timeout=30) as resp:
    health = json.loads(resp.read().decode())
assert health.get("ok"), health
print("OK: railway health 200")

good = (
    "You asked why email stays off. WitnessBC still shows old journalism on the live site, "
    "so outbound email stays blocked until prod DNS switches. TrustField and Noetfield load fine."
)
status, row = post_comprehension("railway-probe-accept", good, "why defer")
print(f"OK: railway comprehension ACCEPT HTTP {status}")
assert status == 200, row
assert row.get("verdict") == "ACCEPT", row
assert row.get("execution_plane") in ("headless_cloud", None, ""), row

status2, row2 = post_comprehension("railway-probe-escalate", escalate_draft, escalate_founder)
print(f"OK: railway escalation probe HTTP {status2}")
assert status2 == 200, row2
assert row2.get("verdict") == "ACCEPT", row2
assert row2.get("escalated") is True, row2
assert len(row2.get("attempts") or []) == 2, row2

status3, row3 = post_comprehension("railway-probe-block", parrot_draft, "why")
print(f"OK: railway parrot BLOCKED HTTP {status3}")
assert status3 == 200, row3
assert row3.get("verdict") == "BLOCKED", row3
assert len(row3.get("attempts") or []) >= 1, row3

if os.environ.get("FBE_VERIFY_EVAL_BATCH", "").strip() == "1":
    eval_body = {"write_receipt": False}
    req = urllib.request.Request(
        f"{worker}/api/fbe/comprehension-eval-batch/v1",
        data=json.dumps(eval_body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        eval_row = json.loads(resp.read().decode())
    assert eval_row.get("ok"), eval_row
    assert float(eval_row.get("pass_rate") or 0) >= 0.875, eval_row
    assert int(eval_row.get("evaluated") or 0) >= 8, eval_row
    print(
        "OK: railway eval batch",
        eval_row.get("passed"),
        "/",
        eval_row.get("evaluated"),
        "pass_rate",
        eval_row.get("pass_rate"),
    )
PY

echo "PASS: validate-cloud-comprehension-railway-v1"
