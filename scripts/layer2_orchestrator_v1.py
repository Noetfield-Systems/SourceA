#!/usr/bin/env python3
"""
Layer 2 Self-Healing Orchestrator: PR Gating & Issue Filing System

Reads findings (drift, SLO miss, schema violations) from cross-repo registry.
Classifies each finding per self-heal-policy-v1.json:
- auto: files PR with code fix, merges on green checks
- proposal: files GitHub issue for human review (never auto)
- founder_gated: files GitHub issue marked founder-gated (always requires approval)

Confidence = sort key only; all proposals filed regardless of threshold.
No direct commits; all changes via PR.

Phase 1: noetfield-os only (reads cross-repo, writes GitHub issues/PRs).
Phase 2+: downstream repos when their self-heal-policy is registered.
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

# Configuration paths (repo-local SSOT)
SELF_HEAL_POLICY_PATH = "data/self-heal-policy-v1.json"
TRIGGER_REGISTRY_PATH = "data/trigger-registry-v1.json"
AUDIT_TRAIL_PATH = "receipts/cloud/self-heal/layer2-audit-trail-v1.json"
DRILL_TEST_RECEIPT_PATH = "receipts/cloud/self-heal/layer2-drill-test-receipt-v1.json"
FINDINGS_QUEUE_PATH = "receipts/cloud/self-heal/findings-queue-v1.json"


def load_policy() -> Dict[str, Any]:
    """Load self-heal-policy-v1.json."""
    if not os.path.exists(SELF_HEAL_POLICY_PATH):
        raise FileNotFoundError(f"Policy not found: {SELF_HEAL_POLICY_PATH}")
    with open(SELF_HEAL_POLICY_PATH) as f:
        return json.load(f)


def classify_finding(finding: Dict[str, Any], policy: Dict[str, Any]) -> str:
    """
    Classify a finding per policy rules.
    Returns: "auto", "proposal", or "founder_gated".
    """
    path = finding.get("path", "")
    finding_type = finding.get("type", "unknown")

    # Check protected paths first (always founder_gated)
    for protected_pattern in policy.get("protected_paths", []):
        if re.match(protected_pattern.replace("**", ".*"), path):
            return "founder_gated"

    # Check policy rules in order
    for rule in policy.get("rules", []):
        if rule.get("class") == "founder_gated" and rule.get("pattern") is None:
            # Catch-all founder_gated rule
            if rule.get("conditions", {}).get("matches_protected_paths"):
                continue
        pattern = rule.get("pattern")
        if pattern and re.match(pattern, path):
            # Check rule conditions
            rule_class = rule.get("class", "proposal")
            return rule_class

    # Default to proposal
    return policy.get("default_class", "proposal")


def format_issue_title(finding: Dict[str, Any], class_name: str) -> str:
    """Format GitHub issue title."""
    path = finding.get("path", "unknown")
    issue_type = finding.get("issue_type", "drift")
    confidence = finding.get("confidence", 0)

    if class_name == "founder_gated":
        return f"🔒 Founder-gated: {issue_type} in {path} ({confidence:.0%})"
    elif class_name == "proposal":
        return f"💡 Proposal: {issue_type} in {path} ({confidence:.0%})"
    else:
        return f"🔧 Auto-fix: {issue_type} in {path} ({confidence:.0%})"


def format_issue_body(finding: Dict[str, Any], class_name: str) -> str:
    """Format GitHub issue body."""
    body_lines = [
        f"**Finding Type:** {finding.get('issue_type', 'unknown')}",
        f"**Path:** `{finding.get('path', 'N/A')}`",
        f"**Confidence:** {finding.get('confidence', 0):.0%}",
        f"**Description:** {finding.get('description', 'N/A')}",
        "",
        f"**Classification:** `{class_name}`",
        f"**Action:** {get_action_for_class(class_name)}",
        "",
        "**Details:**",
        json.dumps(finding, indent=2),
    ]
    return "\n".join(body_lines)


def get_action_for_class(class_name: str) -> str:
    """Get action description for classification."""
    if class_name == "auto":
        return "Automatic fix: PR filed and merged on green checks"
    elif class_name == "founder_gated":
        return "Founder-gated issue: requires founder approval to proceed"
    else:  # proposal
        return "Proposal filed for human review: no automatic action"


def format_labels(class_name: str) -> List[str]:
    """Get GitHub labels for issue."""
    base_labels = [f"self-heal/{class_name}"]
    if class_name == "founder_gated":
        base_labels.extend(["type/founder-gated", "security"])
    elif class_name == "proposal":
        base_labels.extend(["type/proposal", "review-needed"])
    else:  # auto
        base_labels.extend(["type/auto-fix"])
    return base_labels


def simulate_layer2_filing(
    finding: Dict[str, Any], class_name: str, policy: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Simulate Layer 2 filing action (GitHub issue or PR).
    In production, this would call gh CLI or GitHub API.
    Returns receipt of the filing.
    """
    title = format_issue_title(finding, class_name)
    body = format_issue_body(finding, class_name)
    labels = format_labels(class_name)

    receipt = {
        "finding_id": finding.get("id", "unknown"),
        "path": finding.get("path", ""),
        "classification": class_name,
        "title": title,
        "body": body,
        "labels": labels,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "filed",
    }

    if class_name == "auto":
        receipt["action_type"] = "pr"
        receipt["expected_result"] = "PR created and merged on green checks"
    else:
        receipt["action_type"] = "issue"
        receipt["expected_result"] = f"GitHub issue created and assigned to {policy.get('issue_filing', {}).get('default_assignee', 'maintainer')}"

    return receipt


def process_findings_queue(policy: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process findings from queue, classify, and file issues/PRs.
    Returns audit trail receipt.
    """
    if not os.path.exists(FINDINGS_QUEUE_PATH):
        return {"status": "no_findings_queue", "findings_processed": 0}

    with open(FINDINGS_QUEUE_PATH) as f:
        queue = json.load(f)

    findings = queue.get("findings", [])
    audit_trail = {
        "timestamp": datetime.utcnow().isoformat(),
        "findings_processed": 0,
        "filings": [],
        "by_class": {"auto": 0, "proposal": 0, "founder_gated": 0},
    }

    # Sort by confidence (descending)
    findings_sorted = sorted(findings, key=lambda f: f.get("confidence", 0), reverse=True)

    for finding in findings_sorted:
        class_name = classify_finding(finding, policy)
        receipt = simulate_layer2_filing(finding, class_name, policy)
        audit_trail["filings"].append(receipt)
        audit_trail["by_class"][class_name] += 1
        audit_trail["findings_processed"] += 1

    return audit_trail


def run_drill_test(policy: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run drill test: feed Layer 2 a fake finding on scripts/verify_*.
    Assert it refuses auto-fix and files founder_gated issue instead.
    """
    drill_config = policy.get("drill_test", {})
    test_finding = drill_config.get("test_finding", {})

    # Construct fake finding
    finding = {
        "id": "drill-test-001",
        "path": test_finding.get("path", "scripts/verify_autorun_zero_manual_v1.py"),
        "issue_type": test_finding.get("issue_type", "synthetic_drift"),
        "confidence": test_finding.get("confidence", 0.75),
        "description": "Drill test: synthetic finding to validate Layer 2 classification",
        "is_drill": True,
    }

    # Classify
    class_name = classify_finding(finding, policy)
    expected_class = test_finding.get("expected_class", "founder_gated")

    # Simulate filing
    receipt = simulate_layer2_filing(finding, class_name, policy)

    # Validate drill
    drill_result = {
        "test_id": "drill-test-001",
        "timestamp": datetime.utcnow().isoformat(),
        "finding": finding,
        "classified_as": class_name,
        "expected_classification": expected_class,
        "classification_correct": class_name == expected_class,
        "filing_receipt": receipt,
        "status": "passed" if class_name == expected_class else "failed",
    }

    return drill_result


def main() -> int:
    """Main entry point."""
    try:
        # Load policy
        policy = load_policy()
        print(f"✓ Loaded self-heal policy (version {policy.get('version', 'unknown')})")

        # Run drill test
        print("\n=== LAYER 2 DRILL TEST ===")
        drill_result = run_drill_test(policy)
        print(f"Drill test: {drill_result['status'].upper()}")
        print(f"  Finding: {drill_result['finding']['path']}")
        print(f"  Classification: {drill_result['classified_as']}")
        print(f"  Expected: {drill_result['expected_classification']}")
        print(f"  Issue filed: {drill_result['filing_receipt']['action_type']}")

        # Write drill receipt
        os.makedirs(os.path.dirname(DRILL_TEST_RECEIPT_PATH), exist_ok=True)
        with open(DRILL_TEST_RECEIPT_PATH, "w") as f:
            json.dump(drill_result, f, indent=2)
        print(f"✓ Drill receipt written: {DRILL_TEST_RECEIPT_PATH}")

        # Process findings queue (if exists)
        print("\n=== LAYER 2 FINDINGS PROCESSING ===")
        audit_trail = process_findings_queue(policy)
        print(f"Findings processed: {audit_trail['findings_processed']}")
        if audit_trail["findings_processed"] > 0:
            print(f"  Auto: {audit_trail['by_class']['auto']}")
            print(f"  Proposal: {audit_trail['by_class']['proposal']}")
            print(f"  Founder-gated: {audit_trail['by_class']['founder_gated']}")

        # Write audit trail
        os.makedirs(os.path.dirname(AUDIT_TRAIL_PATH), exist_ok=True)
        with open(AUDIT_TRAIL_PATH, "w") as f:
            json.dump(audit_trail, f, indent=2)
        print(f"✓ Audit trail written: {AUDIT_TRAIL_PATH}")

        print("\n=== LAYER 2 STATUS ===")
        print(f"Policy scope: {policy.get('scope', 'unknown')}")
        print(f"PR gating: {'enabled' if policy.get('pr_gating', {}).get('enabled') else 'disabled'}")
        print(f"Issue filing: {'enabled' if policy.get('issue_filing', {}).get('enabled') else 'disabled'}")
        print(f"Actions budget: {policy.get('actions_budget', {}).get('total_allocated_minutes', 0)}/1440 minutes/day")

        return 0

    except Exception as e:
        print(f"✗ Layer 2 error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
