#!/usr/bin/env bash
# worker_verify_closeout_v1.sh — ONLY approved VERIFY closeout path (receipt + broker + closeout_sa_task)
# Usage: bash worker_verify_closeout_v1.sh --sa sa-0857 --evidence "..." [--task-validator validate-foo-v1.sh]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

exec python3 worker_verify_closeout_v1.py "$@"
