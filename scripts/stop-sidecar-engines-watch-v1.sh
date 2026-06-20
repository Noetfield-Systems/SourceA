#!/usr/bin/env bash
PIDFILE="$HOME/.sina/sidecar-engines-watch-v1.pid"
if [[ -f "$PIDFILE" ]]; then
  pid=$(cat "$PIDFILE" 2>/dev/null || true)
  if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
    kill "$pid" 2>/dev/null || true
    echo "Stopped sidecar watch pid=$pid"
  fi
  rm -f "$PIDFILE"
else
  echo "Sidecar watch not running"
fi
