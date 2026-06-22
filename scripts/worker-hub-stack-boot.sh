#!/usr/bin/env bash
# Worker Hub stack — start Hub + Chat Unify + N8N + Mac Law + wire (no browser).
set -uo pipefail
SA="${SINA_SOURCE_A:-$HOME/Desktop/SourceA}"
exec bash "$SA/scripts/portfolio-mail-stack-boot.sh"
