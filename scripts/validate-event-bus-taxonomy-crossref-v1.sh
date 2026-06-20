#!/usr/bin/env bash
# validate-event-bus-taxonomy-crossref-v1.sh — sa-0990 ACT T3 dedup cross-ref
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cross = root / "archive/attachments/2026-06-14/sa-0990-event-bus-taxonomy-t3-crossref_LOCKED_v1.md"
canonical = root / "archive/attachments/2026-06-14/sa-0965-event-bus-topic-taxonomy-spine-learning-loop_LOCKED_v1.md"
receipt = root / "receipts/sa-0965-receipt.json"

assert cross.is_file(), "missing sa-0990 cross-ref doc"
text = cross.read_text(encoding="utf-8")
assert "sa-0965" in text
assert "sa-0965-event-bus-topic-taxonomy-spine-learning-loop_LOCKED_v1.md" in text
assert canonical.is_file(), "canonical sa-0965 attachment missing"
assert receipt.is_file(), "canonical sa-0965 receipt missing"
for marker in ("## Fabric today", "## Spine learning loop", "**Module** | `scripts/runtime/event_bus"):
    assert marker not in text, f"T3 cross-ref must not duplicate table ({marker})"

print("OK: validate-event-bus-taxonomy-crossref-v1 · canonical=sa-0965 · no duplicate table · sa-0990")
PY
