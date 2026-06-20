"""Judge Center pattern SSOT — shared by audit and temporal layers."""
from __future__ import annotations

import re

STALE_PATTERNS = [
    (re.compile(r"\bscratch\b.*\bcanvas\b", re.I), "scratch_canvas_risk"),
    (re.compile(r"\bconfirm\b.*\bauto[- ]?send\b", re.I), "incident_028_class"),
    (re.compile(r"\bsa-0798\b.*\bhero\b|\bhero\b.*\bsa-0798\b", re.I), "incident_027_class"),
    (re.compile(r"\bopen\s+(\d+)\s+(questions|picks|forks)\b", re.I), "open_count_claim"),
    (re.compile(r"\bAUTO[- ]?RUN\b.*\b(live proof|founder objective|P0)\b", re.I), "autorun_p0_stale"),
    (re.compile(r"\bHub ▶ AUTO[- ]?RUN\b", re.I), "rail_a_hero_stale"),
    (re.compile(r"\bLive Rail A AUTO[- ]?RUN proof\b", re.I), "rail_a_hero_stale"),
    (re.compile(r"\bgovernance model is complete\b", re.I), "governance_complete_stale"),
    (re.compile(r"\bMaster Operating Tracker is the permanent founder command center\b", re.I), "tracker_as_ssot_stale"),
]

BAD_PATTERNS = [
    (re.compile(r"\bform is in your sidebar\b", re.I), "false_sidebar_success"),
    (re.compile(r"\blive-founder-decision-form\.canvas\b", re.I), "scratch_canvas_path"),
]

CHAT_ROLES: dict[str, str] = {
    "6245d9dd": "commercial_goal_specialist",
    "e54ddfa8": "governance_goal_specialist",
    "74f5ccab": "maintainer_2",
    "3369d11c": "monorepo_anchor",
    "58148ac9": "brain_executor",
    "a53f3fa1": "maintainer_1_retired",
}
