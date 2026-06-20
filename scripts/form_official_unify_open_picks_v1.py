#!/usr/bin/env python3
"""FORM_OFFICIAL — unify open unpicked rows · dedupe clusters · brain route plans.

Reads: ~/.sina/live-founder-decision-form-intake-v1.json
Writes: data/form-official-unified-open-picks-v1.json
        ~/.sina/form-official-unified-open-picks-v1.json

Law: no mixing · no fragmentation · no duplication in routing SSOT.
FAIL immediate on invent picks — rows stay open until founder PICK on Hub /form/.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
INTAKE = SINA / "live-founder-decision-form-intake-v1.json"
OUT_DATA = ROOT / "data/form-official-unified-open-picks-v1.json"
OUT_SINA = SINA / "form-official-unified-open-picks-v1.json"

# Semantic duplicate clusters — one canonical PICK covers the cluster (no re-ask in chat)
DEDUPE_CLUSTERS: list[dict] = [
    {
        "cluster_id": "CLUSTER-CAP-100",
        "canonical_id": "Q-GATH-06",
        "member_ids": ["Q-GATH-06", "Q-MF-12"],
        "note": "100-cap remind vs build — same law; pick either once",
    },
    {
        "cluster_id": "CLUSTER-NPM-CARD1",
        "canonical_id": "Q-MF-02",
        "member_ids": ["Q-MF-02", "Q-CHAT-PUBLISH-01"],
        "note": "npm Card1 publish timing — thread + chat synthesis same fork",
    },
    {
        "cluster_id": "CLUSTER-CLOUD-PROOF",
        "canonical_id": "Q-CHAT-CLOUD-01",
        "member_ids": ["Q-CHAT-CLOUD-01", "Q-MF-06"],
        "note": "Cloud SSE vs local E2E vs Supabase deploy order — related sequencing",
    },
    {
        "cluster_id": "CLUSTER-UNIFY-GO",
        "canonical_id": "Q-FINAL-05",
        "member_ids": ["Q-FINAL-05", "Q-SESSION-UNIFY-GO", "Q-GATH-05"],
        "note": "Gather complete → UNIFY phase authorization",
    },
]

# Per-row brain plan after founder PICK (route lane + next act)
ROW_PLANS: dict[str, dict] = {
    "Q-GATH-06": {
        "route": "brain",
        "plan": "Lock cap=100 minder · agents BUILD below cap · URGENT remind at cap",
        "proof": "scripts/form_official_minder_v1.py · form_official_gather_extraction_v1.py",
    },
    "Q-MF-01": {
        "route": "brain",
        "plan": "Wire mac_role control_plane_only into all factory spawn paths",
        "proof": "data/cursor-bootstrap-ledger-v1.json · architecture-ledger-v1.json",
    },
    "Q-MF-02": {
        "route": "founder",
        "plan": "Founder npm login → bash scripts/npm_publish_mcp_chain_v1.sh → marketplace submit",
        "proof": "receipts/card-1-sourcea-forge-governance-publish-v1.json",
    },
    "Q-MF-03": {
        "route": "brain",
        "plan": "Single Card1 listing only · defer VIRLUX/Noetfield marketplace cards",
        "proof": "cursor-plugin/sourcea-forge-governance/MARKETPLACE_LISTING.md",
    },
    "Q-MF-04": {
        "route": "worker",
        "plan": "Apply Proof Layer tagline to listing copy + hub commercial surfaces",
        "proof": "validate-mcp-chain-motor-v1.sh",
    },
    "Q-MF-05": {
        "route": "worker",
        "plan": "Execute build order: billing → orchestration → Fal bridge → StoreKit",
        "proof": "bash scripts/validate-video-ad-factory-chain-v1.sh",
    },
    "Q-MF-06": {
        "route": "founder",
        "plan": "Founder names Supabase project ref → WORK: supabase-edge-loop deploy",
        "proof": "data/supabase-edge-loop-v1.json",
    },
    "Q-MF-07": {
        "route": "brain",
        "plan": "Keep scripts/ path until Edge live OR founder EDIT ALLOWED apps/",
        "proof": "scripts/video_ad_factory_orchestrate_v1.py",
    },
    "Q-MF-08": {
        "route": "maintainer",
        "plan": "Validator: block Fal spend when state=HUMAN_APPROVAL_REQUIRED",
        "proof": "scripts/video_ad_rendering_bridge_v1.py",
    },
    "Q-MF-09": {
        "route": "brain",
        "plan": "Register blueprint as multi-factory SSOT in authority index row",
        "proof": "docs/SOURCEA_MULTI_FACTORY_ENTERPRISE_BLUEPRINT_LOCKED_v1.md",
    },
    "Q-MF-10": {
        "route": "founder",
        "plan": "Founder confirm-sent → commercial L3 w3_send_ready honest green",
        "proof": "execution_plane_honesty validators",
    },
    "Q-MF-11": {
        "route": "brain",
        "plan": "Reject fork proposals · map Gemini ideas into SourceA paths only",
        "proof": "data/multi-factory-enterprise-tree-advisory-v1.json",
    },
    "Q-CHAT-LANG-01": {
        "route": "brain",
        "plan": "Apply language mode to vocabulary inject + founder-facing copy law",
        "proof": "scripts/vocabulary_guard_v1.py --tooling",
    },
    "Q-CHAT-NEXT-P0-01": {
        "route": "founder",
        "plan": "Founder daily tap order: form block → INBOX → deploy → commercial",
        "proof": "~/.sina/live-ongoing-prompts-next-10-v1.json",
    },
    "Q-FINAL-01": {
        "route": "brain",
        "plan": "Set STRATEGIC-SLICE north star · parallel outbound + FBE catalog",
        "proof": "brain_outbound_work_order_v1.py",
    },
    "Q-SESSION-INBOX-NEXT": {
        "route": "worker",
        "plan": "RUN INBOX on P0-13 Noetfield freemium bay after form block 1",
        "proof": "phase0-freemium-sandbox-reference-v1.json",
    },
    "Q-THREAD-DEPLOY-01": {
        "route": "maintainer",
        "plan": "Patch validate-all-e2e deploy gate: Agent Run only vs both required",
        "proof": "scripts/validate-all-e2e-v1.sh",
    },
    "Q-THREAD-10STEP-01": {
        "route": "brain",
        "plan": "If A: full WORK 10 steps · B: SAVE spec then WORK · C: plan only",
        "proof": "brain-os/plan-registry",
    },
}

PRIORITY_BLOCKS: list[dict] = [
    {
        "block": 1,
        "title": "Form meta + cap law",
        "pick_ids": ["Q-GATH-06", "Q-SESSION-FORM-BUILD"],
        "route": "founder",
    },
    {
        "block": 2,
        "title": "Language + voice (never chat-only)",
        "pick_ids": ["Q-CHAT-LANG-01", "Q-CHAT-PLUSONE-01"],
        "route": "founder",
    },
    {
        "block": 3,
        "title": "Marketplace + Proof Layer (this thread)",
        "pick_ids": ["Q-MF-01", "Q-MF-02", "Q-MF-03", "Q-MF-04", "Q-MF-09", "Q-MF-11"],
        "route": "founder",
    },
    {
        "block": 4,
        "title": "Cloud factory build order",
        "pick_ids": ["Q-MF-05", "Q-MF-06", "Q-MF-07", "Q-MF-08"],
        "route": "founder",
    },
    {
        "block": 5,
        "title": "Strategic spine + brain cloud",
        "pick_ids": ["Q-FINAL-01", "Q-FINAL-02", "Q-FINAL-03", "Q-FINAL-04", "Q-FINAL-06", "Q-FINAL-07"],
        "route": "founder",
    },
    {
        "block": 6,
        "title": "Session + commercial gates",
        "pick_ids": ["Q-MF-10", "Q-SESSION-INBOX-NEXT", "Q-SESSION-CLOUD-CF06", "Q-THREAD-DEPLOY-01"],
        "route": "founder",
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _cluster_for(qid: str) -> dict | None:
    for c in DEDUPE_CLUSTERS:
        if qid in c["member_ids"]:
            return c
    return None


def build(*, write: bool = True) -> dict:
    if not INTAKE.is_file():
        raise SystemExit(f"FAIL: missing {INTAKE}")
    intake = json.loads(INTAKE.read_text(encoding="utf-8"))
    rows = list(intake.get("rows") or [])
    unpicked = [r for r in rows if not r.get("prior_pick")]
    picked = [r for r in rows if r.get("prior_pick")]

    canonical_unpicked: list[dict] = []
    seen_cluster: set[str] = set()
    for r in unpicked:
        qid = str(r.get("id") or "")
        cluster = _cluster_for(qid)
        if cluster:
            cid = cluster["cluster_id"]
            if cid in seen_cluster and qid != cluster["canonical_id"]:
                continue
            seen_cluster.add(cid)
        plan = ROW_PLANS.get(qid) or {
            "route": "founder",
            "plan": "Founder PICK on Hub /form/ → Brain routes per gather tier",
            "proof": "scripts/canvas_form_apply_picks_v1.py",
        }
        entry = {
            "id": qid,
            "title": r.get("title"),
            "recommended": r.get("recommended"),
            "options": r.get("options"),
            "reply_template": r.get("reply_template"),
            "gather_tier": r.get("gather_tier"),
            "gather_source": r.get("gather_source"),
            "duplicate_cluster": cluster["cluster_id"] if cluster else None,
            "canonical_in_cluster": cluster["canonical_id"] if cluster else qid,
            "brain_plan": plan,
        }
        canonical_unpicked.append(entry)

    result = {
        "ok": True,
        "schema": "form-official-unified-open-picks-v1",
        "saved_at": _now(),
        "fail_policy": "FAIL_IMMEDIATE_NO_TEMPER",
        "form_hub": "http://127.0.0.1:13020/form/",
        "canvas": "FORM_OFFICIAL M1 · Pending confirmations",
        "intake_path": str(INTAKE),
        "totals": {
            "intake_rows": len(rows),
            "unpicked_raw": len(unpicked),
            "unpicked_canonical": len(canonical_unpicked),
            "prior_pick": len(picked),
            "cap": 100,
            "cap_reached": len(rows) >= 100,
        },
        "dedupe_clusters": DEDUPE_CLUSTERS,
        "priority_blocks": PRIORITY_BLOCKS,
        "unpicked_canonical": canonical_unpicked,
        "brain_routing_note": (
            "SourceA Brain plans and routes after PICK — Worker RUN INBOX · "
            "FBE cloud headless · founder gates only where noted"
        ),
        "proof_commands": [
            "python3 scripts/form_official_unify_open_picks_v1.py --json",
            "python3 scripts/brain_form_gather_unify_plan_v1.py --json",
            "bash scripts/validate-form-official-e2e-v1.sh",
        ],
    }

    if write:
        OUT_DATA.parent.mkdir(parents=True, exist_ok=True)
        OUT_DATA.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        SINA.mkdir(parents=True, exist_ok=True)
        OUT_SINA.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        result["paths"] = {"data": str(OUT_DATA), "sina": str(OUT_SINA)}

    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Unify open FORM_OFFICIAL picks · dedupe · brain routes")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    out = build(write=not args.no_write)
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        t = out["totals"]
        print(
            f"OK: unify open picks · raw={t['unpicked_raw']} "
            f"canonical={t['unpicked_canonical']} cap={t['cap_reached']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
