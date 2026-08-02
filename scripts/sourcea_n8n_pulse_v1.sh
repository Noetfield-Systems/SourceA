#!/usr/bin/env bash
# Pulse heartbeat for sourcea_n8n_pulse_v1 — cloud trigger companion.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RECEIPT_DIR="$ROOT/receipts/n8n"
mkdir -p "$RECEIPT_DIR"
TS="$(date -u +%Y%m%dT%H:%M:%SZ)"
FILE_TS="$(date -u +%Y%m%dT%H%M%SZ)"
N8N_URL="${SOURCEA_N8N_HEALTH_URL:-}"
GATES_URL="${SOURCEA_GATES_URL:-https://sourcea-founder-gates-v1.sina-kazemnezhad-ca.workers.dev}"

n8n_ok=False
gates_ok=False
n8n_detail=""
gates_detail=""

if [ -n "$N8N_URL" ]; then
  code=$(curl -sS -o /tmp/n8n_pulse_body.txt -w "%{http_code}" --max-time 15 "$N8N_URL" || echo 000)
  n8n_detail="http_$code"
  [ "$code" = "200" ] && n8n_ok=True
else
  n8n_detail="SOURCEA_N8N_HEALTH_URL_unset"
fi

gcode=$(curl -sS -o /tmp/gates_pulse_body.txt -w "%{http_code}" --max-time 15 "$GATES_URL/health" || echo 000)
gates_detail="http_$gcode"
[ "$gcode" = "200" ] && gates_ok=True

python3 - <<PY
import json
from pathlib import Path
out = {
  "schema": "sourcea_n8n_pulse_v1",
  "loop_id": "sourcea_n8n_pulse_v1",
  "deadman": "sourcea-deadman-v1",
  "trigger_host": "cloud",
  "last_fired_at": "$TS",
  "n8n": {"ok": $n8n_ok, "detail": "$n8n_detail"},
  "gates": {"ok": $gates_ok, "detail": "$gates_detail", "url": "$GATES_URL"},
  "ok": True,
}
Path("$RECEIPT_DIR/N8N_PULSE_${FILE_TS}.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
PY
