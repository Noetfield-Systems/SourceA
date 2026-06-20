#!/usr/bin/env bash
# Morning brief — English or Farsi only (never mixed in one utterance).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LANG_CHOICE="${1:-en}"

if [[ ! -f "$ROOT/sina-bowl/brief.txt" ]]; then
  python3 "$ROOT/scripts/build-sina-daily-bowl.py"
fi

if [[ "$LANG_CHOICE" == "fa" || "$LANG_CHOICE" == "farsi" ]]; then
  BRIEF="$ROOT/sina-bowl/brief.fa.txt"
  VOICE_LANG="fa-IR"
else
  BRIEF="$ROOT/sina-bowl/brief.txt"
  VOICE_LANG="en-US"
fi

TEXT="$(cat "$BRIEF")"
if [[ "$LANG_CHOICE" == "fa" || "$LANG_CHOICE" == "farsi" ]] && echo "$TEXT" | grep -qE '[A-Za-z]'; then
  echo "ERROR: Farsi brief contains English — run build-sina-daily-bowl.py" >&2
  exit 1
fi

if command -v say >/dev/null 2>&1; then
  if [[ "$LANG_CHOICE" == "fa" || "$LANG_CHOICE" == "farsi" ]]; then
    say -r 165 "$TEXT" 2>/dev/null || say -r 165 -v "Damascus" "$TEXT" 2>/dev/null || say -r 165 "$TEXT"
  else
    say -r 180 "$TEXT"
  fi
else
  echo "$TEXT"
fi
