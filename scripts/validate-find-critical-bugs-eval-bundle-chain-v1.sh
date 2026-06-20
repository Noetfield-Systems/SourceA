#!/usr/bin/env bash
# sa-0131–sa-0140 — eval-1b phase-s1 bundle wired in find_critical_bugs.py
set -euo pipefail
cd "$(dirname "$0")"

grep -q 'validate-eval-packet-v1b-phase-s1-t1-bundle-v1.sh' find_critical_bugs.py
grep -q 'Eval-1b phase-s1 T1 bundle' find_critical_bugs.py
test -x validate-eval-packet-v1b-phase-s1-t1-bundle-v1.sh

echo "OK: validate-find-critical-bugs-eval-bundle-chain-v1 · eval bundle critical wired (sa-0131–sa-0140)"
