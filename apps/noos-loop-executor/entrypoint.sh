#!/usr/bin/env bash
set -euo pipefail
cd /app
exec python3 -m noos_loop_executor.server --port "${PORT:-8080}"
