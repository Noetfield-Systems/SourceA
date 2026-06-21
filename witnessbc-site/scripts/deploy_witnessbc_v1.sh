#!/usr/bin/env bash
# Witness AI site — prepare multi-page deploy artifact for witnessbc.com
# Usage:
#   bash scripts/deploy_witnessbc_v1.sh              # build + stage dist/deploy/
#   bash scripts/deploy_witnessbc_v1.sh --wrangler     # stage + wrangler pages deploy (if configured)
#   bash scripts/deploy_witnessbc_v1.sh --verify URL   # curl-check live site after deploy
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
DEPLOY_DIR="$ROOT/dist/deploy"
SINA="${HOME}/.sina"
WRANGLER=0
VERIFY_URL=""
SKIP_RECIPE=0

usage() {
  echo "Usage: bash witnessbc-site/scripts/deploy_witnessbc_v1.sh [--skip-recipe] [--wrangler] [--verify https://witnessbc.com]"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-recipe) SKIP_RECIPE=1; shift ;;
    --wrangler) WRANGLER=1; shift ;;
    --verify)
      VERIFY_URL="${2:-}"
      [[ -n "$VERIFY_URL" ]] || { echo "FAIL: --verify requires URL"; exit 1; }
      shift 2
      ;;
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

if [[ "$SKIP_RECIPE" -eq 0 ]]; then
  echo "=== deploy_witnessbc_v1: run recipe ==="
  bash "$ROOT/scripts/run-recipe.sh"
  echo ""
fi

echo "=== deploy_witnessbc_v1: stage dist/deploy ==="
rm -rf "$DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR/assets" "$DEPLOY_DIR/data"
PAGE_FILES=(index.html platform.html lifecycle.html proof.html compare.html policy.html pricing.html faq.html sources.html learn.html toolkits.html dark.html)
for pf in "${PAGE_FILES[@]}"; do
  cp "$ROOT/$pf" "$DEPLOY_DIR/$pf"
done
if [[ -d "$ROOT/toolkits" ]]; then
  cp -R "$ROOT/toolkits" "$DEPLOY_DIR/toolkits"
fi
if [[ -d "$ROOT/observe" ]]; then
  cp -R "$ROOT/observe" "$DEPLOY_DIR/observe"
fi
cp -R "$ROOT/assets/." "$DEPLOY_DIR/assets/"
# Cloudflare Pages hard limit: 25 MiB per file — skip oversized video (Proof Lab fallback still works)
for big in "$DEPLOY_DIR/assets/"*.mp4; do
  [[ -f "$big" ]] || continue
  sz="$(wc -c <"$big" | tr -d ' ')"
  if [[ "$sz" -gt 26214400 ]]; then
    rm -f "$big"
    echo "SKIP: $(basename "$big") (${sz} bytes > 25 MiB CF Pages limit)"
  fi
done
if [[ -f "$ROOT/data/trust-signals.json" ]]; then
  cp "$ROOT/data/trust-signals.json" "$DEPLOY_DIR/data/trust-signals.json"
fi
if [[ -f "$ROOT/data/proof-scenarios-v1.json" ]]; then
  cp "$ROOT/data/proof-scenarios-v1.json" "$DEPLOY_DIR/data/proof-scenarios-v1.json"
fi
if [[ -f "$ROOT/data/learn-chapters-v1.json" ]]; then
  cp "$ROOT/data/learn-chapters-v1.json" "$DEPLOY_DIR/data/learn-chapters-v1.json"
fi
if [[ -f "$ROOT/data/stripe-links-v1.json" ]]; then
  cp "$ROOT/data/stripe-links-v1.json" "$DEPLOY_DIR/data/stripe-links-v1.json"
fi
if [[ -f "$ROOT/data/toolkits-v1.json" ]]; then
  cp "$ROOT/data/toolkits-v1.json" "$DEPLOY_DIR/data/toolkits-v1.json"
fi
if [[ -f "$ROOT/data/observe-feed-v1.json" ]]; then
  cp "$ROOT/data/observe-feed-v1.json" "$DEPLOY_DIR/data/observe-feed-v1.json"
fi

cat >"$DEPLOY_DIR/_redirects" <<'EOF'
/principles /observe/principles/ 301
/principles/ /observe/principles/ 301
/corrections /observe/corrections/ 301
/corrections/ /observe/corrections/ 301
/stories /observe/ 301
/stories/ /observe/ 301
EOF

cat >"$DEPLOY_DIR/_routes.json" <<'EOF'
{
  "version": 1,
  "include": ["/*"],
  "exclude": []
}
EOF

# SPA-style fallback not needed — explicit HTML routes
cat >"$DEPLOY_DIR/_headers" <<'EOF'
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
EOF

cat >"$DEPLOY_DIR/e2e.sh" <<'EOF'
#!/usr/bin/env bash
# Run E2E from this folder:  bash e2e.sh
exec bash "$(cd "$(dirname "$0")/../.." && pwd)/scripts/wbc-e2e.sh" "$@"
EOF
chmod +x "$DEPLOY_DIR/e2e.sh"
cp "$ROOT/scripts/wbc-e2e.sh" "$DEPLOY_DIR/_wbc-e2e-canonical.sh" 2>/dev/null || true

manifest="$DEPLOY_DIR/deploy-manifest.json"
python3 - <<PY
import json
from pathlib import Path
root = Path("$DEPLOY_DIR")
files = sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())
Path("$manifest").write_text(json.dumps({
    "schema": "witnessbc-deploy-v10",
    "version": "v10.0",
    "files": files,
    "pages": 10,
    "routes": ["_redirects", "_routes.json"],
}, indent=2) + "\n")
PY

echo "OK: staged $(find "$DEPLOY_DIR" -type f | wc -l | tr -d ' ') files → $DEPLOY_DIR"
echo "  E2E:   cd $DEPLOY_DIR && bash e2e.sh"
echo "  Preview: cd $DEPLOY_DIR && python3 -m http.server 8091"
echo ""

if [[ "$WRANGLER" -eq 1 ]]; then
  WRANGLER_CMD=""
  if command -v wrangler >/dev/null 2>&1; then
    WRANGLER_CMD="wrangler"
  elif command -v npx >/dev/null 2>&1; then
    WRANGLER_CMD="npx --yes wrangler"
  else
    echo "FAIL: wrangler not found — install: npm i -g wrangler"
    exit 1
  fi
  PROJECT="${WRANGLER_PAGES_PROJECT:-witnessbc}"
  echo "=== deploy_witnessbc_v1: wrangler pages deploy (project=$PROJECT) ==="
  $WRANGLER_CMD pages deploy "$DEPLOY_DIR" --project-name="$PROJECT" --commit-dirty=true || {
    echo ""
    echo "HINT: create Cloudflare Pages project first:"
    echo "  npx wrangler pages project create $PROJECT --production-branch=main"
    echo "  bash witnessbc-site/scripts/deploy_witnessbc_v1.sh --wrangler"
    exit 1
  }
  echo ""
fi

if [[ -n "$VERIFY_URL" ]]; then
  echo "=== deploy_witnessbc_v1: post-deploy verify ==="
  base="${VERIFY_URL%/}"
  checks=( "$base/" "$base/proof.html" "$base/faq.html" "$base/assets/site.js" )
  for url in "${checks[@]}"; do
    code="$(curl -sS -o /dev/null -w '%{http_code}' -L "$url" || echo "000")"
    if [[ "$code" != "200" ]]; then
      echo "FAIL: $url returned HTTP $code"
      exit 1
    fi
    echo "OK: $url → $code"
  done
  body="$(curl -sS -L "$base/")"
  echo "$body" | grep -q 'brand-disambiguation' || { echo "FAIL: missing brand-disambiguation on home"; exit 1; }
  echo "$body" | grep -q 'proof@witnessbc.com' || { echo "FAIL: missing proof@witnessbc.com on home"; exit 1; }
  echo "$body" | grep -qi 'noetfield' && { echo "FAIL: noetfield leak on home"; exit 1; }
  proof_body="$(curl -sS -L "$base/proof.html")"
  echo "$proof_body" | grep -q 'Proof Lab' || { echo "FAIL: missing Proof Lab on proof.html"; exit 1; }
  echo "$proof_body" | grep -qi 'noetfield' && { echo "FAIL: noetfield leak on proof.html"; exit 1; }
  echo "PASS: post-deploy verify"
fi

receipt="$SINA/witnessbc-site-deploy-receipt-v1.json"
python3 - <<PY
import json
from datetime import datetime, timezone
from pathlib import Path
deploy = Path("$DEPLOY_DIR")
manifest = json.loads((deploy / "deploy-manifest.json").read_text(encoding="utf-8"))
r = {
    "schema": "witnessbc-site-deploy-receipt-v1",
    "ok": True,
    "version": "v10.0",
    "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "deploy_dir": str(deploy),
    "file_count": len(manifest.get("files", [])),
    "wrangler": bool($WRANGLER),
    "verify_url": "$VERIFY_URL" or None,
    "routes": manifest.get("routes", []),
    "coexistence": ["principles"],
}
Path("$receipt").write_text(json.dumps(r, indent=2) + "\n")
print(f"OK: receipt → $receipt")
PY

echo ""
echo "PASS: deploy_witnessbc_v1 — artifact ready at dist/deploy/"
echo "  Next: point witnessbc.com DNS to Cloudflare Pages · or run with --wrangler"
