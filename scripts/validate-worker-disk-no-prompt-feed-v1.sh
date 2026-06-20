#!/usr/bin/env bash
# validate-worker-disk-no-prompt-feed-v1.sh — Worker SSOT disk must not steer Prompt feed / Sina Command
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"
ROOT="$(pwd)"

fail() { echo "FAIL: validate-worker-disk-no-prompt-feed-v1 — $*" >&2; exit 1; }

python3 <<'PY' || fail "worker disk steer check"
import json, re, sys
from pathlib import Path

SINA = Path.home() / ".sina"
ROOT = Path(".")

STALE = re.compile(
    r"Prompt\s+feed|prompt-feed|Sina\s+Command\s*→\s*Prompt|Confirm\s+auto-send",
    re.I,
)

def stale_in_strings(obj, path: str = "", *, skip_forbidden: bool = False) -> list[str]:
    hits: list[str] = []
    if isinstance(obj, dict):
        if obj.get("prompt_feed_lane") is not None:
            hits.append(f"{path}: prompt_feed_lane key (use next_steps_lane)")
        adv = obj.get("advisory")
        if adv in ("prompt_feed", "prompt_feed_live_mirror"):
            hits.append(f"{path}: advisory={adv!r} (use live_next10_mirror)")
        for k, v in obj.items():
            if skip_forbidden and k == "forbidden":
                continue
            if "agent_session_gate_receipt_v1.json" in path and k in (
                "violations",
                "warnings",
            ):
                continue
            hits.extend(
                stale_in_strings(v, f"{path}.{k}" if path else k, skip_forbidden=skip_forbidden)
            )
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits.extend(stale_in_strings(v, f"{path}[{i}]", skip_forbidden=skip_forbidden))
    elif isinstance(obj, str):
        if path.endswith((".tab", ".id")) and obj == "prompt-feed":
            return hits
        if STALE.search(obj):
            hits.append(f"{path}: {STALE.search(obj).group()!r}")
    return hits

def check_json(path: Path) -> list[str]:
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path}: read error {exc}"]
    skip_fb = path.name == "agent-memory-mirror-v1.json"
    errs = stale_in_strings(data, str(path), skip_forbidden=skip_fb)
    if path.name == "founder-missed-actions-card-v1.json":
        for row in data.get("items") or data.get("actions") or data.get("cards") or []:
            if isinstance(row, dict) and row.get("id") == "founder-prompt-feed":
                errs.append(f"{path}: id founder-prompt-feed (use founder-next-steps)")
    if path.name == "agent-memory-mirror-v1.json":
        inj = data.get("inject") or {}
        for v in inj.values():
            if isinstance(v, str) and STALE.search(v):
                errs.append(f"{path}: inject steer {STALE.search(v).group()!r}")
    prompt = str(data.get("prompt") or "")
    for key in ("inbox_after_ack", "last_pickup", "last_deliver"):
        block = data.get(key) or {}
        if isinstance(block, dict):
            prompt += str(block.get("prompt") or "")
    if prompt and STALE.search(prompt):
        errs.append(f"{path}: stale prompt cached")
    return errs

errs: list[str] = []
for rel in (
    "agent-memory-mirror-v1.json",
    "last-truth-bundle-v1.json",
    "agent_session_gate_receipt_v1.json",
    "worker-live-context-v1.json",
    "goal1-lane-broker-v1.json",
    "run-inbox-disk-truth-v1.json",
    "execution-lane-v1.json",
    "worker-prompt-inbox-v1.json",
    "live-ongoing-prompts-next-10-v1.json",
    "founder-missed-actions-card-v1.json",
):
    errs.extend(check_json(SINA / rel))

src = ROOT / "scripts/healthy_prompt_turn_v1.py"
if src.is_file() and STALE.search(src.read_text(encoding="utf-8")):
    errs.append(f"{src}: source still mentions Prompt feed")

guard = ROOT / "scripts/worker_steer_guard_v1.py"
if not guard.is_file():
    errs.append(f"{guard}: missing runtime steer guard")

if errs:
    for e in errs:
        print(e, file=sys.stderr)
    sys.exit(1)
print("OK: worker disk SSOT — no Prompt feed / Sina Command steer")
PY

echo "OK: validate-worker-disk-no-prompt-feed-v1"
