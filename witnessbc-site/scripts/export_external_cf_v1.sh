#!/usr/bin/env bash
# Export Witness AI commercial site for EXTERNAL Cloudflare account deploy.
# Use when witnessbc.com is on founder's own CF email — not SourceA wrangler token.
#
# Usage:
#   bash witnessbc-site/scripts/export_external_cf_v1.sh
#   bash witnessbc-site/scripts/export_external_cf_v1.sh --open
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SINA="${HOME}/.sina"
OPEN=0
DESKTOP="${HOME}/Desktop"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
ZIP_NAME="witnessbc-commercial-v12-${STAMP}.zip"
ZIP_PATH="${DESKTOP}/${ZIP_NAME}"
HANDOFF_JSON="${SINA}/witnessbc-external-cf-handoff-v1.json"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --open) OPEN=1; shift ;;
    -h | --help)
      echo "Usage: bash witnessbc-site/scripts/export_external_cf_v1.sh [--open]"
      exit 0
      ;;
    *) echo "Unknown: $1"; exit 1 ;;
  esac
done

echo "=== export_external_cf_v1: rebuild artifact ==="
bash "$ROOT/scripts/deploy_witnessbc_v1.sh" --skip-recipe

DEPLOY="$ROOT/dist/deploy"
if [[ ! -f "$DEPLOY/index.html" ]]; then
  echo "FAIL: missing $DEPLOY/index.html"
  exit 1
fi

echo "=== export_external_cf_v1: zip → Desktop ==="
rm -f "$ZIP_PATH"
(
  cd "$DEPLOY"
  zip -rq "$ZIP_PATH" . -x "*.DS_Store"
)
BYTES="$(wc -c <"$ZIP_PATH" | tr -d ' ')"
echo "OK: $ZIP_PATH ($BYTES bytes)"

python3 - <<PY
import json
from datetime import datetime, timezone
from pathlib import Path

deploy = Path("$DEPLOY")
manifest = json.loads((deploy / "deploy-manifest.json").read_text(encoding="utf-8"))
handoff = {
    "schema": "witnessbc-external-cf-handoff-v1",
    "ok": True,
    "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "version": "v12-commercial",
    "zip_path": "$ZIP_PATH",
    "zip_bytes": int("$BYTES"),
    "deploy_dir": str(deploy),
    "file_count": len(manifest.get("files", [])),
    "account": "founder-external-cloudflare",
    "do_not_use": [
        "SourceA CLOUDFLARE_API_TOKEN",
        "SourceA GitHub",
        "SourceA Vercel",
        "Noetfield project-gc7lm.vercel.app"
    ],
    "live_today": {
        "url": "https://witnessbc.com",
        "surface": "journalism-home-v2025.12.26.2",
        "note": "Commercial zip is NOT live yet — deploy from founder CF dashboard"
    },
    "routing_modes": [
        {
            "id": "A-replace-home",
            "label": "Commercial at / (replaces journalism homepage)",
            "cf_action": "Upload zip to existing Pages project production",
            "risk": "Journalism / index replaced — /toolkits /principles protected by _routes.json exclude"
        },
        {
            "id": "B-subdomain",
            "label": "Commercial on flow.witnessbc.com (recommended coexistence)",
            "cf_action": "New Pages project + CNAME flow.witnessbc.com",
            "risk": "Low — journalism site untouched at witnessbc.com"
        },
        {
            "id": "C-github-connected",
            "label": "Founder GitHub repo → CF Pages auto-deploy",
            "cf_action": "Push dist/deploy contents to repo root · connect in CF Pages",
            "risk": "Depends on repo branch — use production branch main"
        }
    ],
    "deploy_steps_dashboard": [
        "Log in to Cloudflare with YOUR witnessbc.com account email",
        "Workers & Pages → your witnessbc Pages project (or Create project → Direct Upload)",
        "Upload $ZIP_NAME from Desktop",
        "Production deploy → wait for green",
        "Custom domains: witnessbc.com and/or www.witnessbc.com (or subdomain for mode B)",
        "Verify: curl -sL https://witnessbc.com/ | grep brand-disambiguation",
        "Verify: curl -sL https://witnessbc.com/proof.html | grep proof@witnessbc.com"
    ],
    "deploy_steps_wrangler_founder_machine": [
        "On YOUR machine (logged into founder CF): npm i -g wrangler",
        "wrangler login",
        "unzip ~/Desktop/$ZIP_NAME -d /tmp/witnessbc-deploy",
        "wrangler pages deploy /tmp/witnessbc-deploy --project-name=YOUR_PROJECT_NAME",
        "bash witnessbc-site/scripts/deploy_witnessbc_v1.sh --skip-recipe --verify https://witnessbc.com"
    ],
    "coexistence": {
        "_routes_json": "excludes /toolkits and /principles from this Pages project",
        "journalism_paths_preserved": ["/toolkits", "/toolkits/*", "/principles", "/principles/*"],
        "commercial_paths": ["/", "/platform", "/proof", "/pricing", "/faq", "/learn", "/policy", "/compare", "/lifecycle", "/sources"]
    },
    "verify_checks": [
        "home contains brand-disambiguation",
        "home contains proof@witnessbc.com",
        "home contains layout-ultra-v12 OR Open Proof Lab",
        "proof.html contains Proof Lab",
        "no noetfield.com in HTML",
        "/toolkits still returns journalism (if coexistence mode A)"
    ]
}
Path("$HANDOFF_JSON").write_text(json.dumps(handoff, indent=2) + "\n")
print(f"OK: handoff → $HANDOFF_JSON")
PY

echo ""
echo "PASS: external CF handoff ready"
echo "  Zip:     $ZIP_PATH"
echo "  Receipt: $HANDOFF_JSON"
echo ""
echo "NEXT (founder — your Cloudflare account):"
echo "  1. Open Cloudflare dashboard (your witnessbc.com email)"
echo "  2. Pages → Upload $ZIP_NAME"
echo "  3. Or: wrangler login (your account) → wrangler pages deploy"
echo ""
echo "ROUTING: live site is journalism today. Pick coexistence mode in handoff JSON."

if [[ "$OPEN" -eq 1 ]]; then
  open "$DESKTOP"
fi
