#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail() { echo "FAIL: validate-mega-chat-anchors-v1 — $*" >&2; exit 1; }

python3 <<'PY'
import json
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from ecosystem_master_catalog_v1 import MEGA_CHAT_ANCHORS, mega_chat_anchors_payload

ids = {r["id"] for r in MEGA_CHAT_ANCHORS}
need = {"ECOSYSTEM", "MONOREPO", "MAINTAINER_1", "MAINTAINER_2"}
missing = need - ids
assert not missing, f"missing anchor ids: {missing}"

by_id = {r["id"]: r for r in MEGA_CHAT_ANCHORS}
assert by_id["ECOSYSTEM"]["workspace"] == "SinaaiDataBase"
assert by_id["ECOSYSTEM"]["transcript_id"].startswith("a53f3fa1")
assert by_id["MONOREPO"]["workspace"] == "SinaaiMonoRepo"
assert by_id["MAINTAINER_2"]["workspace"] == "SinaaiDataBase"
assert by_id["MAINTAINER_1"]["transcript_id"].startswith("a53f3fa1")
assert by_id["MAINTAINER_1"].get("cursor_status") == "retired"
assert by_id["MAINTAINER_1"].get("successor_id") == "MAINTAINER_2"
assert by_id["MAINTAINER_2"]["transcript_id"].startswith("74f5ccab")

rt = mega_chat_anchors_payload()
rt_ids = {r["id"] for r in rt}
assert need <= rt_ids, rt_ids

for row in rt:
    if row["id"] in need:
        assert row["counts"]["exists"], f"transcript missing: {row['id']}"

print("PASS: mega_chat_anchors", sorted(need))
PY

grep -q "MAINTAINER_2" "$ROOT/brain-os/narrative-bridge/LATEST_TOUCH_BASE_LOCKED_v1.md" || fail "LATEST missing MAINTAINER_2 anchor row"

echo "OK: validate-mega-chat-anchors-v1"
