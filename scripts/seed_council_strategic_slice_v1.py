#!/usr/bin/env python3
"""Idempotent seed — Council brief + topic + mind share + Track cards + founder directive."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
SINA_HOME = Path.home() / ".sina"
COUNCIL_ROOT = SINA_HOME / "council-room"
MIND_SHARE_PATH = COUNCIL_ROOT / "mind-share.jsonl"
TOPICS_PATH = COUNCIL_ROOT / "topics.jsonl"
DIRECTIVES_PATH = SINA_HOME / "founder-directives.jsonl"
COMMITMENTS_PATH = SINA_HOME / "founder-commitments.json"
SEED_MARKER = COUNCIL_ROOT / "strategic-slice-v1.seed.json"

BRIEF_DOC = "brain-os/law/COUNCIL_BRIEF_STRATEGIC_SLICE_EVAL_L0_ENFORCE_LOCKED_v1.md"
TOPIC_TITLE = "Strategic slice: Eval-1 + L0/L1 + ENFORCE map (not new D-module)"
TOPIC_NOTE = (
    "Founder verdict: GPT/Claude architecture reviews are compare-only. "
    "Ship Eval-1 sustain, L0/L1 deepen, ENFORCE bypass transparency. "
    "Keep rules-in-charge loop. Scope: TrustField + AI Dev Bridge + maintainer."
)

TRACK_CARDS = [
    {
        "id": "track-strategic-slice-v1",
        "title": "Strategic slice — Eval-1 + L0/L1 + ENFORCE map",
        "detail": (
            "Founder verdict LOCKED. Sustain Eval-1 structural benchmark; deepen L0/L1 hub signals; "
            "publish ENFORCE bypass transparency. NOT new D-module. Rules-in-charge loop every round. "
            f"Brief: {BRIEF_DOC}"
        ),
        "priority": "critical",
        "thread": "THREAD-ECOSYSTEM",
        "tab": "command",
        "drill_kind": "council",
        "drill_id": "strategic-slice-v1",
    },
    {
        "id": "track-trustfield-slice-v1",
        "title": "TrustField — align lane to strategic slice",
        "detail": (
            "Read Council brief. Infra/law truth (B-001, GLOBAL_BLOCKERS) only — no SourceA D-module work. "
            "Attest council brief on Scoreboard. Mind Share if lane touches model ingress."
        ),
        "priority": "high",
        "thread": "THREAD-PORTFOLIO",
        "tab": "council-room",
        "drill_kind": "subject",
        "drill_id": "subj-trustfield",
    },
    {
        "id": "track-wire-slice-v1",
        "title": "AI Dev Bridge — wire evidence under strategic slice",
        "detail": (
            "G1/G2/G3 wire proofs via Actions/spine — no new pre-LLM modules. "
            "Report ENFORCE bypass awareness in Mind Share if wire touches OpenRouter."
        ),
        "priority": "high",
        "thread": "THREAD-WIRE",
        "tab": "council-room",
        "drill_kind": "subject",
        "drill_id": "subj-wire-repo",
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def _load_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def _seed_directive() -> dict:
    text = (
        "STRATEGIC SLICE (LOCKED): Next move = Eval-1 sustain + L0/L1 deepen + ENFORCE bypass map — "
        "NOT another D-module. GPT/Claude arch = compare only. Rules-in-charge loop mandatory. "
        f"See {BRIEF_DOC} in Council Room."
    )
    for row in _load_jsonl(DIRECTIVES_PATH):
        if BRIEF_DOC in (row.get("text") or ""):
            return {"ok": True, "skipped": True, "reason": "directive exists"}
    row = {
        "id": f"DIR-{uuid.uuid4().hex[:10]}",
        "at": _now(),
        "text": text,
        "source": "founder_verdict",
        "visible_to": "all_agents",
        "brief_doc": BRIEF_DOC,
    }
    _append_jsonl(DIRECTIVES_PATH, row)
    return {"ok": True, "directive": row}


def _seed_mind_share() -> dict:
    marker = "STRATEGIC-SLICE-EVAL-L0-ENFORCE-v1"
    for row in _load_jsonl(MIND_SHARE_PATH):
        if marker in (row.get("topic") or "") or marker in (row.get("body") or ""):
            return {"ok": True, "skipped": True, "reason": "mind share exists"}
    body = (
        "PROCEDURE (maintainer): Ship strategic slice hub-side only — Eval-1 panel green, "
        "L0/L1 panel green, gate receipts panel shows enforce + bypass note, WTM do_now = slice. "
        "Agents: read COUNCIL_BRIEF_STRATEGIC_SLICE_EVAL_L0_ENFORCE_LOCKED_v1.md before build. "
        "Never convert GPT/Claude architecture paste into new .mdc law without supersession check. "
        "TrustField + AI Dev Bridge: lane work only; maintainer owns SourceA."
    )
    row = {
        "id": f"MIND-{uuid.uuid4().hex[:10]}",
        "at": _now(),
        "agent_id": "sinaai_maintainer",
        "label": "SinaAI Maintainer",
        "lane": "SourceA",
        "repo_root": str(SOURCE_A),
        "kind": "procedure",
        "topic": marker,
        "topic_norm": "strategic-slice-eval-l0-enforce-v1",
        "body": body,
        "stance_hint": "lean_yes",
    }
    _append_jsonl(MIND_SHARE_PATH, row)
    return {"ok": True, "mind_share": row}


def _seed_topic() -> dict:
    for row in _load_jsonl(TOPICS_PATH):
        if (row.get("title") or "").strip() == TOPIC_TITLE:
            return {"ok": True, "skipped": True, "topic": row}
    row = {
        "id": f"COUNCIL-{uuid.uuid4().hex[:10]}",
        "at": _now(),
        "title": TOPIC_TITLE,
        "category": "process",
        "status": "open",
        "created_by": "sinaai_maintainer",
        "related_agents": ["sinaai_maintainer", "trustfield", "ai_dev_bridge_os"],
        "options": [
            {"id": "A", "label": "Proceed — Eval-1 + L0/L1 + ENFORCE map (founder verdict)"},
            {"id": "B", "label": "Defer — pursue L8 embeddings or new D-module first"},
        ],
        "note": TOPIC_NOTE,
        "brief_doc": BRIEF_DOC,
    }
    _append_jsonl(TOPICS_PATH, row)
    return {"ok": True, "topic": row}


def _write_json_atomic(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(path)


def _load_commitments_store() -> dict:
    if not COMMITMENTS_PATH.is_file():
        return {"manual": [], "pinned_ids": [], "started_log": {}}
    try:
        store = json.loads(COMMITMENTS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"manual": [], "pinned_ids": [], "started_log": {}}
    if not isinstance(store, dict):
        return {"manual": [], "pinned_ids": [], "started_log": {}}
    return store


def _seed_track_cards() -> dict:
    store = _load_commitments_store()
    manual = list(store.get("manual") or [])
    pins = set(store.get("pinned_ids") or [])
    added = []
    existing_ids = {m.get("id") for m in manual}
    for card in TRACK_CARDS:
        if card["id"] in existing_ids:
            pins.add(card["id"])
            continue
        item = {
            "id": card["id"],
            "title": card["title"],
            "detail": card["detail"],
            "text": card["detail"],
            "status": "open",
            "priority": card["priority"],
            "thread": card["thread"],
            "tab": card["tab"],
            "drill_kind": card.get("drill_kind", "track"),
            "drill_id": card.get("drill_id", card["id"]),
            "started_at": _now(),
            "never_drop": True,
            "source": "council_brief",
            "brief_doc": BRIEF_DOC,
        }
        manual.insert(0, item)
        pins.add(card["id"])
        added.append(card["id"])
    store["manual"] = manual
    store["pinned_ids"] = sorted(pins)
    store["updated_at"] = _now()
    _write_json_atomic(COMMITMENTS_PATH, store)
    try:
        COMMITMENTS_PATH.chmod(0o600)
    except OSError:
        pass
    return {"ok": True, "added": added, "pinned": sorted(pins)}


def verify_seed_marker() -> tuple[bool, str]:
    """Post-run proof — marker logged with expected brief (sa-0218)."""
    if not SEED_MARKER.is_file():
        return False, "seed marker missing"
    try:
        marker = json.loads(SEED_MARKER.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return False, f"seed marker unreadable: {exc}"
    if marker.get("brief_doc") != BRIEF_DOC:
        return False, "seed marker brief_doc mismatch"
    if marker.get("schema") != "strategic-slice-seed-v1":
        return False, "seed marker schema mismatch"
    return True, "ok"


def run_seed(*, force: bool = False) -> dict:
    if SEED_MARKER.is_file() and not force:
        try:
            prior = json.loads(SEED_MARKER.read_text(encoding="utf-8"))
            if prior.get("brief_doc") == BRIEF_DOC:
                ok, detail = verify_seed_marker()
                if ok:
                    return {"ok": True, "skipped": True, "marker": str(SEED_MARKER), "prior": prior}
        except (json.JSONDecodeError, OSError):
            pass
    results = {
        "directive": _seed_directive(),
        "mind_share": _seed_mind_share(),
        "topic": _seed_topic(),
        "track": _seed_track_cards(),
    }
    for key, row in results.items():
        if not (row or {}).get("ok"):
            return {"ok": False, "error": f"{key} seed failed", "results": results}
    marker = {
        "schema": "strategic-slice-seed-v1",
        "at": _now(),
        "brief_doc": BRIEF_DOC,
        "results": results,
    }
    COUNCIL_ROOT.mkdir(parents=True, exist_ok=True)
    _write_json_atomic(SEED_MARKER, marker)
    ok, detail = verify_seed_marker()
    if not ok:
        return {"ok": False, "error": detail, "results": results}
    return {"ok": True, "marker": str(SEED_MARKER), "results": results}


if __name__ == "__main__":
    import sys

    out = run_seed(force="--force" in sys.argv)
    print(json.dumps(out, indent=2))
