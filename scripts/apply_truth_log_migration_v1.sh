#!/usr/bin/env bash
# Back-compat wrapper — use apply_portfolio_spine_migrations_v1.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec bash "$ROOT/scripts/apply_portfolio_spine_migrations_v1.sh"
