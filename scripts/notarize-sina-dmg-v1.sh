#!/usr/bin/env bash
# Notarize + staple a SourceA .dmg (Chat Unify and other portfolio apps).
# Prerequisites (Apple Developer Program — $99/yr):
#   1. Developer ID Application certificate in Keychain
#   2. App-specific password OR App Store Connect API key in notarytool profile
#
# Setup once:
#   xcrun notarytool store-credentials "SOURCEA_NOTARY" \\
#     --apple-id "you@email.com" --team-id "TEAMID" --password "app-specific-password"
#
# Ship:
#   SINA_NOTARY_KEYCHAIN_PROFILE=SOURCEA_NOTARY bash scripts/notarize-sina-dmg-v1.sh path/to.dmg
#
# Apple docs: https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution
set -euo pipefail

DMG="${1:-}"
PROFILE="${SINA_NOTARY_KEYCHAIN_PROFILE:-SOURCEA_NOTARY}"
RECEIPT="$HOME/.sina/sina-notarize-receipt-v1.json"

if [[ -z "$DMG" || ! -f "$DMG" ]]; then
  echo "usage: SINA_NOTARY_KEYCHAIN_PROFILE=SOURCEA_NOTARY $0 <file.dmg>" >&2
  exit 1
fi

if ! xcrun notarytool history --keychain-profile "$PROFILE" >/dev/null 2>&1; then
  echo "FAIL: notarytool profile '$PROFILE' not configured." >&2
  echo "  Run: xcrun notarytool store-credentials \"$PROFILE\" --apple-id ... --team-id ... --password ..." >&2
  echo "  https://developer.apple.com/help/account/manage-your-team/manage-app-specific-passwords" >&2
  exit 1
fi

echo "→ Submitting to Apple notary service: $DMG"
SUBMIT_JSON="$(mktemp)"
xcrun notarytool submit "$DMG" --keychain-profile "$PROFILE" --wait --output-format json >"$SUBMIT_JSON"

python3 - <<PY
import json, sys
from datetime import datetime, timezone
from pathlib import Path
data = json.loads(Path("$SUBMIT_JSON").read_text())
status = data.get("status") or data.get("message", "")
ok = str(status).upper() == "ACCEPTED"
row = {
    "schema": "sina-notarize-receipt-v1",
    "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "dmg": "$DMG",
    "profile": "$PROFILE",
    "status": status,
    "ok": ok,
    "id": data.get("id"),
    "raw": data,
}
Path("$RECEIPT").write_text(json.dumps(row, indent=2) + "\\n")
print(json.dumps({"ok": ok, "status": status, "receipt": str(Path("$RECEIPT"))}))
if not ok:
    sys.exit(1)
PY

echo "→ Stapling notarization ticket…"
xcrun stapler staple "$DMG"
xcrun stapler validate "$DMG"
echo "✓ Notarized + stapled: $DMG"
