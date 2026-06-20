#!/usr/bin/env python3
"""Synthesize Brain chat reasoning into evidenced FORM_OFFICIAL rows (final fix pass).

Reads live disk + brain chat arc — no invented problems.
Receipt: ~/.sina/form-official-chat-synthesis-v1.json
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
OUT = SINA / "form-official-chat-synthesis-v1.json"
FINAL_FIX = SINA / "live-founder-decision-form-final-fix-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _row(**kwargs) -> dict:
    qid = kwargs["id"]
    rec = kwargs.get("recommended", "A")
    r = dict(kwargs)
    r.setdefault("reply_template", f"ASF: FIVE-STEP — PICK: {qid} {rec}")
    r.setdefault("gather_tier", "P0_final_fix")
    r.setdefault("gather_category", "chat_reasoning")
    r.setdefault("gather_source", "chat_synthesis")
    r.setdefault("gather_phase", "final_fix")
    return r


def synthesize_rows() -> list[dict]:
    fn = _read(SINA / "factory-now-v1.json")
    wo = _read(SINA / "brain-outbound-work-order-active-v1.json")
    loop = _read(SINA / "loop-specialist-config-v1.json")
    fbe_map = _read(ROOT / "data/fbe_cloud_workspace_map_v1.json")
    catalog = _read(ROOT / "data/fbe_catalog_v1.json")
    fs = _read(ROOT / "data/sourcea-full-stack-100-fix-plan-v1.json")
    prog = fs.get("progress") or {}

    queue = str(fn.get("queue_sa") or "")
    valid = int(fn.get("valid_yes") or 0)
    loop_auto = bool(loop.get("loop_auto_dispatch_enabled"))
    catalog_n = len(catalog.get("factories") or catalog.get("items") or [])
    fs_done = int(prog.get("done") or 0)

    rows = [
        _row(
            id="Q-FINAL-01",
            title="North star after FBE-W6 — outbound drain vs cloud catalog sell?",
            question=(
                "Brain chat arc: FBE-W0..W6 shipped · you want 24/7 cloud factories + website catalog. "
                f"Disk also has outbound queue head {queue or 'sa-1100'} (66 upgrades). Which is P0 for daily work?"
            ),
            blocks="Brain chat e6507c62 · FBE fleet · outbound-factory queue · Phase C catalog",
            diskToday=f"valid_yes={valid} · queue={queue} · catalog_items={catalog_n} · full_stack={fs_done}/100",
            recommended="A",
            options=[
                "A — STRATEGIC-SLICE parallel: outbound P0 spine + FBE catalog cloud (recommended)",
                "B — Outbound 66 only — pause FBE catalog until U067",
                "C — FBE catalog/cloud only — pause outbound drain",
                "D — Commercial W1 film only — pause both",
            ],
            effect="Sets daily north star after factory builder proof",
            evidence_path="data/fbe_catalog_v1.json",
            asked_by="Brain chat · cloud migration + factory builder arc",
        ),
        _row(
            id="Q-FINAL-02",
            title="U031 RRL bay — implement on FBE cloud runner or Worker WORK?",
            question=(
                "Queue head U031 needs outbound-rrl-intelligence bay. FBE has cloud runner + bay registry on disk. "
                "Build bay on FBE cloud path, bounded Worker WORK, or defer?"
            ),
            blocks="brain-outbound-work-order-active · fbe_node_graph_v1 · U031 planned",
            diskToday=(
                f"upgrade_ref={wo.get('upgrade_ref')} · bay={wo.get('bay_slug')} · "
                f"pending_cloud_bay={wo.get('pending_cloud_bay')} · execution_plane={wo.get('execution_plane')}"
            ),
            recommended="A",
            options=[
                "A — Build outbound-rrl-intelligence FBE cloud bay first (recommended)",
                "B — Worker bounded WORK on Mac now",
                "C — sign_only until B0503 cloud consumer ships",
                "D — Defer U031 until FORM unify pass done",
            ],
            effect="Unblocks sa-1100 with architecture-aligned execution",
            evidence_path=str(SINA / "brain-outbound-work-order-active-v1.json"),
            asked_by="Brain chat · B0501 + U031 paradox",
        ),
        _row(
            id="Q-FINAL-03",
            title="Mono never_sync_as_authority — lock for all FBE cloud sync?",
            question=(
                "FBE-W3 note: adopt Mono never_sync_as_authority + bundle sync. "
                "Confirm law/graph never authored from cloud — receipts only?"
            ),
            blocks="fbe_cloud_workspace_map_v1.json · fbe_cloud_sync_v1.py",
            diskToday=f"authority_rule={fbe_map.get('authority_rule')} · never_sync_count={len(fbe_map.get('never_sync_as_authority') or [])}",
            recommended="A",
            options=[
                "A — YES — lock never_sync_as_authority on all FBE sync (recommended)",
                "B — Receipts only — no bundle sync yet",
                "C — Allow cloud to author graph SSOT",
                "D — Defer until Railway URL set",
            ],
            effect="Prevents cloud from becoming law SSOT",
            evidence_path=str(ROOT / "data/fbe_cloud_workspace_map_v1.json"),
            asked_by="Brain chat · FBE-W3 Mono adopt note",
        ),
        _row(
            id="Q-FINAL-04",
            title="Vocabulary lock — Kernel · Factory spec · 36 nodes · 14 buyer lines",
            question=(
                "Brain admitted mistake: 14 commercial lines ≠ machine count. CREED SSOT = 36 nodes. "
                "Lock: Kernel=runtime · Factory spec=SKU · 36 nodes=operators · 14 lines=buyers only?"
            ),
            blocks="CREED FACTORY_MESH.json · Brain self-improve pass",
            diskToday="Q-CONF-CREED-36V14 on form · CHURCH 22 nodes · FBE graph 76 nodes",
            recommended="A",
            options=[
                "A — YES — vocabulary law on all Brain/commercial copy (recommended)",
                "B — Hub UI shows 14 only",
                "C — Single merged node count for marketing",
                "D — Defer documentation",
            ],
            effect="Stops repeat 14-vs-36 factory builder confusion",
            evidence_path="YA5/PLUS ONE/CREED/.cursor/governance/FACTORY_MESH.json",
            asked_by="Brain chat · CREED 36 nodes correction",
        ),
        _row(
            id="Q-FINAL-05",
            title="Gathering complete — authorize UNIFY phase on 72+ rows?",
            question=(
                "Extraction/gather done: meta + conflicts + brain cloud + integrity + ENF + commercial on Canvas. "
                "Next: unify duplicates · organize tiers · prioritize P0 picks?"
            ),
            blocks="form-official-gathering-phase-v1.json · live-founder-decision-form-extraction-v1.json",
            diskToday="gathering_phase=active · rows on Canvas · awaiting founder UNIFY go",
            recommended="A",
            options=[
                "A — YES — gathering complete · start UNIFY pass (recommended)",
                "B — More extraction first — agents keep adding rows",
                "C — Pick P0 only now — skip unify",
                "D — Reset form — regather from scratch",
            ],
            effect="Transitions form workflow to organize/prioritize",
            evidence_path=str(SINA / "live-founder-decision-form-extraction-v1.json"),
            asked_by="ASF final fix order · this chat",
        ),
        _row(
            id="Q-FINAL-06",
            title="Brain disk-first law — every strategic turn cites FOUND/NOT FOUND?",
            question=(
                "You ordered: Brain must read most accurate live info · not chat memory. "
                "Lock B0007-style FOUND/NOT FOUND on every Brain strategic reply?"
            ),
            blocks="brain-live-context-v1.json · brain-cloud plan B0007 planned",
            diskToday="brain-live-context wired · form_official_line on surfaces",
            recommended="A",
            options=[
                "A — YES — disk path proof mandatory on Brain turns (recommended)",
                "B — Form picks only — Brain essays allowed",
                "C — Weekly disk pass only",
                "D — Defer until UNIFY done",
            ],
            effect="Prevents repeat Brain vocabulary/queue mistakes",
            evidence_path=str(SINA / "brain-live-context-v1.json"),
            asked_by="Brain chat · analyse and improve yourself",
        ),
        _row(
            id="Q-FINAL-07",
            title=f"Loop auto ON ({loop_auto}) + unmapped bay dispatch — safe?",
            question=(
                f"loop_auto_dispatch_enabled={loop_auto} · U031 bay unmapped · false-done guard wired. "
                "Keep loop auto, require mapped bay only, or pause auto until bays exist?"
            ),
            blocks="loop-specialist-config-v1.json · Q-CONF-FALSE-DONE-GUARD",
            diskToday=f"loop_auto={loop_auto} · sign_only for unmapped · U031 planned not done",
            recommended="C",
            options=[
                "A — Keep loop auto on all items",
                "B — Loop auto OFF until all bays mapped",
                "C — Auto dispatch mapped bays only · sign_only unmapped (recommended)",
                "D — Manual Hub tap per upgrade only",
            ],
            effect="Closes loop auto vs unmapped bay paradox from chat",
            evidence_path=str(SINA / "loop-specialist-config-v1.json"),
            asked_by="Brain cloud E2E · false-done incident",
        ),
        # --- Chat e6507c62 unpicked A/B/C (2026-06-19) — never chat-only ---
        _row(
            id="Q-CHAT-LANG-01",
            title="Agent reply language — فارسی school (unpicked A/B/C)",
            question=(
                "Brain offered language mode 2026-06-19. You did not pick A/B/C yet. "
                "Lock default voice for all human–machine replies so chat cannot lose this fork?"
            ),
            blocks="SINA_PROMPT_OS §4 فارسی · PLUS ONE LOCALE_LAW · founder language school thread",
            diskToday="hub founder-brief-fa · CREED FOUNDER_LANGUAGE_LAW.json · no disk pick yet",
            recommended="B",
            options=[
                "A — فارسی mainly — technical paths may stay English",
                "B — Bilingual — فارسی for meaning · English for paths/proof (recommended)",
                "C — English only — short · plain · no validator voice",
                "D — Founder adds one فارسی tone note on this row before pick",
            ],
            effect="Sets Brain/Worker founder-facing language default until changed on form",
            evidence_path="SINA_PROMPT_OS_SYSTEM_LOCKED_v1.md",
            asked_by="Brain chat e6507c62 · language school · unpicked",
        ),
        _row(
            id="Q-CHAT-NEXT-P0-01",
            title="Brain P0 unlock order — unpicked next taps",
            question=(
                "Brain listed P0 unlocks: Hub form 79 · ocree confirm · RUN INBOX sa-1200 · deploy SSE. "
                "Which is first tap after form rows are saved?"
            ),
            blocks="STRATEGIC-SLICE · commercial L3 75% · queue sa-1200 bound",
            diskToday="must_do_today=form 79 · w3_send_ready RED · inbox_pending sa-1200",
            recommended="A",
            options=[
                "A — Hub official form block 1 first (recommended)",
                "B — RUN INBOX Worker sa-1200 F002 broker submit",
                "C — deploy SSE cloud MCP + VIRLUX redeploy",
                "D — ocree:confirm_sent commercial L3 attest",
            ],
            effect="Orders founder daily path — prevents chat-only priority drift",
            evidence_path="~/.sina/live-ongoing-prompts-next-10-v1.json",
            asked_by="Brain chat e6507c62 · prioritize level-up · unpicked",
        ),
        _row(
            id="Q-CHAT-CLOUD-01",
            title="MCP proof — local PASS vs cloud SSE ship",
            question=(
                "validate-all-e2e 6/6 PASS on local :8787/:8790. Cloud SSE not live. "
                "Ship cloud proof layer now or stay local until form P0 picks done?"
            ),
            blocks="mcp-chain-campus · cursor marketplace Card1 · deploy_mcp_sse_vercel",
            diskToday="E2E local OK · SSE INFO not running · npm publish blocked founder login",
            recommended="B",
            options=[
                "A — deploy SSE + VIRLUX redeploy now",
                "B — Stay local E2E until Hub form P0 block answered (recommended)",
                "C — npm Card1 publish before cloud SSE",
                "D — Defer cloud + npm until UNIFY phase",
            ],
            effect="Cloud vs local proof layer sequencing",
            evidence_path="scripts/validate-all-e2e-v1.sh",
            asked_by="Brain chat e6507c62 · E2E audit · unpicked",
        ),
        _row(
            id="Q-CHAT-PLUSONE-01",
            title="PLUS ONE voice law — wire before Brain copy?",
            question=(
                "You said: find everything on search · PLUS ONE has language resources. "
                "Lock Brain to read CREED language law before founder-facing copy?"
            ),
            blocks="PLUS ONE INDEX · LOCALE_LAW · FOUNDER_LANGUAGE_LAW · FALUX prove",
            diskToday="fa required in LOCALE_LAW · founder-language-report ok · fidelity locale 20% gap",
            recommended="A",
            options=[
                "A — YES — PLUS ONE language law + Prompt OS §4 before voice (recommended)",
                "B — Prompt OS §4 فارسی only — skip PLUS ONE on non-locale topics",
                "C — English commercial copy only — defer فارسی",
                "D — Defer until Q-CHAT-LANG-01 answered",
            ],
            effect="Stops agent improvising voice without campus SSOT",
            evidence_path="YA5/PLUS ONE/CREED/.cursor/governance/FOUNDER_LANGUAGE_LAW.json",
            asked_by="Brain chat e6507c62 · PLUS ONE resources · unpicked",
        ),
        _row(
            id="Q-CHAT-PUBLISH-01",
            title="Cursor marketplace Card1 — npm publish timing",
            question=(
                "Card1 bundle on disk · npm pack ready · founder npm login required. "
                "Publish now or wait for form/language picks?"
            ),
            blocks="cursor-plugin/sourcea-forge-governance · multi-factory advisory Card1",
            diskToday="validate-mcp-chain-motor PASS · npm publish blocked · marketplace submit open",
            recommended="B",
            options=[
                "A — npm login + publish Card1 now",
                "B — After Q-CHAT-NEXT-P0-01 form block + language pick (recommended)",
                "C — Cloud SSE first · then npm",
                "D — Defer marketplace until MergePack L1 ship",
            ],
            effect="Commercial publish sequencing vs governance picks",
            evidence_path="data/multi-factory-enterprise-tree-advisory-v1.json",
            asked_by="Brain chat e6507c62 · bootstrap pack · unpicked",
        ),
    ]
    return rows


def build(*, write: bool = True) -> dict:
    rows = synthesize_rows()
    result = {
        "ok": True,
        "schema": "form-official-chat-synthesis-v1",
        "synthesized_at": _now(),
        "brain_chat": "e6507c62-18c5-4a03-bb35-e804507dff18",
        "law": "Chat reasoning distilled to evidenced form rows only",
        "row_count": len(rows),
        "ids": [r["id"] for r in rows],
        "rows": rows,
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        FINAL_FIX.write_text(
            json.dumps(
                {
                    "schema": "live-founder-decision-form-final-fix-v1",
                    "saved_at": _now(),
                    "edition": "final_fix",
                    "title": "Brain chat reasoning → FORM_OFFICIAL final fix pack",
                    "brain_chat": "e6507c62-18c5-4a03-bb35-e804507dff18",
                    "question_ids": result["ids"],
                    "synthesis_path": str(OUT),
                    "law": "CHECK chat reasoning · UPDATE form · FINAL FIX wire",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        result["paths"] = {"synthesis": str(OUT), "final_fix": str(FINAL_FIX)}
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Chat reasoning → form rows")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    result = build()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"OK: {result['row_count']} synthesis rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
