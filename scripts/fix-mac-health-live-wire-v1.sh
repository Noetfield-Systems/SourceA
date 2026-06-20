#!/usr/bin/env bash
# Wire Mac Health live pulse + H1 bridge — real-time independent app.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

echo "→ Restart Mac Health Guard (live pulse thread)…"
bash "$ROOT/scripts/install-mac-health-launchagent-v1.sh"

SINA_FORCE_RESTART=1 bash "$ROOT/scripts/serve-mac-health-guard.sh" 2>/dev/null || true
pkill -f 'mac-health-guard-server.py' 2>/dev/null || true
sleep 0.5
nohup python3 "$ROOT/scripts/mac-health-guard-server.py" >>"$HOME/.sina/mac-health-guard-server.log" 2>&1 &
for _ in {1..40}; do
  curl -sf "http://127.0.0.1:13024/health" >/dev/null 2>&1 && break
  sleep 0.25
done

echo "→ First live pulse + H1 bridge…"
python3 mac_health_live_v1.py --json | python3 -c "import sys,json; d=json.load(sys.stdin); print('live',d.get('live_status'),'score',d.get('score'),'h1',(d.get('h1_sync') or {}).get('task_id'))"

echo "→ Refresh H1 boot + worker hub…"
python3 worker_hub_v1.py --json --no-cache >/dev/null
bash "$ROOT/scripts/fix-worker-hub-stable-v1.sh" 2>&1 | tail -5

echo "→ Live API check…"
curl -sf "http://127.0.0.1:13024/api/mac-health/live" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('ok'); print('OK live',d.get('live_status'),'pulse',d.get('wired',{}).get('live_age_sec'))"
curl -sf "http://127.0.0.1:13020/api/worker-hub/v1" | python3 -c "import sys,json; d=json.load(sys.stdin); m=d.get('mac_health_live') or {}; print('OK H1 mac',m.get('live_status'),'score',m.get('score'))"

echo ""
echo "✓ Mac Health LIVE wired to H1"
echo "  Heart: http://127.0.0.1:13024/  (polls every 5s)"
echo "  H1:    http://127.0.0.1:13020/  (Mac Heart card)"
echo "  Bridge: ~/.sina/mac-health-h1-bridge-v1.json"
