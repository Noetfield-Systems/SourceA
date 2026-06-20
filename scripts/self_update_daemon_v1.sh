#!/bin/zsh
# Runs once to update daemon plist + install dashboard daemon
source ~/.zshrc 2>/dev/null
cd ~/Desktop/SourceA

API_KEY=$(grep 'ANTHROPIC_API_KEY' ~/.zshrc 2>/dev/null | head -1 | sed "s/.*ANTHROPIC_API_KEY[='\"] *['\"]//; s/['\"].*//; s/export //")

# Update worker plist to use dispatcher
sed "s|__ANTHROPIC_API_KEY_PLACEHOLDER__|${API_KEY}|g" \
    ~/Desktop/SourceA/scripts/com.sourcea.autorun-worker.plist \
    > ~/Library/LaunchAgents/com.sourcea.autorun-worker.plist

# Install dashboard daemon
cp ~/Desktop/SourceA/scripts/com.sourcea.dashboard.plist \
   ~/Library/LaunchAgents/com.sourcea.dashboard.plist

# Reload both
launchctl unload ~/Library/LaunchAgents/com.sourcea.autorun-worker.plist 2>/dev/null
launchctl load   ~/Library/LaunchAgents/com.sourcea.autorun-worker.plist
launchctl unload ~/Library/LaunchAgents/com.sourcea.dashboard.plist 2>/dev/null
launchctl load   ~/Library/LaunchAgents/com.sourcea.dashboard.plist

# Remove self
rm -f ~/Desktop/SourceA/scripts/self_update_daemon_v1.sh
echo "[$(date)] self_update done" >> ~/.sina/autorun-worker.log
