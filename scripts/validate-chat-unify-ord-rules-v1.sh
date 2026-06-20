#!/usr/bin/env bash
# validate-chat-unify-ord-rules-v1 — ORD rules engine smoke (bad-agent + charter fixtures)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FAIL=0

fail() { echo "✗ $1"; FAIL=1; }
pass() { echo "✓ $1"; }

RULES="$ROOT/data/chat-unify-ord-claim-rules-v1.json"
[[ -f "$RULES" ]] || { fail "missing rules JSON"; exit 1; }

python3 - <<PY || { fail "rules JSON structure"; exit 1; }
import json
from pathlib import Path
ROOT = Path("$ROOT")
rules = json.loads((ROOT / "data/chat-unify-ord-claim-rules-v1.json").read_text())
assert rules.get("schema") == "chat-unify-ord-claim-rules-v1"
ver = rules.get("version", "0")
parts = [int(x) for x in ver.split(".")]
assert parts[0] >= 1 and (parts[0] > 1 or parts[1] >= 2)
assert len(rules.get("claim_types") or []) >= 14
assert len(rules.get("consistency_rules") or []) >= 8
print("rules", ver, "types", len(rules["claim_types"]), "consistency", len(rules["consistency_rules"]))
PY
pass "rules JSON loads"

export SINA_SOURCE_A="$ROOT"
cd "$ROOT/scripts"
python3 - <<'PY' || exit 1
import json, sys
from pathlib import Path

from chat_ord_loop_v1 import LOOP_VERSION, STAGE_ORDER, run_ord_stage
from chat_ord_atoms_v1 import ATOMS_VERSION
from chat_ord_claim_rules_v1 import RULES_VERSION

print("ord", LOOP_VERSION, "atoms", ATOMS_VERSION, "rules_py", RULES_VERSION)
parts = [int(x) for x in LOOP_VERSION.split(".")]
assert parts[0] >= 0 and (parts[0] > 0 or parts[1] >= 6), f"ORD {LOOP_VERSION} < 0.6"

BAD = """Batch 4 is APPROVED — run execute-batch-4-v1.sh now.
eval-1b PASS green 100% all validators zero drift wired.
/api/foo-bar-baz returns 200.
I fixed scripts/foo.py committed.
"""

def run_all(draft, rid):
    r = None
    for stage in STAGE_ORDER:
        r = run_ord_stage(stage, draft=draft, run_id=rid, write_receipt=False)
        if not r.get("ok"):
            print("FAIL", stage, r.get("message"))
            sys.exit(1)
    return r

r = run_all(BAD, "validate-bad-agent")
stats = r.get("stats") or {}
assert stats.get("verified", -1) == 0, stats
assert stats.get("disk_mismatch", 0) >= 1, stats
dec = r.get("decision") or {}
assert dec.get("action") in ("block", "escalate", "retry"), dec
print("bad-agent ok verified=0 action=", dec.get("action"))

charter_path = Path.home() / ".sina/chat-unify-kernels/ord-8e0a3f1fe53b.json"
if charter_path.is_file():
    draft = json.loads(charter_path.read_text()).get("raw_input", "")
    if draft:
        r2 = run_all(draft, "validate-charter")
        s2 = r2.get("stats") or {}
        assert s2.get("opinion_count", 0) > 0, s2
        actions = (r2.get("stages") or {}).get("report", {}).get("verify_actions") or []
        assert len(actions) > 0, "no verify_actions"
        parsed = (r2.get("stages") or {}).get("parse", {}).get("parsed") or {}
        act_list = parsed.get("actions") or []
        assert not any("URL\tStatus" in a for a in act_list), act_list[:3]
        print("charter ok opinion=", s2.get("opinion_count"), "verify_actions=", len(actions))
    else:
        print("charter kernel empty — skip")
else:
    print("charter kernel missing — skip charter fixture")
PY

if [[ "$FAIL" -eq 0 ]]; then
  pass "ORD pipeline fixtures"
  echo "VALIDATE PASS: chat-unify-ord-rules-v1"
else
  echo "VALIDATE FAIL"
  exit 1
fi
