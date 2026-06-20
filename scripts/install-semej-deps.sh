#!/usr/bin/env bash
# One-time SEMEJ setup: Playwright + Chromium driver for CDP attach.
set -euo pipefail
echo "Installing Playwright for SEMEJ…"
python3 -m pip install --user playwright
python3 -m playwright install chromium
echo "Done. Next: run semej-start-chrome.sh and sign in to your AI sites in Chrome."
