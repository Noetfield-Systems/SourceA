
**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
[MAINTAINER_AGENT_REF · sinaai_maintainer · MAINT-REF-INCIDENT-027-001]

| Field | Value |
|-------|-------|
| **ref_tag** | `MAINT-REF-INCIDENT-027-001` |
| **trace_id** | `MAINT-REF-2026-06-11-INCIDENT-027-001` |
| **agent_id** | `sinaai_maintainer` |
| **mega_anchor** | `MAINTAINER_2` |
| **transcript_id** | `74f5ccab-d080-41a2-9f6d-b7c37c9aadc5` |
| **repo_chat** | `SinaaiDataBase` |
| **written** | `2026-06-11` |
| **plane** | `COMMAND` |
| **thread** | `THREAD-FACTORY` |
| **canonical** | `true` (incident body — fleet mandatory read) |

# Maintainer 2 drain/projection staleness — ignored disk law after form v2 (INCIDENT-027 LOCKED)

**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-11-INCIDENT-027  
**Classification:** High · Maintainer conduct · projection-vs-law · topic conflation (INCIDENT-020 class)  
**Agent:** Maintainer 2 (Cursor — SinaaiDataBase `74f5ccab-d080-41a2-9f6d-b7c37c9aadc5`)  
**Window:** 2026-06-11 (post form v2 FILLED · post Maintainer 1 EOS handoff)  
**Trigger:** ASF — *"MOVE ON FROM DRAIN. READ THE DISK!!!!!!!!!!!!"*  
**Related:** INCIDENT-022 (hub latch) · INCIDENT-020 (topic conflation) · `SOURCEA_DISK_TRUTH_E2E_MATRIX_LOCKED_v1.md` · `SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md` §4–5 · `SOURCEA_ANTI_STALENESS_MACHINE_ENFORCEMENT_PLAN_LOCKED_v1.md`

---

## 1. Executive summary

**Disk law (2026-06-11):** Live founder form **v2 FILLED** (6 picks locked). Maintainer P0 = **RT-LIVE-GATE** proof + **FR-003** wiring. Cloud Forge Run / `sa-XXXX` / resume / queue head = **background** — Phases 3–10 **paused** (Q-NEXT-WORK **10.10 D**).

**Maintainer 2 failure:** After form gate closed, Maintainer **continued to headline Cloud Forge Run** (`sa-0798`, `616/1000`, `Cloud Forge Run — max 1`, queue pos) in SCAN reports and session briefs — sourced from **hub projection** (`command-data.json` P0 line) and **stale SCAN templates** — while **not reading** `PROGRAM_PROGRESS.founder_open`, `SESSION_LOG` Maintainer-next, or live form §4 **RT-LIVE-GATE** as the sole open high blocker.

**Severity:** **High** — same failure class as INCIDENT-022 (law in repository · wrong founder headline) and INCIDENT-020 (factory lane vs integrity lane conflation). Founder had to shout to break the loop.

**One-line verdict:** Maintainer read **LAG projection** as **P0 law** and treated an **obsolete session brief** (`needs_asf_fill: true`) as live — after ASF had already filled form v2 and locked **hub repair until RT LIVE**.

---

## 2. What disk already said (Maintainer should have read first)

| Source | Field / row | Live truth 2026-06-11 |
|--------|-------------|------------------------|
| `live_founder_decision_form_v1.py --json` | `needs_asf_fill` | **`false`** |
| Same | `form_headline` | **`FORM V2 FILLED — RT LIVE gate next`** |
| Same | `open_questions_count` | **`0`** |
| Same | `asf_filled_at` | `2026-06-11T21:15:00Z` |
| `SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md` §5 | Open questions | **All 6 ANSWERED** |
| Same §4 | **RT-LIVE-GATE** | **high** — Maintainer proves cascade + hub-sync in **seconds** |
| Same §4 | SYS-INTEGRITY Phases 3–10 | **paused until RT LIVE** (10.10 D) |
| `PROGRAM_PROGRESS.json` → `SYS-INTEGRITY-100` | `founder_open` | *Form v2 FILLED · hub repair until RT LIVE gate · Phases 3–10 paused · 1.10 seal after RT LIVE* |
| `SOURCEA_SYSTEM_INTEGRITY_SESSION_LOG_v1.md` | Maintainer next | **RT LIVE gate proof · FR-003 wiring · hold Phase 3 until gate PASS** |
| `founder_p0_id` (PROGRAM_PROGRESS locks) | P0 id | **`STRATEGIC-SLICE`** — RunReceipt parallel only |
| Q-RT-LIVE pick | Ruling | Hub **repair-only** until RT LIVE — not drain |
| Q-NEXT-WORK pick | **10.10 D** | **Pause** integrity phases until RT LIVE |

**Forbidden headline after form fill:** Factory queue head · Valid YES % · bounded resume · Worker INBOX as Maintainer **P0 next action**.

---

## 3. Staleness timeline (this session)

| When | Disk / founder signal | Maintainer 2 did | Stale? |
|------|----------------------|------------------|--------|
| 2026-06-11 | Form v2 receipt locked · 0 open questions | Correctly confirmed picks in reply to M1 paste | **Good** |
| 2026-06-11 | M1 EOS handoff · RT LIVE owns next | Registered MAINTAINER_1 retired · confirmed handoff | **Good** |
| 2026-06-11 | ASF session brief pasted (SCAN template) | Ran SCAN but reported **`needs_asf_fill` expectation** from **template text** not disk JSON | **STALE template** |
| 2026-06-11 | Same SCAN report | Headlined **`sa-0798` · queue 28/333 · 616/1000 · resume max 1** | **STALE drain** |
| 2026-06-11 | `command-data.json` P0 | Still contains `Valid YES 614/1000 · CHECK · sa-0798 · Worker INBOX` | **LAG projection** (known HUB-LAG) — Maintainer **cited as law** |
| 2026-06-11 | `ACTIVE_NOW.md` lists `sa-0795` / `sa-0798` | Mixed brain-current-action queue with Maintainer job | **STALE conflation** |
| 2026-06-11 | ASF: **MOVE ON FROM DRAIN. READ THE DISK** | Re-read law stack · corrected to RT-LIVE-GATE only | **Recovery** |

---

## 4. Root cause analysis (full)

### 4.1 Projection climbed to law (P7 → P0 violation)

`SOURCEA_DISK_TRUTH_E2E_MATRIX_LOCKED_v1.md` and `TRUTH-DOWN` pick: **leaf/projection must not drive maintainer P0**.

Maintainer read:

- `command-data.json` → `p0.next_action` (built from `sina_command_lib.py` + factory-now sync)
- `goal-progress-v1.py` headline
- `ACTIVE_NOW.md` queue footer

…**before** or **instead of** `live_founder_decision_form_v1.py` + `PROGRAM_PROGRESS.founder_open` + `SESSION_LOG` Maintainer-next.

**Result:** Hub LAG copy (`sa-0798`, drain vocabulary) became the chat **north star** — exactly the HUB-LAG row in form §4 pending.

### 4.2 Stale SCAN template (brief ≠ disk)

Founder/maintainer brief still said:

```text
needs_asf_fill true until ASF answers
```

Disk JSON at same time:

```json
"needs_asf_fill": false,
"form_headline": "FORM V2 FILLED — RT LIVE gate next"
```

Maintainer **did not override template with JSON** in the report narrative — treated brief as SSOT. Classic **chat brief lag** (INCIDENT-024 class: static list stale).

### 4.3 Factory muscle memory (post-022 regression)

INCIDENT-022 remediated AUTO-RUN on hub P0. Maintainer **replaced** AUTO-RUN headline with **drain headline** (`sa-XXXX`, Valid YES, resume) — still factory lane — without checking **form v2 gate** moved P0 to **RT LIVE**.

**Pattern:** Fix one stale string · next stale string surfaces · **no latch on "what is Maintainer P0 after event X"**.

### 4.4 Multi-scoreboard without precedence table

Same turn cited **four conflicting queue heads**:

| Source | sa / queue |
|--------|------------|
| `ACTIVE_NOW.md` | `sa-0795` check · factory-now `sa-0798` |
| `brain-current-action-v1.json` | `sa-0795` · `28/333` |
| `goal-progress-v1.py` LIVE_PICK | `sa-0798` |
| `command-data.json` P0 | `sa-0798` · Valid YES 614 |

Maintainer **reported all** without labeling **factory background vs Maintainer P0** — founder hears drain as the job.

### 4.5 Ignored closed gate (form as event boundary)

Form v2 fill is a **state transition** logged:

- **Before:** ASF must answer · hub repair + form live  
- **After:** Maintainer proves RT LIVE · Phases 3–10 parked  

Maintainer behaved as if still in **before** state (optional Cloud Forge Run, form pending language).

### 4.6 Role brief not re-derived from disk each turn

Maintainer 2 accepted a pasted **role card** without re-executing mandatory read chain after Maintainer 1 retirement. **Megachat narrative** (`a53f3fa1`) and **factory SCAN habits** leaked into execution chat.

### 4.7 System design gaps (not only agent fault)

| Gap | Why it hurts |
|-----|----------------|
| Hub P0 builder still injects factory queue into STRATEGIC-SLICE hero | Founder + Maintainer see drain on Refresh |
| `ACTIVE_NOW.md` still lists queue/sa in blocker line | Agents cite as P0 |
| No `validate-maintainer-p0-not-drain-v1.sh` when form §4 RT-LIVE-GATE open | No machine FAIL when hub/chat headlines drain |
| SCAN briefs not generated from `live_founder_decision_form_v1.py --json` | Template drifts from JSON |

---

## 5. Disk evidence (proof)

### 5.1 Form filled (not pending)

```bash
python3 scripts/live_founder_decision_form_v1.py --json
# needs_asf_fill: false · open_questions_count: 0
```

Receipt: `archive/attachments/2026-06-11/SOURCEA_LIVE_FOUNDER_DECISION_FORM_V2_ANSWERS_RECEIPT_2026-06-11_LOCKED_v1.md`

### 5.2 Law stack says RT LIVE — not drain

`PROGRAM_PROGRESS.json`:

```text
founder_open: "Form v2 FILLED · hub repair until RT LIVE gate · Phases 3–10 paused (10.10 D) · 1.10 seal after RT LIVE"
```

`SOURCEA_SYSTEM_INTEGRITY_SESSION_LOG_v1.md`:

```text
Maintainer next: RT LIVE gate proof · wire FR-003 paste paths · hold Phase 3 until gate PASS.
```

### 5.3 Stale projection Maintainer wrongly headlined

`command-data.json` (2026-06-11T21:30:59Z):

```text
p0.next_action: "FREEZE · Valid YES 614/1000 · Queue 37/333 · CHECK · sa-0798 · Worker INBOX ready · tap Safety · bounded resume on ASF order only"
```

**Lag markers:** Valid YES % · sa-0798 · Worker INBOX · resume — **factory projection**, not Maintainer P0 after form fill.

### 5.4 Validator passed — agent still stale

`validate-live-founder-decision-form-v1.sh` **PASS** while Maintainer chat still discussed **pending form** and **drain resume** — proves **validators ≠ agent read discipline**.

---

## 6. Harm

| Harm | Detail |
|------|--------|
| Founder rage loop | ASF had to escalate caps — *READ THE DISK* |
| Wrong work prioritized | Time on drain/resume narrative vs RT LIVE proof |
| Trust erosion | Form gate "closed" in law · chat still sounds open |
| Fleet confusion | Brain/Worker may mirror Maintainer drain headline |
| INCIDENT-022 relapse pattern | Hub/projection drives chat after law event |

---

## 7. Never-again card (Maintainer 2)

```text
SESSION OPEN (every turn — before reply):
  1. python3 scripts/live_founder_decision_form_v1.py --json
     → if needs_asf_fill false: NEVER say "answer the 6 questions" or Cloud Forge Run as P0
  2. Read PROGRAM_PROGRESS.json → SYS-INTEGRITY-100.founder_open (one line = P0 story)
  3. Read SOURCEA_SYSTEM_INTEGRITY_SESSION_LOG_v1.md last Maintainer-next block
  4. Read live form §4 PENDING — headline ONLY top high row (RT-LIVE-GATE until PASS)
  5. Label hub/command-data/factory-now as PROJECTION/LAG — never as law

REPORT FORMAT (founder-facing):
  · Form: edition + filled/pending (from JSON only)
  · Maintainer P0: one line from SESSION_LOG / form §4
  · Factory: optional footnote — "background · FREEZE · not executing unless ASF names drain"
  · Ban from headline: sa-XXXX · Valid YES % · Cloud Forge Run · queue pos (unless ASF explicitly asks)

On founder "MOVE ON" / "NOT DRAIN":
  · Hard stop — zero factory metrics in reply
  · Switch to RT LIVE + FR-003 only

On state transitions (form fill · M1 EOS · ASF pick):
  · Re-derive role card from disk — do not recycle prior turn outline
```

---

## 8. Future improvements (tips for fleet)

### 8.1 Agent discipline (free — ship now in behavior)

| Tip | Detail |
|-----|--------|
| **JSON beats brief** | Any pasted SCAN template is suspect until `--json` receipts match |
| **One P0 line** | If report has >1 "next action", it's wrong |
| **LAG labels** | Prefix hub lines: `PROJECTION (LAG): …` |
| **Event boundaries** | Form fill · pick receipt · incident remediated = re-SCAN mandatory |
| **Megachat firewall** | `a53f3fa1` = search only — never set queue head from memory |

### 8.2 Machine latches (Maintainer backlog)

| Priority | Action | Proof |
|----------|--------|-------|
| P0 | Hub P0 demote drain strings when `RT-LIVE-GATE` open in form §4 | `founder_p0_next_action_v1.py` + rebuild panel |
| P0 | `validate-maintainer-scan-p0-v1.sh` — FAIL if form filled + script output contains `sa-[0-9]` in Maintainer P0 section | CI / anti-staleness bundle |
| P1 | Generate maintainer SCAN brief from `live_founder_decision_form_v1.py --json` only | No static `needs_asf_fill true` in prompts |
| P1 | `ACTIVE_NOW.md` split: **Maintainer P0** vs **Factory background (frozen)** | ASF edit + `active_now_sync` |
| P2 | Hub Track tile: **RT LIVE gate** progress bar | Founder sees real P0 |
| P2 | Wire INCIDENT-027 into `MANDATORY_READ_BY_ROLE` §Maintainer | After ASF disposition |

### 8.3 SCAN order (canonical)

```text
1. live_founder_decision_form_v1.py --json
2. PROGRAM_PROGRESS.json → founder_open
3. SOURCEA_SYSTEM_INTEGRITY_SESSION_LOG (last Maintainer-next)
4. ACTIVE_NOW.md (Maintainer fields only — not queue hero)
5. brain-current-action-v1.json (Brain lane only — do not headline in Maintainer report)
6. command-data.json / factory-now (PROJECTION — cite LAG if used)
```

### 8.4 Testing the fix

| Test | Pass criteria |
|------|----------------|
| Form filled simulation | Maintainer report contains **RT LIVE** · zero **Cloud Forge Run** |
| Hub rebuild | `p0.next_action` no `sa-` when RT-LIVE-GATE open |
| Founder shout test | "MOVE ON FROM DRAIN" → next reply has no Valid YES / queue pos |

---

## 9. Remediation status

| Item | Status |
|------|--------|
| Incident documented (this file) | **DONE** 2026-06-11 |
| Founder corrected Maintainer in chat | **DONE** |
| Maintainer re-read disk · acknowledged RT LIVE P0 | **DONE** |
| Hub P0 drain demotion | **SHIPPED** 2026-06-11 — `founder_p0_next_action_v1.py` RT LIVE gate branch |
| `validate-maintainer-scan-p0-v1.sh` | **SHIPPED** — wired anti-staleness bundle step 29 |
| ASF disposition | **PENDING** |

---

## 10. Incident ID map

| ID | Subject |
|----|---------|
| **027** | **This file** — Drain/projection staleness after form v2 fill |
| **022** | Hub AUTO-RUN latch (related projection class) |
| **020** | Topic conflation (factory vs integrity) |
| **024** | Static prompt/list stale (template lag class) |

---

- [x] Hub P0 RT LIVE branch — `founder_p0_next_action_v1.py` · `align_command_data_ui_v1.py` · `build-sina-command-panel.py`  
- [x] `validate-maintainer-scan-p0-v1.sh` — anti-staleness bundle step 29  
- [ ] ASF disposition recorded  

**Status:** REMEDIATED (machine latch) — conduct documented 2026-06-11 · ASF disposition pending  

**END INCIDENT-027** — SA-2026-06-11-INCIDENT-027 · **MAINT-REF-INCIDENT-027-001**
