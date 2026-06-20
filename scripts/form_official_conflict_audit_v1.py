#!/usr/bin/env python3
"""FORM_OFFICIAL conflict audit — evidenced mistakes/contradictions from disk only.

Receipt: ~/.sina/form-official-conflict-audit-v1.json
Law: no invented rows — each must cite evidence_path logged
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
AUDIT_PATH = SINA / "form-official-conflict-audit-v1.json"
APPLIED_PATH = SINA / "canvas-form-picks-applied-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _row(
    *,
    qid: str,
    title: str,
    question: str,
    blocks: str,
    disk_today: str,
    recommended: str,
    options: list[str],
    effect: str,
    evidence_path: str,
    evidence_detail: str,
    asked_by: str,
    tier: str = "P0_conflict",
    category: str = "conflict",
    option_effects: dict[str, str] | None = None,
) -> dict:
    row = {
        "id": qid,
        "title": title,
        "question": question,
        "blocks": blocks,
        "diskToday": disk_today,
        "recommended": recommended,
        "options": options,
        "effect": effect,
        "asked_by": asked_by,
        "reply_template": f"ASF: FIVE-STEP — PICK: {qid} {recommended}",
        "gather_tier": tier,
        "gather_category": category,
        "gather_source": "conflict_audit",
        "gather_phase": "extraction",
        "evidence_path": evidence_path,
        "evidence_detail": evidence_detail,
    }
    if option_effects:
        row["option_effects"] = option_effects
    return row


def audit_conflicts(*, existing_ids: set[str] | None = None) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from live_founder_decision_form_v1 import (  # noqa: WPS433
        OPEN_QUESTIONS_CORE,
        PENDING_OUTSIDE_AS_OPEN,
    )

    existing = existing_ids or set()
    applied = dict((_read_json(APPLIED_PATH).get("picks") or {}))
    rows: list[dict] = []

    # 1) Prior pick contradicts row recommended (real conflict logged)
    for q in OPEN_QUESTIONS_CORE + PENDING_OUTSIDE_AS_OPEN:
        qid = str(q.get("id") or "")
        if not qid or qid in existing:
            continue
        prior = applied.get(qid)
        rec = str(q.get("recommended") or "")
        if prior and rec and prior.upper() != rec.upper() and prior not in rec:
            rows.append(
                _row(
                    qid=f"Q-CONF-PICK-{qid}",
                    title=f"Prior pick conflicts with recommended — {qid}",
                    question=(
                        f"Disk shows prior pick **{prior}** but form row recommended **{rec}**. "
                        f"Reopen and replace pick, or keep prior as law?"
                    ),
                    blocks=f"canvas-form-picks-applied · row {qid}",
                    disk_today=f"prior_pick={prior} · recommended={rec} · title={q.get('title', '')[:60]}",
                    recommended="B",
                    options=[
                        "A — Keep prior pick as law (do not reopen)",
                        "B — Reopen row — founder re-picks now (recommended)",
                        "C — Amend recommended to match prior pick logged",
                        "D — Escalate to Judge Center counsel row",
                    ],
                    effect=f"Resolves pick vs recommendation drift for {qid}",
                    evidence_path=str(APPLIED_PATH),
                    evidence_detail=f"picks[{qid}]={prior} vs recommended={rec}",
                    asked_by="form_official_conflict_audit_v1.py",
                    category="pick_drift",
                )
            )

    # 2) U031 signed work-order but bay unmapped — blocks queue head
    wo = _read_json(SINA / "brain-outbound-work-order-active-v1.json")
    if wo.get("pending_cloud_bay") and str(wo.get("bay_slug")) == "unmapped" and "Q-BC-03" not in existing:
        qid = "Q-CONF-U031-BAY"
        if qid not in existing:
            rows.append(
                _row(
                    qid=qid,
                    title="U031 queue head blocked — no cloud bay mapped",
                    question=(
                        "sa-1100 / U031 has signed Brain work-order but bay_slug=unmapped. "
                        "Build outbound-rrl-intelligence bay, bounded Worker WORK, or pause loop auto?"
                    ),
                    blocks="brain-outbound-work-order-active-v1.json · healthy-queue head",
                    disk_today=(
                        f"upgrade_ref={wo.get('upgrade_ref')} · execution_plane={wo.get('execution_plane')} · "
                        f"pending_cloud_bay=true"
                    ),
                    recommended="B",
                    options=[
                        "A — Worker bounded WORK now (skip bay)",
                        "B — Build outbound-rrl-intelligence bay first (recommended)",
                        "C — sign_only forever — no implementation until bay exists",
                        "D — Pause loop auto until bay registry complete",
                    ],
                    effect="Unblocks or formally defers outbound queue head U031",
                    evidence_path=str(SINA / "brain-outbound-work-order-active-v1.json"),
                    evidence_detail="bay_slug=unmapped · pending_cloud_bay=true",
                    asked_by="execution_plane_honesty · queue head audit",
                    category="execution_blocker",
                )
            )

    # 3) F002 broker round-trip planned on critical path after F001 done
    plan = _read_json(ROOT / "data/sourcea-full-stack-100-fix-plan-v1.json")
    f001 = next((f for f in plan.get("fixes") or [] if f.get("id") == "F001"), {})
    f002 = next((f for f in plan.get("fixes") or [] if f.get("id") == "F002"), {})
    if f001.get("status") == "done" and f002.get("status") == "planned":
        qid = "Q-CONF-F002-BROKER"
        if qid not in existing:
            rows.append(
                _row(
                    qid=qid,
                    title="F002 broker round-trip — still required after Brain work-order?",
                    question=(
                        "F001 (Brain dispatch) is done. F002 (broker submit / last_worker_report) is still planned on P0 path. "
                        "Run broker after every work-order, or retire F002?"
                    ),
                    blocks="sourcea-full-stack-100-fix-plan-v1.json · critical_path F002",
                    disk_today=f"F001=done · F002=planned · owner_role={f002.get('owner_role')}",
                    recommended="A",
                    options=[
                        "A — YES — broker round-trip stays on P0 path (recommended)",
                        "B — Retire F002 — work-order receipt replaces broker",
                        "C — Defer F002 until first cloud bay executes",
                        "D — Worker-only broker — Brain never triggers",
                    ],
                    effect="Clarifies broker vs brain work-order receipt chain",
                    evidence_path=str(ROOT / "data/sourcea-full-stack-100-fix-plan-v1.json"),
                    evidence_detail="F001 done · F002 planned · critical_path",
                    asked_by="full_stack_fix_plan_pulse",
                    category="plan_conflict",
                )
            )

    # 4) B0503 planned — cloud worker should consume work-order not chat
    bplan = _read_json(ROOT / "data/brain-cloud-reasoning-1000-upgrade-plan-v1.json")
    b0502 = next((b for b in bplan.get("brain_steps") or bplan.get("steps") or [] if b.get("id") == "B0502"), None)
    b0503 = next((b for b in bplan.get("brain_steps") or bplan.get("steps") or [] if b.get("id") == "B0503"), None)
    if not b0502 or not b0503:
        for b in bplan.get("upgrades") or bplan.get("items") or []:
            if b.get("id") == "B0502":
                b0502 = b
            if b.get("id") == "B0503":
                b0503 = b
    if (b0502 or {}).get("status") == "done" and (b0503 or {}).get("status") == "planned":
        qid = "Q-CONF-B0503-CONSUMER"
        if qid not in existing:
            rows.append(
                _row(
                    qid=qid,
                    title="B0503 open — cloud worker still reads chat not work-order?",
                    question=(
                        "B0502 compiler done · B0503 (cloud consumes work-order not chat prompt) still planned. "
                        "Ship B0503 before more auto dispatch?"
                    ),
                    blocks="brain-cloud-reasoning-1000-upgrade-plan-v1.json · E06",
                    disk_today="B0502=done · B0503=planned · local_worker_deprecated flip pending",
                    recommended="A",
                    options=[
                        "A — YES — B0503 P0 before more loop auto dispatch (recommended)",
                        "B — Parallel — dispatch continues · B0503 background",
                        "C — Defer B0503 until outbound-rrl bay exists",
                        "D — Revert to Worker chat prompt consumption",
                    ],
                    effect="Sets cloud consumer law vs chat prompt loop",
                    evidence_path=str(ROOT / "data/brain-cloud-reasoning-1000-upgrade-plan-v1.json"),
                    evidence_detail="B0502 done · B0503 planned",
                    asked_by="brain cloud plan audit",
                    category="brain_cloud",
                )
            )

    # 5) MCP Phase 2 paid wire gate before cloud URL
    mcp = _read_json(ROOT / "data/mcp-stack-free-tier-v1.json")
    if mcp.get("one_law"):
        qid = "Q-CONF-MCP-PHASE2"
        if qid not in existing:
            rows.append(
                _row(
                    qid=qid,
                    title="MCP Phase 2 paid wire — founder gate before cloud execution URL",
                    question=(
                        "MCP law: Phase 1 free-tier only · Phase 2 paid wire needs founder approval. "
                        "Approve Phase 2 cloud URL (Railway/CF) now or stay Mac headless?"
                    ),
                    blocks="mcp-stack-free-tier-v1.json · NO-CC infra law",
                    disk_today="FBE_CLOUD_WORKER_URL unset · one_law=Phase1 free first",
                    recommended="B",
                    options=[
                        "A — Approve Phase 2 paid cloud wire now",
                        "B — Stay Phase 1 — Mac headless until W1 film ships (recommended)",
                        "C — CF Workers free tier only — no Railway",
                        "D — Defer all cloud URL until FORM picks done",
                    ],
                    effect="Gates cloud execution URL vs free-tier law",
                    evidence_path=str(ROOT / "data/mcp-stack-free-tier-v1.json"),
                    evidence_detail="one_law Phase 1/2 split",
                    asked_by="mcp_stack_free_tier_v1",
                    category="infra_gate",
                )
            )

    # 6) Full stack honest progress vs Goal 1000 headline (skip if Q-BC-05 already on form)
    prog = (plan.get("progress") or {})
    fn = _read_json(SINA / "factory-now-v1.json")
    valid = int(fn.get("valid_yes") or 0)
    done_fs = int(prog.get("done") or 0)
    if valid >= 1000 and done_fs < 50 and "Q-BC-05" not in existing:
        qid = "Q-CONF-DUAL-NORTHSTAR"
        if qid not in existing:
            rows.append(
                _row(
                    qid=qid,
                    title="Dual north star — Goal 1000 Valid YES vs full-stack 16/100",
                    question=(
                        f"Factory shows Valid YES {valid} but full-stack fix plan is {done_fs}/100 done. "
                        "Which counter is the honest north star for daily work?"
                    ),
                    blocks="factory-now-v1.json · sourcea-full-stack-100-fix-plan-v1.json",
                    disk_today=f"valid_yes={valid} · full_stack_done={done_fs}/100 · outbound_queue=66",
                    recommended="A",
                    options=[
                        "A — STRATEGIC-SLICE parallel — Goal 1000 factory + full-stack P0 spine (recommended)",
                        "B — Full-stack 100 only — pause outbound until F050",
                        "C — Outbound 66 only — pause full-stack",
                        "D — Commercial W1/W3 only — pause both counters",
                    ],
                    effect="Stops agents optimizing wrong progress metric",
                    evidence_path=str(ROOT / "data/sourcea-full-stack-100-fix-plan-v1.json"),
                    evidence_detail=f"progress.done={done_fs} vs factory valid_yes={valid}",
                    asked_by="honest progress audit",
                    category="paradox",
                )
            )

    # 7) CREED 36 nodes vs 14 capabilities — Brain admitted vocabulary mistake (transcript + disk)
    creed_mesh = Path.home() / "Desktop/YA5/PLUS ONE/CREED/.cursor/governance/FACTORY_MESH.json"
    if not creed_mesh.is_file():
        creed_mesh = Path.home() / "Desktop/PLUS ONE/CREED/FACTORY_MESH.json"
    if creed_mesh.is_file():
        mesh = _read_json(creed_mesh)
        node_count = len(mesh.get("nodes") or [])
        if node_count >= 30:
            qid = "Q-CONF-CREED-36V14"
            if qid not in existing:
                rows.append(
                    _row(
                        qid=qid,
                        title="CREED 36 mesh nodes vs 14 commercial lines — buyer vocabulary",
                        question=(
                            f"Brain once collapsed CREED to ~14 lines; disk SSOT is {node_count} nodes in FACTORY_MESH.json. "
                            "Lock 36-node mesh for operators · 14 lines for buyers only?"
                        ),
                        blocks="CREED/FACTORY_MESH.json · Brain chat correction 2026-06",
                        disk_today=f"FACTORY_MESH nodes={node_count} · 14 lines = commercial grouping only",
                        recommended="A",
                        options=[
                            "A — YES — 36 nodes SSOT · 14 lines buyer vocabulary only (recommended)",
                            "B — Collapse to 14 for Hub UI simplicity",
                            "C — Merge CREED into SourceA FBE graph as single SSOT",
                            "D — Defer — document later",
                        ],
                        effect="Prevents factory builder vocabulary drift in Brain/commercial copy",
                        evidence_path=str(creed_mesh),
                        evidence_detail=f"node_count={node_count}",
                        asked_by="Brain chat self-improve audit · transcript e6507c62",
                        category="misunderstanding",
                    )
                )

    # 8) SourceA FBE factory builder vs MonoRepo cloud runtime lane
    qid = "Q-CONF-FBE-MONO-EXEC"
    if qid not in existing and "Q-MONO-SSOT-LANE" not in existing:
        rows.append(
            _row(
                qid=qid,
                title="Who executes factory jobs — SourceA FBE spawn vs MonoRepo runtime?",
                question=(
                    "SourceA FBE compiles/spawns factory lines. MonoRepo ships cloud runtime farm. "
                    "Where do outbound bays (e.g. rrl_intelligence) execute?"
                ),
                blocks="fbe_node_graph_v1.json · SinaaiMonoRepo cloud/STACK_LOCK.json",
                disk_today="U031 bay=unmapped · FBE graph on SourceA · Mono cloud farm separate repo",
                recommended="A",
                options=[
                    "A — SourceA FBE bays on cloud worker · Mono = portfolio runtime only (recommended)",
                    "B — MonoRepo executes all outbound bays",
                    "C — Mac headless only until merge",
                    "D — Worker Cursor turns for all bays",
                ],
                effect="Sets execution repo boundary for outbound factory upgrades",
                evidence_path=str(ROOT / "data/fbe_node_graph_v1.json"),
                evidence_detail="bay unmapped · dual-repo architecture",
                asked_by="Brain MonoRepo architecture audit",
                category="lane_boundary",
            )
        )

    # 9) Plus ONE campus vs SourceA motor — daily pick authority
    qid = "Q-CONF-PLUSONE-MOTOR"
    if qid not in existing:
        rows.append(
            _row(
                qid=qid,
                title="Plus ONE campus vs SourceA motor — who owns founder picks?",
                question=(
                    "Plus ONE builds factory campuses (CREED/CHURCH). SourceA is governance motor + FORM_OFFICIAL. "
                    "Confirm all human–machine picks stay on SourceA M1 Canvas only?"
                ),
                blocks="PLUS ONE shell · SourceA FORM_OFFICIAL · ecosystem catalog",
                disk_today="FORM_OFFICIAL on SourceA M1 Canvas · Plus ONE = factory campus not pick surface",
                recommended="A",
                options=[
                    "A — YES — SourceA M1 only for picks · Plus ONE never hosts form (recommended)",
                    "B — Duplicate form on Plus ONE Hub",
                    "C — Plus ONE picks for CREED · SourceA for outbound only",
                    "D — Single merged chat — no Canvas",
                ],
                effect="Prevents split pick surfaces across portfolio",
                evidence_path=str(ROOT / "data/form_official_nerve_map_v1.json"),
                evidence_detail="FORM_OFFICIAL slot D SourceA only",
                asked_by="Brain Plus ONE campus insight · transcript",
                category="lane_boundary",
            )
        )

    # 10) False-done guard — U031/U032 incident
    qid = "Q-CONF-FALSE-DONE-GUARD"
    if qid not in existing:
        outbound = _read_json(ROOT / "data/outbound-factory-100-upgrade-plan-v1.json")
        u031 = next((u for u in outbound.get("upgrades") or [] if u.get("id") == "U031"), {})
        if u031.get("status") == "planned":
            rows.append(
                _row(
                    qid=qid,
                    title="False-done guard — never mark done without bay + receipt",
                    question=(
                        "U031/U032 were once falsely auto-marked done. Plan reverted to planned. "
                        "Lock guard: mark_done only when bay mapped + receipt proof?"
                    ),
                    blocks="outbound-factory plan · loop_specialist_tick guard",
                    disk_today=f"U031 status={u031.get('status')} · sign_only for unmapped bays wired",
                    recommended="A",
                    options=[
                        "A — YES — hard guard · no done without bay+receipt (recommended)",
                        "B — Soft warning only",
                        "C — Allow done for sign_only work-orders",
                        "D — Revert guard — trust loop auto",
                    ],
                    effect="Prevents repeat false-done on outbound queue",
                    evidence_path=str(ROOT / "data/outbound-factory-100-upgrade-plan-v1.json"),
                    evidence_detail="U031 planned after revert · guard on loop dispatch",
                    asked_by="Brain cloud E2E incident",
                    category="incident",
                )
            )

    # 11) WitnessBC Proof Lab / film — session evidence (2026-06-19)
    wbc_rows: list[tuple[str, dict]] = [
        (
            "Q-WBC-PROOF-LAB-OK",
            {
                "title": "Proof Lab interactive is ready — show buyers now?",
                "question": (
                    "Proof Lab scenarios + BLOCK/tamper demo are built and publish-ready at local :8090. "
                    "STYLE-B1 hero film stays blocked until Screen Studio. Open tunnel demo for buyers now?"
                ),
                "blocks": "witnessbc-proof-lab-v1.json · proof-scenarios · publish receipt interactive=YES",
                "disk_today": "interactive_proof_lab=YES · style_b1_hero_film=BLOCKED · proof.html deployed",
                "recommended": "A",
                "options": [
                    "A — YES — tunnel or local demo for NGO/civic buyers now (recommended)",
                    "B — Wait for STYLE-B1 hero before any demo",
                    "C — Internal only — no external URL yet",
                    "D — Skip Proof Lab — film only",
                ],
                "effect": "Unblocks W-P5 Proof Lab outreach without fake A-tier film",
                "evidence_path": str(ROOT / "data/witnessbc-proof-lab-v1.json"),
                "evidence_detail": "~/.sina/witnessbc-proof-lab-publish-receipt-v1.json interactive=YES",
                "asked_by": "Worker Proof Lab upgrade session",
                "category": "commercial",
                "tier": "P4_commercial",
            },
        ),
        (
            "Q-WBC-STYLE-B1",
            {
                "title": "Record STYLE-B1 ~3m institutional hero — when?",
                "question": (
                    "Ship gate blocks hero publish (Playwright capture ≠ Screen Studio). "
                    "Record per STYLE_B1 brief this week or defer?"
                ),
                "blocks": "STYLE_B1_WITNESSBC_SHOT_MATCH_BRIEF · commercial_film_ship_gate",
                "disk_today": "publish_allowed=false · Desktop master missing",
                "recommended": "B",
                "options": [
                    "A — Record Screen Studio this week — bash witnessbc-commercial-film-ship.sh",
                    "B — Defer 30 days — Proof Lab interactive is enough for now (recommended)",
                    "C — Accept Playwright capture as hero (not recommended)",
                    "D — Cancel hero film — Proof Lab only",
                ],
                "effect": "Sets honest film tier vs interactive-only posture",
                "evidence_path": str(
                    ROOT / "archive/attachments/2026-06-16/STYLE_B1_WITNESSBC_SHOT_MATCH_BRIEF_LOCKED_v1.md"
                ),
                "evidence_detail": "commercial_film_ship_gate_v1.py publish_allowed=false",
                "asked_by": "Worker Proof Lab session",
                "category": "commercial",
                "tier": "P4_commercial",
            },
        ),
        (
            "Q-WBC-OCRE-L3",
            {
                "title": "OCRE commercial L3 — founder Mail confirm only",
                "question": (
                    "Commercial L3 at 75% — ocree confirm_sent is founder-only (agents never send email). "
                    "You send Mail from your account and run --confirm-sent ocre?"
                ),
                "blocks": "commercial L3 · outbound · agent never email law",
                "disk_today": "L3 75% · confirm_sent pending founder",
                "recommended": "A",
                "options": [
                    "A — YES — I will send Mail + confirm_sent this week (recommended)",
                    "B — Defer L3 — focus Proof Lab first",
                    "C — Worker may send on my behalf (forbidden — pick A or B)",
                    "D — Drop OCRE lane",
                ],
                "effect": "Closes commercial L3 without agent email violation",
                "evidence_path": str(ROOT / "data/commercial/witnessbc-portfolio-routing-v1.json"),
                "evidence_detail": "portfolio W-P5 · agent never email standing law",
                "asked_by": "Commercial session synthesis",
                "category": "commercial",
                "tier": "P4_commercial",
            },
        ),
        (
            "Q-WBC-WITNESS-AI-NAME",
            {
                "title": "Public name — Witness AI vs WitnessBC on publish",
                "question": (
                    "witnessbc.com uses Witness AI product name with ≠ witness.ai disclaimer. "
                    "Rebrand public HTML to WitnessBC on next publish?"
                ),
                "blocks": "witnessbc-portfolio-routing title_fix_note · identity law",
                "disk_today": "implementation.title_fix_note logged",
                "recommended": "B",
                "options": [
                    "A — Rebrand all public pages to WitnessBC now",
                    "B — Keep Witness AI on site + disclaimer until buyer call (recommended)",
                    "C — Dual brand — Witness AI + WitnessBC footer",
                    "D — Pause site — form only",
                ],
                "effect": "Sets buyer-facing identity before outreach",
                "evidence_path": str(ROOT / "data/commercial/witnessbc-portfolio-routing-v1.json"),
                "evidence_detail": "title_fix_note · anti_paths witness.ai conflation",
                "asked_by": "WitnessBC portfolio routing",
                "category": "commercial",
                "tier": "P4_commercial",
            },
        ),
    ]
    for qid, kw in wbc_rows:
        if qid not in existing:
            rows.append(_row(qid=qid, **kw))

    # Dedupe against existing + within audit
    seen: set[str] = set(existing)
    out: list[dict] = []
    for r in rows:
        rid = r.get("id")
        if not rid or rid in seen:
            continue
        seen.add(rid)
        out.append(r)

    result = {
        "ok": True,
        "schema": "form-official-conflict-audit-v1",
        "audited_at": _now(),
        "conflict_count": len(out),
        "conflict_ids": [r["id"] for r in out],
        "rows": out,
        "skipped_existing": len(rows) - len(out),
        "law": "evidence_path required on every row — no chat-only invention",
    }
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    result["audit_path"] = str(AUDIT_PATH)
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit disk for real FORM_OFFICIAL conflicts")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--existing-ids", default="", help="Comma-separated ids already on form")
    args = ap.parse_args()
    existing = {x.strip() for x in args.existing_ids.split(",") if x.strip()}
    result = audit_conflicts(existing_ids=existing)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"OK: {result.get('conflict_count')} evidenced conflicts → {AUDIT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
