#!/usr/bin/env bash
# validate-judge-alarm-h2-one-line-v1.sh — sa-0810 H1 one-line alarm vs full strip on H2 weekly
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-judge-alarm-h2-one-line-v1 — $*" >&2; exit 1; }

python3 - <<'PY' || fail "judge alarm H1 one-line vs H2 full batch"
import json
from pathlib import Path

strip_path = Path.home() / ".sina/judge-center/latest-alarm-strip-v1.json"
receipt_path = Path.home() / ".sina/judge-center/latest-run-receipt-v1.json"
reg_path = Path.home() / ".sina/h2-pending-registry-v1.json"
boot_path = Path("agent-control-panel/worker-hub/boot.json")

for p in (strip_path, receipt_path, reg_path, boot_path):
    if not p.is_file():
        raise SystemExit(f"missing {p}")

strip = json.loads(strip_path.read_text(encoding="utf-8"))
receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
reg = json.loads(reg_path.read_text(encoding="utf-8"))
boot = json.loads(boot_path.read_text(encoding="utf-8"))

if strip.get("schema") != "hub-judge-alarm-strip-v1":
    raise SystemExit(f"bad strip schema: {strip.get('schema')!r}")
if not strip.get("ok"):
    raise SystemExit("latest-alarm-strip ok=false")
if not receipt.get("ok"):
    raise SystemExit("latest-run-receipt ok=false")

headline = (strip.get("headline") or "").strip()
levels = strip.get("levels") or []
if len(levels) < 4:
    raise SystemExit(f"full batch requires P0-P3 levels, got {len(levels)}")

h1_judge = ((boot.get("daily_rooms") or {}).get("judge_center") or {}).get("headline") or ""
h1_judge = h1_judge.strip()
if h1_judge != headline:
    raise SystemExit("H1 boot daily_rooms judge headline != strip headline (must be one-line)")

reg_judge = (reg.get("judge_headline") or "").strip()
if reg_judge and reg_judge != headline:
    raise SystemExit("h2-pending-registry judge_headline != strip headline")

case_id = strip.get("case_id") or ""
if receipt.get("case_id") and receipt.get("case_id") != case_id:
    raise SystemExit(f"receipt case_id {receipt.get('case_id')!r} != strip {case_id!r}")

# H2 weekly-only: machines surface law — full batch lives logged; H1 alarm strip is one line
machines = Path("agent-control-panel/machines/index.html")
if not machines.is_file():
    raise SystemExit("missing machines/index.html")
text = machines.read_text(encoding="utf-8")
if "Run Judge" not in text or "Weekly review" not in text:
    raise SystemExit("H2 machines missing weekly judge run controls")

print(
    f"OK: validate-judge-alarm-h2-one-line-v1 · case_id={case_id} "
    f"headline={headline[:48]!r} · levels={len(levels)} · receipt ok"
)
PY

echo "OK: validate-judge-alarm-h2-one-line-v1 · sa-0810"
