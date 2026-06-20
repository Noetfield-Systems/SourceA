#!/usr/bin/env bash
# UI FIRST CHECK — ONE command, any directory. Mandatory before ANY UI edit.
#
#   bash ~/Desktop/SourceA/scripts/wbc-ui-first-check.sh
#   bash ~/Desktop/SourceA/scripts/wbc-ui-first-check.sh --path witnessbc-site/content/toolkits.html
#   bash ~/Desktop/SourceA/scripts/wbc-ui-first-check.sh --surface hub_form --ack
#
set -euo pipefail

WBC_SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WBC_ROOT="$(cd "$WBC_SCRIPT/.." && pwd)"
LAW="$WBC_ROOT/brain-os/law/enforcement/SOURCEA_UI_UPGRADE_MANDATORY_PROCESS_LOCKED_v1.md"

PATH_ARG=""
SURFACE=""
DO_ACK=0
DO_PRINT=0

usage() {
  cat <<EOF
UI FIRST CHECK — mandatory before ANY form · app · website · hub · canvas UI edit

  bash $WBC_SCRIPT/wbc-ui-first-check.sh                    # wire + validate all gates
  bash $WBC_SCRIPT/wbc-ui-first-check.sh --path <file>       # classify path + show ack cmd
  bash $WBC_SCRIPT/wbc-ui-first-check.sh --surface <id> --ack   # ack surface (12h TTL)
  bash $WBC_SCRIPT/wbc-ui-first-check.sh --checklist <id>   # print UP-0..UP-7 + app checklist

Law: brain-os/law/enforcement/SOURCEA_UI_UPGRADE_MANDATORY_PROCESS_LOCKED_v1.md
Rules: 024 · 025 · 026 (alwaysApply — ZERO EXCEPTION)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --path) PATH_ARG="${2:-}"; shift 2 ;;
    --surface) SURFACE="${2:-}"; shift 2 ;;
    --ack) DO_ACK=1; shift ;;
    --checklist) DO_PRINT=1; SURFACE="${2:-}"; shift 2 ;;
    -h | --help) usage; exit 0 ;;
    *) echo "Unknown: $1"; usage; exit 1 ;;
  esac
done

[[ -f "$LAW" ]] || { echo "FAIL: missing UI upgrade law"; exit 1; }

echo "=== UI FIRST CHECK (mandatory · zero exception) ==="
echo "    root: $WBC_ROOT"
echo ""

python3 "$WBC_SCRIPT/ui_upgrade_first_check_v1.py" --wire --surface "${SURFACE:-worker_hub}" --json >/dev/null
echo "OK  live wire refreshed"
echo ""

bash "$WBC_SCRIPT/validate-ui-first-check-mandatory-all-agents-v1.sh"
echo ""
bash "$WBC_SCRIPT/validate-ui-zero-drift-v1.sh"
echo ""

if [[ -n "$PATH_ARG" ]]; then
  echo "--- classify: $PATH_ARG ---"
  python3 "$WBC_SCRIPT/ui_upgrade_path_classifier_v1.py" --path "$PATH_ARG" --json
  echo ""
fi

if [[ -n "$SURFACE" && "$DO_ACK" -eq 1 ]]; then
  echo "--- ack surface: $SURFACE ---"
  python3 "$WBC_SCRIPT/ui_upgrade_first_check_v1.py" --surface "$SURFACE" --ack --json
  echo ""
fi

if [[ -n "$SURFACE" && "$DO_PRINT" -eq 1 ]]; then
  echo "--- checklist: $SURFACE ---"
  python3 "$WBC_SCRIPT/ui_upgrade_mandatory_gate_v1.py" --surface "$SURFACE" --print-checklist
  python3 "$WBC_SCRIPT/ui_upgrade_ledger_v1.py" --surface "$SURFACE" --show --json
  echo ""
fi

cat <<'SEQ'

GUARD SEQUENCE (machine-enforced before UI write):
  ui_upgrade_path_classifier_v1.py → ui_upgrade_first_check_v1.py --ack
  → ui_upgrade_mandatory_gate_v1.py → ui_upgrade_ledger_v1.py → pre_write_guard_v1.py

Machine blocks without ack: UI_UPGRADE_FIRST_CHECK_REQUIRED
SEQ

echo ""
echo "PASS: UI FIRST CHECK guard chain OK · no invitation"
