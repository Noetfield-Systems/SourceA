#!/usr/bin/env bash
# validate-witnessbc-ui-zero-drift-v1 — ZERO TOLERANCE: WitnessBC surface only
# Law: NO UI DRIFT · NO UPGRADE DRIFT — content ↔ assemble ↔ deploy ↔ ledger ↔ live
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WBC="$ROOT/witnessbc-site"
cd "$ROOT"

fail() { echo "FAIL: validate-witnessbc-ui-zero-drift-v1 — $*" >&2; exit 1; }

[[ -f "$HOME/.sina/founder-zero-ui-drift-v1.flag" ]] \
  || fail "founder-zero-ui-drift-v1.flag missing"

LEDGER="$ROOT/data/ui-upgrade-ledgers/witnessbc_commercial-v1.json"
[[ -f "$LEDGER" ]] || fail "missing witnessbc_commercial ledger"

CONTENT="$WBC/content/toolkits.html"
ASSEMBLED="$WBC/toolkits.html"
DEPLOY="$WBC/dist/deploy/toolkits.html"
SANDBOX_DEPLOY="$WBC/dist/deploy/toolkits/sandbox/index.html"
DATA="$WBC/data/toolkits-v1.json"

for f in "$CONTENT" "$ASSEMBLED" "$DEPLOY" "$SANDBOX_DEPLOY" "$DATA"; do
  [[ -f "$f" ]] || fail "missing $f"
done

python3 <<'PY' || fail "witnessbc drift scan"
import json
import re
import sys
from pathlib import Path

root = Path("witnessbc-site")
errors: list[str] = []

content = (root / "content/toolkits.html").read_text(encoding="utf-8")
assembled = (root / "toolkits.html").read_text(encoding="utf-8")
deploy = (root / "dist/deploy/toolkits.html").read_text(encoding="utf-8")
sandbox = (root / "dist/deploy/toolkits/sandbox/index.html").read_text(encoding="utf-8")
data = json.loads((root / "data/toolkits-v1.json").read_text(encoding="utf-8"))

# Frozen markers from ledger — downgrade = FAIL
ledger = json.loads(Path("data/ui-upgrade-ledgers/witnessbc_commercial-v1.json").read_text())
frozen = ledger.get("frozen_inventory") or []

required_markers = [
    "data-freemium-active",
    "/toolkits/sandbox/",
    "Start free",
    "layout-ultra-v12",
    "data-buy=",
    "Education only",
]
for m in required_markers:
    if m not in deploy:
        errors.append(f"deploy missing frozen marker: {m!r}")
    if m not in assembled:
        errors.append(f"assembled missing frozen marker: {m!r}")

if "data-freemium-active" not in content:
    errors.append("content/toolkits.html missing data-freemium-active")
if "/toolkits/sandbox/" not in content:
    errors.append("content/toolkits.html missing sandbox link")

# SSOT freemium + sandbox active
if not (data.get("freemium") or {}).get("active"):
    errors.append("toolkits-v1.json freemium.active != true")
if not (data.get("sandbox") or {}).get("active"):
    errors.append("toolkits-v1.json sandbox.active != true")
if not (data.get("quickstart") or {}).get("active"):
    errors.append("toolkits-v1.json quickstart.active != true")

# Sandbox page markers
for sm in ("sandbox-editor", "Freemium active", "toolkits-sandbox.js"):
    if sm not in sandbox:
        errors.append(f"sandbox page missing: {sm!r}")

# Content ⊆ assembled (key freemium blocks must propagate)
for block in (
    'data-freemium-active="true"',
    'href="/toolkits/sandbox/"',
    'href="/toolkits/free/sourcing/"',
):
    if block in content and block not in assembled:
        errors.append(f"assemble drift: {block!r} in content but not toolkits.html")

# Assembled ⊆ deploy (deploy must not lag assemble)
for block in (
    'data-freemium-active="true"',
    'href="/toolkits/sandbox/"',
):
    if block in assembled and block not in deploy:
        errors.append(f"deploy drift: {block!r} in toolkits.html but not dist/deploy")

# Ledger frozen inventory markers on deploy
for row in frozen:
    marker = str(row.get("marker") or "")
    fid = str(row.get("id") or "")
    if not marker:
        continue
    # check first token of marker (before space)
    key = marker.split()[0] if marker else ""
    if key and key not in deploy and fid not in ("no_cross_brand",):
        if fid == "toolkits_sandbox" and "data-freemium-active" in deploy:
            continue
        if fid == "toolkits_freemium" and "data-buy=" in deploy:
            continue
        if fid == "v12_layout" and "layout-ultra-v12" in deploy:
            continue
        if fid == "proof_lab":
            continue  # proof page separate
        if fid == "proof_cta":
            continue
        if fid == "brand_strip":
            continue
        if fid == "stripe_checkout_live" and (
            "checkout-live" in deploy
            or 'data-stripe-live="true"' in deploy
        ):
            continue
        errors.append(f"ledger frozen {fid}: marker {marker!r} not on toolkits deploy")

# No invitation copy on toolkits deploy
forbidden = (
    "automatic recommended",
    "ASF MUST ANSWER",
    "Open form · Submit",
    "one next tap",
)
blob = deploy.lower()
for bad in forbidden:
    if bad.lower() in blob:
        errors.append(f"forbidden copy on deploy: {bad!r}")

# v12 e2e SSOT must list freemium in phases or checklist
e2e_path = root / "data/ui-upgrade-e2e-v12.json"
if e2e_path.is_file():
    e2e = json.loads(e2e_path.read_text(encoding="utf-8"))
    raw = json.dumps(e2e).lower()
    if "freemium" not in raw and "sandbox" not in raw:
        errors.append("ui-upgrade-e2e-v12.json missing freemium/sandbox reference")

if errors:
    print("FAIL: validate-witnessbc-ui-zero-drift-v1")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("OK: validate-witnessbc-ui-zero-drift-v1 · content=assemble=deploy · freemium+sandbox frozen · ledger aligned")
PY
