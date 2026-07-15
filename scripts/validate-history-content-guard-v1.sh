#!/usr/bin/env bash
# History/content guard — patterns come ONLY from external policy (CI secret / env).
# In-repo blocklists with sensitive literals are forbidden.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

POLICY_FILE="${SOURCEA_HISTORY_GUARD_POLICY_FILE:-}"
POLICY_B64="${SOURCEA_HISTORY_GUARD_POLICY_B64:-}"
POLICY_URL="${SOURCEA_HISTORY_GUARD_POLICY_URL:-}"

if [[ -n "${POLICY_FILE}" && -f "${POLICY_FILE}" ]]; then
  :
elif [[ -n "${POLICY_B64}" ]]; then
  POLICY_FILE="$(mktemp)"
  printf '%s' "${POLICY_B64}" | base64 --decode > "${POLICY_FILE}"
  trap 'rm -f "${POLICY_FILE}"' EXIT
elif [[ -n "${POLICY_URL}" ]]; then
  POLICY_FILE="$(mktemp)"
  curl -fsSL "${POLICY_URL}" -o "${POLICY_FILE}"
  trap 'rm -f "${POLICY_FILE}"' EXIT
elif [[ "${CI:-}" == "true" || "${GITHUB_ACTIONS:-}" == "true" ]]; then
  echo "FAIL: SOURCEA history guard policy missing in CI (set SOURCEA_HISTORY_GUARD_POLICY_B64 secret)."
  exit 2
else
  echo "SKIP: no external history-guard policy configured (local founder session)."
  exit 0
fi

mapfile -t PATTERNS < <(grep -vE '^\s*(#|$)' "${POLICY_FILE}" || true)
if [[ ${#PATTERNS[@]} -eq 0 ]]; then
  echo "FAIL: history-guard policy file is empty."
  exit 2
fi

FAIL=0
for pat in "${PATTERNS[@]}"; do
  if git grep -I -n -E -- "${pat}" HEAD -- . \
    ':(exclude)node_modules' \
    ':(exclude)**/node_modules/**' \
    ':(exclude)package-lock.json' \
    ':(exclude)**/*.lock' \
    >/tmp/history-guard-hits.txt 2>/dev/null; then
    echo "FAIL: policy pattern matched:"
    echo "  /${pat}/"
    head -50 /tmp/history-guard-hits.txt
    FAIL=1
  fi
done

if [[ "${FAIL}" -ne 0 ]]; then
  exit 1
fi
echo "PASS: history content guard (external policy)."
exit 0
