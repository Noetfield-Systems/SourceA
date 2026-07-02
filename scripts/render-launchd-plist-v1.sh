#!/usr/bin/env bash
# render a launch plist template with the current user's ~/.sina paths
set -euo pipefail
template="$1"
dest="$2"
SINA_HOME="${HOME}/.sina"
sed "s|__SINA_HOME__|${SINA_HOME}|g" "$template" > "$dest"
