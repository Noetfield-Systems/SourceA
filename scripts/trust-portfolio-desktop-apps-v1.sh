#!/usr/bin/env bash
# Remove quarantine + re-sign portfolio desktop apps so double-click opens a window.
set -euo pipefail
SA="${SINA_SOURCE_A:-$HOME/Desktop/SourceA}"
ENT="$SA/brand/macos-apps/entitlements-local.plist"
LSREGISTER="/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
NAMES=("Worker Hub" "Portfolio Mail" "Chat Unify" "N8N Integration" "Cloud Workers")

sign_one() {
  local app="$1"
  [[ -d "$app" ]] || return 0
  xattr -cr "$app" 2>/dev/null || true
  local inner
  inner="$(find "$app/Contents/MacOS" -maxdepth 1 -type f -perm +111 2>/dev/null | head -1)"
  if [[ -n "$inner" && -f "$ENT" ]]; then
    codesign --force --sign - --entitlements "$ENT" --timestamp=none "$inner" 2>/dev/null || true
    codesign --force --deep --sign - --entitlements "$ENT" --timestamp=none "$app" 2>/dev/null || true
  else
    codesign --force --deep --sign - --timestamp=none "$app" 2>/dev/null || true
  fi
  [[ -x "$LSREGISTER" ]] && "$LSREGISTER" -f -R -trusted "$app" 2>/dev/null || true
  echo "trusted: $app"
}

for base in "$HOME/Desktop" "$HOME/Applications"; do
  for name in "${NAMES[@]}"; do
    sign_one "$base/${name}.app"
  done
done

echo "Done — if macOS still blocks: Right-click app → Open → Open (one time only)."
echo ""
echo "For paying downloaders: ad-hoc sign is NOT enough — need Developer ID + notarization."
echo "  bash \"$SA/scripts/diagnose-chat-unify-gatekeeper-v1.sh\""
echo "  https://developer.apple.com/account/resources/certificates/list"
