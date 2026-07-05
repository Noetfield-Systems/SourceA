#!/usr/bin/env bash
# validate-cloud-forge-run-hundred-rows-vocabulary-v1.sh — redirects to INCIDENT-045 realistic motor law
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec bash "$ROOT/scripts/validate-cloud-forge-run-realistic-motor-law-v1.sh"
