#!/bin/bash
# Portfolio Mail — opens native .app (no Terminal). Rebuild: bash scripts/build-portfolio-mail-standalone-app-v1.sh
PM_APP="$HOME/Desktop/Portfolio Mail.app"
if [[ -d "$PM_APP" ]]; then
  exec /usr/bin/open "$PM_APP"
fi
cd "$HOME/Desktop/SourceA" || exit 1
exec bash "$HOME/Desktop/SourceA/scripts/build-portfolio-mail-standalone-app-v1.sh"
