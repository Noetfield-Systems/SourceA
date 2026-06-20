#!/usr/bin/env bash
# WitnessBC E2E — cwd-safe wrapper (any directory)
exec bash "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/witnessbc-site/scripts/wbc-e2e.sh" "$@"
