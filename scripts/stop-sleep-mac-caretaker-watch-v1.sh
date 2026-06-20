#!/usr/bin/env bash
PIDFILE="$HOME/.sina/sleep-mac-caretaker-watch-v1.pid"
if [[ -f "$PIDFILE" ]]; then
  pid=$(cat "$PIDFILE" 2>/dev/null || true)
  if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
    kill "$pid" 2>/dev/null || true
    echo "Stopped sleep caretaker pid=$pid"
  fi
  rm -f "$PIDFILE"
else
  echo "Caretaker watch not running"
fi
