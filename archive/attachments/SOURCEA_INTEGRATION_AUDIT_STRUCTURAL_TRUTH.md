# SOURCEA Integration Audit — Structural Truth

**Saved:** 2026-06-12T19:58:28Z · **Retrofit:** doc-datetime-law batch retrofit
- **generated:** 2026-06-12T19:58:28Z
- **workspace:** `/Users/sinakazemnezhad/Desktop/SourceA`
- **purpose:** External LLM integration audit — schemas + execution logic + runtime
- **naming:** JudgeRoom = Judge Center (`judge_center_*`) · ThreadRoom = `thread_room_*`

---
## 1. THE SCHEMAS

### 1.1 M1 Canvas — TypeScript row types

```typescript
type QType = "choice4" | "yesno" | "text";
type Owner = "F" | "M" | "B";

type FormOption = {
  key: string;
  label: string;
  short: string;
  ifYouPick: string;
};

type FormQuestion = {
  id: string;
  phase: string;
  category: string;
  categoryLabel: string;
  subject: string;
  question: string;
  help: string;
  diskToday: string;
  type: QType;
  options?: FormOption[];
  recommended?: string;
  textLabel?: string;
  textPlaceholder?: string;
  maintainerAction: string;
  founderAction: string;
  agent?: string;
  agentLabel?: string;
  decisive?: boolean;
  shipped?: string;
};

type Step = { id: string; text: string; owner: Owner; decisive?: boolean };
```

### 1.2 M1 Canvas — OpenRowSpec type + terminology

```typescript
export type OpenRowSpec = {
  id: string;
  subject: string;
  /** One-line what this row is about */
  summary: string;
  /** Full case — must be readable without opening another chat */
  caseStory: string;
  /** Why you are being asked */
  whyItMatters: string;
  /** Plain English disk state */
  diskTodayPlain: string;
  ownerAgentId: string;
  ownerChatName: string;
  ownerDoes: string;
  diskRecordBy: string;
  terms?: { term: string; means: string }[];
  optionsPlain: Record<string, string>;
  /** What happens logged if you pick this key */
  optionEffects?: Record<string, string>;
};

export const FORM_TERMINOLOGY_REQUIRED: { term: string; sayInstead: string }[] = [
  { term: "Hub Track", sayInstead: "sidebar projection only — not the form office" },
  { term: "Maintainer explains in chat", sayInstead: "case written on the form row (this card)" },
  { term: "EXTERNAL_CRITIC", sayInstead: "ChatGPT/advisor paste — report only, never build order" },
  { term: "FORM_OFFICIAL", sayInstead: "this Canvas — Pending confirmations · Submit when done" },
  { term: "Canva", sayInstead: "Cursor Canvas" },
  { term: "616 / factory drain hero", sayInstead: "background honest counter — not pitch headline" },
  { term: "pre-execution", sayInstead: "Before money or settlement moves — governance gate" },
  { term: "RWA infrastructure", sayInstead: "Real-world asset readiness · evidence · policy — not token custody pitch" },
  { term: "evidence-grade", sayInstead: "Tamper FAIL on camera · receipt logged" },
  { term: "governance architect", sayInstead: "Design + audit layer — not legal advice" },
  { term: "Trust Brief", sayInstead: "Named product SKU — Trust Brief" },
  { term: "hub is not a goal", sayInstead: "Hub projects disk — building the agentic engine is the goal" },
  { term: "§OPEN_QUESTIONS", sayInstead: "use plain English on the form card" },
  { term: "616 hero", sayInstead: "use plain English on the form card" },
  { term: "Trust OS build", sayInstead: "use plain English on the form card" },
  { term: "We move money", sayInstead: "RPAA-safe advisory only — see linkedin-voice.yaml perimeter.say" },
];
```

**Canonical open-row example (7.05):**

```typescript
"7.05": {
    id: "7.05",
    subject: "Who wins when agents push AUTO-RUN but you still have open form picks?",
    summary:
      "Some chats treated “start the factory” as today’s top job while your form office still had unanswered permission rows. This row locks form-first: your picks beat chat heroes.",
    caseStory:
      "What happened: In early June, Brain and factory lanes surfaced “START AUTO RUN” and factory drain scores as the daily headline. " +
      "At the same time you still had open rows on this Canvas — including film prep, wire proof, and commercial closure. " +
      "Your rule (already present as pick 9.07 A and FR-003): the form office wins. Agents execute your confirmed picks; they do not skip them because a chat hero looks urgent. " +
      "Concrete example: Brain suggested running factory drain while you still had 15 open Canvas rows. That would rebuild Hub and burn agent time instead of filming Week-1 proof or honest Week-3 outreach. " +
      "This row is Conflict Case 1 in the ACE conflict room — not a new law, just your call on how we handle it going forward.",
    whyItMatters:
      "If AUTO-RUN wins over open picks, agents silently reorder your six-month arc. You think you decided on film and first dollar; they ship Hub features and factory plans instead.",
    diskTodayPlain:
      "Case 1 logged in ACE · continue_work mode · FR-003 + pick 9.07 A already say form-first · this row asks you to confirm DEFER (keep working, review weekly)",
    ownerAgentId: "aect",
    ownerChatName: "AECT",
    ownerDoes:
      "AECT marks Case 1 disposition in the conflict room registry — no extra narrative chat needed once you pick.",
    diskRecordBy:
      "Maintainer 2 writes only your PICK to form JSON (~30 seconds). AECT owns the conflict-room row.",
    terms: [
      { term: "AUTO-RUN", means: "Factory lane asking agents to drain plan queue — not your P0 unless you pick it" },
      { term: "form office", means: "This Canvas — Pending confirmations · Submit when done" },
    ],
    optionsPlain: {
      DEFER:
        "Log DEFER — keep executing current picks; Case 1 stays open for weekly review (recommended · matches how you already work)",
      A: "Auto-resolve now — permanently declare form-first law wins in ACE without weekly review",
      B: "Escalate live — schedule a founder call on Case 1 before any related work continues",
      C: "Stop related work — freeze factory and Hub rebuild until Case 1 is closed",
    },
    optionEffects: {
      DEFER: "Case 1 stays logged · agents keep film/W3 picks · weekly ACE review · no new hero overrides",
      A: "ACE registry updated · form-first permanent · Brain/factory must refuse AUTO-RUN hero when form rows open",
      B: "Case 1 escalated · AECT schedules founder sync · related lanes pause until call",
      C: "Hard stop on factory drain + Hub rebuild heroes until you close Case 1",
    },
  }
}
```

### 1.3 Form machine — payload() return shape

```python
def payload() -> dict:
    form_ok = FORM_MD.is_file()
    norm_ok = NORM_MD.is_file()
    first_ok = FIRST_FORM_ARCHIVE.is_file()
    pending_high = 0
    if form_ok:
        body = FORM_MD.read_text(encoding="utf-8", errors="replace")
        pending_high += body.count("| **high** |")
    open_rows = all_open_questions()
    oq_count = len(open_rows)
    numbered_questions = [
        {**q, "number": i, "search_key": f"Q{i} {q.get('id', '')}"}
        for i, q in enumerate(open_rows, start=1)
    ]
    answers_ok = ANSWERS_RECEIPT_MD.is_file() and ANSWERS_RECEIPT_JSON.is_file()
    awaiting_picks = oq_count > 0
    return {
        "ok": form_ok and norm_ok and first_ok and answers_ok,
        "schema": "live-founder-decision-form-v2",
        "form_edition": FORM_EDITION,
        "asf_filled_at": ASF_FILLED_AT,
        "drift_floor": DRIFT_FLOOR,
        "first_form": {
            "saved": first_ok,
            "archive_path": str(FIRST_FORM_ARCHIVE),
            "snapshot_path": str(FIRST_FORM_JSON),
            "question_count": len(FIRST_FORM_QUESTIONS),
        },
        "second_form": {
            "saved": SECOND_FORM_ARCHIVE.is_file() and SECOND_FORM_JSON.is_file(),
            "archive_path": str(SECOND_FORM_ARCHIVE),
            "snapshot_path": str(SECOND_FORM_JSON),
            "applied_pick_count": len(_canvas_applied_pick_ids()),
            "open_remaining_count": oq_count,
        },
        "v2_answers": {
            "filled": True,
            "count": len(ANSWERED_V2),
            "receipt_md": str(ANSWERS_RECEIPT_MD),
            "receipt_json": str(ANSWERS_RECEIPT_JSON),
            "rows": ANSWERED_V2,
        },
        "updated_at": _now(),
        "form_path": str(FORM_MD),
        "norm_path": str(NORM_MD),
        "hub_repair_policy": HUB_REPAIR_POLICY,
        "needs_asf_fill": not answers_ok,
        "awaiting_founder_picks": awaiting_picks,
        "hub_tab": "track",
        "doc_pick": "SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md",
        "answers_doc_pick": str(ANSWERS_RECEIPT_MD.relative_to(ROOT)),
        "first_form_doc_pick": str(FIRST_FORM_ARCHIVE.relative_to(ROOT)),
        "second_form_doc_pick": str(SECOND_FORM_ARCHIVE.relative_to(ROOT)),
        "answered_count": len(SHIPPED_CANVAS) + len(CANVAS_SESSION_PICKS) + len(ANSWERED_V2),
        "canvas_session_picks": CANVAS_SESSION_PICKS,
        "canvas_shipped": sorted(SHIPPED_CANVAS),
        "canvas_open": sorted(q["id"] for q in open_rows),
        "canvas_open_count": oq_count,
        "form_intake": {
            "path": str(INTAKE_PATH),
            "pending_count": len(_load_intake_questions()),
            "policy": "Agents append new human-permission forks via form_conflict_intake_v1.py — regen Canvas + Submit",
        },
        "founder_voice_sources": _founder_voice_sources(),
        "open_questions": numbered_questions,
        "open_questions_count": oq_count,
        "form_headline": _form_headline(oq_count),
        "pending_outside_count": pending_high,
        "norm_caps_locked": norm_ok and "100% equivalent" in NORM_MD.read_text(encoding="utf-8", errors="replace"),
        "live_policy": "form v2 filled · hub repair until RT LIVE gate PASS · read receipt on SCAN",
        "founder_reply_law": "SOURCEA_LIVE_FOUNDER_DECISION_FORM_V2_ANSWERS_RECEIPT_2026-06-11_LOCKED_v1.md",
        "parse_pick_demo": _parse_pick("ASF: FIVE-STEP — PICK: 10.10 D — pause"),
    }
```

### 1.4 Form open-question row shape (Python dict)

```json
{
  "id": "7.05",
  "number": 5,
  "title": "string",
  "question": "string",
  "blocks": "string",
  "diskToday": "string",
  "recommended": "KEY",
  "options": ["KEY — label"],
  "effect": "string",
  "option_effects": { "KEY": "effect line" },
  "asked_by": "string",
  "reply_template": "ASF: FIVE-STEP — PICK: {id} {KEY}"
}
```

**Disk paths:** `~/.sina/live-founder-decision-form-v1.json` · `~/.sina/canvas-form-picks-applied-v1.json` · `~/.sina/forms/thread-enforcement-forks-v1.yaml`

### 1.5 Governance Event Spine

```python
EVENT_TYPES = frozenset(
    {
        "FOUNDER_PICK",
        "FOUNDER_SIGNAL",
        "WORKER_ROUND",
        "LAW_TOUCHED",
        "PROPAGATION",
        "VALIDATOR_PASS",
        "EXTERNAL_CRITIC_INGEST",
        "RECOVERY_FOUND",
        "IMPACT_SCAN",
    }
)

OBJECT_KINDS = frozenset({"law", "task", "founder_request", "pick", "system"})


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _checksum(row: dict) -> str:
    body = {k: v for k, v in row.items() if k != "checksum"}
    raw = json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _version_for_object(object_id: str) -> int:
    if not SPINE_PATH.is_file():
        return 1
    last = 0
    for line in SPINE_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        if o.get("object_id") == object_id:
            last = max(last, int(o.get("version") or 0))
    return last + 1


def append_event(
    *,
    event_type: str,
    object_id: str,
    object_kind: str,
    agent_id: str = "system",
    parent_event_id: str = "",
    correlation_id: str = "",
    payload: dict | None = None,
    projection_targets: list[str] | None = None,
    gate: str = "",
    proof: str = "",
    version: int | None = None,
    law_id: str = "",
    skill_id: str = "",
    validator_set: list[str] | None = None,
    affected_objects: list[str] | None = None,
    projection_version: str = "",
    status: str = "committed",
) -> dict:
    if event_type not in EVENT_TYPES:
        return {"ok": False, "error": f"invalid event_type: {event_type}"}
    if object_kind not in OBJECT_KINDS:
        return {"ok": False, "error": f"invalid object_kind: {object_kind}"}
    ver = version if version is not None else _version_for_object(object_id)
    cid = correlation_id or str(uuid.uuid4())
    eid = f"GEV-{uuid.uuid4().hex[:12]}"
    replay_pointer = f"{event_type}:{object_id}:{ver}"
    vset = list(dict.fromkeys(validator_set or ([] if not proof else [proof] if proof.endswith(".sh") else [])))
    row = {
        "schema": SCHEMA,
        "event_id": eid,
        "parent_event_id": parent_event_id or None,
        "correlation_id": cid,
        "at": _now(),
        "agent_id": agent_id,
        "event_type": event_type,
        "object_id": object_id,
        "object_kind": object_kind,
        "version": ver,
        "law_id": law_id or None,
        "skill_id": skill_id or None,
        "validator_set": vset,
        "affected_objects": affected_objects or [],
        "replay_pointer": replay_pointer,
        "replay_key": replay_pointer,
        "projection_version": projection_version or PROJECTION_VERSION,
        "status": status,
        "payload": payload or {},
        "projection_targets": projection_targets or [],
        "gate": gate or None,
        "proof": proof or None,
    }
    row["checksum"] = _checksum(row)
    SINA.mkdir(parents=True, exist_ok=True)
    with SPINE_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"ok": True, "event": row, "path": str(SPINE_PATH)}


def read_all_rows() -> list[dict]:
    if not SPINE_PATH.is_file():
        return []
    rows: list[dict] = []
    for line in SPINE_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def find_by_replay_pointer(replay_pointer: str) -> dict | None:
    for row in reversed(read_all_rows()):
        ptr = row.get("replay_pointer") or row.get("replay_key")
        if ptr == replay_pointer:
            return row
    return None


def find_by_event_id(event_id: str) -> dict | None:
    for row in reversed(read_all_rows()):
        if row.get("event_id") == event_id:
            return row
    return None


def find_last(*, event_type: str = "", status: str = "") -> dict | None:
    rows = read_all_rows()
    for row in reversed(rows):
        if event_type and row.get("event_type") != event_type:
            continue
        if status and row.get("status") != status:
            continue
        ok, _ = validate_row(row)
        if not ok:
            continue
        return row
    return None


def object_history(*, object_id: str, max_version: int | None = None) -> list[dict]:
    out: list[dict] = []
    for row in read_all_rows():
        if row.get("object_id") != object_id:
            continue
        ver = int(row.get("version") or 0)
        if max_version is not None and ver > max_version:
            continue
        out.append(row)
    return out


def tail(*, n: int = 20, event_type: str = "") -> list[dict]:
    if not SPINE_PATH.is_file():
        return []
    rows: list[dict] = []
    for line in SPINE_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event_type and o.get("event_type") != event_type:
            continue
        rows.append(o)
    return rows[-n:]


def replay_candidates(*, event_type: str = "WORKER_ROUND", limit: int = 10) -> list[dict]:
    """G4-ready: list recent rows with replay_key for recovery."""
    return tail(n=limit * 3, event_type=event_type)[-limit:]


def validate_row(row: dict) -> tuple[bool, str]:
    schema = row.get("schema")
    if schema not in (SCHEMA, SCHEMA_LEGACY):
        return False, "bad schema"
    base = (
        "event_id",
        "correlation_id",
        "at",
        "agent_id",
        "event_type",
        "object_id",
        "object_kind",
        "version",
        "checksum",
    )
    for f in base:
        if not row.get(f):
            return False, f"missing {f}"
    if not (row.get("replay_pointer") or row.get("replay_key")):
        return False, "missing replay_pointer"
    if schema == SCHEMA:
        for f in ("validator_set", "affected_objects", "projection_version", "status"):
            if f not in row:
                return False, f"missing {f}"
    if row.get("event_type") not in EVENT_TYPES:
        return False, "bad event_type"
    exp = row.get("checksum")
    row_copy = dict(row)
    chk = _checksum(row_copy)
    if exp != chk:
        return False, "checksum mismatch"
    return True, "ok"
```

**Live spine row (last line):**

```json
{"schema": "governance-event-spine-v1.1", "event_id": "GEV-b4cef39a9b57", "parent_event_id": null, "correlation_id": "de8a0b23-3ac8-4144-be84-dc853f039309", "at": "2026-06-12T19:45:48Z", "agent_id": "maintainer", "event_type": "RECOVERY_FOUND", "object_id": "governance_self_heal_g7", "object_kind": "system", "version": 55, "law_id": "GOV_EVENT_SPINE", "skill_id": "governance-self-heal-g7", "validator_set": ["validate-governance-self-heal-g7-v1.sh"], "affected_objects": ["projection:hub", "projection:monitor", "projection:catalog"], "replay_pointer": "RECOVERY_FOUND:governance_self_heal_g7:55", "replay_key": "RECOVERY_FOUND:governance_self_heal_g7:55", "projection_version": "hub-align-v1", "status": "committed", "payload": {"heal_count": 1, "warn": 2, "fail": 0}, "projection_targets": ["hub", "monitor", "catalog", "truth_bundle"], "gate": "governance_self_heal_daemon_v1", "proof": "/Users/sinakazemnezhad/.sina/governance-self-heal-receipt-v1.json", "checksum": "f77338f163e7bfde"}
```

### 1.6 Receipt — enforcement-action-receipt-v1

```json
{
  "schema": "enforcement-action-receipt-v1",
  "receipt_id": "RCP-5ae2032dda4e",
  "intent_id": "copilot-allow-8cea24e2",
  "action": "enable",
  "object_id": "NF-COPILOT-POLICY-DEMO",
  "rule_id": "P-001",
  "agent_id": "investor_demo",
  "policy_id": "COPILOT-ALLOW-READONLY",
  "approval_ref": "TLE-2026-001",
  "demo_case": "allow",
  "gate_status": "PASS",
  "gate_reasons": [],
  "created_at": "2026-06-12T18:27:22Z",
  "law": "brain-os/demo/governance_demo_policy_v1.json",
  "outcome": "COMMITTED",
  "status": "DONE",
  "evidence": "EXECUTE_STUB: policy applied",
  "spine_event_id": "GEV-246e49437117",
  "spine_checksum": "3ee5caec0f1f71e8",
  "proof_path": "/Users/sinakazemnezhad/.sina/demo-enforcement/receipts/demo-ca940bf32c6b.json",
  "receipt_checksum": "96f6e3c8228ed130"
}
```

**Receipt write + checksum (commit_intent_v1):**

```python
def _checksum(body: dict) -> str:
    stripped = {k: v for k, v in body.items() if k != "receipt_checksum"}
    raw = json.dumps(stripped, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def verify_receipt_checksum(rec: dict) -> bool:
    expected = rec.get("receipt_checksum")
    if not expected:
        return False
    return _checksum(rec) == expected


def _write_receipt(rec: dict, *, bind_spine: bool) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    rec = dict(rec)
    rec.pop("receipt_checksum", None)
    rec.pop("spine_event_id", None)
    rec.pop("spine_checksum", None)

    if bind_spine:
        from governance_event_spine_v1 import append_event  # noqa: WPS433

        RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
        LATEST_DEMO.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
        spine_res = append_event(
            event_type="VALIDATOR_PASS",
            object_id=str(rec.get("object_id") or "ENFORCEMENT-DEMO"),
            object_kind="system",
            agent_id=str(rec.get("agent_id") or "commit_intent_v1"),
            law_id=str(rec.get("rule_id") or "ENFORCEMENT_6MO"),
            skill_id="commit_intent_v1",
            validator_set=["validate-enforcement-demo-v1.sh", "validate-universe-invariants-v1.sh"],
            affected_objects=[str(rec.get("object_id") or "ENFORCEMENT-DEMO")],
            gate="commit_intent",
            proof=str(LATEST_DEMO),
            payload={
                "intent_id": rec.get("intent_id"),
                "outcome": rec.get("outcome"),
                "action": rec.get("action"),
            },
        )
        if spine_res.get("ok"):
            ev = spine_res["event"]
            rec["spine_event_id"] = ev.get("event_id")
            rec["spine_checksum"] = ev.get("checksum")
            rec["proof_path"] = str(LATEST_DEMO)

    rec["receipt_checksum"] = _checksum(rec)
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    LATEST_DEMO.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    with RECEIPT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec
```

### 1.7 Demo fixtures

```json
{
  "schema": "governance-demo-policy-v1",
  "rules": [
    {
      "id": "P-001",
      "description": "High-risk Copilot policy enable requires approval_ref",
      "deny_when": {
        "intent": "apply_copilot_policy_change",
        "risk": "high",
        "missing_field": "approval_ref"
      }
    }
  ]
}
```

```json
{
  "schema": "governance-demo-intents-v1",
  "block_case": {
    "intent": "apply_copilot_policy_change",
    "policy_id": "COPILOT-DENY-EXTERNAL-SHARE",
    "action": "enable",
    "risk": "high",
    "agent_id": "investor_demo",
    "object_id": "NF-COPILOT-POLICY-DEMO"
  },
  "allow_case": {
    "intent": "apply_copilot_policy_change",
    "policy_id": "COPILOT-ALLOW-READONLY",
    "action": "enable",
    "risk": "high",
    "approval_ref": "TLE-2026-001",
    "agent_id": "investor_demo",
    "object_id": "NF-COPILOT-POLICY-DEMO"
  }
}
```

### 1.8 Hub + Judge projection schema ids

| File | schema |
|------|--------|
| command-data.json | schema_version: 5 |
| command-data-runtime.json | hub-runtime-projection-v1 |
| command-data-canonical.json | hub-canonical-projection-v1 |
| hub_home_founder_view_v1.py | hub-home-founder-v2-light |
| hub_judge_alarm_strip_v1.py | hub-judge-alarm-strip-v1 |
| judge_center_audit_v1 | judge-center-audit-v2 |
| judge_center_bench_v1 | judge-center-bench-v1 |
| judge_center_run_v1 | judge-center-run-receipt-v1 |

### 1.9 Agent governance trace (parallel log)

```python
#!/usr/bin/env python3
"""Append-only governance trace — workspace select, loop, reviews."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EVENTS_PATH = Path.home() / ".sina" / "agent-governance-events.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_governance_event(
    event: str,
    *,
    workspace_id: str | None = None,
    detail: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict:
    row = {
        "at": _now(),
        "event": event,
        "workspace_id": workspace_id,
        "detail": (detail or "")[:2000],
    }
    if extra:
        row.update(extra)
    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with EVENTS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    try:
        EVENTS_PATH.chmod(0o600)
    except OSError:
        pass
    return {"ok": True, "logged": event}


def tail_events(*, workspace_id: str | None = None, limit: int = 50) -> list[dict]:
    if not EVENTS_PATH.is_file():
        return []
    rows: list[dict] = []
    for line in EVENTS_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if workspace_id:
        rows = [r for r in rows if r.get("workspace_id") == workspace_id]
    return rows[-limit:]


def governance_trace_payload(workspace_id: str | None = None, limit: int = 3) -> dict:
    events = tail_events(workspace_id=workspace_id, limit=limit if workspace_id else 20)
    if workspace_id:
        events = events[-limit:]
    return {
        "ok": True,
        "path": str(EVENTS_PATH),
        "events": events,
        "count": len(events),
    }
```

---
## 2. JUDGEROOM & HUB LOGIC — BLOCK · ALLOW · TAMPER · STALE

> Demo enforcement: BLOCK/ALLOW/TAMPER. Judge+Hub: STALE/BAD/TRUSTED. Gatekeeper: PASS/FAIL.

### 2.1 ALLOW/BLOCK — governance_demo_gate_v1.py (full)

```python
#!/usr/bin/env python3
"""Copilot governance demo gate — rule P-001 only (no factory queue)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "brain-os/demo/governance_demo_policy_v1.json"


def load_policy(path: Path | None = None) -> dict:
    p = path or POLICY_PATH
    return json.loads(p.read_text(encoding="utf-8"))


def evaluate(intent: dict, policy: dict | None = None) -> dict:
    pol = policy or load_policy()
    rules = pol.get("rules") or []
    p001 = next((r for r in rules if r.get("id") == "P-001"), None)
    if not p001:
        return {
            "safe_to_execute": False,
            "rule_id": "",
            "reason": "P-001 policy missing",
        }

    deny = p001.get("deny_when") or {}
    if intent.get("intent") != deny.get("intent"):
        return {
            "safe_to_execute": True,
            "rule_id": "P-001",
            "reason": "not a copilot policy change intent",
        }

    missing = deny.get("missing_field") or ""
    risk = deny.get("risk")
    if risk and intent.get("risk") == risk and missing and not intent.get(missing):
        return {
            "safe_to_execute": False,
            "rule_id": "P-001",
            "reason": f"high-risk enable requires {missing}",
            "policy_id": intent.get("policy_id"),
        }

    return {
        "safe_to_execute": True,
        "rule_id": "P-001",
        "reason": "approval_ref present or risk not high",
        "policy_id": intent.get("policy_id"),
    }


def main() -> int:
    import argparse
    import sys

    ap = argparse.ArgumentParser(description="Governance demo gate — P-001")
    ap.add_argument("--intent", required=True, help="Intent JSON file")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    intent = json.loads(Path(args.intent).read_text(encoding="utf-8"))
    row = evaluate(intent)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        status = "PASS" if row.get("safe_to_execute") else "DENY"
        print(f"{status}: {row.get('reason')} (rule {row.get('rule_id')})")
    return 0 if row.get("safe_to_execute") else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

### 2.2 ALLOW/BLOCK — commit_copilot_demo()

```python
def commit_copilot_demo(case: str, *, dry_run: bool = False) -> dict:
    """Copilot wedge demo — governance_demo_gate only (no factory queue bypass)."""
    sys.path.insert(0, str(SCRIPTS))
    from governance_demo_gate_v1 import evaluate  # noqa: WPS433

    intent = _load_copilot_case(case)
    gate = evaluate(intent)
    intent_id = intent.get("intent_id")
    object_id = str(intent.get("object_id") or "NF-COPILOT-POLICY-DEMO")

    base = {
        "schema": "enforcement-action-receipt-v1",
        "receipt_id": f"RCP-{uuid.uuid4().hex[:12]}",
        "intent_id": intent_id,
        "action": str(intent.get("action") or "enable"),
        "object_id": object_id,
        "rule_id": "P-001",
        "agent_id": str(intent.get("agent_id") or "investor_demo"),
        "policy_id": intent.get("policy_id"),
        "approval_ref": intent.get("approval_ref"),
        "demo_case": case,
        "gate_status": "PASS" if gate.get("safe_to_execute") else "DENY",
        "gate_reasons": [] if gate.get("safe_to_execute") else [gate.get("reason") or "P-001 DENY"],
        "created_at": _now(),
        "law": "brain-os/demo/governance_demo_policy_v1.json",
    }

    if not gate.get("safe_to_execute"):
        base["outcome"] = "BLOCKED"
        receipt = _write_copilot_receipt(base, bind_spine=False)
        return {"ok": False, "blocked": True, "demo_gate": gate, "receipt": receipt}

    if dry_run:
        base["outcome"] = "DRY_RUN"
        base["evidence"] = "EXECUTE_STUB: policy applied (dry-run)"
        return {"ok": True, "dry_run": True, "demo_gate": gate, "receipt_preview": base}

    base["outcome"] = "COMMITTED"
    base["status"] = "DONE"
    base["evidence"] = "EXECUTE_STUB: policy applied"
    receipt = _write_copilot_receipt(base, bind_spine=True)
    return {"ok": True, "demo_gate": gate, "receipt": receipt}
```

### 2.3 TAMPER — validate-demo-enforcement-v1.sh (full)

```bash
#!/usr/bin/env bash
# validate-demo-enforcement-v1.sh — Copilot P-001 demo (BLOCK / ALLOW / tamper)
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"

LATEST="${HOME}/.sina/demo-enforcement/receipts/latest-demo-receipt.json"
TAMPER_TEST=0
[[ "${1:-}" == "--tamper-test" ]] && TAMPER_TEST=1

fail() { echo "FAIL: validate-demo-enforcement-v1 — $*" >&2; exit 1; }

[[ -f brain-os/demo/governance_demo_policy_v1.json ]] || fail "policy missing"
[[ -f scripts/governance_demo_gate_v1.py ]] || fail "demo gate missing"
[[ -f scripts/commit_intent_v1.py ]] || fail "commit_intent_v1.py missing"

if python3 scripts/commit_intent_v1.py --demo-enforcement --case block --json >/tmp/copilot-block.json 2>/dev/null; then
  fail "block case must exit non-zero"
fi
grep -q '"blocked": true' /tmp/copilot-block.json || fail "block case did not return blocked"

python3 scripts/commit_intent_v1.py --demo-enforcement --case allow --json >/tmp/copilot-allow.json \
  || fail "allow case failed"
grep -q '"outcome": "COMMITTED"' /tmp/copilot-allow.json || fail "allow not COMMITTED"
grep -q '"status": "DONE"' /tmp/copilot-allow.json || fail "allow missing DONE status"

[[ -f "$LATEST" ]] || fail "latest copilot receipt missing"

python3 - <<'PY' || fail "receipt integrity"
import json
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from commit_intent_v1 import verify_receipt_checksum
from governance_event_spine_v1 import find_by_event_id

latest = Path.home() / ".sina/demo-enforcement/receipts/latest-demo-receipt.json"
rec = json.loads(latest.read_text(encoding="utf-8"))
if rec.get("outcome") != "COMMITTED":
    raise SystemExit("outcome not COMMITTED")
if rec.get("rule_id") != "P-001":
    raise SystemExit("rule_id not P-001")
if not verify_receipt_checksum(rec):
    raise SystemExit("checksum invalid")
spine_id = rec.get("spine_event_id")
if not spine_id:
    raise SystemExit("missing spine_event_id")
if not find_by_event_id(str(spine_id)):
    raise SystemExit(f"spine row missing: {spine_id}")
print("OK: copilot receipt + spine + P-001")
PY

if [[ "$TAMPER_TEST" -eq 1 ]]; then
  cp "$LATEST" "${LATEST}.bak"
  python3 - <<'PY' || fail "tamper inject"
import json
from pathlib import Path
p = Path.home() / ".sina/demo-enforcement/receipts/latest-demo-receipt.json"
rec = json.loads(p.read_text(encoding="utf-8"))
rec["gate_status"] = "PASS_TAMPERED"
p.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
PY
  if python3 - <<'PY'
import json, sys
from pathlib import Path
sys.path.insert(0, "scripts")
from commit_intent_v1 import verify_receipt_checksum
rec = json.loads((Path.home() / ".sina/demo-enforcement/receipts/latest-demo-receipt.json").read_text())
sys.exit(0 if verify_receipt_checksum(rec) else 1)
PY
  then
    mv "${LATEST}.bak" "$LATEST"
    fail "tamper should FAIL checksum"
  fi
  mv "${LATEST}.bak" "$LATEST"
  echo "OK: tamper detected"
fi

echo "OK: validate-demo-enforcement-v1 · Copilot BLOCK/ALLOW · receipt · spine"
```

### 2.4 PASS/FAIL — gatekeeper run_gatekeeper()

```python
def run_gatekeeper(
    *,
    sa_id: str = "",
    phase: str = "",
    task_text: str = "",
    role: str = "",
    engine: str = "",
    worker_stuck: bool = False,
    caller: str = "gatekeeper",
    check_broker: bool = True,
) -> dict:
    """Deterministic invariant — no LLM."""
    reasons: list[str] = []

    missing = _law_files()
    if missing:
        return _fail(["LAW_FILES_MISSING"] + missing, caller=caller)

    sys.path.insert(0, str(SCRIPTS))
    from active_now_v1 import load_active_now  # noqa: WPS433
    from execution_law_enforce_v1 import validate_execution  # noqa: WPS433
    from sourcea_pick_lib import PHASE_ORDER  # noqa: WPS433

    active = load_active_now()
    if not active.get("ok"):
        return _fail([active.get("error", "ACTIVE_NOW_MISSING")], caller=caller)

    try:
        queue = _queue_current()
    except (OSError, json.JSONDecodeError) as exc:
        return _fail([f"QUEUE_READ_FAIL: {exc}"], caller=caller, active=active)

    if queue.get("commercial_default"):
        reasons.append("COMMERCIAL_QUEUE_BLOCKED")

    # In overnight/founder_absent mode ACTIVE_NOW pos advances every 30s —
    # skip the alignment drift check to avoid false BLOCKED_NO_WORKER skips.
    founder_mode = (active.get("founder_mode") or "").lower()
    sleep_esc = active.get("sleep_escalation") or False
    overnight_mode = "absent" in founder_mode and sleep_esc
    if not overnight_mode:
        reasons.extend(_active_now_align(active, queue))
    if check_broker and not overnight_mode:
        reasons.extend(_broker_drift(queue))

    try:
        s6 = PHASE_ORDER.index("phase-s6-wtm-pre-llm")
        s5 = PHASE_ORDER.index("phase-s5-commercial-lanes")
        if s5 <= s6:
            reasons.append("HIERARCHY_PHASE_ORDER_VIOLATION")
    except ValueError:
        reasons.append("HIERARCHY_PHASE_ORDER_MISSING")

    probe_sa = (sa_id or queue.get("sa_id") or active.get("current_sa_id") or "").lower()
    probe_phase = phase or queue.get("phase") or ""
    law = validate_execution(
        task_text=task_text,
        sa_id=probe_sa,
        phase=probe_phase,
        caller=caller,
    )
    if not law.get("allowed"):
        reasons.append("EXECUTION_LAW_DENIED")
        reasons.extend(law.get("violation_reasons") or [])

    if role and engine:
        from operating_mode_enforce_v1 import check_engine  # noqa: WPS433

        eng = check_engine(
            role=role,
            engine=engine,
            worker_stuck=worker_stuck,
            caller=caller,
        )
        if not eng.get("valid"):
            reasons.append(eng.get("reason") or "ENGINE_DENIED")

    if probe_sa and queue.get("sa_id") and probe_sa != queue["sa_id"]:
        reasons.append(f"TASK_SA_MISMATCH: task={probe_sa} queue={queue['sa_id']}")

    if role in ("", "worker", "act", "check", "verify") or caller.startswith(
        ("start_goal1", "healthy-drain", "goal1_auto", "worker")
    ):
        from worker_factory_evidence_gate_v1 import run_factory_gate  # noqa: WPS433

        fg = run_factory_gate(
            caller=caller,
            role=role or "worker",
            require_inbox=False,
            sa_id=queue.get("sa_id") or probe_sa,
        )
        if not fg.get("ok"):
            reasons.extend(fg.get("reasons") or [])

    ctx = {
        "caller": caller,
        "checked_at": _now(),
        "goal": active.get("current_goal"),
        "sprint": active.get("current_sprint"),
        "founder_mode": active.get("founder_mode"),
        "queue_path": queue.get("queue_path"),
        "queue_pos": queue.get("queue_pos"),
        "queue_total": queue.get("queue_total"),
        "sa_id": queue.get("sa_id") or probe_sa,
        "queue_role": queue.get("queue_role"),
        "phase": queue.get("phase"),
        "active_now_hash8": active.get("hash8"),
        "hierarchy_match": "HIERARCHY_PHASE_ORDER_VIOLATION" not in reasons,
        "queue_match": not any("MISMATCH" in r or "DRIFT" in r for r in reasons),
        "execution_law": law.get("validation_passed"),
    }

    if reasons:
        return _fail(reasons, **ctx)

    row = _pass(**ctx)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row
```

### 2.5 ALLOW/DENY — execution_law validate_execution()

```python
def validate_execution(
    *,
    task_text: str = "",
    sa_id: str = "",
    phase: str = "",
    caller: str = "cli",
) -> dict:
    """Goal validator — refuse if outside ACTIVE_NOW + GOAL_HIERARCHY."""
    if not HIERARCHY.is_file() or not EXECUTION_LAW.is_file():
        return {
            "ok": False,
            "allowed": False,
            "validation_passed": "NO",
            "error": "EXECUTION_LAW_FILES_MISSING",
            "message": REFUSE_MSG,
        }

    active = _load_active()
    if not active.get("ok"):
        return {
            "ok": False,
            "allowed": False,
            "validation_passed": "NO",
            "error": active.get("error"),
            "message": REFUSE_MSG,
        }

    goal = active.get("current_goal", "")
    sprint = active.get("current_sprint", "")
    queue = active.get("current_queue", "")
    active_sa = active.get("current_sa_id", "")
    blocker = active.get("current_blocker", "")

    probe = " ".join(
        filter(
            None,
            [task_text, sa_id, phase, caller],
        )
    ).lower()

    reasons: list[str] = []
    allowed = True

    pre_llm_active = _text_has_any(goal + sprint + queue, PRE_LLM_SIGNALS)

    # Commercial while Pre-LLM infrastructure is active
    if pre_llm_active:
        if _text_has_any(probe, COMMERCIAL_SIGNALS):
            allowed = False
            reasons.append("commercial_while_pre_llm_active")
        if sa_id and re.match(r"sa-05\d+", sa_id, re.I):
            allowed = False
            reasons.append("sa-05xx_while_pre_llm_active")
        if phase == COMMERCIAL_PHASE:
            allowed = False
            reasons.append("phase-s5_while_pre_llm_active")

    # Infrastructure redesign while enforcement incomplete
    if _text_has_any(blocker, ("drift", "reconcile", "enforcement", "incomplete", "stopped")):
        if _text_has_any(probe, REDESIGN_SIGNALS):
            allowed = False
            reasons.append("redesign_while_enforcement_incomplete")

    # sa_id outside active queue range when explicitly bound
    if sa_id and active_sa and sa_id.lower().startswith("sa-"):
        if sa_id.lower().startswith("sa-05") and pre_llm_active:
            allowed = False
            reasons.append("sa_outside_active_goal")

    why = (
        "Active goal/sprint/queue match; work within Pre-LLM eval-dispatch spine."
        if allowed
        else "; ".join(reasons) or "outside_active_founder_goal"
    )

    row = {
        "ok": True,
        "allowed": allowed,
        "validation_passed": "YES" if allowed else "NO",
        "active_goal": goal,
        "active_sprint": sprint,
        "active_queue": queue,
        "active_sa_id": active_sa,
        "why_execution_allowed": why if allowed else None,
        "violation_reasons": reasons,
        "caller": caller,
        "law": "SOURCEA_EXECUTION_LAW_LOCKED_v1.md",
    }
    if not allowed:
        row["message"] = REFUSE_MSG
        row["status"] = "HIERARCHY_VIOLATION"
    _log({**row, "event": "VALIDATE", "probe_sa": sa_id, "probe_phase": phase})
    return row
```

### 2.6 STALE patterns — judge_center_patterns_v1.py (full)

```python
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
```

### 2.7 STALE scan — _scan_alarms()

```python
def _scan_alarms(text: str, form: dict) -> list[dict]:
    alarms: list[dict] = []
    open_count = int(form.get("open_questions_count") or 0)

    for pat, code in BAD_PATTERNS:
        for m in pat.finditer(text):
            alarms.append({"tag": "BAD", "code": code, "excerpt": m.group(0)[:120]})

    for pat, code in STALE_PATTERNS:
        for m in pat.finditer(text):
            tag = "STALE"
            detail = m.group(0)[:120]
            if code == "open_count_claim":
                claimed = int(m.group(1))
                if claimed != open_count:
                    alarms.append(
                        {
                            "tag": tag,
                            "code": code,
                            "excerpt": detail,
                            "disk": f"form open_questions_count={open_count}",
                        }
                    )
                else:
                    alarms.append({"tag": "RIGHT", "code": "open_count_match", "excerpt": detail})
            elif code == "success_without_path" and "FOUND —" not in text[-5000:]:
                alarms.append({"tag": tag, "code": code, "excerpt": detail})
            elif code not in ("success_without_path",):
                alarms.append({"tag": tag, "code": code, "excerpt": detail})

    if not alarms:
        alarms.append({"tag": "UNPROVEN", "code": "no_alarm_match", "excerpt": "no stale/bad patterns in sample"})
    # Dedupe by code + excerpt prefix
    seen: set[str] = set()
    unique: list[dict] = []
    for a in alarms:
        key = f"{a.get('code')}:{str(a.get('excerpt',''))[:80]}"
        if key in seen:
            continue
        seen.add(key)
        unique.append(a)
    return unique
```

### 2.8 STALE settle — _settle_alarm()

```python
def _settle_alarm(alarm: dict, disk: dict, chat_id: str) -> dict:
    code = str(alarm.get("code") or "")
    tag = str(alarm.get("tag") or "")

    if code in ("false_sidebar_success", "scratch_canvas_path", "scratch_canvas_risk"):
        return {
            "outcome": "ESCALATE_INCIDENT",
            "class": "BAD",
            "resolution": "INCIDENT-029 class — chat claimed form UI without M1 Canvas proof",
            "form_action": "Q-M2-029 YES",
        }

    if code in ("incident_027_class", "incident_028_class"):
        inc = "027" if "027" in code else "028"
        return {
            "outcome": "ESCALATE_INCIDENT",
            "class": "BAD",
            "resolution": f"INCIDENT-{inc} conduct — hub/chat projection drift",
            "form_action": f"Q-M2-{inc} YES" if inc == "029" else "Q-M2-FORM-SYNC YES",
        }

    if code == "autorun_p0_stale" and disk["no_autorun"]:
        return {
            "outcome": "SETTLED_STALE",
            "class": "STALE",
            "resolution": "Chat AUTO-RUN hero is stale — form 2.03 A + Q-RT-LIVE YES + kill_flag win",
            "form_action": None,
        }

    if code == "governance_complete_stale" and disk["awaiting_founder_picks"]:
        return {
            "outcome": "SETTLED_STALE",
            "class": "STALE",
            "resolution": f"Governance not complete — {disk['open_questions_count']} form rows await Canvas PICK",
            "form_action": "Q-M2-FORM-SYNC YES",
        }

    if code == "tracker_as_ssot_stale":
        return {
            "outcome": "SETTLED_STALE",
            "class": "STALE",
            "resolution": "Master Tracker is map only — form JSON + founder_open win picks",
            "form_action": None,
        }

    if code == "rail_a_hero_stale" and disk["no_autorun"]:
        return {
            "outcome": "SETTLED_STALE",
            "class": "STALE",
            "resolution": "Rail A AUTO-RUN hero rejected — ENFORCE W1+W3 per 9.07 A",
            "form_action": None,
        }

    if code == "open_count_claim" and alarm.get("tag") == "STALE":
        return {
            "outcome": "SETTLED_STALE",
            "class": "STALE",
            "resolution": f"Chat count wrong — disk open_questions_count={disk['open_questions_count']}",
            "form_action": None,
        }

    if code == "open_count_match":
        return {
            "outcome": "SETTLED_ANSWERED",
            "class": "RIGHT",
            "resolution": "Open count matches form JSON",
            "form_action": None,
        }

    if tag == "UNPROVEN" and code == "no_alarm_match":
        return {
            "outcome": "ESCALATE_BENCH",
            "class": "UNPROVEN",
            "resolution": "No pattern hit — manual specialist audit or extend L1 patterns",
            "form_action": None,
        }

    if tag == "STALE":
        return {
            "outcome": "SETTLED_STALE",
            "class": "STALE",
            "resolution": alarm.get("excerpt", "stale vs disk")[:160],
            "form_action": None,
        }

    if tag == "BAD":
        return {
            "outcome": "ESCALATE_INCIDENT",
            "class": "BAD",
            "resolution": alarm.get("excerpt", "bad conduct")[:160],
            "form_action": "Q-M2-029 YES",
        }

    return {
        "outcome": "ESCALATE_BENCH",
        "class": tag or "UNPROVEN",
        "resolution": alarm.get("excerpt", "needs bench review")[:160],
        "form_action": None,
    }
```

### 2.9 Judge bench classification — bench()

```python
def bench(counsel: dict) -> dict:
    briefs = counsel.get("briefs") or []
    form_rows = _collect_form_actions(briefs)
    answered = _answered_pick_ids()
    form_rows = [r for r in form_rows if str(r.get("id", "")).split()[0] not in answered]

    # System-wide resolution (founder-facing)
    trusted = [b["chat_id"] for b in briefs if b.get("overall") in ("RIGHT", "TRUSTED")]
    past_only = [b["chat_id"] for b in briefs if b.get("overall") == "PAST_STALE_ONLY"]
    active_stale = [b["chat_id"] for b in briefs if b.get("overall") in ("STALE", "ACTIVE_STALE", "REVERT")]
    bad_chats = [b["chat_id"] for b in briefs if b.get("overall") in ("BAD", "ACTIVE_BAD")]
    right_chats = trusted

    executive = (
        f"Judge Center batch {counsel.get('case_id')}: "
        f"{len(trusted)} TRUSTED/RIGHT · {len(past_only)} PAST_STALE_ONLY · "
        f"{len(active_stale)} ACTIVE_STALE · {len(bad_chats)} BAD · "
        f"{len(form_rows)} form actions. "
        "RECENT window wins over archaeology. Binding PICK still on M1 Canvas."
    )

    remediation: list[dict] = []
    for b in briefs:
        if b.get("overall") not in ("BAD", "ACTIVE_BAD", "STALE", "ACTIVE_STALE", "REVERT"):
            continue
        remediation.append(
            {
                "chat_id": b.get("chat_id"),
                "role": b.get("role"),
                "prompt": (
                    f"[JUDGE REMEDIATION] Chat {b.get('chat_id')} classified {b.get('overall')}. "
                    f"Re-read live_founder_decision_form_v1.py --json before any P0/complete claim. "
                    f"Ignore: {', '.join(b.get('ignore_stale') or [])}. "
                    f"Keep: {', '.join(b.get('keep_using') or [])}."
                ),
            }
        )

    return {
        "schema": "judge-center-bench-v1",
        "case_id": counsel.get("case_id"),
        "benched_at": _now(),
        "counsel_ref": counsel.get("counselled_at"),
        "executive_resolution": executive,
        "summary": {
            "trusted": trusted,
            "past_stale_only": past_only,
            "active_stale": active_stale,
            "right": right_chats,
            "stale": active_stale,
            "bad": bad_chats,
            "temporal_summary": {
                "trusted": trusted,
                "past_stale_only": past_only,
                "active_stale": active_stale,
                "bad": bad_chats,
            },
            "form_actions_count": len(form_rows),
        },
        "founder_resolution": _founder_resolution_lines(briefs),
        "form_row_drafts": form_rows,
        "remediation_prompts": remediation,
        "founder_pick_required": [
            r.get("pick_hint") or r.get("id")
            for r in form_rows
            if str(r.get("id", "")).split()[0] not in answered
        ],
    }
```

### 2.10 Hub P0–P3 strip — build_strip()

```python
def build_strip(*, refresh_judge: bool = False) -> dict:
    if refresh_judge:
        import subprocess
        import sys

        root = Path(__file__).resolve().parents[1]
        chats = "58148ac9,6245d9dd,e54ddfa8,74f5ccab,3369d11c,a53f3fa1"
        subprocess.run(
            [sys.executable, str(root / "scripts/judge_center_run_v1.py"), "--chats", chats, "--json"],
            check=False,
            capture_output=True,
        )

    resolution = _read_json(JUDGE_DIR / "latest-resolution-v1.json")
    ts = (resolution.get("summary") or {}).get("temporal_summary") or {}
    active = list(ts.get("active_stale") or [])
    bad = list(ts.get("bad") or [])
    past = list(ts.get("past_stale_only") or [])
    trusted = list(ts.get("trusted") or []) + list((resolution.get("summary") or {}).get("right") or [])

    form: dict = {}
    try:
        import sys

        root = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(root / "scripts"))
        from live_founder_decision_form_v1 import payload as form_payload  # noqa: WPS433

        form = form_payload()
    except Exception:
        form = {}

    open_count = int(form.get("open_questions_count") or 0)
    picks_required = list(resolution.get("founder_pick_required") or [])

    p0_items: list[dict] = []
    for cid in active:
        p0_items.append({"id": cid, "tag": "ACTIVE_STALE", "label": f"Chat {cid[:8]} — wrong today"})
    for cid in bad:
        p0_items.append({"id": cid, "tag": "BAD", "label": f"Chat {cid[:8]} — BAD conduct"})

    p1_items: list[dict] = []
    if open_count > 0:
        p1_items.append(
            {
                "id": "FORM_OPEN",
                "tag": "NEEDS_PICK",
                "label": f"M1 Canvas — {open_count} open PICK(s)",
                "count": open_count,
            }
        )
    for pid in picks_required[:6]:
        p1_items.append({"id": pid, "tag": "JUDGE_PICK", "label": f"Judge draft: {pid}"})

    p2_items = [
        {"id": cid, "tag": "PAST_STALE_ONLY", "label": f"Chat {cid[:8]} — archaeology only · trust recent"}
        for cid in past
    ]

    p3_items: list[dict] = []
    if not p0_items and not p1_items:
        p3_items.append(
            {
                "id": "ALL_CLEAR",
                "tag": "OK",
                "label": resolution.get("executive_resolution") or "No active stale · trust recent windows",
            }
        )
    for cid in trusted:
        p3_items.append({"id": cid, "tag": "TRUSTED", "label": f"Chat {cid[:8]} — trusted"})

    levels = [
        {
            "level": "P0",
            "severity": "critical",
            "title": "Active wrong today",
            "count": len(p0_items),
            "items": p0_items,
            "tone": "red" if p0_items else "muted",
        },
        {
            "level": "P1",
            "severity": "founder_action",
            "title": "Form PICK / judge drafts",
            "count": len(p1_items),
            "items": p1_items,
            "tone": "amber" if p1_items else "muted",
        },
        {
            "level": "P2",
            "severity": "archaeology",
            "title": "Past stale only — trust recent",
            "count": len(p2_items),
            "items": p2_items[:8],
            "tone": "blue" if p2_items else "muted",
        },
        {
            "level": "P3",
            "severity": "info",
            "title": "Clear / trusted",
            "count": len(p3_items),
            "items": p3_items[:4],
            "tone": "green",
        },
    ]

    headline = "ALL CLEAR"
    tone = "green"
    if p0_items:
        headline = f"P0 — {len(p0_items)} active alarm(s)"
        tone = "red"
    elif p1_items:
        headline = f"P1 — {open_count} form fork(s) open"
        tone = "amber"
    elif p2_items:
        headline = f"P2 — {len(p2_items)} past-stale · recent clean"
        tone = "blue"

    row = {
        "ok": True,
        "schema": SCHEMA,
        "built_at": _now(),
        "headline": headline,
        "tone": tone,
        "case_id": resolution.get("case_id"),
        "executive_resolution": resolution.get("executive_resolution"),
        "levels": levels,
        "summary": {
            "active_stale": len(active),
            "bad": len(bad),
            "past_stale_only": len(past),
            "trusted": len(trusted),
            "form_open": open_count,
        },
        "sources": {
            "resolution": str(JUDGE_DIR / "latest-resolution-v1.json"),
            "form": str(Path.home() / ".sina/live-founder-decision-form-v1.json"),
        },
        "law": "CROSS_CHAT_TRUTH_ALARM_FORM_OFFICIAL_2026-06-12_LOCKED_v1.md",
    }
    return row
```

### 2.11 Hub form wire refresh

```javascript
async function refreshLiveFormWire({ rerender = false } = {}) {
    try {
      const res = await fetch(`${API}/api/live-founder-decision-form-v1`, { cache: "no-store" });
      if (!res.ok) return;
      const form = await res.json();
      if (form && form.ok !== false) {
        D.live_founder_decision_form = form;
        if (D.home_founder_view) {
          D.home_founder_view.founder_decision_form = form;
          const wires = D.home_founder_view.live_wires;
          if (Array.isArray(wires)) {
            const w = wires.find((x) => x.id === "form");
            if (w) w.value = String(form.open_questions_count ?? 0);
          }
        }
        if (rerender && activeTab === "command") render();
      }
    } catch {
      /* hub may be restarting */
    }
  }

  async function hubAutoSync({ silent = true, full = false } = {}) {
    if (hubAutoSyncInFlight && !full) {
      return false;
    }
    if (!(await pingApi())) {
      const up = await ensureServer();
      if (!up) return false;
    }
    hubAutoSyncInFlight = true;
    try {
      if (full) {
        const ctrl = new AbortController();
        const timer = setTimeout(() => ctrl.abort(), 120000);
        const res = await fetch(`${API}/refresh`, { method: "POST", signal: ctrl.signal });
        clearTimeout(timer);
        const json = await res.json();
        if (json.data) {
          applyPayload(jso
```

---
## 3. RUNTIME ENVIRONMENT

### 3.1 Entry points

| Role | Entry | Port |
|------|-------|------|
| Hub | serve-sina-command.sh → sina-command-server.py | 13020 |
| Rebuild worker | hub_rebuild_worker_v1.py | 13030 |
| Form SSOT | live_founder_decision_form_v1.py --json | CLI |
| Form submit | canvas_form_submit_v1.py | CLI/API |
| Judge pipeline | judge_center_run_v1.py | CLI |
| Thread pipeline | thread_room_run_v1.py | CLI |
| Demo | commit_intent_v1.py --demo-enforcement | CLI |

### 3.2 Environment variables

```bash
SINA_COMMAND_PORT=13020
SINA_FORCE_RESTART=1
SINA_GATE_MODE=...
SINA_GATE_RESTART=1
SINA_PANEL_BUILD_ON_START=1
SINA_SKIP_PANEL_BUILD=1
SINA_AUDIT_STRICT=1
SOURCEA_DEMO_ENFORCE=1
PYTHONPATH=.../SourceA/scripts
```

### 3.3 Append-only logs

| Path | Producer |
|------|----------|
| ~/.sina/governance-event-spine-v1.jsonl | governance_event_spine_v1 |
| ~/.sina/agent-governance-events.jsonl | agent_governance_events |
| ~/.sina/gatekeeper-v1.jsonl | gatekeeper_v1 |
| ~/.sina/execution-law-enforce-v1.jsonl | execution_law_enforce_v1 |
| ~/.sina/demo-enforcement/receipt-log.jsonl | commit_intent_v1 |
| ~/.sina/judge-center/cases.jsonl | judge_center_audit_v1 |
| ~/.sina/command-server.log | serve-sina-command |

### 3.4 canvas_form_submit_v1.py (full)

```python
#!/usr/bin/env python3
"""FORM_OFFICIAL batch submit — Canvas confirms → disk → hub (founder Submit only)."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def submit(*, cascade_hub: bool = True, strict_hub: bool = True) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from canvas_form_apply_picks_v1 import apply, CANVAS_DATA  # noqa: WPS433

    apply_result = apply(canvas_path=CANVAS_DATA, dry_run=False)

    steps: list[dict] = [{"step": "canvas_apply", **apply_result}]

    def _run(label: str, cmd: list[str], *, timeout: int = 300) -> dict:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
        return {
            "step": label,
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout_tail": (proc.stdout or "")[-400:],
            "stderr_tail": (proc.stderr or "")[-400:],
        }

    steps.append(_run("write_receipt", [sys.executable, str(SCRIPTS / "live_founder_decision_form_v1.py"), "--write-receipt"]))
    steps.append(_run("sync_picks_locked", [sys.executable, str(SCRIPTS / "sync_picks_locked_v1.py")]))
    steps.append(_run("generate_canvas", [sys.executable, str(SCRIPTS / "generate_integrity_canvas_form_data_v1.py")]))
    steps.append(_run("form_reconcile", [sys.executable, str(SCRIPTS / "form_open_questions_reconcile_v1.py"), "--json"]))
    steps.append(_run("judge_alarm_strip", [sys.executable, str(SCRIPTS / "hub_judge_alarm_strip_v1.py"), "--refresh-judge"]))

    if cascade_hub:
        steps.append(
            _run(
                "build_hub",
                [sys.executable, str(SCRIPTS / "build-sina-command-panel.py")],
                timeout=300,
            )
        )
        steps.append(_run("hub_self_refresh", [sys.executable, str(SCRIPTS / "hub_self_refresh_v1.py")]))
        steps.append(
            _run(
                "governance_cascade",
                [sys.executable, str(SCRIPTS / "governance_propagation_cascade_v1.py"), "--reason", "form-canvas-submit"],
            )
        )

    from live_founder_decision_form_v1 import payload  # noqa: WPS433

    form = payload()
    core_labels = {"canvas_apply", "write_receipt", "sync_picks_locked", "generate_canvas", "form_reconcile", "judge_alarm_strip"}
    hub_labels = {"build_hub", "hub_self_refresh", "governance_cascade"}
    core_ok = bool(apply_result.get("ok")) and all(
        s.get("ok") for s in steps if s.get("step") in core_labels
    )
    hub_ok = all(s.get("ok") for s in steps if s.get("step") in hub_labels) if cascade_hub else True
    return {
        "ok": core_ok,
        "hub_synced": hub_ok,
        "applied_now": apply_result.get("applied_now", 0),
        "open_questions_count": form.get("open_questions_count"),
        "open_question_ids": [q.get("id") for q in (form.get("open_questions") or [])],
        "steps": steps,
        "shipped": apply_result.get("shipped") or [],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Batch submit M1 Canvas confirms → disk + hub")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-hub", action="store_true", help="Disk + canvas only — skip hub rebuild")
    args = ap.parse_args()
    result = submit(cascade_hub=not args.no_hub)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            f"{'OK' if result.get('ok') else 'FAIL'}: applied_now={result.get('applied_now')} "
            f"open={result.get('open_questions_count')}"
        )
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

### 3.5 judge_center_run_v1.py (full)

```python
#!/usr/bin/env python3
"""Judge Center — run full L1 Audit → L2 Counsel → L3 Bench pipeline.

Usage:
  python3 scripts/judge_center_run_v1.py --chats 6245d9dd,e54ddfa8,74f5ccab
  python3 scripts/judge_center_run_v1.py --chats 6245d9dd --json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
JUDGE_DIR = Path.home() / ".sina/judge-center"


def main() -> int:
    parser = argparse.ArgumentParser(description="Judge Center full pipeline")
    parser.add_argument("--chats", required=True, help="Comma-separated chat id prefixes")
    parser.add_argument("--write-form", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    py = sys.executable
    audit_raw = subprocess.check_output(
        [py, str(SCRIPTS / "judge_center_audit_v1.py"), "--chats", args.chats, "--json"],
        text=True,
    )
    audit = json.loads(audit_raw)
    audit_path = JUDGE_DIR / "last-audit-batch.json"
    JUDGE_DIR.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    subprocess.check_call(
        [py, str(SCRIPTS / "judge_center_counsel_v1.py"), "--packet", str(audit_path)],
    )
    counsel_path = JUDGE_DIR / "latest-counsel-v1.json"
    counsel = json.loads(counsel_path.read_text(encoding="utf-8"))

    bench_cmd = [
        py,
        str(SCRIPTS / "judge_center_bench_v1.py"),
        "--brief",
        str(JUDGE_DIR / "counsel" / f"{counsel['case_id']}.json"),
        "--json",
    ]
    if args.write_form:
        bench_cmd.insert(-1, "--write-form")
    judgment_raw = subprocess.check_output(bench_cmd, text=True)
    judgment = json.loads(judgment_raw)

    receipt = {
        "schema": "judge-center-run-receipt-v1",
        "ok": True,
        "chats": args.chats.split(","),
        "case_id": judgment.get("case_id"),
        "executive_resolution": judgment.get("executive_resolution"),
        "paths": {
            "audit": str(audit_path),
            "counsel": str(JUDGE_DIR / "counsel" / f"{counsel['case_id']}.json"),
            "resolution": str(JUDGE_DIR / "resolutions" / f"{judgment['case_id']}.json"),
            "latest_resolution": str(JUDGE_DIR / "latest-resolution-v1.json"),
        },
    }
    (JUDGE_DIR / "latest-run-receipt-v1.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )

    if args.json:
        print(json.dumps({"receipt": receipt, "judgment": judgment}, indent=2))
    else:
        print("=== JUDGE CENTER RESOLUTION ===")
        print(judgment.get("executive_resolution"))
        for line in judgment.get("founder_resolution") or []:
            print(line)
        print(f"\nReceipt: {JUDGE_DIR / 'latest-run-receipt-v1.json'}")
        print(f"Resolution: {JUDGE_DIR / 'latest-resolution-v1.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### 3.6 thread_room_run_v1.py (full)

```python
#!/usr/bin/env python3
"""Thread Room — Scout → Cartographer → Curator pipeline.

Usage:
  python3 scripts/thread_room_run_v1.py --chats 58148ac9,6245d9dd,e54ddfa8 --json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
THREAD_DIR = Path.home() / ".sina/thread-room"


def main() -> int:
    ap = argparse.ArgumentParser(description="Thread Room full pipeline")
    ap.add_argument("--chats", required=True)
    ap.add_argument("--write-form", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    py = sys.executable

    scout_raw = subprocess.check_output(
        [py, str(SCRIPTS / "thread_room_scout_v1.py"), "--chats", args.chats, "--json"],
        text=True,
    )
    scout = json.loads(scout_raw)
    subprocess.check_call(
        [py, str(SCRIPTS / "thread_room_cartographer_v1.py"), "--latest", "--json"],
        stdout=subprocess.DEVNULL,
    )
    carto = json.loads((THREAD_DIR / "latest-map-v1.json").read_text(encoding="utf-8"))

    cur_cmd = [py, str(SCRIPTS / "thread_room_curator_v1.py"), "--latest", "--json"]
    if args.write_form:
        cur_cmd.insert(-1, "--write-form")
    cur_raw = subprocess.check_output(cur_cmd, text=True)
    curation = json.loads(cur_raw)

    receipt = {
        "schema": "thread-room-run-receipt-v1",
        "ok": True,
        "chats": args.chats.split(","),
        "case_id": curation.get("case_id"),
        "executive_summary": curation.get("executive_summary"),
        "paths": {
            "scout": str(THREAD_DIR / "latest-scout-v1.json"),
            "map": str(THREAD_DIR / "latest-map-v1.json"),
            "curation": str(THREAD_DIR / "latest-curation-v1.json"),
        },
    }
    (THREAD_DIR / "latest-run-receipt-v1.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )

    if args.json:
        print(json.dumps({"receipt": receipt, "curation": curation, "scout": scout, "map": carto}, indent=2))
    else:
        print(curation.get("executive_summary"))
        print(f"Receipt: {THREAD_DIR / 'latest-run-receipt-v1.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### 3.7 Sync truth table

| SSOT | Hub reads | Refresh |
|------|-----------|--------|
| form payload | command-data + home wire | Submit / rebuild |
| canvas picks | not listed in hub | M1 Submit |
| judge resolution | alarm strip | hub_judge_alarm_strip |
| spine jsonl | cascade | append_event |
| demo receipt | Actions | commit_intent allow |


---
*End structural truth export.*
