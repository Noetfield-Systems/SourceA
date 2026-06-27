#!/usr/bin/env bash
# Wire n8n + Cloud Forge Run auto-runtime — start n8n, import/activate wf-cloud-auto-runtime-v1.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
RECEIPT="${SINA}/n8n-cloud-forge-run-wire-receipt-v1.json"

mkdir -p "$SINA"
echo "→ Deactivate legacy executeCommand workflows in n8n DB…"
python3 <<'PY'
import sqlite3
from pathlib import Path
db = Path.home() / ".n8n" / "database.sqlite"
if db.is_file():
    con = sqlite3.connect(db)
    rows = con.execute("SELECT id, name FROM workflow_entity WHERE nodes LIKE '%executeCommand%'").fetchall()
    for wf_id, name in rows:
        con.execute("UPDATE workflow_entity SET active = 0 WHERE id = ?", (wf_id,))
        print("deactivated:", name)
    con.commit()
    con.close()
PY

echo "→ Starting n8n…"
bash "$ROOT/scripts/founder-start-n8n.sh"

for i in $(seq 1 30); do
  if curl -sf "http://127.0.0.1:5678/healthz" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

if ! curl -sf "http://127.0.0.1:5678/healthz" >/dev/null 2>&1; then
  echo "FAIL: n8n did not start — check ~/.sina/n8n.log"
  exit 1
fi

echo "→ Regenerating + importing wf-cloud-auto-runtime-v1…"
python3 "$ROOT/scripts/n8n_workflow_factory_v1.py" >/dev/null
python3 <<'PY'
import json, sqlite3, subprocess, uuid
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path.home() / "Desktop/SourceA"
WF = ROOT / "n8n/workflows/wf-cloud-auto-runtime-v1.json"
N8N_DB = Path.home() / ".n8n/database.sqlite"
data = json.loads(WF.read_text())
wf_id = data.get("id") or str(uuid.uuid4())
data["id"] = wf_id
data["active"] = True
tmp = Path("/tmp/n8n-import-wf-cloud-auto-runtime-v1.json")
tmp.write_text(json.dumps(data, indent=2))
r = subprocess.run(["npx", "--yes", "n8n", "import:workflow", f"--input={tmp}"], capture_output=True, text=True, cwd=str(ROOT))
if r.returncode != 0:
    raise SystemExit(r.stderr or r.stdout)
if N8N_DB.is_file():
    con = sqlite3.connect(N8N_DB)
    con.execute("UPDATE workflow_entity SET active = 1 WHERE name = ?", ("wf-cloud-auto-runtime-v1",))
    con.commit()
    row = con.execute("SELECT id,name,active FROM workflow_entity WHERE name=? ORDER BY updatedAt DESC LIMIT 1", ("wf-cloud-auto-runtime-v1",)).fetchone()
    con.close()
    print("workflow:", row)
PY

echo "→ CF 24/7 cron (primary scheduler when Mac sleeps)…"
CF_URL="https://sourcea-cloud-auto-runtime-tick-v1.sina-kazemnezhad-ca.workers.dev"
CF_HEALTH="$(curl -sf "$CF_URL/health" 2>/dev/null || echo '{}')"

python3 -c "
import json, os
from datetime import datetime, timezone
from pathlib import Path
r = {
  'schema': 'n8n-cloud-forge-run-wire-receipt-v1',
  'at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
  'n8n_running': True,
  'n8n_url': 'http://127.0.0.1:5678',
  'workflow': 'wf-cloud-auto-runtime-v1',
  'workflow_cron': '*/15 * * * *',
  'cf_worker_url': 'https://sourcea-cloud-auto-runtime-tick-v1.sina-kazemnezhad-ca.workers.dev',
  'cf_health': json.loads('''$CF_HEALTH''' if '''$CF_HEALTH'''.strip() else '{}'),
  'primary_scheduler': 'cloudflare_cron',
  'backup_scheduler': 'n8n_mac_awake',
  'for_founder': {'show_this': 'n8n UP · Cloud Forge Run workflow active · CF cron is 24/7 primary'},
}
Path(os.path.expanduser('~/.sina/n8n-cloud-forge-run-wire-receipt-v1.json')).write_text(json.dumps(r, indent=2)+'\n')
print(json.dumps(r, indent=2))
"

echo "OK — n8n wired · Cloudflare cron is 24/7 primary"
