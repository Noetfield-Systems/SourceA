#!/usr/bin/env bash
# Pre-push gate: yamllint + actionlint on .github/workflows/*.yml
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WF_DIR="${ROOT}/.github/workflows"
TOOLS="${ROOT}/scripts/.tools"
PY="${PYTHON:-/usr/bin/python3}"

mkdir -p "$TOOLS"

if ! command -v yamllint >/dev/null 2>&1; then
  "$PY" -m pip install --quiet --user yamllint 2>/dev/null || "$PY" -m pip install --quiet yamllint
  export PATH="$($PY -m site --user-base 2>/dev/null)/bin:$PATH"
fi

if ! command -v actionlint >/dev/null 2>&1; then
  if [[ ! -x "${TOOLS}/actionlint" ]]; then
    arch="$(uname -m)"
    case "$arch" in
      arm64|aarch64) asset="actionlint_1.7.7_darwin_arm64.tar.gz" ;;
      *) asset="actionlint_1.7.7_darwin_amd64.tar.gz" ;;
    esac
    curl -sSfL "https://github.com/rhysd/actionlint/releases/download/v1.7.7/${asset}" \
      | tar -xz -C "$TOOLS" actionlint
  fi
  export PATH="${TOOLS}:$PATH"
fi

command -v yamllint >/dev/null || { echo "FAIL: yamllint unavailable" >&2; exit 1; }
command -v actionlint >/dev/null || { echo "FAIL: actionlint unavailable" >&2; exit 1; }

echo "yamllint ${WF_DIR}"
yamllint -d relaxed "${WF_DIR}"/*.yml

echo "actionlint"
actionlint "${WF_DIR}"/*.yml

echo "OK: github workflows validated"
