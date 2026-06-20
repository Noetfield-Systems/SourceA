#!/usr/bin/env bash
set -euo pipefail
rm -f "$HOME/.sina/agent-cancel-v1.flag"
echo "Removed agent-cancel flag — factory may run again."
bash "$HOME/Desktop/SourceA/runtime-wrapper-demo.sh"
