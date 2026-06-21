#!/usr/bin/env bash
# Sync witnessbc-site/dist/deploy → deploy-witnessbc-agentic-governance GitHub repo
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEPLOY="$ROOT/witnessbc-site/dist/deploy"
REPO="${WITNESSBC_DEPLOY_REPO:-$ROOT/.tmp/deploy-witnessbc-agentic-governance}"
REMOTE="${WITNESSBC_DEPLOY_REMOTE:-https://github.com/kazemnezhadsina144-dot/deploy-witnessbc-agentic-governance.git}"

bash "$ROOT/witnessbc-site/scripts/deploy_witnessbc_v1.sh" --skip-recipe

if [[ ! -d "$REPO/.git" ]]; then
  mkdir -p "$(dirname "$REPO")"
  git clone "$REMOTE" "$REPO"
fi

rsync -a --delete \
  --exclude '.git' \
  --exclude '.vercel' \
  --exclude 'README.md' \
  "$DEPLOY"/ "$REPO/"

cat > "$REPO/vercel.json" << 'EOF'
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "framework": null,
  "installCommand": "",
  "buildCommand": "",
  "cleanUrls": true,
  "trailingSlash": false,
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" }
      ]
    }
  ]
}
EOF

cd "$REPO"
if git diff --quiet && git diff --cached --quiet; then
  echo "OK: deploy-witnessbc-agentic-governance already in sync"
  exit 0
fi

git add -A
git commit -m "Sync witnessbc-site/dist/deploy from SourceA monorepo."
git push origin main
echo "PASS: pushed $(git rev-parse --short HEAD) → $REMOTE"
