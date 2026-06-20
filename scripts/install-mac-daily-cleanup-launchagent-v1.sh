#!/usr/bin/env bash
# Install mid-job Mac daily cleanup LaunchAgent (every 2 hours, 8:00–23:00).
set -euo pipefail
SA="$(cd "$(dirname "$0")/.." && pwd)"
PLIST="$HOME/Library/LaunchAgents/com.sina.mac-daily-cleanup.plist"
WRAPPER="$HOME/.sina/run-mac-daily-cleanup-mid.sh"
LOG="$HOME/.sina/mac-daily-cleanup-launchagent.log"

mkdir -p "$HOME/Library/LaunchAgents" "$HOME/.sina"

cat >"$WRAPPER" <<WRAP
#!/usr/bin/env bash
set -euo pipefail
SOURCEA="${SA}"
export PYTHONPATH="\$SOURCEA/scripts:\${PYTHONPATH:-}"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:\${PATH:-}"
HOUR=\$(date +%H)
if [[ "\$HOUR" -lt 8 || "\$HOUR" -gt 23 ]]; then
  exit 0
fi
bash "\$SOURCEA/scripts/mac-daily-cleanup-v1.sh" --mid --quiet >>"${LOG}" 2>&1
WRAP
chmod +x "$WRAPPER"

cat >"$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.sina.mac-daily-cleanup</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${WRAPPER}</string>
  </array>
  <key>StartInterval</key>
  <integer>7200</integer>
  <key>RunAtLoad</key>
  <true/>
  <key>StandardOutPath</key>
  <string>${LOG}</string>
  <key>StandardErrorPath</key>
  <string>${LOG}</string>
  <key>ThrottleInterval</key>
  <integer>300</integer>
</dict>
</plist>
PLIST

UID_N="$(id -u)"
launchctl bootout "gui/${UID_N}/com.sina.mac-daily-cleanup" 2>/dev/null || true
launchctl bootstrap "gui/${UID_N}" "$PLIST"
launchctl enable "gui/${UID_N}/com.sina.mac-daily-cleanup" 2>/dev/null || true
echo "OK: com.sina.mac-daily-cleanup installed (mid tier every 2h · 08:00–23:00)"
echo "Log: ${LOG}"
