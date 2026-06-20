#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

from agent_essay_discourse import essay_discourse_payload

app = Path(__file__).resolve().parents[1] / "agent-control-panel" / "assets" / "app.js"
src = app.read_text(encoding="utf-8")
assert "function renderEssayNudgeBanner" in src, "renderEssayNudgeBanner missing"
assert "sa-0307" in src, "sa-0307 marker missing"
assert "sa-0357" in src, "sa-0357 marker missing"
assert "renderEssayNudgeBanner(essayD)" in src or "renderEssayNudgeBanner(data()" in src, (
    "Council/Today must call renderEssayNudgeBanner"
)
assert "sc-essay-nudge-banner" in src, "nudge banner class missing"
assert ".slice(0, 6)" in src, "sa-0317: show up to 6 nudges"

ed = essay_discourse_payload()
assert "essay_nudges" in ed, "essay_discourse must expose essay_nudges"
print(
    f"OK: validate-essay-nudge-banner-v1 · {ed.get('nudge_count', 0)} nudges "
    "(sa-0307 sa-0317 sa-0357)"
)
PY
