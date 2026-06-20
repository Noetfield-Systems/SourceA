#!/usr/bin/env bash
# Dispatch ready activation gates v1.1 — hub must match orchestrator_dispatch_ready()
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"
python3 dispatch_ready_lock.py
