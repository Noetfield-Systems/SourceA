#!/usr/bin/env bash
# Sync Cloud Workers.app bundle from live SourceA (run after UI/hub changes).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUNDLE="$ROOT/brand/macos-apps/Cloud Workers.app/Contents/Resources/cloud-workers-bundle"
mkdir -p "$BUNDLE/shared" "$BUNDLE/app" "$BUNDLE/scripts/fbe/lib"
cp "$ROOT/scripts/cloud-workers-standalone/index.html" "$BUNDLE/app/index.html"
for f in cloud-workers-panel.js sina-main-terminal.js sina-main-terminal.css official-links-bar.js official-links-bar.css; do
  cp "$ROOT/agent-control-panel/shared/$f" "$BUNDLE/shared/$f"
done
for f in cloud-workers-server.py cloud_workers_hub_v1.py cloud_auto_runtime_v1.py hub_cloud_forge_run_proceed_v1.py cloud_auto_runtime_single_cycle_gate_v1.py autonomous_drain_receipt_cloud_v1.py; do
  cp "$ROOT/scripts/$f" "$BUNDLE/scripts/$f"
done
cp "$ROOT/scripts/fbe/lib/hub_cloud_proxy_v1.py" "$BUNDLE/scripts/fbe/lib/hub_cloud_proxy_v1.py"
cp "$ROOT/scripts/fbe/lib/cloud_forge_run_queue_v1.py" "$BUNDLE/scripts/fbe/lib/cloud_forge_run_queue_v1.py"
echo "OK synced Cloud Workers.app bundle from SourceA"
