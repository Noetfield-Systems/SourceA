#!/usr/bin/env bash
# sa-0653 — pre_llm user_signals store record_hub_touch on hub build
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"

python3 - <<'PY'
from pathlib import Path

from pre_llm.user_signals.store import record_hub_touch

ROOT = Path(".").resolve()
build = (ROOT / "scripts" / "build-sina-command-panel.py").read_text(encoding="utf-8")
store = (ROOT / "scripts" / "pre_llm" / "user_signals" / "store.py").read_text(encoding="utf-8")
refresh = (ROOT / "scripts" / "hub_self_refresh_v1.py").read_text(encoding="utf-8")

assert "from pre_llm.user_signals.store import record_hub_touch" in build, build
assert "record_hub_touch(" in build, "build must call record_hub_touch"
assert 'source="hub_build"' in build, "build must pass source=hub_build"
assert "_HUB_REFRESH_SOURCES" in store and "hub_build" in store, store
assert "record_hub_touch" in refresh and "hub_self_refresh" in refresh, refresh

out = record_hub_touch(hub_tab="validator-build", active_repo="SourceA", source="hub_build")
sig = out.get("signals") or {}
assert sig.get("last_refresh_at"), sig
signals = sig.get("signals") or []
assert signals and signals[-1].get("source") == "hub_build", signals[-1]

print("OK: validate-user-signals-record-hub-touch-on-build-v1 · hub_build wired on panel build")
PY
