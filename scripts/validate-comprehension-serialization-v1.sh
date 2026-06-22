#!/usr/bin/env bash
# validate-comprehension-serialization-v1.sh — circular JSON + 422 transport regression (offline)
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="$(pwd)/scripts:${PYTHONPATH:-}"

python3 <<'PY'
import io
import json
import sys
import time
import urllib.error
from unittest.mock import patch

sys.path.insert(0, "scripts")
from fbe.lib.execution_contract_v1 import json_safe_dict, normalize_receipt
from fbe.lib import hub_cloud_proxy_v1 as proxy_mod

# Fix 37 — circular refs in execution receipt must serialize
job = {
    "ok": True,
    "verdict": "ACCEPT",
    "config_version": "1.1.0",
    "variation_key": "default",
    "meaning_score": 88,
    "attempts": [{"verdict": "ACCEPT", "meaning_score": 88}],
    "for_founder": {"show_this": "test"},
    "execution_plane": "headless_cloud",
}
contract = {
    "job_id": "serialization-test",
    "factory_id": "comprehension-loop-factory-v1",
    "tenant_id": "sourcea",
    "execution_mode": "CLOUD_ONLY",
    "policy_pack": "default",
    "policy_hash": "test",
}
rec = normalize_receipt(job, contract=contract, started_at=time.time(), policy_passed=True)
rec["execution_receipt"] = rec  # deliberate cycle
safe = json_safe_dict(rec)
payload = json.dumps(safe)
assert "ACCEPT" in payload
print("OK: json_safe_dict breaks circular execution_receipt")

# Fix 38 — 422 + verdict BLOCKED is bay receipt, not transport error
blocked_body = {
    "ok": False,
    "verdict": "BLOCKED",
    "for_founder": {"blocked": True, "why": "parrot draft"},
    "attempts": [{"verdict": "BLOCKED"}],
}


class FakeHTTPError(urllib.error.HTTPError):
    def __init__(self):
        super().__init__(url="http://test", code=422, msg="Unprocessable", hdrs={}, fp=io.BytesIO(json.dumps(blocked_body).encode()))


def fake_urlopen(req, timeout=0):
    raise FakeHTTPError()


with patch.object(proxy_mod, "cloud_worker_url", return_value="https://example.test"), patch(
    "urllib.request.urlopen", side_effect=fake_urlopen
):
    row = proxy_mod.proxy_to_cloud(
        path="/api/fbe/comprehension-loop/v1",
        body={"draft": "sites=RED", "founder_message": "why"},
    )
assert row.get("verdict") == "BLOCKED", row
assert row.get("error") != "cloud_proxy_http_error", row
assert row.get("proxied") is True
print("OK: 422 BLOCKED not cloud_proxy_http_error")

# Fix 38 — client path treats BLOCKED bay receipt as valid (not transport error)
from cloud_comprehension_bay_client_v1 import analyze_via_cloud  # noqa: WPS433

blocked_receipt = {
    "ok": False,
    "verdict": "BLOCKED",
    "for_founder": {"blocked": True, "why": "parrot"},
    "attempts": [{"verdict": "BLOCKED"}],
    "execution_plane": "headless_cloud",
    "proxied": True,
    "config_version": "1.1.0",
}

with patch("cloud_comprehension_bay_client_v1._cloud_proxy", return_value=blocked_receipt):
    client_row = analyze_via_cloud(
        draft="sites=RED defer ON gate PASS wired.",
        founder_message="why",
        write_receipt=False,
    )
assert client_row.get("verdict") == "BLOCKED", client_row
raw = client_row.get("raw") or {}
assert raw.get("error") != "cloud_proxy_http_error", raw
print("OK: client analyze_via_cloud accepts BLOCKED bay receipt")
PY

echo "PASS: validate-comprehension-serialization-v1"
