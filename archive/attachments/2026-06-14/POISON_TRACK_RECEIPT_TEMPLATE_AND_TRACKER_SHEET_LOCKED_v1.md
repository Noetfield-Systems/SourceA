# Poison track — receipt template + Governance tracker sheet (LOCKED v1)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Parent:** `SINA_POISON_TRACKING_METHOD_LOCKED_v1.md`  
**Path:** `~/.sina/poison-track-receipt-v1.json` (write on PT-1 · update through PT-9)

---

## 1. JSON receipt template

```json
{
  "schema": "poison-track-receipt-v1",
  "track_id": "PT-20260614-034",
  "opened_at": "2026-06-14T19:00:00Z",
  "closed_at": null,
  "trigger": "T1|T2|T3|T4|T5|T6|T7",
  "class_tags": ["POISON", "PROPAGATION"],
  "p_classes": ["P1-INJECT", "P3-API", "P4-RUNTIME"],
  "incidents": ["INCIDENT-034", "INCIDENT-028"],
  "chats": {
    "brain": "58148ac9-135c-448d-b428-b57988738fa3",
    "worker": "fd67502f-5f95-43b8-bdfc-f2dba306f828",
    "governance": "e54ddfa8-531b-40de-8443-d8167f80a614",
    "commercial": "6245d9dd",
    "executor": "e54ddfa8-531b-40de-8443-d8167f80a614"
  },
  "drift_lines": [
    {
      "chat": "brain",
      "line": 121,
      "date": "2026-06-06",
      "excerpt": "Prompt feed Confirm auto-send",
      "founder_facing": true
    }
  ],
  "pipeline_map": [
    {
      "rank": 1,
      "writer": ".cursor/rules/prompt-queue.mdc v6",
      "surface": "alwaysApply rule",
      "consumer": "all Cursor sessions",
      "owner": "cursor_executor",
      "status": "fixed_v8"
    }
  ],
  "snapshot": {
    "r1_brain_validator": "PASS|FAIL",
    "r2_worker_validator": "PASS|FAIL",
    "r3_live_wire": "PASS|FAIL",
    "session_gate_brain": "PASS|FAIL",
    "session_gate_worker": "PASS|FAIL",
    "stability_12s": "PASS|FAIL"
  },
  "open_ars": ["AR-034-01", "AR-034-03"],
  "streak_r9": 0,
  "owner_fix": "cursor_executor|maintainer_2|governance",
  "tracker": "governance_specialist",
  "approver": "ASF",
  "artifacts": [
    "archive/attachments/2026-06-14/OLD_INJECT_HUNT_CHAT_TIMELINE_PIPELINE_MAP_LOCKED_v1.md"
  ]
}
```

**Write rule:** Executor creates/updates on PT-1 and PT-5. Governance owns `streak_r9` and `closed_at`.

---

## 2. Governance tracker sheet (copy every poison session)

```
POISON TRACK ID: ___________
Opened: ___________  Trigger: T_
P-CLASS: ___________  Incidents: ___________
Class tags: POISON / CONDUCT / BOTH / DRIFT / PROPAGATION

── PT-1 SNAPSHOT (executor) ──
R1 brain validator:     PASS / FAIL
R2 worker validator:    PASS / FAIL
R3 live wire:           PASS / FAIL
Brain session gate:     PASS / FAIL
Worker session gate:    PASS / FAIL
12s stability:          PASS / FAIL / N/A

── PT-2 DRIFT LINE (gov + executor) ──
First founder-facing drift: chat ___ line ___ date ___
Excerpt: ___________

── PT-3 PIPELINE (executor) ──
Root writer #1: ___________  owner: ___________  status: OPEN/FIXED
Root writer #2: ___________  owner: ___________  status: OPEN/FIXED

── PT-5 REMEDIATE ──
Disk/heal actions this session: ___________
jsonl event logged: Y / N

── PT-7 VERIFY ──
R10 API (GET/POST split): PASS / FAIL / N/A
Close-line gate on ship: PASS / FAIL

── PT-8 STREAK ──
R9 count: ___ / 3  (Brain+Worker consecutive green)
Open ARs: ___________

── PT-9 CLOSE ──
Recommend close to ASF: Y / N
ASF confirmed: Y / N
```

---

## 3. jsonl events (append to `~/.sina/agent-governance-events.jsonl`)

| Event | When |
|-------|------|
| `POISON_TRACK_OPENED` | PT-0 |
| `POISON_TRACK_SNAPSHOT` | PT-1 |
| `POISON_TRACK_WRITER_NAMED` | PT-3 |
| `POISON_TRACK_REMEDIATED` | PT-5 |
| `POISON_TRACK_VERIFY_PASS` | PT-7 all required R green |
| `POISON_TRACK_CLOSED` | PT-9 ASF sign-off |

---

## 4. Conflict-hard decision tree

```text
Founder sees conflicting advice?
  ├─ YES → PT-0 classify
  │     ├─ Automation still running wrong? → BOTH → conduct audit + PT
  │     ├─ Only words wrong? → POISON → PT-1..9
  │     └─ Law changed but surfaces old? → PROPAGATION → cascade + PT
  └─ NO → normal session gate only
```

---

**END companion**
