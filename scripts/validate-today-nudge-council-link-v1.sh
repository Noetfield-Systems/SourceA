#!/usr/bin/env bash
# validate-today-nudge-council-link-v1.sh — sa-0854 / sa-0804 Today nudge → council-room tab
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

bash validate-essay-nudge-banner-v1.sh

python3 - <<'PY'
from pathlib import Path

from agent_essay_discourse import essay_discourse_payload

app = Path(__file__).resolve().parents[1] / "agent-control-panel" / "assets" / "app.js"
src = app.read_text(encoding="utf-8")

assert "function renderToday" in src, "renderToday missing"
assert "function renderEssayNudgeBanner" in src, "renderEssayNudgeBanner missing"

# Today tab must embed essay nudge banner
today_start = src.index("function renderToday")
today_end = src.index("function renderDaily", today_start)
today_block = src[today_start:today_end]
assert "renderEssayNudgeBanner" in today_block, "renderToday must call renderEssayNudgeBanner (sa-0854)"

banner_start = src.index("function renderEssayNudgeBanner")
banner_end = src.index("function renderScoreboardChecks", banner_start)
banner_block = src[banner_start:banner_end]
assert 'data-tab="council-room"' in banner_block, (
    "renderEssayNudgeBanner must link to council-room tab (sa-0854)"
)
assert "sc-essay-nudge-banner" in banner_block, "nudge banner class missing"
assert "sc-goto-tab" in banner_block, "goto-tab handler class missing"

assert ".sc-goto-tab" in src and "data-tab" in src, "sc-goto-tab binding missing in app.js"

ed = essay_discourse_payload()
nudges = ed.get("nudge_count", 0)
print(
    f"OK: validate-today-nudge-council-link-v1 · Today→council-room link wired "
    f"· nudges={nudges} (sa-0854)"
)
PY
