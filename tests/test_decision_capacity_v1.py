#!/usr/bin/env python3
from __future__ import annotations
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.decision_capacity_v1 import close_capacity_loop  # noqa: E402
from human_tax_meter_v1 import record_human_tax_event  # noqa: E402


class DecisionCapacitySourceATests(unittest.TestCase):
    def test_close_loop(self):
        loop = close_capacity_loop(
            decision_class="EMAIL_DRAFT",
            event_types=["TOOL_CANCELLATION", "MANUAL_RESTART"],
            existing_policy_coverage=0.2,
        )
        self.assertIsNotNone(loop)
        assert loop is not None
        self.assertEqual(loop["incident_type"], "MISSING_DECISION_CAPACITY")

    def test_meter_emits_capacity(self):
        ev = record_human_tax_event(
            task_id="task_cap_unit",
            event_type="GOAL_RESTATEMENT",
            decision_class="WEBPAGE_CHANGE",
            prior_event_types=["SCOPE_RESTATEMENT", "MANUAL_CORRECTION"],
        )
        self.assertIn("decision_capacity", ev)
        self.assertEqual(ev["decision_capacity"]["work_status"], "FROZEN")


if __name__ == "__main__":
    unittest.main()
