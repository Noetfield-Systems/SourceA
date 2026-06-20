#!/usr/bin/env bash
# validate-essay-mark-best-v1.sh — sa-0799 mark_best actor+attestation contract
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
from pathlib import Path

from agent_essay_discourse import (
    BEST_PATH,
    ensure_mark_best_attestation,
    essay_discourse_payload,
    handle_essay_action,
    mark_best_essay,
)

src = Path("agent_essay_discourse.py").read_text(encoding="utf-8")
assert "sa-0799" in src or "MARK_BEST_ACTORS" in src, "sa-0799 marker missing"

contract = (essay_discourse_payload().get("mark_best_contract") or {})
assert contract.get("requires_attestation") is True, contract
assert set(contract.get("actors") or []) == {"founder", "maintainer"}, contract
assert contract.get("not_fleet_verify") is True, contract

deny = mark_best_essay(subject="governance-drift-detection", essay_id="ESSAY-fake")
assert deny.get("ok") is False, deny
assert deny.get("code") == "mark_best_actor_required", deny

deny2 = handle_essay_action({"action": "mark_best", "subject": "x", "essay_id": "y", "actor": "founder"})
assert deny2.get("ok") is False, deny2
assert deny2.get("code") == "mark_best_attestation_required", deny2

deny3 = mark_best_essay(
    subject="governance-drift-detection",
    essay_id="ESSAY-fake",
    actor="founder",
    attestation="bad-token",
)
assert deny3.get("ok") is False, deny3
assert deny3.get("code") == "mark_best_attestation_invalid", deny3

deny4 = mark_best_essay(
    subject="governance-drift-detection",
    essay_id="ESSAY-fake",
    actor="executor",
    attestation="x",
)
assert deny4.get("ok") is False, deny4

ed = essay_discourse_payload()
topics = ed.get("topics") or []
topic = next((t for t in topics if (t.get("essays") or [])), None)
if topic:
    essay_id = topic["essays"][0]["id"]
    subject = topic.get("subject") or topic.get("subject_norm")
    token = ensure_mark_best_attestation()["token"]
    had_best = BEST_PATH.read_text(encoding="utf-8") if BEST_PATH.is_file() else None
    try:
        ok = mark_best_essay(subject=subject, essay_id=essay_id, actor="maintainer", attestation=token)
        assert ok.get("ok") is True, ok
        assert ok.get("marked_by") == "maintainer", ok
        assert BEST_PATH.is_file(), "best-by-subject.json must exist after mark"
        best_map = json.loads(BEST_PATH.read_text(encoding="utf-8"))
        assert isinstance(best_map, dict), best_map
        sn = ok.get("subject_norm")
        assert best_map.get(sn) == essay_id, best_map
    finally:
        if had_best is None:
            BEST_PATH.unlink(missing_ok=True)
        else:
            BEST_PATH.write_text(had_best, encoding="utf-8")

print("OK: validate-essay-mark-best-v1 · actor+attestation contract enforced (sa-0799)")
PY
