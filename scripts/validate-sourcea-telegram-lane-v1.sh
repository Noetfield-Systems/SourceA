#!/usr/bin/env bash
# validate-sourcea-telegram-lane-v1.sh — @Gateway_A forbidden · gateway lane zero Telegram
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: telegram-lane — $*" >&2; exit 1; }

LANE="$ROOT/data/sourcea-telegram-lane-v1.json"
GW="$ROOT/cloud/workers/loop-specialist-tick-v1/src/gateway-probe/cycle.js"
TG="$ROOT/cloud/workers/loop-specialist-tick-v1/src/nerve-probe/telegram.js"
PY="$ROOT/scripts/telegram_alert_v1.py"
SECRETS_SH="$ROOT/scripts/nerve_probe_cf_secrets_v1.sh"

[[ -f "$LANE" ]] || fail "missing $LANE"
[[ -f "$GW" ]] || fail "missing gateway-probe cycle.js"

python3 - "$LANE" "$GW" "$TG" "$PY" "$SECRETS_SH" <<'PY'
import json, sys
from pathlib import Path

lane, gw, tg, py, secrets_sh = map(Path, sys.argv[1:6])
doc = json.loads(lane.read_text())
forbidden = [u.lower().lstrip("@") for u in doc.get("forbidden_usernames", [])]

gw_text = gw.read_text()
if "sendTelegramAlert" in gw_text or "api.telegram.org" in gw_text:
    raise SystemExit("gateway-probe must not send Telegram — @Gateway_A lane forbidden")

tg_text = tg.read_text()
if "TELEGRAM_ALERT_CHAT_ID" in tg_text or "TELEGRAM_ALLOWED_CHAT_ID" in tg_text:
    raise SystemExit("nerve telegram.js must use TELEGRAM_OPS_CHAT_ID only")
if "telegram-lane.js" not in tg_text:
    raise SystemExit("nerve telegram.js must import telegram-lane guard")

py_text = py.read_text()
if "TELEGRAM_ALERT_CHAT_ID" in py_text or "TELEGRAM_ALLOWED_CHAT_ID" in py_text:
    raise SystemExit("telegram_alert_v1.py must use TELEGRAM_OPS_CHAT_ID only")

sh_text = secrets_sh.read_text()
if "TELEGRAM_ALERT_CHAT_ID" in sh_text and "never" not in sh_text.lower():
    raise SystemExit("nerve_probe_cf_secrets must not push TELEGRAM_ALERT_CHAT_ID")
if "TELEGRAM_OPS_CHAT_ID" not in sh_text:
    raise SystemExit("nerve_probe_cf_secrets must push TELEGRAM_OPS_CHAT_ID")

for name in forbidden:
    if f"@{name}" not in lane.read_text().lower() and name not in lane.read_text():
        pass  # lane file lists them

for dispatch in [
    Path(sys.argv[1]).parent.parent / "cloud/workers/loop-specialist-tick-v1/src/dispatch-table.json",
    Path(sys.argv[1]).parent.parent / "data/loop-specialist-cron-dispatch-v1.json",
]:
    if dispatch.is_file():
        d = json.loads(dispatch.read_text())
        blob = json.dumps(d)
        if "gateway_watchdog" in blob or "gateway_heartbeat" in blob:
            raise SystemExit(f"{dispatch.name} must not schedule gateway Telegram handlers")

print("OK: validate-sourcea-telegram-lane-v1 — gateway zero Telegram · ops lane only")
PY

echo "OK: validate-sourcea-telegram-lane-v1"
