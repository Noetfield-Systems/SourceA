#!/usr/bin/env python3
"""SourceA Phase A tests — NF-GOVERNED-WORK-PACKET-CONTROL-V1."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "fbe" / "lib"))

from execution_contract_v1 import (  # noqa: E402
    validate_goal_contract_envelope,
    map_cycle_to_work_packet_terminal,
)
from human_tax_meter_v1 import classify_owner_message, record_human_tax_event  # noqa: E402
from lib.governed_work_packet_v1 import (  # noqa: E402
    may_resume_after_incident,
    reject_false_done,
    reject_unnecessary_fanout,
)


class GovernedWorkPacketSourceATests(unittest.TestCase):
    def test_goal_contract_requires_authority_hash(self):
        errs = validate_goal_contract_envelope(
            {
                "goal_id": "g1",
                "owner": "founder",
                "goal_version": 1,
                "intent": "x",
                "acceptance_predicates": ["a"],
                "scope_allowlist": ["apps/x/**"],
                "forbidden_effects": [],
                "budgets": {
                    "max_attempts": 1,
                    "max_children": 1,
                    "max_minutes": 10,
                    "max_cost_usd": 1,
                    "max_human_tax_units": 5,
                },
                "evidence_required": ["receipt"],
                "stop_policy": "STOP_AND_INCIDENT",
            }
        )
        self.assertTrue(any("authority_hash" in e for e in errs))

    def test_terminals_map(self):
        self.assertEqual(
            map_cycle_to_work_packet_terminal("COMPLETE", has_artifact=True),
            "ACCEPTED_ARTIFACT",
        )
        self.assertEqual(
            map_cycle_to_work_packet_terminal("BLOCKED_WITH_REASON", has_artifact=False),
            "BOUNDED_FAILURE",
        )

    def test_human_tax_restatement(self):
        self.assertEqual(
            classify_owner_message("do the same page only again", prior_goal_intent="same page"),
            "GOAL_RESTATEMENT",
        )
        ev = record_human_tax_event(
            task_id="task_test",
            event_type="GOAL_RESTATEMENT",
            active_human_seconds=30,
        )
        self.assertEqual(ev["schema"], "noetfield.human_tax_event.v1")
        self.assertGreater(ev["htu_delta"], 0)

    def test_fanout_and_false_done_and_resume(self):
        self.assertEqual(reject_unnecessary_fanout(max_workers=1, requested_workers=5), "UNNECESSARY_FANOUT")
        self.assertEqual(reject_false_done(claim_done=True, evidence_valid=False), "FALSE_DONE_WITHOUT_EVIDENCE")
        self.assertFalse(may_resume_after_incident(prior_plan_hash="p1", new_plan_hash="p1"))
        self.assertTrue(may_resume_after_incident(prior_plan_hash="p1", new_plan_hash="p2"))


if __name__ == "__main__":
    unittest.main()
