#!/usr/bin/env python3
"""FORM_OFFICIAL extraction & gathering — merge ALL questions/misunderstandings onto Canvas.

Phase: extraction → gather → (later) unify · organize · prioritize
Receipt: ~/.sina/live-founder-decision-form-extraction-v1.json
Intake:  ~/.sina/live-founder-decision-form-intake-v1.json (Canvas OPEN_FORM_QUESTIONS source)
Flag:    ~/.sina/form-official-gathering-phase-v1.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
THREAD_GATHER_JSON = ROOT / "data/form-official-gather-thread-marketplace-factory-v1.json"
SESSION_ARCHITECT_JSON = ROOT / "data/form-official-gather-session-architect-v1.json"
EXTRACTION_PATH = SINA / "live-founder-decision-form-extraction-v1.json"
INTAKE_PATH = SINA / "live-founder-decision-form-intake-v1.json"
GATHERING_FLAG = SINA / "form-official-gathering-phase-v1.json"
MINDER_RECEIPT = SINA / "form-official-gather-minder-v1.json"
GATHER_CAP = 100
APPLIED_PATH = SINA / "canvas-form-picks-applied-v1.json"

TIER_ORDER = {
    "P0_meta": 0,
    "P0_final_fix": 1,
    "P0_conflict": 2,
    "P0_brain_cloud": 3,
    "P1_integrity_core": 4,
    "P2_pending_outside": 5,
    "P3_enforcement": 6,
    "P4_commercial": 7,
}

# Misunderstandings / paradoxes surfaced in Brain chat (extraction pass)
GATHER_META_ROWS: list[dict] = [
    {
        "id": "Q-GATH-01",
        "title": "Form looks empty — which Canvas view is the form office?",
        "question": "You see an empty form. Disk has open rows but wrong view shows 100-pack only. Which surface is FORM_OFFICIAL?",
        "blocks": "INCIDENT-029 · founder perception · Canvas view routing",
        "diskToday": "OPEN_FORM_QUESTIONS on disk · Pending confirmations view · not agent-pov 100-pack",
        "recommended": "A",
        "options": [
            "A — Pending confirmations view ONLY is form office (recommended)",
            "B — 100-agent POV tab is form office",
            "C — Hub Track tab is form office",
            "D — Chat ASF picks only — no Canvas",
        ],
        "effect": "Sets mandatory founder navigation for all human–machine picks",
        "option_effects": {
            "A": "Hub action opens M1 Canvas → Pending confirmations · all gather rows visible",
            "B": "Revert INCIDENT-029 · 100-pack becomes office (not law)",
            "C": "Hub projection becomes pick surface (027 regression)",
            "D": "Canvas retired · chat-only picks",
        },
        "asked_by": "Brain chat · form empty report 2026-06-19",
        "reply_template": "ASF: FIVE-STEP — PICK: Q-GATH-01 A",
        "gather_tier": "P0_meta",
        "gather_category": "misunderstanding",
    },
    {
        "id": "Q-GATH-02",
        "title": "Canva vs Cursor Canvas — lock terminology",
        "question": "You said CANVA FORM twice before. Law says Cursor Canvas. Confirm FORM_OFFICIAL = Cursor Canvas M1?",
        "blocks": "FR-FORM terminology · integrity-open-row-spec.ts",
        "diskToday": "spec says Canva → Cursor Canvas · M1 slot D path on disk",
        "recommended": "A",
        "options": [
            "A — YES — FORM_OFFICIAL = Cursor Canvas only (recommended)",
            "B — Migrate to Canva.com external form",
            "C — Both — dual surface",
            "D — Rename to Form Office only — drop Canvas word",
        ],
        "effect": "Stops agents searching Canva.com or wrong scratch canvases",
        "asked_by": "Brain chat · CANVA FORM correction",
        "reply_template": "ASF: FIVE-STEP — PICK: Q-GATH-02 A",
        "gather_tier": "P0_meta",
        "gather_category": "misunderstanding",
    },
    {
        "id": "Q-GATH-03",
        "title": "Gathering phase — re-surface prior picks for unify pass?",
        "question": "52 rows already have disk picks but you want extraction/gather first. Show ALL rows on Canvas now (including prior picks)?",
        "blocks": "canvas-form-picks-applied-v1.json · gathering phase law",
        "diskToday": "applied=52 · gathered 72+ on Canvas · founder wants accurate conflicts",
        "recommended": "A",
        "options": [
            "A — YES — show ALL rows on Canvas · mark prior pick on card (recommended)",
            "B — Open rows only — hide prior picks until unify phase",
            "C — Reset all applied picks — full re-pick",
            "D — Pause gathering — answer Q-BC only",
        ],
        "effect": "Controls whether INCIDENT-029 open list is intake-only or full catalog",
        "asked_by": "ASF extraction phase order 2026-06-19",
        "reply_template": "ASF: FIVE-STEP — PICK: Q-GATH-03 A",
        "gather_tier": "P0_meta",
        "gather_category": "phase_law",
    },
    {
        "id": "Q-GATH-04",
        "title": "Local Worker INBOX as P0 — strategic mistake?",
        "question": "Treating local Worker INBOX as north star blocked Brain cloud pivot. Confirm Brain work-order primary?",
        "blocks": "brain_outbound_work_order_v1 · B0501 · execution_path_vocabulary",
        "diskToday": "brain_work_order_primary=YES · U031 signed · bay unmapped",
        "recommended": "A",
        "options": [
            "A — YES — Brain signs · cloud/API executes · Mac control plane (recommended)",
            "B — NO — revert to Worker INBOX daily P0",
            "C — Hybrid without compiler — manual only",
            "D — Defer until Third Form Q-BC picks done",
        ],
        "effect": "Locks strategic spine for outbound factory + Auto Runtime",
        "asked_by": "Brain chat · paradox audit",
        "reply_template": "ASF: FIVE-STEP — PICK: Q-GATH-04 A",
        "gather_tier": "P0_meta",
        "gather_category": "paradox",
    },
    {
        "id": "Q-GATH-05",
        "title": "Extraction → gather → unify → prioritize — confirm sequence",
        "question": "You are in extraction/gathering NOW. Agents must not reorganize until gather complete. Confirm sequence?",
        "blocks": "FORM_OFFICIAL phase law · Q-GATH gathering",
        "recommended": "A",
        "options": [
            "A — YES — gather all first · unify second · prioritize third (recommended)",
            "B — Skip gather — unify immediately",
            "C — Prioritize first — gather later",
            "D — Ship code only — no form phases",
        ],
        "effect": "Prevents premature filtering that hid 51 rows from Canvas",
        "asked_by": "ASF extraction phase 2026-06-19",
        "reply_template": "ASF: FIVE-STEP — PICK: Q-GATH-05 A",
        "gather_tier": "P0_meta",
        "gather_category": "phase_law",
    },
    {
        "id": "Q-GATH-06",
        "title": "Gather cap 100 — founder fill · agents build",
        "question": (
            "When FORM_OFFICIAL reaches 100 gathered rows, agents stop adding and remind you to fill. "
            "Until cap: agents focus BUILD plans. Confirm?"
        ),
        "blocks": "ASF order 2026-06-19 · gather cap · minder reminder",
        "diskToday": "gather_cap=100 · rows stay until ASF PICK · minder receipt on disk",
        "recommended": "A",
        "options": [
            "A — YES — 100 cap · remind minder fast · else BUILD (recommended)",
            "B — No cap — keep gathering forever",
            "C — Cap at 50 — fill sooner",
            "D — Stop form — chat only",
        ],
        "effect": "Locks gather→fill→unify sequence · agents do not spam new rows at cap",
        "asked_by": "ASF FORM_OFFICIAL gather law 2026-06-19",
        "reply_template": "ASF: FIVE-STEP — PICK: Q-GATH-06 A",
        "gather_tier": "P0_meta",
        "gather_category": "phase_law",
    },
]

# Session-critical forks — stay on form until founder PICK (evidence on disk)
SESSION_GATHER_ROWS: list[dict] = [
    {
        "id": "Q-SESSION-INBOX-NEXT",
        "title": "Next INBOX head — Noetfield freemium bay (P0-13)?",
        "question": "Unified queue head is P0-13 Noetfield freemium cloud bay. Run INBOX on this next after form glance?",
        "blocks": "phase0-freemium-sandbox-reference · plans-unified-worker-queue",
        "diskToday": "P0-01 P0-02 done · P0-13 pending · cat-noetfield-freemium on disk",
        "recommended": "A",
        "options": [
            "A — YES — RUN INBOX P0-13 next (recommended)",
            "B — WitnessBC Proof Lab first",
            "C — Pause INBOX — form fills only",
            "D — Skip phase0 — outbound only",
        ],
        "effect": "Sets Worker next act after form session",
        "asked_by": "RUN INBOX session",
        "gather_tier": "P0_final_fix",
        "gather_category": "session_build",
    },
    {
        "id": "Q-SESSION-FORM-BUILD",
        "title": "Form open + BUILD — parallel OK?",
        "question": "84+ rows on form. Worker still RUN INBOX and build plans while you fill A/B/C/D on official form?",
        "blocks": "FORM_OFFICIAL §1b · Worker INBOX law",
        "diskToday": "form gathering active · factory SINGLE_SA · queue sa-1200",
        "recommended": "A",
        "options": [
            "A — YES — parallel form fill + Worker BUILD (recommended)",
            "B — Form only — freeze INBOX until empty",
            "C — BUILD only — ignore form until RT LIVE",
            "D — Brain only — no Worker",
        ],
        "effect": "Prevents factory freeze while form has open PICKs",
        "asked_by": "ASF gather posture",
        "gather_tier": "P0_meta",
        "gather_category": "session_build",
    },
    {
        "id": "Q-SESSION-TUNNEL-DEMO",
        "title": "Proof Lab public demo — free tunnel?",
        "question": "publish_witnessbc_landing_v1.py can expose Proof Lab via free trycloudflare tunnel (no paid Cloudflare). Run tunnel for buyers?",
        "blocks": "publish_witnessbc_landing_v1.py · proof URL receipt",
        "diskToday": "local :8090/proof.html ready · tunnel optional",
        "recommended": "B",
        "options": [
            "A — YES — run --backend tunnel now",
            "B — Local only until you say tunnel (recommended)",
            "C — Paid Cloudflare Pages — not yet",
            "D — No public URL",
        ],
        "effect": "Sets buyer demo URL posture without paid infra",
        "asked_by": "Proof Lab publish session",
        "gather_tier": "P4_commercial",
        "gather_category": "session_build",
    },
    {
        "id": "Q-SESSION-UNIFY-GO",
        "title": "After you fill — Brain UNIFY pass on all rows?",
        "question": "When you finish PICKs (or hit cap), Brain runs unify · organize · prioritize on gathered rows. Auto-start UNIFY?",
        "blocks": "brain_form_gather_unify_plan_v1.py · Q-GATH-05 sequence",
        "diskToday": "gather phase active · unify plan on disk",
        "recommended": "A",
        "options": [
            "A — YES — auto UNIFY when open count drops below 10 (recommended)",
            "B — Manual — you say unify",
            "C — Skip unify — ship code only",
            "D — Reset form — regather",
        ],
        "effect": "Closes gather→fill→unify pipeline",
        "asked_by": "Brain form gather plan",
        "gather_tier": "P0_meta",
        "gather_category": "phase_law",
    },
    {
        "id": "Q-SESSION-PHASE0-SPOT",
        "title": "Phase0 13/13 on disk — spot-check or trust?",
        "question": "Phase0 pulse shows 13/13 complete after WitnessBC P0-03/P0-08. Trust machine or you spot-check Proof Lab + Trust Center?",
        "blocks": "phase0-freemium-sandbox-reference-v1.json · pulse receipt",
        "diskToday": "13/13 marked · validators PASS on bays",
        "recommended": "B",
        "options": [
            "A — Trust machine — move to outbound scale",
            "B — Spot-check Proof Lab + Trust Center once (recommended)",
            "C — Re-run full phase0 pulse audit",
            "D — Reopen all P0 rows",
        ],
        "effect": "Sets verification depth before scale",
        "asked_by": "Phase0 closeout session",
        "gather_tier": "P0_final_fix",
        "gather_category": "session_build",
    },
    {
        "id": "Q-SESSION-CLOUD-CF06",
        "title": "Cloud factory step6 federated FAIL — fix or defer?",
        "question": "CF-STEP6_FEDERATED failed (remote_status=None, Railway rate limit). P0 fix federated bay or defer?",
        "blocks": "cloud factory receipt · unified queue CF items",
        "diskToday": "step6_federated FAIL · rate limited",
        "recommended": "B",
        "options": [
            "A — P0 fix federated remote now",
            "B — Defer — local bays + INBOX first (recommended)",
            "C — Drop cloud factory from queue",
            "D — Retry Railway hourly auto",
        ],
        "effect": "Prioritizes local factory vs cloud remote",
        "asked_by": "Unified plans queue",
        "gather_tier": "P0_brain_cloud",
        "gather_category": "session_build",
    },
    {
        "id": "Q-SESSION-WBC-SUMMARY",
        "title": "WitnessBC work summary — deposit to vault?",
        "question": "WitnessBC lane + Proof Lab factory + film ship gate summary on disk. Deposit summary receipt to vault for portfolio?",
        "blocks": "witnessbc-work-summary-receipt-v1.json · commercial pipeline",
        "diskToday": "WBC lane cp-47ccf0bd93 · proof_lab bay PASS",
        "recommended": "A",
        "options": [
            "A — YES — vault deposit summary (recommended)",
            "B — Wait until STYLE-B1 hero ships",
            "C — Chat only — no vault",
            "D — Commercial only — no portfolio row",
        ],
        "effect": "Locks WitnessBC session evidence for fleet",
        "asked_by": "WitnessBC summary session",
        "gather_tier": "P4_commercial",
        "gather_category": "session_build",
    },
    {
        "id": "Q-CW-BATCH3",
        "title": "Cloud Forge Run batch 2 done at CLOUD-SEC-200 — start batch 3?",
        "question": "Railway queue_batch_complete=true · head CLOUD-SEC-200. Generate and lock batch 3 (CLOUD-SEC-201..300) now?",
        "blocks": "cloud-forge-run-queue-active-v1.json · secondary-cloud-forge-run-batch-3",
        "diskToday": "queue_batch_complete true · last_completed CLOUD-SEC-200 · 2026-06-23T08:55Z",
        "recommended": "B",
        "options": [
            "A — YES — generate batch 3 and arm Cloud Workers Proceed",
            "B — PAUSE — celebrate batch 2 · batch 3 after sourcea.app fix (recommended)",
            "C — Manual — founder picks row range in chat",
            "D — Retire Cloud Forge Run — no more CLOUD-SEC packs",
        ],
        "effect": "Arms or pauses next 100-pack Cloud Forge Run",
        "asked_by": "Cloud Workers audit 2026-06-23",
        "gather_tier": "P0_brain_cloud",
        "gather_category": "cloud_workers",
    },
    {
        "id": "Q-CW-SOURCEA-APP",
        "title": "sourcea.app still down (CF 1016) — fix DNS before batch 3?",
        "question": "sourcea-com.pages.dev works · sourcea.app custom domain pending CNAME. Prioritize Cloudflare Pages DNS activation?",
        "blocks": "sourcea.app commercial landing · MVP intake",
        "diskToday": "pages.dev OK · sourcea.app Error 1016 · CNAME not set",
        "recommended": "A",
        "options": [
            "A — YES — fix sourcea.app DNS first (recommended)",
            "B — Batch 3 first — DNS later",
            "C — Use pages.dev only for now",
            "D — Move to Vercel per locked doc",
        ],
        "effect": "Sets commercial domain priority vs Cloud Forge Run batch 3",
        "asked_by": "Cloud Workers audit 2026-06-23",
        "gather_tier": "P0_brain_cloud",
        "gather_category": "cloud_workers",
    },
    {
        "id": "Q-CW-HUB-RETIRE",
        "title": "Retire Worker Hub from official links bar?",
        "question": "Cloud Workers.app is now primary cockpit for Proceed. Remove or demote Worker Hub :13020 from desktop app link bar?",
        "blocks": "official-links-bar.js · hub-cloud-forge-run-proceed-v1.json",
        "diskToday": "Cloud Workers first in link bar · Hub marked legacy optional",
        "recommended": "B",
        "options": [
            "A — Remove Worker Hub from link bar entirely",
            "B — Keep demoted — legacy glance only (recommended)",
            "C — Restore Hub first — revert link order",
            "D — Merge Hub into Cloud Workers single app",
        ],
        "effect": "Desktop app navigation · agent proceed guidance",
        "asked_by": "Cloud Workers audit 2026-06-23",
        "gather_tier": "P1_integrity_core",
        "gather_category": "cloud_workers",
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_applied() -> dict[str, str]:
    if not APPLIED_PATH.is_file():
        return {}
    try:
        return dict(json.loads(APPLIED_PATH.read_text(encoding="utf-8")).get("picks") or {})
    except Exception:
        return {}


def _tier_for_row(q: dict, *, source: str) -> str:
    if q.get("gather_tier"):
        return str(q["gather_tier"])
    qid = str(q.get("id") or "")
    if qid.startswith("Q-BC-"):
        return "P0_brain_cloud"
    if qid.startswith("Q-WBC-") or qid.startswith("Q-SESSION-"):
        return "P4_commercial" if qid.startswith("Q-WBC-") else "P0_final_fix"
    if qid.startswith("ENF-"):
        return "P3_enforcement"
    if qid.startswith("11.") or qid == "Q-PLAN-300":
        return "P4_commercial"
    if source == "pending_outside":
        return "P2_pending_outside"
    return "P1_integrity_core"


def _normalize_row(q: dict, *, source: str, applied: dict[str, str]) -> dict:
    qid = str(q.get("id") or "")
    prior = applied.get(qid)
    row = dict(q)
    row["gather_source"] = source
    row["gather_tier"] = _tier_for_row(q, source=source)
    row["gather_category"] = row.get("gather_category") or source
    row["gather_phase"] = "extraction"
    if prior:
        row["prior_pick"] = prior
        disk = str(row.get("diskToday") or row.get("disk") or "").strip()
        suffix = f"prior disk pick: {prior}"
        row["diskToday"] = f"{disk} · {suffix}".strip(" · ") if disk else suffix
    if not row.get("reply_template"):
        rec = str(row.get("recommended") or "A")
        row["reply_template"] = f"ASF: FIVE-STEP — PICK: {qid} {rec}"
    return row


def _load_thread_gather_rows() -> list[dict]:
    if not THREAD_GATHER_JSON.is_file():
        return []
    try:
        return list(json.loads(THREAD_GATHER_JSON.read_text(encoding="utf-8")).get("rows") or [])
    except (OSError, json.JSONDecodeError):
        return []


def _load_session_architect_rows() -> list[dict]:
    if not SESSION_ARCHITECT_JSON.is_file():
        return []
    try:
        return list(json.loads(SESSION_ARCHITECT_JSON.read_text(encoding="utf-8")).get("rows") or [])
    except (OSError, json.JSONDecodeError):
        return []


def _load_chat_synthesis_rows() -> list[dict]:
    try:
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "form_official_chat_synthesis_v1.py"), "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        data = json.loads(proc.stdout or "{}")
        return list(data.get("rows") or [])
    except Exception:
        path = SINA / "form-official-chat-synthesis-v1.json"
        if path.is_file():
            try:
                return list(json.loads(path.read_text(encoding="utf-8")).get("rows") or [])
            except Exception:
                return []
        return []


def _load_conflict_audit_rows() -> list[dict]:
    """Evenced conflicts from disk — form_official_conflict_audit_v1.py."""
    existing: set[str] = set()
    for q in GATHER_META_ROWS:
        if q.get("id"):
            existing.add(str(q["id"]))
    if INTAKE_PATH.is_file():
        try:
            for q in json.loads(INTAKE_PATH.read_text(encoding="utf-8")).get("rows") or []:
                if q.get("id"):
                    existing.add(str(q["id"]))
        except Exception:
            pass
    try:
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "form_official_conflict_audit_v1.py"),
                "--json",
                "--existing-ids",
                ",".join(sorted(existing)),
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        data = json.loads(proc.stdout or "{}")
        return list(data.get("rows") or [])
    except Exception:
        path = SINA / "form-official-conflict-audit-v1.json"
        if path.is_file():
            try:
                return list(json.loads(path.read_text(encoding="utf-8")).get("rows") or [])
            except Exception:
                return []
        return []


def _sync_minder_reminder(total: int, *, write: bool) -> dict:
    """At GATHER_CAP: flash founder minder to fill. Below cap: agents focus BUILD."""
    at_cap = total >= GATHER_CAP
    hub_form = "http://127.0.0.1:13020/form/"
    reminder = {
        "schema": "form-official-gather-minder-v1",
        "at": _now(),
        "row_count": total,
        "gather_cap": GATHER_CAP,
        "cap_reached": at_cap,
        "agent_posture": "remind_founder_fill" if at_cap else "focus_build_plans",
        "one_line": (
            f"FORM_OFFICIAL · {total}/{GATHER_CAP} CAP — ASF FILL NOW · {hub_form}"
            if at_cap
            else f"FORM_OFFICIAL · {total}/{GATHER_CAP} gathering · agents BUILD until cap"
        ),
        "founder_tap": hub_form,
        "pick_format": "ASF: FIVE-STEP — PICK: [id] KEY",
        "law": "Rows stay until founder PICK · at 100 remind minder fast · else focus plans",
    }
    if not write:
        return reminder

    SINA.mkdir(parents=True, exist_ok=True)
    MINDER_RECEIPT.write_text(json.dumps(reminder, indent=2) + "\n", encoding="utf-8")

    rem_path = SINA / "founder-active-reminders-v1.json"
    rem: dict = {}
    if rem_path.is_file():
        try:
            rem = json.loads(rem_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            rem = {}
    rem.update(
        {
            "schema": "founder-active-reminders-v1",
            "set_at": _now(),
            "set_by": "form_official_gather_extraction_v1",
            "title": "FORM_OFFICIAL 100 CAP — fill official form" if at_cap else "FORM_OFFICIAL gather — BUILD parallel",
            "one_line": reminder["one_line"],
            "plan_doc": "SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md",
            "registry": str(hub_form),
            "form_gather_cap": at_cap,
            "honest_counts": {
                **(rem.get("honest_counts") or {}),
                "form_open": total,
                "form_gather_cap": GATHER_CAP,
            },
            "fix_order": [
                {
                    "priority": 1,
                    "id": "FORM-FILL",
                    "action": f"Hub → Answer on official form ({hub_form})",
                    "owner": "founder_tap",
                },
                {
                    "priority": 2,
                    "id": "RUN-INBOX",
                    "action": "Worker RUN INBOX — build plans parallel",
                    "owner": "founder_tap_worker",
                },
            ]
            if at_cap
            else (rem.get("fix_order") or [])[:3],
        }
    )
    rem_path.write_text(json.dumps(rem, indent=2) + "\n", encoding="utf-8")
    subprocess.run(
        [sys.executable, str(SCRIPTS / "founder_active_reminders_v1.py"), "--sync-h2"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    return reminder


def gather(*, write: bool = True) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from live_founder_decision_form_v1 import (  # noqa: WPS433
        OPEN_QUESTIONS_CORE,
        PENDING_OUTSIDE_AS_OPEN,
        _load_enf_open_questions,
        _load_intake_questions,
    )

    applied = _load_applied()
    buckets: list[tuple[str, list[dict]]] = [
        ("gather_meta", GATHER_META_ROWS),
        ("session_build", SESSION_GATHER_ROWS),
        ("session_architect", _load_session_architect_rows()),
        ("thread_marketplace_factory", _load_thread_gather_rows()),
        ("chat_synthesis", _load_chat_synthesis_rows()),
        ("conflict_audit", _load_conflict_audit_rows()),
        ("brain_cloud_intake", _load_intake_questions()),
        ("integrity_core", OPEN_QUESTIONS_CORE),
        ("pending_outside", PENDING_OUTSIDE_AS_OPEN),
        ("enforcement", _load_enf_open_questions()),
    ]

    seen: set[str] = set()
    merged: list[dict] = []
    by_source: dict[str, int] = {}

    for source, rows in buckets:
        count = 0
        for q in rows:
            qid = q.get("id")
            if not qid or qid in seen:
                continue
            seen.add(qid)
            merged.append(_normalize_row(q, source=source, applied=applied))
            count += 1
        by_source[source] = count

    merged.sort(key=lambda r: (TIER_ORDER.get(str(r.get("gather_tier")), 99), str(r.get("id"))))

    for i, row in enumerate(merged, start=1):
        row["number"] = i
        row["search_key"] = f"Q{i} {row.get('id')}"

    prior_count = sum(1 for r in merged if r.get("prior_pick"))
    open_fresh = len(merged) - prior_count
    minder = _sync_minder_reminder(len(merged), write=False)
    founder_reminder = minder.get("one_line")

    extraction = {
        "schema": "live-founder-decision-form-extraction-v1",
        "gathered_at": _now(),
        "phase": "extraction_gathering",
        "law": "Gather ALL → then unify · organize · prioritize — do not filter by applied during gather",
        "total_count": len(merged),
        "prior_pick_count": prior_count,
        "fresh_count": open_fresh,
        "by_source": by_source,
        "tier_counts": {
            tier: sum(1 for r in merged if r.get("gather_tier") == tier) for tier in TIER_ORDER
        },
        "rows": merged,
        "ids": [r["id"] for r in merged],
        "founder_reminder": founder_reminder,
        "founder_reminder_threshold": 100,
    }

    intake = {
        "schema": "live-founder-decision-form-intake-v1",
        "updated_at": _now(),
        "pack": "FORM_OFFICIAL_EXTRACTION_GATHER_v1",
        "phase": "extraction_gathering",
        "third_form_ref": "live-founder-decision-form-third-v1.json",
        "extraction_ref": str(EXTRACTION_PATH),
        "row_count": len(merged),
        "policy": "Full gather on Canvas · prior picks shown on card · unify phase follows founder order",
        "rows": merged,
    }

    open_cap = 0
    try:
        lf = SINA / "live-founder-decision-form-v1.json"
        if lf.is_file():
            open_cap = int(json.loads(lf.read_text(encoding="utf-8")).get("open_questions_count") or 0)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        open_cap = 0

    gathering_flag = {
        "schema": "form-official-gathering-phase-v1",
        "active": open_cap < 100,
        "phase": "hold_until_founder_fill" if open_cap >= 100 else "extraction_gathering",
        "started_at": _now(),
        "skip_applied_filter": True,
        "row_count": len(merged),
        "open_count": open_cap,
        "cap": 100,
        "append_blocked": open_cap >= 100,
        "law": "Rows stay until founder fills · at 100 urgent remind · Brain builds under cap",
        "minder_script": "scripts/form_official_minder_v1.py",
    }

    result = {
        "ok": len(merged) > 0,
        "gathered_at": _now(),
        "total_count": len(merged),
        "prior_pick_count": prior_count,
        "fresh_count": open_fresh,
        "by_source": by_source,
        "tier_counts": extraction["tier_counts"],
        "first_ten_ids": [r["id"] for r in merged[:10]],
        "extraction_path": str(EXTRACTION_PATH),
        "intake_path": str(INTAKE_PATH),
        "gathering_flag_path": str(GATHERING_FLAG),
        "founder_reminder": founder_reminder,
    }

    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        EXTRACTION_PATH.write_text(json.dumps(extraction, indent=2) + "\n", encoding="utf-8")
        INTAKE_PATH.write_text(json.dumps(intake, indent=2) + "\n", encoding="utf-8")
        GATHERING_FLAG.write_text(json.dumps(gathering_flag, indent=2) + "\n", encoding="utf-8")
        _sync_minder_reminder(len(merged), write=True)
        result["written"] = True
        result["cap_reached"] = len(merged) >= GATHER_CAP
        result["minder_one_line"] = founder_reminder

    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="FORM_OFFICIAL extraction & gathering")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write", action="store_true", default=True)
    ap.add_argument("--wire", action="store_true", help="Run form_official_wire_e2e after gather")
    args = ap.parse_args()
    result = gather(write=args.write)
    if args.wire and result.get("ok"):
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "form_official_wire_e2e_v1.py"), "--sync-surfaces", "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        try:
            wire = json.loads(proc.stdout or "{}")
        except json.JSONDecodeError:
            wire = {"ok": False, "error": "wire parse fail"}
        result["wire"] = wire
        result["ok"] = bool(result.get("ok")) and bool(wire.get("ok"))
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            f"{'OK' if result.get('ok') else 'FAIL'}: gathered={result.get('total_count')} "
            f"prior={result.get('prior_pick_count')} fresh={result.get('fresh_count')}"
        )
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
