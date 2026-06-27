#!/usr/bin/env bash
# Diagnose why macOS Gatekeeper blocks Chat Unify — writes receipt for founder.
set -euo pipefail
APP="${1:-$HOME/Desktop/Chat Unify.app}"
DMG="${2:-$HOME/Desktop/SourceA/sites/SourceA-landing/green-unified/downloads/chat-unify-mac-v1.dmg}"
RECEIPT="$HOME/.sina/chat-unify-gatekeeper-receipt-v1.json"

IDENTITIES="$(security find-identity -v -p codesigning 2>/dev/null | grep -c 'Developer ID Application' || true)"
SIG="$(codesign -dv "$APP" 2>&1 | awk -F= '/^Signature=/{print $2}' || echo missing)"
SPCTL="$(spctl -a -vv -t install "$APP" 2>&1 | tail -1 || true)"
QATTR="$(xattr -l "$APP" 2>/dev/null | grep -c com.apple.quarantine || true)"

python3 - <<PY
import json
from datetime import datetime, timezone
from pathlib import Path

identities = int("${IDENTITIES:-0}")
sig = "${SIG}".strip()
spctl = """${SPCTL}""".strip()
quarantine = int("${QATTR:-0}") > 0
adhoc = sig == "adhoc"
blocked = "rejected" in spctl.lower() or adhoc

fixes = []
if identities == 0:
    fixes.append({
        "step": 1,
        "action": "Join Apple Developer Program + create Developer ID Application certificate",
        "url": "https://developer.apple.com/account/resources/certificates/list",
    })
    fixes.append({
        "step": 2,
        "action": "Store notarytool credentials (app-specific password)",
        "url": "https://appleid.apple.com/account/manage",
    })
    fixes.append({
        "step": 3,
        "action": "Rebuild: SINA_NOTARY_KEYCHAIN_PROFILE=SOURCEA_NOTARY bash scripts/publish_chat_unify_dmg_v1.sh",
        "url": "scripts/notarize-sina-dmg-v1.sh",
    })
else:
    fixes.append({
        "step": 1,
        "action": "Re-sign with Developer ID + notarize DMG",
        "cmd": "bash scripts/publish_chat_unify_dmg_v1.sh",
    })

if adhoc and blocked:
    fixes.append({
        "step": "now",
        "action": "Local-only workaround: Right-click Chat Unify.app → Open → Open (once). Does NOT fix paying downloaders.",
    })

row = {
    "schema": "chat-unify-gatekeeper-receipt-v1",
    "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "app": "$APP",
    "dmg": "$DMG",
    "signature": sig,
    "gatekeeper": spctl,
    "developer_id_certs_in_keychain": identities,
    "quarantine": quarantine,
    "blocked": blocked,
    "problem": (
        "Chat Unify is ad-hoc signed and not notarized — macOS Gatekeeper blocks it for downloaders."
        if adhoc
        else "Gatekeeper check failed — see gatekeeper field."
    ),
    "apple_refs": [
        "https://developer.apple.com/help/account/certificates/create-developer-id-certificates",
        "https://support.apple.com/guide/security/gatekeeper-and-notarization-sec5599b66df/web",
    ],
    "fixes": fixes,
}
Path("$RECEIPT").write_text(json.dumps(row, indent=2) + "\\n")
print(json.dumps(row, indent=2))
PY
