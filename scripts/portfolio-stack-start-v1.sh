#!/usr/bin/env bash
# Portfolio stack — start all local apps + wire (Hub · Mail · Chat Unify · N8N · Mac Law).
set -uo pipefail
SA="${SINA_SOURCE_A:-$HOME/Desktop/SourceA}"
CURL="${CURL:-/usr/bin/curl}"
LOG="${HOME}/.sina/portfolio-stack-start-v1.log"

mkdir -p "${HOME}/.sina"
{
  echo "=== portfolio-stack-start $(date) ==="
  bash "$SA/scripts/portfolio-mail-stack-boot.sh"
  for p in 13020 13023 13026; do
    if "$CURL" -sf -m 2 "http://127.0.0.1:${p}/health" >/dev/null 2>&1; then
      echo "port ${p}: UP"
    else
      echo "port ${p}: DOWN"
    fi
  done
  if "$CURL" -sf -m 2 "http://127.0.0.1:8781/api/mac-law/health" >/dev/null 2>&1; then
    echo "mac-law: UP"
  else
    echo "mac-law: DOWN"
  fi
} >>"$LOG" 2>&1
