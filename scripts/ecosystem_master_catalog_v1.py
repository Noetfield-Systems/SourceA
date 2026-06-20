#!/usr/bin/env python3
"""Master catalog payload — everything on one page for hub + agents."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from governance_paths_v1 import AUTHORITY_INDEX

INDEX = AUTHORITY_INDEX
ANTI_STALE = ROOT / "scripts/validate-anti-staleness-bundle-v1.sh"
INTEGRITY = ROOT / "scripts/validate-integrity-batch-2-v1.sh"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _authority_rows() -> list[dict]:
    if not INDEX.is_file():
        return []
    text = INDEX.read_text(encoding="utf-8", errors="replace")
    rows = []
    for line in text.splitlines():
        if not line.startswith("| `"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4 or parts[1] in ("ID", "----"):
            continue
        rid = parts[1].strip("` ")
        doc = parts[2].strip("` ")
        if doc.endswith(".md") or "_LOCKED" in doc:
            rows.append({"id": rid, "doc": doc})
    return rows


_A53F3FA1_JSONL = (
    Path.home()
    / ".cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiDataBase/agent-transcripts"
    / "a53f3fa1-081c-4373-bc55-76feb501a61d/a53f3fa1-081c-4373-bc55-76feb501a61d.jsonl"
)

MEGA_CHAT_ANCHORS: list[dict[str, str]] = [
    {
        "id": "ECOSYSTEM",
        "workspace": "SinaaiDataBase",
        "transcript_id": "a53f3fa1-081c-4373-bc55-76feb501a61d",
        "role": "Narrative advisor · T0–T12 archive — retired from active repo list · search only",
        "jsonl": _A53F3FA1_JSONL,
    },
    {
        "id": "MAINTAINER_1",
        "workspace": "SinaaiDataBase",
        "transcript_id": "a53f3fa1-081c-4373-bc55-76feb501a61d",
        "role": "End of service 2026-06-11 · integrity playbook · form v2 · narrative advisor only",
        "jsonl": _A53F3FA1_JSONL,
        "cursor_status": "retired",
        "successor_id": "MAINTAINER_2",
        "shared_transcript_with": "ECOSYSTEM",
    },
    {
        "id": "MAINTAINER_2",
        "workspace": "SinaaiDataBase",
        "transcript_id": "74f5ccab-d080-41a2-9f6d-b7c37c9aadc5",
        "role": "Active maintainer · hub ops · anti-staleness · RT LIVE · bowl",
        "jsonl": (
            Path.home()
            / ".cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiDataBase/agent-transcripts"
            / "74f5ccab-d080-41a2-9f6d-b7c37c9aadc5/74f5ccab-d080-41a2-9f6d-b7c37c9aadc5.jsonl"
        ),
    },
    {
        "id": "MONOREPO",
        "workspace": "SinaaiMonoRepo",
        "transcript_id": "3369d11c-791f-48dd-98cd-0a62c123a98c",
        "role": "SSOT lock · mx queue · runtime E2E · agent-auto",
        "jsonl": (
            Path.home()
            / ".cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiMonoRepo/agent-transcripts"
            / "3369d11c-791f-48dd-98cd-0a62c123a98c/3369d11c-791f-48dd-98cd-0a62c123a98c.jsonl"
        ),
    },
    {
        "id": "MONOREPO_PRIOR",
        "workspace": "SinaaiMonoRepo",
        "transcript_id": "720ee790-74f3-42ea-916f-1ab24e920a90",
        "role": "Predecessor — Architecture Replay (read with MONOREPO)",
        "jsonl": (
            Path.home()
            / ".cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiMonoRepo/agent-transcripts"
            / "720ee790-74f3-42ea-916f-1ab24e920a90/720ee790-74f3-42ea-916f-1ab24e920a90.jsonl"
        ),
    },
]


def _count_transcript(path: Path) -> dict:
    if not path.is_file():
        return {"exists": False, "founder_prompts": 0, "assistant_lines": 0, "total_records": 0}
    user = assistant = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            import json as _json

            o = _json.loads(line)
        except Exception:
            continue
        if o.get("role") == "user":
            user += 1
        elif o.get("role") == "assistant":
            assistant += 1
    st = path.stat()
    return {
        "exists": True,
        "founder_prompts": user,
        "assistant_lines": assistant,
        "total_records": user + assistant,
        "size_mb": round(st.st_size / 1048576, 2),
        "mtime_utc": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
    }


AGENT_DOMAIN_MATRIX: list[dict] = [
    {
        "domain": "governance",
        "skill": "sina-conscious-recovery",
        "gate": "scripts/cursor_entry_gate.py",
        "proof": "scripts/validate-integrity-batch-2-v1.sh",
        "reference_proven": "governance_propagation_cascade_v1.py + ~/.sina/governance-propagation-receipt-v1.json",
        "reference_market": "REF_CONSTELLATION L6 — ThinkFleet Shield tone",
    },
    {
        "domain": "technical",
        "skill": "sina-sourcea-worker",
        "gate": "scripts/goal1_lane_broker.py worker-submit",
        "proof": "scripts/cursor_entry_gate.py --role worker",
        "reference_proven": "goal1-lane-broker-events.jsonl + WORKER_ROUND_REPORT",
        "reference_market": "REF_CONSTELLATION L3 — Temporal durability pattern",
    },
    {
        "domain": "vc",
        "skill": "sina-research-intake",
        "gate": "SOURCEA_EXTERNAL_ADVISOR_CONTRACT_LOCKED_v3.md",
        "proof": "agent-research evaluate scores",
        "reference_proven": "investor/ folder + L1 classify hold",
        "reference_market": "REF_CONSTELLATION §5 — outcome receipts",
    },
    {
        "domain": "ui",
        "skill": "anti-staleness-machine",
        "gate": "validate-anti-staleness-bundle-v1.sh",
        "proof": "scripts/validate-serve-panel-build-v1.sh",
        "reference_proven": "hub built_at + HUB_SOURCE_UI_ALIGNMENT",
        "reference_market": "REF_CONSTELLATION §7 — Stripe docs zone",
    },
    {
        "domain": "debug",
        "skill": "truth-projection",
        "gate": "scripts/find_critical_bugs.py",
        "proof": "scripts/validate-anti-staleness-bundle-v1.sh",
        "reference_proven": "SOURCEA_DISK_TRUTH_E2E_MATRIX RT rows",
        "reference_market": "REF_CONSTELLATION L1 — Datadog when multi-service",
    },
    {
        "domain": "research",
        "skill": "sina-research-intake",
        "gate": "scripts/prompt_feasibility_gate.py",
        "proof": "~/.sina/agent-research/items.jsonl stages",
        "reference_proven": "META_REASONING L9 evaluate before promote",
        "reference_market": "GPT paste = EXTERNAL_CRITIC L1 only",
    },
    {
        "domain": "portfolio",
        "skill": "sina-trustfield",
        "gate": "MANDATORY_CHAT_HANDOFF_INDEX",
        "proof": "lane verify + fleet registry",
        "reference_proven": "AGENT_FLEET_REGISTRY.json sessions",
        "reference_market": "REF_CONSTELLATION — Sierra CX lane",
    },
]


def mega_chat_anchors_payload() -> list[dict]:
    out: list[dict] = []
    for row in MEGA_CHAT_ANCHORS:
        jsonl = Path(row["jsonl"])
        counts = _count_transcript(jsonl)
        payload: dict = {
            "id": row["id"],
            "workspace": row["workspace"],
            "transcript_id": row["transcript_id"],
            "role": row["role"],
            "path": str(jsonl),
            "counts": counts,
            "projection": "RT",
        }
        for opt in ("cursor_status", "successor_id", "shared_transcript_with"):
            if row.get(opt):
                payload[opt] = row[opt]
        out.append(payload)
    return out


def _scripts_from_bundle(path: Path) -> list[str]:
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    return re.findall(r'"validate-[^"]+\.sh"', text)


def catalog_payload() -> dict:
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from authority_root_coverage_audit import audit  # noqa: WPS433
    from governance_completion_backlog_audit import audit as backlog  # noqa: WPS433

    coverage = audit()
    open_items = backlog()
    validators = sorted(
        set(_scripts_from_bundle(ANTI_STALE) + _scripts_from_bundle(INTEGRITY))
    )
    all_validate = sorted(p.name for p in (ROOT / "scripts").glob("validate-*.sh"))

    return {
        "ok": True,
        "built_at": _now(),
        "law_path": "SOURCEA_ECOSYSTEM_MASTER_CATALOG_LOCKED_v1.md",
        "counts": {
            "authority_rows": len(_authority_rows()),
            "root_locked_files": coverage.get("total", 0),
            "coverage_tiers": coverage.get("counts", {}),
            "validators_bundled": len(validators),
            "validators_total_scripts": len(all_validate),
            "backlog_open": open_items.get("total", 0),
        },
        "this_chat_thread": [
            {"id": "LAW-PURITY", "artifact": "SINA_AUTHORITY_INDEX_MAP §LAW PURITY"},
            {"id": "GOV-UNIFY", "artifact": "SOURCEA_AUTHORITY_REGISTRY_GOV_UNIFY_BATCH_2026-06-11"},
            {"id": "PHASE2", "artifact": "SOURCEA_PHASE2_INTEGRITY_PICK_RECEIPT_2026-06-11"},
            {"id": "TERMINOLOGY", "artifact": "SOURCEA_FOUNDER_MACHINE_TERMINOLOGY_DICTIONARY"},
            {"id": "LIVE-GOV-BP", "artifact": "SOURCEA_LIVE_GOVERNANCE_BIG_PICTURE"},
            {"id": "SSOT-FOUNDATION", "artifact": "SOURCEA_SSOT_FOUNDATION_WRITING_GUIDE"},
            {"id": "CASCADE", "artifact": "governance_propagation_cascade_v1.py"},
            {"id": "BACKLOG-E19", "artifact": "validate-governance-completion-backlog-v1.sh"},
            {"id": "CATALOG", "artifact": "SOURCEA_ECOSYSTEM_MASTER_CATALOG"},
            {"id": "LOST-LINK", "artifact": "SOURCEA_LOST_LINK_RECOVERY_ETHICS"},
            {"id": "FROZEN-REVIVAL", "artifact": "SOURCEA_FROZEN_ARCHIVE_REVIVAL_AUDIT"},
            {"id": "TRUTH-TREE", "artifact": "LIVE_GOV_BP §2b + SYSTEM_MAP_TREE §11"},
            {"id": "CONSCIOUS-RECOVERY-SKILL", "artifact": "agent-skills/shared/conscious-recovery/SKILL.md"},
            {"id": "LOST-LINK-ETHICS", "artifact": "SOURCEA_LOST_LINK_RECOVERY_ETHICS"},
            {"id": "FROZEN-REVIVAL", "artifact": "SOURCEA_FROZEN_ARCHIVE_REVIVAL_AUDIT"},
            {"id": "TRUTH-TREE-LOCK", "artifact": "LIVE_GOV_BP §2b + SYSTEM_MAP_TREE §11"},
            {"id": "TODAY-CLOSEOUT", "artifact": "SOURCEA_TODAY_SESSION_UNIFIED_CLOSEOUT_RECEIPT_2026-06-11"},
            {"id": "CROSS-EXPAND-11", "artifact": "CROSS_DOC_LINKAGE §13"},
            {"id": "LIVE-FOUNDER-FORM", "artifact": "SOURCEA_LIVE_FOUNDER_DECISION_FORM"},
            {"id": "FOUNDER-MSG-NORM", "artifact": "SOURCEA_FOUNDER_MESSAGE_NORMALIZATION"},
            {"id": "CROSS-EXPAND-12", "artifact": "CROSS_DOC_LINKAGE §14"},
        ],
        "live_founder_decision_form_path": "SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md",
        "mega_chat_anchors": mega_chat_anchors_payload(),
        "agent_domain_matrix": AGENT_DOMAIN_MATRIX,
        "gpt_vnext_gap": {
            "have": [
                "event_append: governance-event-spine-v1.1.jsonl + agent-governance-events.jsonl",
                "router: goal1_lane_broker + governance_propagation_cascade (global→domain pattern in golden rule)",
                "graph: knowledge_edges law→skill→agent→artifact→projection",
                "materializer: build-sina-command-panel + align_command_data_ui + ecosystem_master_catalog JSON",
                "projection_disposable: canonical/runtime split + validate-hub-projection-disposable-v1.sh",
                "golden_rule: brain-os/law/GOVERNANCE_RUNTIME_GOLDEN_RULE_LOCKED_v1.md",
                "g4_replay: governance_replay_worker_v1.py (context-aware dry-run + --resume)",
                "monitor: monitor :13021 + agent_truth_bundle",
                "enforcement: 279 validate scripts + AS bundle",
                "token_compress: MANDATORY_READ by role + skill + row lookup",
                "self_heal: governance_self_heal_daemon_v1.py (G7) + s10-eternal-loop + conscious-recovery",
            ],
            "gap": [
                "agents_never_write_files — Worker still writes (scoped by lane law)",
                "hub_full_rebuild_RT — still LAG minutes",
            ],
            "truth_bundle_fix": [
                "repair_sourcea_registry_v1.py",
                "REGISTRY.json 1000 plans restored",
                "validate-truth-bundle-registry-v1.sh",
            ],
            "g3_shipped": [
                "governance_projection_g3_v1.py",
                "governance-projection-queue-v1.jsonl",
                "governance-projection-gate-v1.json",
                "validate-governance-projection-g3-v1.sh",
            ],
            "g7_shipped": [
                "governance_self_heal_daemon_v1.py",
                "GOVERNANCE_SELF_HEAL_G7_LOCKED_v1.md",
                "validate-governance-self-heal-g7-v1.sh",
                "monitor_live_sync maybe_run_heal_from_monitor (30m)",
                "com.sourcea.g7-governance-self-heal.plist (hourly)",
            ],
            "g4_shipped": [
                "governance_replay_worker_v1.py",
                "governance-replay-receipt-v1.json",
                "validate-governance-replay-v1.sh",
            ],
            "g1_g2_shipped": [
                "governance-event-spine-v1.1 schema (15 fields)",
                "governance-event-spine-v1.jsonl",
                "governance-reference-graph-v1.json",
                "validate-governance-event-spine-v1.sh",
                "validate-hub-projection-disposable-v1.sh",
                "GOVERNANCE_RUNTIME_GOLDEN_RULE_LOCKED_v1.md",
            ],
        },
        "today_closeout_path": "SOURCEA_TODAY_SESSION_UNIFIED_CLOSEOUT_RECEIPT_2026-06-11_LOCKED_v1.md",
        "conscious_recovery_stack": {
            "skill": "agent-skills/shared/conscious-recovery/SKILL.md",
            "cursor_name": "sina-conscious-recovery",
            "rule": ".cursor/rules/lost-link-recovery-reward.mdc",
            "law": "SOURCEA_LOST_LINK_RECOVERY_ETHICS_LOCKED_v1.md",
            "mandatory_read": "MANDATORY_READ_BY_ROLE_LOCKED_v1.md v1.3",
            "sync": "scripts/sync-cursor-agent-skills.sh",
            "paired_skills": ["agent-self-audit-loop", "truth-projection", "skill-007-ecosystem-conflict-resolution"],
        },
        "truth_tree_down_only": {
            "thorn": "P0 SINA_OS_SSOT + LAW PURITY",
            "trunk": "P1 authority index + governance entry",
            "branch": "P2 topic LOCKED at row path",
            "leaf": "P4 hub/monitor · P6 chat/RESEARCH",
            "fallen": "P7 archive — never climbs",
            "enforcers": [
                "validate-law-purity-ssot-v1.sh",
                "validate-no-archive-as-law-v1.sh",
                "authority_root_coverage_audit.py",
                "validate-governance-propagation-live-v1.sh",
            ],
        },
        "threads": [
            {"id": "STRATEGIC-SLICE", "role": "Hub founder P0"},
            {"id": "THREAD-FACTORY", "role": "RunReceipt parallel"},
            {"id": "THREAD-MAINTAINER", "role": "Law · hub · validators"},
            {"id": "SYS-INTEGRITY-100", "role": "100-step + Canvas"},
            {"id": "THREAD-MERGEPACK", "role": "Active parallel evidence"},
            {"id": "THREAD-PORTFOLIO", "role": "TrustField · Noetfield"},
        ],
        "foundation_stack": [
            {"tier": "P0", "doc": "SINA_OS_SSOT_LOCKED.md", "live": "partial"},
            {"tier": "P0", "doc": "META_REASONING_POLICY_STACK", "live": "hub tab"},
            {"tier": "P0", "doc": "SOURCEA_SSOT_FOUNDATION_WRITING_GUIDE", "live": "new"},
            {"tier": "P1", "doc": "SINA_AUTHORITY_INDEX_MAP", "live": "validators"},
            {"tier": "P5", "doc": "INTEGRITY PACK 5 (SESSION-INTEGRITY-10)", "live": "validators PASS"},
            {"tier": "hatch", "doc": "governance_propagation_cascade", "live": "wired broker"},
        ],
        "authority_rows": _authority_rows(),
        "validators_bundled": [v.strip('"') for v in validators],
        "validators_total_sample": all_validate[:50],
        "backlog": open_items.get("items", []),
        "live_honest": {
            "monitor_rt": True,
            "broker_cascade": True,
            "hub_full_rebuild": "LAG minutes",
            "paper_water_risk": "law without hatch receipt",
        },
    }


def main() -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = catalog_payload()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        c = row["counts"]
        print(f"catalog: authority={c['authority_rows']} locked={c['root_locked_files']} validators={c['validators_total_scripts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
