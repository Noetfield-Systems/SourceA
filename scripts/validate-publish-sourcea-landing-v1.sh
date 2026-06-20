#!/usr/bin/env bash
# validate-publish-sourcea-landing-v1.sh — public scenario/proof + boot-proof.json
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

fail() { echo "FAIL: validate-publish-sourcea-landing-v1 — $*" >&2; exit 1; }

[[ -f scripts/publish_sourcea_landing_v1.py ]] || fail "missing publish script"
[[ -f "${SINA}/sourcea-public-urls-v1.json" ]] || fail "not published — run publish_sourcea_landing_v1.py first"

python3 - <<'PY' || fail "public urls contract"
import json
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

sina = Path.home() / ".sina"
pub = json.loads((sina / "sourcea-public-urls-v1.json").read_text())
for key in ("base_url", "scenario_url", "proof_url", "w1_proof_url", "boot_proof_url"):
    u = pub.get(key) or ""
    assert u.startswith("https://"), f"{key} must be https, got {u!r}"
    assert "127.0.0.1" not in u and "localhost" not in u, f"{key} localhost: {u}"

receipt = {}
rp = sina / "sourcea-landing-publish-receipt-v1.json"
if rp.is_file():
    receipt = json.loads(rp.read_text())

def fetch(url: str, timeout: int = 20) -> tuple[int, str]:
    try:
        with urlopen(url, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", errors="replace")
    except URLError:
        return 0, ""

scenario = pub["scenario_url"]
code, body = fetch(scenario)
local_ok = False
if code != 200 and receipt.get("backend") == "cloudflared_tunnel":
    base = pub["base_url"].rstrip("/")
    local = scenario.replace(base, "http://127.0.0.1:8190", 1)
    lcode, lbody = fetch(local, timeout=10)
    if lcode == 200:
        code, body = lcode, lbody
        local_ok = True

assert code == 200, f"scenario not reachable: {scenario}"
assert "Governance Gauntlet" in body or "proof-quiz" in body or "scenario" in body.lower()

boot_url = pub["boot_proof_url"]
bcode, bbody = fetch(boot_url)
if bcode != 200 and local_ok:
    local_boot = boot_url.replace(pub["base_url"].rstrip("/"), "http://127.0.0.1:8190", 1)
    bcode, bbody = fetch(local_boot, timeout=10)
assert bcode == 200, f"boot-proof not reachable: {boot_url}"
boot = json.loads(bbody)
assert boot.get("schema") == "sourcea-boot-proof-v1"
assert boot.get("verdict") in ("PASS", "BLOCK")
assert isinstance(boot.get("checks"), list) and len(boot["checks"]) >= 4

where = "local tunnel" if local_ok else "public"
print(f"OK: {where}", pub["scenario_url"])
print("OK: boot-proof", boot.get("verdict"), "· checks", len(boot.get("checks", [])))
PY

bash scripts/validate-commercial-outbound-e2e-v1.sh

echo "PASS: validate-publish-sourcea-landing-v1"
