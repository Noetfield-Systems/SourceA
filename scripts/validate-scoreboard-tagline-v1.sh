#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

from agent_scoreboard import SCOREBOARD_TAGLINE, scoreboard_payload

src = Path("agent_scoreboard.py").read_text(encoding="utf-8")
assert "SCOREBOARD_TAGLINE" in src, "SCOREBOARD_TAGLINE constant missing"
assert "sa-0304" in src, "sa-0304 marker missing"

tl = SCOREBOARD_TAGLINE.lower()
assert "auto-checks" in tl and "green" in tl, f"tagline must mention auto-checks green: {SCOREBOARD_TAGLINE!r}"
assert "not asf verify" in tl, f"tagline must deny ASF verify authority: {SCOREBOARD_TAGLINE!r}"

sb = scoreboard_payload()
assert sb.get("tagline") == SCOREBOARD_TAGLINE, "scoreboard_payload tagline drift"

ess = Path("hub_essentials_index.py").read_text(encoding="utf-8")
assert "ASF verify ✓" not in ess, "hub_essentials_index still promotes ASF verify"
assert "auto-checks green" in ess, "hub_essentials_index missing auto-checks green copy"

print(f"OK: validate-scoreboard-tagline-v1 · {SCOREBOARD_TAGLINE[:56]}… (sa-0304)")
PY
