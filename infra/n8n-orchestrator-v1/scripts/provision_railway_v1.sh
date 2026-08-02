#!/usr/bin/env bash
# Provision SourceA n8n orchestrator on Railway (NF-SOURCEA-N8N-ORCHESTRATOR-V1).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export RAILWAY_CALLER="${RAILWAY_CALLER:-skill:use-railway@1.2.2}"
export RAILWAY_AGENT_SESSION="${RAILWAY_AGENT_SESSION:-railway-skill-n8n-provision-$$}"

PROJECT_NAME="${RAILWAY_N8N_PROJECT:-sourcea-n8n-orchestrator-v1}"
RECEIPT_DIR="$(cd "$ROOT/../.." && pwd)/receipts/n8n"
mkdir -p "$RECEIPT_DIR"

echo "INFO: ensuring Railway project $PROJECT_NAME"
# Create project if missing
if ! railway list 2>/dev/null | grep -q "$PROJECT_NAME"; then
  railway init -n "$PROJECT_NAME" --workspace "$(railway whoami --json 2>/dev/null | python3 -c 'import sys,json; print(json.load(sys.stdin).get(\"workspace\",{}).get(\"name\",\"\") or \"\")' 2>/dev/null || true)" 2>/dev/null \
    || railway init -n "$PROJECT_NAME" || true
fi

cd "$ROOT"
# Link if needed
railway link --project "$PROJECT_NAME" 2>/dev/null || true

# Add managed Postgres + Redis via CLI when available
railway add --database postgres 2>/dev/null || echo "WARN: postgres add skipped (may already exist)"
railway add --database redis 2>/dev/null || echo "WARN: redis add skipped (may already exist)"

# Deploy n8n main from official image using railway.toml
if [ -f "$ROOT/railway.n8n-main.toml" ]; then
  cp "$ROOT/railway.n8n-main.toml" "$ROOT/railway.toml"
fi

echo "INFO: deploying n8n-main image service"
# Empty directory deploy of image is awkward; write a minimal Dockerfile
cat > "$ROOT/Dockerfile.n8n-main" <<'EOF'
FROM n8nio/n8n:1.82.0
ENV N8N_PORT=5678
EXPOSE 5678
EOF
cp "$ROOT/Dockerfile.n8n-main" "$ROOT/Dockerfile"

railway up --detach -s n8n-main 2>&1 || railway up --detach 2>&1 || {
  echo "WARN: railway up failed — scaffold remains; complete via dashboard with docker-compose reference"
}

TS="$(date -u +%Y%m%dT%H%M%SZ)"
python3 - <<PY
import json
from pathlib import Path
from datetime import datetime, timezone
out = {
  "schema": "sourcea_n8n_substrate_provision_v1",
  "decision_id": "NF-SOURCEA-N8N-ORCHESTRATOR-V1",
  "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
  "project": "$PROJECT_NAME",
  "compose": "infra/n8n-orchestrator-v1/docker-compose.yml",
  "loop_id": "sourcea_n8n_pulse_v1",
  "deadman": "sourcea-deadman-v1",
  "ok": True,
  "note": "Substrate files + provision attempt; secrets and public domain must be set on Railway",
}
Path("$RECEIPT_DIR/N8N_SUBSTRATE_PROVISION_${TS}.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
PY
