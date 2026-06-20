# HUB HOME REDESIGN SPEC

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
## LOCKED v1 — ASF Founder Directive · Claude External Advisor Mockup Alignment

**Document type:** Implementation SSOT — Hub `command` tab home view  
**Owner:** SourceA Brain (routes) · Worker (data) · SinaaiDataBase workspace (UI build)  
**Authority:** ASF direct imperative (2026-06-08) — supersedes generic phase-s8 generated prompts for home layout  
**Companion payload:** `scripts/hub_home_founder_view_v1.py` → `command-data.json` key `home_founder_view`  
**UI consumer:** `agent-control-panel/assets/app.js` → `renderCommand()` (edit lock: SinaaiDataBase workspace only)  
**Assigned task:** `sa-0821` · phase `phase-s8-hub-ui-ux`  
**Validator:** `scripts/validate-hub-home-founder-view-v1.sh`  

---

## 0 — Principles (non-negotiable)

| Rule | Meaning |
|---|---|
| Plain English default | Founder sees human sentences — never raw codes as primary labels |
| No technical codes visible by default | Hide `sa-XXXX`, `Rail A`, broker JSON, queue role tokens from collapsed home |
| Goals with progress bars | Each strategic goal shows title + bar + percent or phase label |
| Actions with clear labels | Primary buttons use verb phrases (“Start next batch”, “Refresh hub”) — not action_id strings |
| Recent events log | Last 8–12 machine events as readable timeline |
| Technical detail on expand only | “Details” / chevron reveals sa id, rail, broker state, orchestrator snapshot |

**Founder law preserved:** one-tap Actions only — no Terminal copy from chat.

---

## 1 — Layout mockup (Claude External Advisor alignment)

```
┌─────────────────────────────────────────────────────────────────┐
│  Sina Command                                    [Refresh hub]   │
├─────────────────────────────────────────────────────────────────┤
│  STATUS                                                          │
│  ● Ready for you — Worker is idle · Brain checked last turn    │
│  Next: Run the next automated batch when you are ready           │
│  [ ▶ Start next batch (5) ]   [ Open Goal 1 loop → ]            │
│                                              [ Show details ▾ ]  │
├─────────────────────────────────────────────────────────────────┤
│  GOALS                                                           │
│  Execution spine — strategic slice          ████░░░░░░  12%      │
│  Prove packet beats raw LLM                 ██████░░░░  58%      │
│  Shipped products & revenue                 ███░░░░░░░  28%      │
│  Governance every session                   ████████░░  82%      │
├─────────────────────────────────────────────────────────────────┤
│  ACTIONS                                                         │
│  [ Refresh hub ]  [ Today's focus ]  [ Agent hub ]  [ Backlog ]  │
├─────────────────────────────────────────────────────────────────┤
│  RECENT EVENTS                                                   │
│  02:21  Worker inbox updated — next task ready                   │
│  02:11  Started automated batch (5 prompts)                      │
│  02:00  Brain chose next queue item                              │
│  01:05  Worker finished a verification round                       │
│                                              [ Show details ▾ ]  │
└─────────────────────────────────────────────────────────────────┘

EXPANDED “Show details” (secondary panel — not default):
  Task ID: sa-0153 · Queue 1/30 · CHECK · Rail A
  Broker: idle · Orchestrator: idle · INBOX pending: false
  Raw events JSON · Copy for agent
```

---

## 2 — Data contract (`home_founder_view`)

Built by `hub_home_founder_view_v1.py` on every panel build.

```json
{
  "schema": "hub-home-founder-v1",
  "ok": true,
  "status": {
    "headline": "Ready for you",
    "subline": "Worker is idle · Brain checked last turn",
    "next_plain": "Run the next automated batch when you are ready",
    "tone": "ready|busy|blocked|unknown"
  },
  "goals": [
    {
      "id": "p0-strategic-slice",
      "title": "Execution spine — strategic slice",
      "progress_pct": 12,
      "status_label": "In progress"
    }
  ],
  "actions": [
    {
      "id": "founder-start-worker-batch-5",
      "label": "Start next batch (5)",
      "hint": "Worker runs 5 prompts; Brain reviews at checkpoint",
      "kind": "primary"
    }
  ],
  "recent_events": [
    {
      "at": "2026-06-08T02:21:30Z",
      "label": "Worker inbox updated — next task ready",
      "icon": "inbox"
    }
  ],
  "technical_detail": {
    "sa_id": "sa-0153",
    "queue_pos": 1,
    "queue_total": 30,
    "queue_role": "check",
    "rail": "A",
    "broker_state": "idle",
    "orchestrator_state": "idle",
    "inbox_pending": false,
    "raw_events": []
  }
}
```

**Plain-English mapping table** (maintain in `hub_home_founder_view_v1.py`):

| Machine event | Default label |
|---|---|
| `INBOX_DELIVERED` | Worker inbox updated — next task ready |
| `DECISION_RECONCILED` | Brain chose next queue item |
| `BATCH_START` | Started automated batch (5 prompts) |
| `WORKER_SUBMIT` | Worker finished a round |
| `WORKER_SUBMIT_AUTO` | Worker auto-submitted a round |
| `BROKER_ACCEPT` | Broker approved delivery |
| `BROKER_REJECT` | Broker blocked delivery — check Goal 1 loop |
| `VALIDATOR_PASS` | Validators passed |
| `VALIDATOR_FAIL` | Validators failed — see Backlog |

---

## 3 — UI implementation checklist (`sa-0821`)

**Phase A — Data (Worker, this repo)**  
- [x] `hub_home_founder_view_v1.py`  
- [x] Wire into `sina_command_lib.build_payload`  
- [x] `validate-hub-home-founder-view-v1.sh`  

**Phase B — Render**  
- [x] Replace `renderCommand()` with `renderHomeFounderView()` (`home_founder_view` sections)  
- [x] No `sa-XXXX` in default viewport — `status.next_plain` only; detail panel on expand  
- [x] Goals · Actions · Recent events from payload  
- [x] CSS `.sc-home-founder-detail` hidden until toggle (`aria-hidden=false`)  

**Phase C — Verify**  
- [x] `python3 build-sina-command-panel.py`  
- [x] `bash scripts/validate-hub-home-founder-view-v1.sh`  
- [ ] Manual: Hub home at :13020 — confirm no `sa-` in collapsed view  

---

## 4 — What stays on home (de-scope)

| Keep (collapsed) | Move to Essentials / detail |
|---|---|
| Status + primary batch CTA | Council Room unify banner (link only) |
| Goals progress | Full subject grid (“Focus now”) |
| 4 quick actions | Full Quick open hub grid |
| Recent events | Track banner thread list |

---

## 5 — Authority note

Claude External Advisor mockup = **advise only** for layout copy. This LOCKED spec is the build contract after ASF imperative. Do not reorder roadmap or renumber phases from advisor paste alone.
