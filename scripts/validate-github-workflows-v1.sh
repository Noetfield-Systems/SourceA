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
  if [[ -x "${TOOLS}/actionlint" ]] && "${TOOLS}/actionlint" --version >/dev/null 2>&1; then
    export PATH="${TOOLS}:$PATH"
  else
    os="$(uname -s)"
    arch="$(uname -m)"
    case "${os}:${arch}" in
      Linux:aarch64|Linux:arm64) asset="actionlint_1.7.7_linux_arm64.tar.gz" ;;
      Linux:*) asset="actionlint_1.7.7_linux_amd64.tar.gz" ;;
      Darwin:arm64|Darwin:aarch64) asset="actionlint_1.7.7_darwin_arm64.tar.gz" ;;
      Darwin:*) asset="actionlint_1.7.7_darwin_amd64.tar.gz" ;;
      *) echo "FAIL: unsupported platform ${os}/${arch} for actionlint bootstrap" >&2; exit 1 ;;
    esac
    curl -sSfL "https://github.com/rhysd/actionlint/releases/download/v1.7.7/${asset}" \
      | tar -xz -C "$TOOLS" actionlint
    chmod +x "${TOOLS}/actionlint"
    export PATH="${TOOLS}:$PATH"
  fi
fi

command -v yamllint >/dev/null || { echo "FAIL: yamllint unavailable" >&2; exit 1; }
command -v actionlint >/dev/null || { echo "FAIL: actionlint unavailable" >&2; exit 1; }

echo "yamllint ${WF_DIR}"
yamllint -d relaxed "${WF_DIR}"/*.yml

echo "actionlint"
actionlint "${WF_DIR}"/*.yml

echo "OK: github workflows validated"
