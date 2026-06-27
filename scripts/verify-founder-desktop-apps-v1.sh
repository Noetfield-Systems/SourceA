#!/usr/bin/env bash
# Light realtime smoke — founder session safe · ≤90s · curl health only.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail=0

check() {
  local name="$1" url="$2"
  if curl -sf --max-time 8 "$url" >/dev/null 2>&1; then
    echo "PASS $name $url"
  else
    echo "FAIL $name $url" >&2
    fail=$((fail + 1))
  fi
}

check_json() {
  local name="$1" url="$2" py="$3"
  if curl -sf --max-time 8 "$url" | python3 -c "$py" 2>/dev/null; then
    echo "PASS $name $url"
  else
    echo "FAIL $name $url" >&2
    fail=$((fail + 1))
  fi
}

# Start servers from Desktop apps if ports down (best effort)
for port_script in "13023:chat-unify-server.py" "13027:cloud-workers-server.py" "13028:portfolio-mail-server.py"; do
  port="${port_script%%:*}"
  script="${port_script##*:}"
  if ! curl -sf --max-time 2 "http://127.0.0.1:${port}/health" >/dev/null 2>&1; then
    python3 "$ROOT/scripts/$script" >>"$HOME/.sina/verify-desktop-apps-boot.log" 2>&1 &
    sleep 2
  fi
done

check "chat_unify_health" "http://127.0.0.1:13023/health"
check "chat_unify_form" "http://127.0.0.1:13023/form/"
check_json "chat_unify_form_api" "http://127.0.0.1:13023/api/live-founder-decision-form-v1" \
  "import sys,json; d=json.load(sys.stdin); u=d.get('form_page_url',''); assert '13023/form' in u, u; print('form_url',u)"

check_json "cloud_workers_health" "http://127.0.0.1:13027/health" \
  "import sys,json; d=json.load(sys.stdin); assert d.get('ok') and d.get('service')=='cloud-workers'; print('railway_live',d.get('railway_live'))"

check "portfolio_mail_health" "http://127.0.0.1:13028/health"
check "portfolio_mail_hub" "http://127.0.0.1:13028/mail-hub/"

check_json "chat_unify_hub_pro" "http://127.0.0.1:13023/api/hub-pro-skills/v1?app=chat_unify" \
  "import sys,json; d=json.load(sys.stdin); assert d.get('app_id'); print('hub_pro',d.get('app_id'))"

check_json "chat_unify_api_station" "http://127.0.0.1:13023/api/api-station/v1?app=chat-unify" \
  "import sys,json; d=json.load(sys.stdin); print('tasks',len(d.get('tasks',[])))"

# Bundle manifest freshness (Chat Unify on Desktop)
manifest="$HOME/Desktop/Chat Unify.app/Contents/Resources/chat-unify-bundle/bundle-wire-manifest-v1.json"
if [[ -f "$manifest" ]]; then
  if python3 -c "import json,sys; m=json.load(open('$manifest')); assert m.get('form_ui','').endswith('/form/'); print('manifest',m.get('built_at'))"; then
    echo "PASS chat_unify_manifest $manifest"
  else
    echo "FAIL chat_unify_manifest stale" >&2
    fail=$((fail + 1))
  fi
else
  echo "WARN chat_unify_manifest missing — rebuild Chat Unify.app" >&2
fi

if [[ "$fail" -gt 0 ]]; then
  exit 1
fi
echo "OK verify-founder-desktop-apps-v1"
