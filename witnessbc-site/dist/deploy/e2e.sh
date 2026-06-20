#!/usr/bin/env bash
# Run E2E from this folder:  bash e2e.sh
exec bash "$(cd "$(dirname "$0")/../.." && pwd)/scripts/wbc-e2e.sh" "$@"
