#!/usr/bin/env bash
# SourceA green-unified landing — canonical run recipe (sync · deploy · validate · receipt)
# Pattern: witnessbc-site/scripts/run-recipe.sh · validate-sourcea-landing-e2e-v1.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(cd "$ROOT/../.." && pwd)"
SINA="${HOME}/.sina"
RECEIPT="${SINA}/sourcea-landing-run-receipt-v1.json"
OPEN=0
SERVE=0
JSON=0
E2E=0
PORT="${PORT:-5180}"
BASE="http://127.0.0.1:${PORT}"

usage() {
  echo "Usage: bash SourceA-landing/green-unified/scripts/run-recipe.sh [--open] [--serve] [--e2e] [--json]"
  echo "  (no flags)  sync nav/footer · deploy · desktop validate · write receipt"
  echo "  --open      open canonical URL after PASS (requires server on :${PORT})"
  echo "  --serve     hint: cd ~/Desktop/agentrun-app && ./serve.sh (port ${PORT})"
  echo "  --e2e       full Playwright E2E after desktop validate (requires server)"
  echo "  --json      print receipt JSON to stdout"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --open) OPEN=1; shift ;;
    --serve) SERVE=1; shift ;;
    --e2e) E2E=1; shift ;;
    --json) JSON=1; shift ;;
    -h | --help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown arg: $1"
      usage
      exit 1
      ;;
  esac
done

PAGES=(
  index.html
  platform.html
  team.html
  growth.html
  scenario.html
  proof.html
  proof/live.html
  compare.html
  pricing.html
  security.html
  status.html
  sources.html
  loops/index.html
  loops/outreach.html
  loops/ops-monitor.html
  loops/research.html
  loops/eval-booking.html
  loops/session-gate.html
  loops/proof-export.html
)

t0=$SECONDS
started_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "=== SOURCEA-LANDING-RUN-RECIPE start ${started_at} ==="
echo ""

echo "=== step 1: preflight ==="
for f in \
  "$ROOT/index.html" \
  "$ROOT/sourcea.css" \
  "$ROOT/sourcea-motion.js" \
  "$ROOT/sourcea-live-console.js" \
  "$ROOT/sourcea-trust-bar.js" \
  "$ROOT/sourcea-aeg-live.js" \
  "$ROOT/proof/live.html" \
  "$ROOT/sourcea-w1-player.js" \
  "$ROOT/sourcea-loops-hub.js" \
  "$ROOT/data/loops-catalog.json" \
  "$REPO/scripts/sync_sourcea_landing_pages_v1.py" \
  "$REPO/scripts/deploy_sourcea_desktop_landing_v1.py" \
  "$REPO/scripts/bootstrap_sourcea_desktop_deploy_v1.sh" \
  "$REPO/scripts/ui_upgrade_baseline_guard_v1.py" \
  "$REPO/scripts/validate-ui-upgrade-no-downgrade-v1.sh" \
  "$REPO/scripts/validate-sourcea-desktop-landing-v1.sh"; do
  [[ -f "$f" ]] || { echo "FAIL: missing $f"; exit 1; }
done
for p in "${PAGES[@]}"; do
  [[ -f "$ROOT/$p" ]] || { echo "FAIL: missing page $ROOT/$p"; exit 1; }
done
page_count="${#PAGES[@]}"
grep -q "hello@sourcea.com" "$ROOT/index.html" || { echo "FAIL: no hello@sourcea.com in index"; exit 1; }
grep -qi "noetfield.com\|operations@noetfield" "$ROOT/index.html" && { echo "FAIL: Noetfield leak in index"; exit 1; }
AGENTGO="${HOME}/Desktop/SA4"
AGENTRUN="${HOME}/Desktop/agentrun-app"
if [[ ! -d "$AGENTGO" || ! -d "$AGENTRUN" ]]; then
  bash "$REPO/scripts/bootstrap_sourcea_desktop_deploy_v1.sh" || {
    echo "FAIL: deploy targets missing after bootstrap"
    echo "  Run: bash ~/Desktop/SourceA/scripts/bootstrap_sourcea_desktop_deploy_v1.sh"
    exit 1
  }
fi
[[ -d "$AGENTGO" ]] || {
  echo "FAIL: deploy target missing — $AGENTGO (AgentGo legacy :8080)"
  echo "  Clone or restore SA4 desktop app before run-recipe deploy"
  exit 1
}
[[ -d "$AGENTRUN" ]] || {
  echo "FAIL: deploy target missing — $AGENTRUN (Agent Run canonical :5180)"
  echo "  Clone or restore agentrun-app before run-recipe deploy"
  exit 1
}
echo "OK: preflight · ${page_count} pages · green-unified on disk · SA4 + agentrun-app present"
echo ""
echo "=== step 1b: ui upgrade baseline (no downgrade) ==="
python3 "$REPO/scripts/ui_upgrade_baseline_guard_v1.py" verify-all --json | python3 - <<'PY'
import json, sys
row = json.load(sys.stdin)
if not row.get("ok"):
    for f in row.get("failures") or []:
        print("FAIL:", f)
    sys.exit(1)
print(f"OK: ui-upgrade-baseline v{row.get('baseline_version')} · {row.get('file_count')} files")
PY
echo ""

echo "=== step 2: sync nav · footer · explore ==="
python3 "$REPO/scripts/sync_sourcea_landing_pages_v1.py"
echo ""

echo "=== step 2b: inject live sourcea-boot terminal ==="
python3 "$REPO/scripts/inject_sourcea_boot_terminal_v1.py" || { echo "FAIL: boot terminal inject"; exit 1; }
echo ""

echo "=== step 2c: inject Buyer 1 trust signals ==="
python3 "$REPO/scripts/inject_landing_buyer_trust_v1.py" || { echo "FAIL: buyer trust inject"; exit 1; }
bash "$REPO/scripts/validate-landing-buyer-trust-v1.sh" || { echo "FAIL: buyer trust validate"; exit 1; }
echo ""

echo "=== step 2d: inject AEG live proof ==="
python3 "$REPO/scripts/inject_landing_aeg_proof_v1.py" || { echo "FAIL: aeg live inject"; exit 1; }
echo ""

echo "=== step 3: deploy → agentrun-app + SA4 ==="
python3 "$REPO/scripts/deploy_sourcea_desktop_landing_v1.py"
echo ""

echo "=== step 4: desktop validate ==="
bash "$REPO/scripts/validate-sourcea-desktop-landing-v1.sh"
echo ""

e2e_status="skipped"
if [[ "$E2E" -eq 1 ]]; then
  echo "=== step 5: full E2E (Playwright) ==="
  if ! curl -sf "${BASE}/sourcea/" >/dev/null 2>&1; then
    echo "FAIL: server not reachable at ${BASE}/sourcea/"
    echo "  Start: cd ~/Desktop/agentrun-app && ./serve.sh"
    exit 1
  fi
  SOURCEA_E2E_BASE="$BASE" bash "$REPO/scripts/validate-sourcea-landing-e2e-v1.sh"
  e2e_status="pass"
  echo ""
fi

elapsed=$((SECONDS - t0))
mkdir -p "$SINA"
DEPLOYED="${HOME}/Desktop/agentrun-app/sourcea"
REPO="$REPO" \
ROOT="$ROOT" \
RECEIPT="$RECEIPT" \
STARTED_AT="$started_at" \
ELAPSED="$elapsed" \
PAGE_COUNT="$page_count" \
E2E_STATUS="$e2e_status" \
BASE="$BASE" \
DEPLOYED="$DEPLOYED" \
JSON_OUT="$JSON" \
python3 - <<'PY'
import json
import os
from pathlib import Path

repo = Path(os.environ["REPO"])
root = Path(os.environ["ROOT"])
deployed = Path(os.environ["DEPLOYED"])
pages = [
    "index.html", "platform.html", "team.html", "growth.html",
    "scenario.html", "proof.html", "compare.html", "pricing.html",
    "loops/index.html", "loops/outreach.html", "loops/ops-monitor.html", "loops/research.html",
]
receipt = {
    "schema": "sourcea-landing-run-recipe-v1",
    "ok": True,
    "at": os.environ["STARTED_AT"],
    "elapsed_sec": int(os.environ["ELAPSED"]),
    "recipe": [
        "preflight",
    "sync_sourcea_landing_pages_v1.py",
    "ui_upgrade_baseline_guard_v1.py verify-all",
    "deploy_sourcea_desktop_landing_v1.py",
        "validate-sourcea-desktop-landing-v1.sh",
    ],
    "verify": "bash SourceA-landing/green-unified/scripts/run-recipe.sh",
    "page_count": int(os.environ["PAGE_COUNT"]),
    "pages": pages,
    "e2e": os.environ["E2E_STATUS"],
    "canonical_url": f'{os.environ["BASE"]}/sourcea/',
    "paths": {
        "source": str(root),
        "deployed": str(deployed),
        "sina_css": str(Path.home() / ".sina/sourcea-green-unified-v1.css"),
        "sina_motion": str(Path.home() / ".sina/sourcea-green-unified-motion-v1.js"),
    },
}
if os.environ["E2E_STATUS"] == "pass":
    receipt["recipe"].append("validate-sourcea-landing-e2e-v1.sh")
Path(os.environ["RECEIPT"]).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
if os.environ.get("JSON_OUT") == "1":
    print(json.dumps(receipt, indent=2))
PY

echo "OK: receipt → ${RECEIPT}"
echo ""
echo "PASS: sourcea-landing run recipe (${elapsed}s)"
echo "  source     ${ROOT}/"
echo "  deployed   ${DEPLOYED}/"
echo "  live       ${BASE}/sourcea/"
echo "  legacy     http://127.0.0.1:8080/sourcea/"
echo ""

if [[ "$OPEN" -eq 1 ]]; then
  if curl -sf "${BASE}/sourcea/" >/dev/null 2>&1; then
    open "${BASE}/sourcea/"
  else
    echo "WARN: server not up — open file instead"
    open "${DEPLOYED}/index.html"
  fi
fi

if [[ "$SERVE" -eq 1 ]]; then
  echo "Start Agent Run server:"
  echo "  cd ~/Desktop/agentrun-app && ./serve.sh"
  echo "Then: ${BASE}/sourcea/"
fi
