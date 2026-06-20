#!/usr/bin/env bash
# enter-founder-work-mode-v1.sh — alias for mac control plane (founder daily boot)
set -euo pipefail
exec bash "$(cd "$(dirname "$0")" && pwd)/enter-mac-control-plane-v1.sh"
