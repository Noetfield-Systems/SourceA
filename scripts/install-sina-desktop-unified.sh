#!/bin/zsh
# Install Sina Command + mini-apps on Desktop as proper .app bundles with icons.
set -euo pipefail
SA="$(cd "$(dirname "$0")/.." && pwd)"
exec "$SA/scripts/install-sina-macos-apps.sh"
