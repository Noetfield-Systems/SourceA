#!/usr/bin/env bash
# validate-demo-film-quality-v1.sh — block mock/weak proof films from ship (DEMO-500)
set -euo pipefail
cd "$(dirname "$0")/.."

fail() { echo "FAIL: validate-demo-film-quality-v1 — $*" >&2; exit 1; }

W1_MP4="SourceA-landing/green-unified/assets/w1-demo.mp4"
RECEIPT="${HOME}/.sina/enforcement/w1-film-receipt-v1.json"
PROSPECT_REEL="commercial-video-factory/src/ProspectReel.tsx"

[[ -f "$RECEIPT" ]] || fail "missing w1-film-receipt-v1.json — run run_w1_film_pipeline_v1.sh"
[[ -f "$W1_MP4" ]] || fail "missing $W1_MP4"

python3 - <<'PY' || fail "receipt quality contract"
import json
from pathlib import Path

rec = json.loads(Path.home().joinpath(".sina/enforcement/w1-film-receipt-v1.json").read_text())
assert rec.get("schema") == "w1-film-receipt-v1"
assert rec.get("status") in ("embed_live", "filmed")
broll = str(rec.get("broll_source") or "")
assert broll, "broll_source required"
assert "TerminalMock" not in broll
assert "remotion-prospect" not in broll.lower() or "ui.webm" in broll or "landing-broll" in broll
law = rec.get("law") or ""
assert "real UI" in law or "ui" in broll.lower()
beats = set(rec.get("beats") or [])
assert {"BLOCK", "ALLOW", "tamper-FAIL"} <= beats
mp4 = Path("SourceA-landing/green-unified/assets/w1-demo.mp4")
assert mp4.stat().st_size > 100_000, "w1-demo.mp4 too small"
mock_blocked = rec.get("mock_ship_blocked")
if mock_blocked is not None:
    assert mock_blocked is True or rec.get("source_tier"), "mock_ship flag"
print("OK: W1 film quality · tier", rec.get("source_tier", "pipeline"), "· broll", broll[:80])
PY

if [[ -f "$PROSPECT_REEL" ]]; then
  if grep -q 'TerminalMock' "$PROSPECT_REEL"; then
    grep -q 'SHIP_BLOCKED_MOCK' "$PROSPECT_REEL" || fail "ProspectReel TerminalMock must not ship outbound"
    grep -q 'broll_video_file' "$PROSPECT_REEL" || fail "ProspectReel must wire real broll_video_file"
    [[ -f "commercial-video-factory/public/broll/w1-proof.mp4" ]] || fail "missing Remotion public broll — run commercial_video_factory_v1.py"
  fi
fi

grep -q 'assets/w1-demo.mp4' SourceA-landing/green-unified/proof.html || fail "proof.html missing w1-demo.mp4 embed"

echo "OK: validate-demo-film-quality-v1"
