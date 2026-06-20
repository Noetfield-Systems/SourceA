#!/usr/bin/env bash
# Scan repo for likely secrets before cleanup snapshot commits.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/infra/cleanup/secret-scan-report.txt"

cd "$ROOT"
mkdir -p "$(dirname "$OUT")"

PATTERN='(api[_-]?key|secret|password|BEGIN.*PRIVATE KEY|sk-[a-zA-Z0-9]{20,}|SUPABASE_SERVICE_ROLE|eyJ[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]+\.)'

{
  echo "# Secret scan report — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "# Review hits before git snapshot. Redact or gitignore — do not commit keys."
  echo
  if command -v gitleaks >/dev/null 2>&1; then
    echo "## gitleaks"
    gitleaks detect --no-git --source "$ROOT" 2>&1 || true
    echo
  fi
  echo "## ripgrep heuristic"
  rg -n -i "$PATTERN" \
    --glob '*.md' --glob '*.txt' --glob '*.log' --glob '*.json' \
    --glob '*.yaml' --glob '*.yml' --glob '*.env*' \
    --glob '!.git/**' --glob '!node_modules/**' --glob '!.venv/**' \
    "$ROOT" 2>/dev/null || true
} | tee "$OUT"

echo "Report: $OUT"
