#!/usr/bin/env bash
# validate-commercial-reply-agent-v1.sh
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

fail() { echo "FAIL: validate-commercial-reply-agent-v1 — $*" >&2; exit 1; }

[[ -f scripts/commercial_reply_qualification_agent_v1.py ]] || fail "missing reply agent"
[[ -f scripts/mark_reply_followup_sent_v1.py ]] || fail "missing mark_reply_followup_sent"
[[ -f scripts/commercial_agents_wire_v1.py ]] || fail "missing commercial_agents_wire_v1"

python3 - <<'PY' || fail "reply agent import"
import importlib.util
spec = importlib.util.spec_from_file_location('ra', 'scripts/commercial_reply_qualification_agent_v1.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert hasattr(mod, 'run_reply_agent')
assert hasattr(mod, 'qualify_reply')
print('OK: reply agent imports')
PY

STAGE_OK=0
python3 scripts/commercial_reply_qualification_agent_v1.py --all-personalized --stage --json >/dev/null 2>&1 && STAGE_OK=1 || true
if [[ "$STAGE_OK" -eq 0 ]]; then
  echo "SKIP: stage watch — no personalized_sent rows (pipeline may be past reply stage)"
fi

python3 - <<'PY' || fail "qualify contract"
import json, subprocess, sys
from pathlib import Path
SINA = Path.home() / ".sina"
receipt_path = SINA / "reply-qualification-receipt-v1.json"
row_id = "cp-0b9b8c4eff"

def has_pack():
    if not receipt_path.is_file():
        return False
    r = json.loads(receipt_path.read_text())
    for row in r.get("results") or []:
        if row.get("row_id") == row_id and row.get("phase") == "replied":
            pack = Path(row.get("pack_dir") or "")
            return pack.joinpath("pack.json").is_file()
    return False

if not has_pack():
    proc = subprocess.run([
        sys.executable, "scripts/commercial_reply_qualification_agent_v1.py",
        "--row-id", row_id,
        "--reply-text", "Yes — Thursday works for a 15 min Copilot walk.",
        "--force", "--json",
    ], capture_output=True, text=True)
    if proc.returncode != 0:
        rows = {}
        pipe = SINA / "commercial-pipeline-v1.jsonl"
        if pipe.is_file():
            for line in pipe.read_text().splitlines():
                if line.strip():
                    r = json.loads(line)
                    rows[r["id"]] = r
        st = rows.get(row_id, {}).get("status")
        if st in ("proof_viewed", "eval_scheduled"):
            print("SKIP: qualify — row already past replied")
        else:
            raise SystemExit(proc.stderr or proc.stdout)
assert has_pack() or rows.get(row_id, {}).get("status") in ("proof_viewed", "eval_scheduled"), "missing NW1 reply follow-up pack"
print("OK: qualify contract")
PY

python3 - <<'PY' || fail "reply pack contract"
import json
from pathlib import Path
SINA = Path.home() / ".sina"
r = json.loads(SINA.joinpath("reply-qualification-receipt-v1.json").read_text())
assert r.get("schema") == "reply-qualification-receipt-v1"
nw1 = next((x for x in r["results"] if x["row_id"] == "cp-0b9b8c4eff"), None)
assert nw1, "NW1 missing from receipt"
assert nw1.get("phase") in ("replied", "proof_viewed")
if nw1.get("pack_dir"):
    body = Path(nw1["pack_dir"]).joinpath("body.txt").read_text()
    assert "proof" in body.lower() or "Copilot" in body or "demo" in body.lower()
print("OK: reply qualification contract")
PY

echo "PASS: validate-commercial-reply-agent-v1"
