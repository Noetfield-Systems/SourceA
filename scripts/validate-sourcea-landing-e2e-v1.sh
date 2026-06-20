#!/usr/bin/env bash
# SourceA green-unified landing E2E — deploy, static crawl, Playwright responsive + nav.
# Canonical: http://127.0.0.1:5180/sourcea/ (Agent Run). SA4 :8080 is legacy one-pager only.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
BASE="${SOURCEA_E2E_BASE:-http://127.0.0.1:5180}"
GREEN="$ROOT/SourceA-landing/green-unified"
DEPLOYED="$HOME/Desktop/agentrun-app/sourcea"

echo "=== validate-sourcea-landing-e2e-v1 ==="

# 0) Server up
if ! curl -sf "${BASE}/sourcea/" >/dev/null 2>&1; then
  echo "FAIL: landing not reachable at ${BASE}/sourcea/ — start: cd ~/Desktop/agentrun-app && ./serve.sh"
  exit 1
fi
echo "OK: server ${BASE}"

# 1) Deploy + desktop validator
python3 scripts/deploy_sourcea_desktop_landing_v1.py >/dev/null
bash scripts/validate-sourcea-desktop-landing-v1.sh

# 2) Template ↔ deploy sync
SYNC_FILES=(
  index.html
  growth.html
  proof.html
  sourcea.css
  sourcea-motion.js
  sourcea-trust-bar.js
  sourcea-live-console.js
  data/trust-signals.json
  data/factory-live.json
)
for f in "${SYNC_FILES[@]}"; do
  diff -q "$GREEN/$f" "$DEPLOYED/$f" >/dev/null || {
    echo "FAIL: deploy out of sync — $f"
    exit 1
  }
done
echo "OK: green-unified synced to agentrun-app (${#SYNC_FILES[@]} files)"

# 3) Static HTTP + link crawl
python3 - <<'PY'
import urllib.request, re, sys
BASE = __import__("os").environ.get("SOURCEA_E2E_BASE", "http://127.0.0.1:5180")
PAGES = [
  "/sourcea/", "/sourcea/platform.html", "/sourcea/team.html", "/sourcea/growth.html",
  "/sourcea/scenario.html", "/sourcea/proof.html", "/sourcea/proof/live.html", "/sourcea/compare.html",
  "/sourcea/pricing.html", "/sourcea/security.html", "/sourcea/status.html", "/sourcea/sources.html",
  "/sourcea/loops/index.html", "/sourcea/loops/outreach.html",
  "/sourcea/loops/ops-monitor.html", "/sourcea/loops/research.html",
  "/sourcea/loops/eval-booking.html", "/sourcea/loops/session-gate.html",
  "/sourcea/loops/proof-export.html",
]
ASSETS = [
  "/sourcea/sourcea.css", "/sourcea/sourcea-motion.js", "/sourcea/sourcea-trust-bar.js",
  "/sourcea/sourcea-live-console.js", "/sourcea/data/trust-signals.json",
  "/sourcea/data/boot-proof.json", "/assets/agentrun.js", "/assets/agentrun.css",
]
fails = []
for path in PAGES + ASSETS:
    try:
        r = urllib.request.urlopen(BASE + path, timeout=10)
        if r.status != 200:
            fails.append(f"{path}: status {r.status}")
    except Exception as e:
        fails.append(f"{path}: {e}")

href_re = re.compile(r'href="(/sourcea/[^"#?]+)"')
seen = set()
for path in PAGES:
    html = urllib.request.urlopen(BASE + path).read().decode("utf-8", "replace")
    if 'href="/sourcea/growth.html"' not in html:
        fails.append(f"{path}: missing growth nav")
    if "sourcea-motion.js" not in html or "agentrun.js" not in html:
        fails.append(f"{path}: missing script tags")
    for m in href_re.findall(html):
        if m in seen:
            continue
        seen.add(m)
        try:
            urllib.request.urlopen(BASE + m, timeout=10)
        except Exception as e:
            fails.append(f"broken link {m}: {e}")

idx = urllib.request.urlopen(BASE + "/sourcea/").read().decode()
for anchor in ("team", "reference", "growth", "sandbox", "proof", "platform"):
    if f'id="{anchor}"' not in idx:
        fails.append(f"index missing #{anchor}")
if "sa-chain-beats" not in idx:
    fails.append("index missing sa-chain-beats")
if "sa-buyer-toggle" not in idx:
    fails.append("index missing sa-buyer-toggle")

proof = urllib.request.urlopen(BASE + "/sourcea/proof.html").read().decode()
if "sa-chain-beats" not in proof:
    fails.append("proof.html missing sa-chain-beats")

try:
    trust = urllib.request.urlopen(BASE + "/sourcea/data/trust-signals.json", timeout=10).read().decode()
    if '"valid_yes"' not in trust:
        fails.append("trust-signals.json missing valid_yes")
except Exception as e:
    fails.append(f"trust-signals.json: {e}")

if fails:
    for f in fails:
        print("FAIL:", f)
    sys.exit(1)
print(f"OK: static crawl — {len(PAGES)} pages, {len(ASSETS)} assets, {len(seen)} internal links")
PY

# 4) Playwright E2E (run from temp dir so ESM resolves playwright)
E2E_DIR="${TMPDIR:-/tmp}/sourcea-landing-e2e-$$"
mkdir -p "$E2E_DIR"
if [[ ! -d "$E2E_DIR/node_modules/playwright" ]]; then
  (cd "$E2E_DIR" && npm init -y >/dev/null 2>&1 && npm install playwright@1.61.0 --silent)
  (cd "$E2E_DIR" && npx playwright install chromium >/dev/null 2>&1) || true
fi
cp "$ROOT/scripts/sourcea-landing-e2e-v1.mjs" "$E2E_DIR/"
(
  cd "$E2E_DIR"
  export SOURCEA_E2E_BASE="$BASE"
  node sourcea-landing-e2e-v1.mjs
)

rm -rf "$E2E_DIR"
echo "validate-sourcea-landing-e2e-v1.sh: ALL PASS"
