#!/usr/bin/env bash
set -euo pipefail
RW="$HOME/Desktop/SourceA/runtime-wrapper"
CANCEL="$HOME/.sina/agent-cancel-v1.flag"
echo "=== SourceA Runtime Wrapper demo ==="
if [[ -f "$CANCEL" ]]; then
  echo ""
  echo "NOTE: agent-cancel flag is ON (Mac Health Stop). Dispatches will BLOCK until you resume."
  echo "To see PASS receipts after this demo, run:"
  echo "  rm -f ~/.sina/agent-cancel-v1.flag && bash ~/Desktop/SourceA/runtime-wrapper-demo.sh"
  echo ""
fi
echo "--- 1. status ---"
"$RW" status --json
echo ""
echo "--- 2. profile set agency ---"
"$RW" profile set agency --json
echo ""
echo "--- 3. governance llm.chat dry-run ---"
"$RW" dispatch --action llm.chat --profile governance --context '{"task_id":"demo","user":"hello","stub_llm":true}' --dry-run --json || true
echo ""
echo "--- 4. agency outreach dry-run ---"
"$RW" dispatch --action outreach.send --profile agency --context '{"approval_ref":"form-pick-1","template_id":"nw1"}' --dry-run --json || true
echo ""
echo "--- 5. validator ---"
bash "$HOME/Desktop/SourceA/scripts/validate-sourcea-runtime-wrapper-v1.sh"
echo ""
if [[ -f "$CANCEL" ]]; then
  echo "=== DONE (wrapper OK · global BLOCK expected while cancel flag on) ==="
else
  echo "=== DONE (wrapper OK · expect PASS on dry-run steps above) ==="
fi
