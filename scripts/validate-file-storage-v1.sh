#!/usr/bin/env bash
# File storage governance — tier placement enforcement.
# Law: brain-os/system/FILE_STORAGE_GOVERNANCE_LOCKED_v1.md §6
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export ROOT
SINA="${HOME}/.sina"
TRACKER="$ROOT/brain-os/system/SOURCEA_MASTER_OPERATING_TRACKER_LOCKED_v1.md"

errors=0
warns=0

_fail() { echo "FAIL: $1" >&2; errors=$((errors + 1)); }
_warn() { echo "WARN: $1" >&2; warns=$((warns + 1)); }

echo "=== validate-file-storage-v1 ==="

# 1) LOCKED in forbidden Tier-1 paths; full law mirror in RESEARCH
while IFS= read -r f; do
  case "$f" in
    */scripts/*|*/agent-control-panel/*|*/.cursor/*)
      _fail "LOCKED outside brain-os in forbidden path: ${f#"$ROOT"/}"
      ;;
    */RESEARCH/*)
      if grep -q 'RESEARCH_INTAKE_AND_SAVE_LOCK_LOCKED' <<<"$f"; then
        if grep -q '^# RESEARCH INTAKE AND SAVE LOCK' "$f" 2>/dev/null && ! grep -q 'Tier-1 canonical pointer' "$f" 2>/dev/null; then
          _fail "full Tier-1 law copy in RESEARCH (MISS-003): ${f#"$ROOT"/}"
        fi
      fi
      ;;
  esac
done < <(find "$ROOT" -name '*_LOCKED_v1.md' -not -path '*/brain-os/*' 2>/dev/null)

legacy_root=$(find "$ROOT" -maxdepth 1 -name '*_LOCKED_v1.md' 2>/dev/null | wc -l | tr -d ' ')
if [[ "$legacy_root" -gt 0 ]]; then
  _warn "legacy root LOCKED count=$legacy_root (MISS-001 migration deferred)"
fi

# 2–3) RESEARCH _META.yaml + execution_authority
python3 <<'PY'
import sys
from pathlib import Path

root = Path(__import__("os").environ["ROOT"])
research = root / "RESEARCH" / "by_date"
missing = []
bad_auth = []
if research.is_dir():
    for meta in research.rglob("_META.yaml"):
        try:
            text = meta.read_text(encoding="utf-8", errors="replace")
            if "execution_authority: true" in text or "execution_authority: 'true'" in text:
                bad_auth.append(str(meta.relative_to(root)))
        except OSError:
            pass
    for d in research.rglob("*"):
        if not d.is_dir():
            continue
        files = [f for f in d.iterdir() if f.is_file() and f.name != "_META.yaml"]
        subdirs = [x for x in d.iterdir() if x.is_dir()]
        if files and not subdirs and not (d / "_META.yaml").is_file():
            missing.append(str(d.relative_to(root)))
if missing:
    for m in missing[:10]:
        print(f"FAIL: missing _META.yaml in {m}", file=sys.stderr)
    if len(missing) > 10:
        print(f"FAIL: ... and {len(missing) - 10} more", file=sys.stderr)
    sys.exit(1)
if bad_auth:
    for b in bad_auth:
        print(f"FAIL: _META execution_authority true: {b}", file=sys.stderr)
    sys.exit(1)
print("OK: RESEARCH _META.yaml scan")
PY

# 4) Runtime state .json in wrong Tier-1 trees (allow plan-registry + script schemas/fixtures)
while IFS= read -r j; do
  case "$j" in
    */brain-os/plan-registry/*|*/scripts/eval_packet*|*/scripts/execution_spine/*|*/scripts/fixtures/*|*/brain-os/demo/*)
      continue
      ;;
  esac
  _fail "runtime .json in Tier-1 code tree: ${j#"$ROOT"/}"
done < <(find "$ROOT/brain-os" "$ROOT/scripts" -name '*.json' -not -path '*/node_modules/*' 2>/dev/null)

# 5) manual_fallback: true without ASF trace
if [[ -f "$SINA/active-execution-rail-v1.json" ]]; then
  python3 <<'PY'
import json, sys
from pathlib import Path
p = Path.home() / ".sina/active-execution-rail-v1.json"
row = json.loads(p.read_text())
if row.get("manual_fallback") is True:
    trace = row.get("manual_fallback_trace_tag") or row.get("asf_trace_id") or ""
    if not trace:
        print("FAIL: manual_fallback true without ASF trace ID", file=sys.stderr)
        sys.exit(1)
print("OK: active-execution-rail manual_fallback policy")
PY
fi

# 6) Section 8 Tier-2 canonical paths must exist
python3 <<'PY'
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__import__("os").environ["ROOT"]) / "scripts"))
from execution_event_log_v1 import ensure_daily_events_file  # noqa: E402

ensure_daily_events_file(actor="validate-file-storage-v1")

sina = Path.home() / ".sina"
today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
tier2 = [
    sina / "runtime/execution.json",
    sina / "next-execution-pointer-v1.json",
    sina / "active-execution-rail-v1.json",
    sina / "brain/reconciled_decision.yaml",
    sina / "events" / f"{today}.jsonl",
]
for p in tier2:
    if not p.exists():
        print(f"FAIL: Section 8 pointer missing: {p}", file=sys.stderr)
        sys.exit(1)
print("OK: tracker Section 8 Tier-2 pointers exist")
PY

# 7) Unregistered ~/.sina/*.json — WARN (MISS-004)
python3 <<'PY'
import re, sys
from pathlib import Path

home = Path.home() / ".sina"
tracker = Path(__import__("os").environ["ROOT"]) / "brain-os/system/SOURCEA_MASTER_OPERATING_TRACKER_LOCKED_v1.md"
text = tracker.read_text(encoding="utf-8")
registered = set()
for m in re.finditer(r"~/.sina/([^`\\s]+)", text):
    registered.add(m.group(1).split("/")[-1])
core = {
    "next-execution-pointer-v1.json",
    "active-execution-rail-v1.json",
    "worker-prompt-inbox-v1.json",
    "healthy-drain-orchestrator-v1.json",
    "healthy-queue-state-v1.json",
    "healthy-queue-30-active.json",
    "goal1-lane-broker-v1.json",
    "cursor_entry_gate_receipt_v1.json",
    "eval_1b_ci_mode_v1.json",
    "eval_packet_v1b_report.json",
    "brain-goal1-validation-v1.json",
    "worker_turn_state_v1.json",
    "worker_round_report_v1.json",
}
registered |= core
jsons = sorted(home.glob("*.json"))
unreg = [p.name for p in jsons if p.name not in registered]
if unreg:
    print(f"WARN: ~/.sina unregistered json count={len(unreg)} (MISS-004)", file=sys.stderr)
if not (home / "next-execution-pointer-v1.json").is_file():
    print("FAIL: core runtime missing: next-execution-pointer-v1.json", file=sys.stderr)
    sys.exit(1)
print("OK: ~/.sina core runtime present")
PY

if [[ $errors -gt 0 ]]; then
  echo "validate-file-storage-v1 FAIL errors=$errors warns=$warns" >&2
  exit 1
fi
echo "OK: validate-file-storage-v1 (warns=$warns)"
exit 0
