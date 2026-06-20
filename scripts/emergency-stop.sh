#!/usr/bin/env bash
# One command — emergency stop Sina Command (same as kill-sina-command.sh).
set -euo pipefail
exec "$(cd "$(dirname "$0")" && pwd)/kill-sina-command.sh"
