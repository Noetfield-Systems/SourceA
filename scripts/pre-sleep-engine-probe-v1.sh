#!/usr/bin/env bash
# Probe all 4 pre-sleep engines — dry/live signal only, no boss queue advance.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
FAIL=0

probe() {
  local name="$1" ok="$2" detail="$3"
  if [[ "$ok" == "1" ]]; then
    echo "✅ $name — $detail"
  else
    echo "❌ $name — $detail"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== PRE-SLEEP ENGINE PROBE (4 engines) ==="

# 1 Worker
if grep -q 'pending=1' "$ROOT/.sina-loop/INBOX.md" 2>/dev/null; then
  hdr=$(head -1 "$ROOT/.sina-loop/INBOX.md")
  probe "Worker SourceA" 1 "INBOX ready — $hdr"
else
  probe "Worker SourceA" 0 "INBOX not pending — deliver may be needed"
fi

# 2 Claude Code CLI — prep lane in pre-sleep (boss ACT blocked until sleep — correct)
CLI=$(command -v claude 2>/dev/null || echo "")
PREP_COUNT=$(ls -1 "$HOME/.sina/sidecar/cli-prep/" 2>/dev/null | wc -l | tr -d ' ')
if [[ -n "$CLI" ]] && python3 scripts/sidecar_prep_cli_v1.py --json >/dev/null 2>&1; then
  probe "Claude Code CLI (prep)" 1 "binary=$CLI · prep lane OK · $PREP_COUNT plan(s) logged"
elif [[ -n "$CLI" ]]; then
  probe "Claude Code CLI (prep)" 0 "binary present · prep lane failed"
else
  probe "Claude Code CLI (prep)" 0 "claude binary not found"
fi
# Boss-queue CLI ACT must stay blocked in pre-sleep
if python3 scripts/operating_mode_enforce_v1.py --check-engine --role act --engine cli >/dev/null 2>&1; then
  probe "CLI boss ACT gate" 0 "should be INVALID in pre-sleep (ASF/Worker owns ACT)"
else
  probe "CLI boss ACT gate" 1 "correctly blocked until arm sleep"
fi

# 3 Claude API
if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
  if python3 scripts/sidecar_scout_api_v1.py --dry-run >/dev/null 2>&1; then
    probe "Claude API (scout)" 1 "ANTHROPIC_API_KEY set · scout dry-run OK"
  else
    probe "Claude API (scout)" 0 "key set but scout failed"
  fi
else
  probe "Claude API (scout)" 0 "ANTHROPIC_API_KEY not set"
fi

# 4 OpenRouter (probe — not boss queue on healthy pack)
OR_OUT=$(python3 -c "
import sys
sys.path.insert(0, 'scripts')
try:
    from eval_packet_v1b.runner import _openrouter_ready
    ok = _openrouter_ready()
    print('ready' if ok else 'blocked')
except Exception as e:
    print('error:' + str(e)[:80])
" 2>/dev/null || echo "error")
case "$OR_OUT" in
  ready)   probe "OpenRouter" 1 "credits/wiring OK (live eval arm available)" ;;
  blocked) probe "OpenRouter" 1 "honest BLOCKED — structural-only OK for healthy pack" ;;
  *)       probe "OpenRouter" 0 "$OR_OUT" ;;
esac

echo "=== PROBE failures=$FAIL ==="
exit "$FAIL"
