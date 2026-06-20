#!/usr/bin/env bash
# validate-agent-no-hub-rebuild-stuck-v1.sh — agent entry docs must not mandate default strict build
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-agent-no-hub-rebuild-stuck-v1 — $*" >&2; exit 1; }

LAW="$ROOT/AGENT_NO_HUB_REBUILD_STUCK_LOCKED_v1.md"
[[ -f "$LAW" ]] || fail "missing law doc"

python3 - <<'PY' || fail "agent doc scan"
import re
from pathlib import Path

ROOT = Path("/Users/sinakazemnezhad/Desktop/SourceA")
must_have = [
    ROOT / "brain-os/enforcement/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md",
    ROOT / "brain-os/contract/MANDATORY_BRAIN_CHAT_LOCKED_v1.md",
    ROOT / "agent-skills/sourcea_worker/SKILL.md",
    ROOT / ".cursor/rules/no-hub-rebuild-stuck.mdc",
]
for p in must_have:
    if not p.is_file():
        raise SystemExit(f"missing {p}")

worker = (ROOT / "brain-os/enforcement/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md").read_text()
if "validate-super-fast-hub-v1.sh" not in worker:
    raise SystemExit("worker mandatory must cite validate-super-fast-hub-v1")
if re.search(r"DEFAULT VERIFY[\s\S]{0,400}build-sina-command-panel", worker):
    raise SystemExit("worker DEFAULT VERIFY still mandates build-sina-command-panel")

brain = (ROOT / "brain-os/contract/MANDATORY_BRAIN_CHAT_LOCKED_v1.md").read_text()
if "validate-super-fast-hub-v1.sh" not in brain:
    raise SystemExit("brain mandatory must cite validate-super-fast-hub-v1")

skill = (ROOT / "agent-skills/sourcea_worker/SKILL.md").read_text()
if re.search(r"VERIFY closeout[\s\S]{0,300}build-sina-command-panel", skill):
    raise SystemExit("worker skill VERIFY still mandates build-sina-command-panel")

print("OK: agent no-hub-rebuild-stuck doc wiring")
PY

echo "OK: validate-agent-no-hub-rebuild-stuck-v1"
