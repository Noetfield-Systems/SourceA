#!/usr/bin/env bash
# Deploy SourceA landing to Desktop AgentGo + Agent Run, start servers, open pages
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 scripts/deploy_sourcea_desktop_landing_v1.py

bash "$ROOT/scripts/bootstrap_sourcea_desktop_deploy_v1.sh" || {
  echo "FAIL: deploy targets missing — run bootstrap first"
  exit 1
}

AGENTGO="$HOME/Desktop/SA4"
AGENTRUN="$HOME/Desktop/agentrun-app"

start_server() {
  local dir="$1" port="$2" name="$3"
  if lsof -i ":$port" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "OK: $name already on :$port"
    return
  fi
  (cd "$dir" && python3 -m http.server "$port" --bind 127.0.0.1 >/dev/null 2>&1 &)
  sleep 0.4
  echo "OK: $name started → http://127.0.0.1:$port/sourcea/"
}

start_server "$AGENTGO" 8080 "AgentGo"
start_server "$AGENTRUN" 5180 "Agent Run"

open "http://127.0.0.1:8080/sourcea/"
open "http://127.0.0.1:5180/sourcea/"

echo "DONE: SourceA on Desktop — AgentGo :8080 · Agent Run :5180"
