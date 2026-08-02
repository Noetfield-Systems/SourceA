#!/usr/bin/env bash
# validate-brain-disk-no-prompt-feed-v1.sh — Brain SSOT disk must not steer Prompt feed / Sina Command
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"
ROOT="$(pwd)"

fail() { echo "FAIL: validate-brain-disk-no-prompt-feed-v1 — $*" >&2; exit 1; }

python3 <<'PY' || fail "brain disk steer check"
import json, re, sys
from pathlib import Path

SINA = Path.home() / ".sina"
ROOT = Path(".")

STALE = re.compile(
    r"Prompt\s+feed|prompt-feed|Sina\s+Command\s*→\s*Prompt|Confirm\s+auto-send",
    re.I,
)

def stale_in_strings(obj, path: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("inject",) and isinstance(v, dict):
                for vv in v.values():
                    if isinstance(vv, str) and STALE.search(vv):
                        hits.append(f"{path}.{k}: {STALE.search(vv).group()!r}")
            hits.extend(stale_in_strings(v, f"{path}.{k}" if path else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits.extend(stale_in_strings(v, f"{path}[{i}]"))
    elif isinstance(obj, str):
        if path.endswith(".tab") and obj == "prompt-feed":
            return hits
        if STALE.search(obj):
            hits.append(f"{path}: {STALE.search(obj).group()!r}")
    return hits

errs: list[str] = []
for rel in (
    "brain-live-context-v1.json",
    "brain-current-action-v1.json",
    "brain-goal1-validation-v1.json",
    "brain-fast-startup-v1.json",
    "governance-brain-wire-v1.json",
    "agent-live-surfaces-v1.json",
    "brain/BRAIN_LIVE_SURFACES_v1.json",
):
    p = SINA / rel
    if not p.is_file():
        if rel == "brain-live-context-v1.json":
            errs.append(f"{p}: missing — run brain_live_context_v1.py")
        continue
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errs.append(f"{p}: read error {exc}")
        continue
    errs.extend(stale_in_strings(data, str(p)))

gate = SINA / "agent_session_gate_receipt_v1.json"
if gate.is_file():
    try:
        data = json.loads(gate.read_text(encoding="utf-8"))
        if data.get("role") == "brain":
            errs.extend(stale_in_strings(data.get("inject") or {}, str(gate) + ".inject"))
            for key in ("founder_close_line", "mandatory_next", "founder_line"):
                val = str(data.get(key) or "")
                if val and STALE.search(val):
                    errs.append(f"{gate}: {key} stale steer")
    except (OSError, json.JSONDecodeError):
        pass

ctx = SINA / "brain-live-context-v1.json"
if ctx.is_file():
    data = json.loads(ctx.read_text())
    if "RUN INBOX" not in str(data.get("founder_close_line") or ""):
        errs.append(f"{ctx}: founder_close_line missing RUN INBOX positive path")
    if "Prompt feed" in str(data.get("text_block") or ""):
        errs.append(f"{ctx}: text_block mentions Prompt feed")

if not (ROOT / "scripts/brain_live_context_v1.py").is_file():
    errs.append("missing scripts/brain_live_context_v1.py")

if errs:
    for e in errs:
        print(e, file=sys.stderr)
    sys.exit(1)
print("OK: brain disk SSOT — no Prompt feed / Sina Command steer")
PY

echo "OK: validate-brain-disk-no-prompt-feed-v1"
