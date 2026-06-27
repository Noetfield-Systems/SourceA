#!/usr/bin/env bash
# Build signed Chat Unify.app and publish .dmg into green-unified dist for Pages hosting.
# STAB-018 · STAB-019
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
APP_NAME="Chat Unify"
DESKTOP="$HOME/Desktop/${APP_NAME}.app"
DOWNLOADS_DIR="$ROOT/sites/SourceA-landing/green-unified/downloads"
DMG_NAME="chat-unify-mac-v1.dmg"
DMG_PATH="$DOWNLOADS_DIR/$DMG_NAME"
STAGING_DMG="/tmp/sourcea-chat-unify-publish.dmg"

echo "→ Building Chat Unify standalone app…"
bash "$ROOT/scripts/build-chat-unify-standalone-app-v1.sh"

if [[ ! -d "$DESKTOP" ]]; then
  echo "FAIL: Desktop app missing: $DESKTOP" >&2
  exit 1
fi

mkdir -p "$DOWNLOADS_DIR"
rm -f "$STAGING_DMG" "$DMG_PATH"
hdiutil create -volname "Chat Unify" -srcfolder "$DESKTOP" -ov -format UDZO "$STAGING_DMG"
mv "$STAGING_DMG" "$DMG_PATH"

if [[ -n "${SINA_NOTARY_KEYCHAIN_PROFILE:-}" ]]; then
  echo "→ Notarizing DMG (profile: $SINA_NOTARY_KEYCHAIN_PROFILE)…"
  bash "$ROOT/scripts/notarize-sina-dmg-v1.sh" "$DMG_PATH"
elif xcrun notarytool history --keychain-profile "SOURCEA_NOTARY" >/dev/null 2>&1; then
  echo "→ Notarizing DMG (profile: SOURCEA_NOTARY)…"
  SINA_NOTARY_KEYCHAIN_PROFILE=SOURCEA_NOTARY bash "$ROOT/scripts/notarize-sina-dmg-v1.sh" "$DMG_PATH"
else
  echo "WARN: DMG is NOT notarized — downloaders will see Gatekeeper block." >&2
  echo "  Diagnose: bash scripts/diagnose-chat-unify-gatekeeper-v1.sh" >&2
  echo "  Fix: Apple Developer ID + notarytool — see scripts/notarize-sina-dmg-v1.sh" >&2
fi

BYTES=$(stat -f%z "$DMG_PATH" 2>/dev/null || stat -c%s "$DMG_PATH")
SHA=$(shasum -a 256 "$DMG_PATH" | awk '{print $1}')

python3 - <<PY
import json
from datetime import datetime, timezone
from pathlib import Path
row = {
    "schema": "sourcea-download-artifact-v1",
    "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "product": "chat-unify",
    "version": "4.8.0",
    "filename": "$DMG_NAME",
    "public_path": "/downloads/$DMG_NAME",
    "public_url": "https://sourcea.app/downloads/$DMG_NAME",
    "bytes": int("$BYTES"),
    "sha256": "$SHA",
    "build_script": "scripts/publish_chat_unify_dmg_v1.sh",
}
Path("$DOWNLOADS_DIR/chat-unify-mac-v1.json").write_text(json.dumps(row, indent=2) + "\\n")
Path.home().joinpath(".sina/chat-unify-dmg-publish-receipt-v1.json").write_text(json.dumps(row, indent=2) + "\\n")
print(json.dumps({"ok": True, "dmg": str(Path("$DMG_PATH")), "bytes": row["bytes"], "url": row["public_url"]}))
PY

echo "✓ DMG ready: $DMG_PATH"
echo "  Public URL after landing publish: https://sourcea.app/downloads/$DMG_NAME"
