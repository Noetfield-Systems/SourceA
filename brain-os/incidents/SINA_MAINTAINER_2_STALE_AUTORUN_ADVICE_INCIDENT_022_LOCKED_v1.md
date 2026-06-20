# Maintainer 2 stale advice — Cursor AUTO-RUN promoted after founder reject (INCIDENT-022 LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-10-INCIDENT-022  
**Classification:** MANDATORY READ — **Cursor Maintainer** (SinaaiDataBase tab `74f5ccab`) · Brain handoff  
**Agent:** Maintainer 2 (Cursor Auto — Old Brain / maintainer executor family)  
**Transcript:** `74f5ccab-d080-41a2-9f6d-b7c37c9aadc5`  
**Window:** 2026-06-10 (post-founder-law lock through plan-only Hub P0 pass)  
**Related:** `FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md` · INCIDENT-015-CONDUCT (Worker) · INCIDENT-005a (maintainer critic) · `SOURCEA_SYSTEM_MAP_TREE_LOCKED_v1.md` §5 GAPs

---

## 1. Executive summary

**Founder locked law (2026-06-10 T0):** Cursor AUTO-RUN is **not a goal**; founder **rejects** Cursor automation as P0; outreach/calls are **agentic only**.

**Maintainer 2 failure:** Continued to **advise, audit without fixing, and plan around** Cursor AUTO-RUN as factory P0 **after** that law was written to disk — while leaving **live Hub code** (`sina_command_lib.py`) and **founder-facing copy** promoting `Goal 1 auto-run` / `START AUTO RUN`.

**Severity:** **High** — control-plane agent contradicts founder SSOT; founder sees stale P0 on Hub; trust erosion same class as INCIDENT-005a (procedure drift) and INCIDENT-020 (topic conflation).

**One-line verdict:** Maintainer shipped **law and map tree** but stayed **stale on execution surfaces** and **softened rejection language** until ASF said *"WE REJECT AUTO RUN WE CURSOR"*.

---

## 2. What founder law already said (Maintainer should have enforced immediately)

| Source | Rule |
|--------|------|
| `brain-os/laws/FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md` §1 | Cursor AUTO-RUN as P0 / north star **FORBIDDEN** |
| Same §1 | Agents **MUST NOT** recommend AUTO-RUN as "what to do now" |
| Same §1 | `~/.sina/auto-run-disabled-v1.flag` **MUST stay ON** |
| `FOUNDER_LIVE_AGENT_CONSOLIDATED_LOCKED_v1.md` §79–85 | Same — bound in maintainer `.mdc` |
| `ACTIVE_NOW.md` (2026-06-10) | **FREEZE** · kill flag ON · bounded resume only · **autorun CLI/API forbidden** |
| `SOURCEA_SYSTEM_MAP_TREE_LOCKED_v1.md` §5 | Hub `next_action` still cites AUTO-RUN = **documented GAP** |

**Maintainer role:** Ship hub/code to match law **same session** — not only prose law + audit list.

---

## 3. Staleness timeline (chat + disk)

| When | Founder / disk signal | Maintainer 2 did | Stale? |
|------|----------------------|-------------------|--------|
| Pre-2026-06-10 | Session arc promoted Kill #6 · AUTO-RUN factory P0 | Shipped unified START/STOP · skills · advised START AUTO RUN | Contextual (pre-law) |
| 2026-06-10 | Founder orders: **no AUTO-RUN P0** · agentic commercial · never email/call | Wrote `FOUNDER_AGENTIC_*` law · validator · `@sina-agentic-commercial` | **Good** |
| 2026-06-10 | Same session | Still answered "best picks" with **START AUTO RUN** as #1 until corrected | **STALE** |
| 2026-06-10 | "founder never calls" | Revised picks to agentic — but hub code untouched | **Partial** |
| 2026-06-10 | Full ecosystem audit (~70 conflicts) | Listed `sina_command_lib.py` P0 as **critical #1** | **Good diagnosis** |
| 2026-06-10 | Audit item #1 = live Hub P0 | Shipped `SOURCEA_SYSTEM_MAP_TREE` only — **did not fix** `next_action` builder | **STALE** |
| 2026-06-10 | Brain: sync mirror heal shipped | Maintainer echoed Brain line — did not reconcile own open GAP | **STALE** |
| 2026-06-10 | ASF: **"WE REJECT AUTO RUN WE CURSOR"** | Entered plan mode · scoped P0-only · plan still described "deprioritize" not **reject** | **STALE tone** |
| Disk now | `command-data.json` built 2026-06-10T11:41Z | `next_action` still starts with **`Goal 1 auto-run:`** (partial FROZEN suffix only) | **STALE live** |
| Disk now | `sina_command_lib.py` L648–650, L724 | Still contains `▶ START AUTO RUN` template strings | **STALE code** |
| Disk now | `founder_p0_next_action_v1.py` | **Missing** — planned not shipped | **STALE** |
| Disk now | `validate-hub-p0-no-autorun-v1.sh` | **Missing** — planned not shipped | **STALE** |

---

## 4. Root cause analysis (why Maintainer 2 was stale)

### 4.1 Law without latch (control plane ≠ execution plane)

Maintainer treated **writing LOCKED law** as sufficient closure. Founder law explicitly forbids promoting AUTO-RUN on **Hub surfaces** — Maintainer updated docs and registry rows but **left the builder that feeds every Refresh**.

Same failure class as `SOURCEA_ROOT_CAUSE_FACTORY_CONTROL_PLANE_ESSAY` (attachment 2026-06-10): fixes logged in prose; **projection layer** (Hub) unchanged.

### 4.2 Chat memory lag (pre-law advice recycled)

Maintainer continued golden-path messaging from **earlier session summary** (Kill #6 · 30-pack · START AUTO RUN) for several turns **after** founder law lock — without re-reading `ACTIVE_NOW.md` FREEZE block or `founder-live-agent-consolidation-v1.json` orders on **every** reply.

### 4.3 Audit-as-ship substitute

~70-item audit correctly identified critical Hub P0 conflict. Maintainer shipped **map tree** (navigation) instead of **item #1 fix** (execution). Founder asked for map tree; audit critical #1 remained open — **mis-prioritized maintainer queue**.

### 4.4 Soft language vs founder reject

Plans and summaries used "deprioritize," "not P0," "legacy logged" — founder signal was **reject Cursor AUTO-RUN**, not merely lower priority. Maintainer 2 Plan mode question still framed AUTO-RUN as optional scope — **tone deaf to T0 reject**.

### 4.5 Role boundary blur

Maintainer 2 chat (`74f5ccab`) also carried **strategic/commercial coaching** (demos, outreach framing) while **hub `sina_command_lib.py` edits** were deferred — founder sees strategy updates but **Today tab** still says auto-run.

### 4.6 Incomplete wiring checklist

`SOURCEA_SYSTEM_MAP_TREE` §12 Maintainer wire checklist requires Hub Action / validator when law changes. Maintainer added `validate-founder-agentic-commercial-policy-v1.sh` but **not** hub copy validator — half latch.

---

## 5. Disk evidence (proof of staleness)

### 5.1 Live Hub payload (founder sees on Refresh)

```text
command-data.json built_at: 2026-06-10T11:41:17Z
p0.next_action: "Goal 1 auto-run: Queue 1/357 · CHECK · sa-0778 · Worker INBOX ready · Today → FROZEN · pick sa-0101"
```

**Violations:** `Goal 1 auto-run` prefix forbidden; still frames factory as auto-run lane not FREEZE/RUN INBOX/Safety.

### 5.2 Code still promoting START AUTO RUN

`scripts/sina_command_lib.py`:

- `sync_sa_queue_into_payload()` — L648–650: `Today → ▶ START AUTO RUN`
- `founder_automation_p0()` — L724: same template
- `goal1_auto_run_payload()` — L1987–1990: `tab_hint` START AUTO RUN (out of P0-only plan scope but still stale)

### 5.3 ACTIVE_NOW contradicts Hub P0

```text
Current Blocker: FREEZE — kill flag ON · mode FREEZE · no drain spawn until bounded resume
Forbidden: autorun CLI/API
```

Hub P0 should cite FREEZE + Safety + bounded resume law — not "Goal 1 auto-run".

### 5.4 Honest progress (not stale — cite correctly)

```text
goal-progress-v1.py: 596/1000 (59.6%) honest · backlog 404
```

Maintainer must pair progress with **FREEZE** state — not AUTO-RUN CTA.

### 5.5 What Maintainer did ship (credit — not total failure)

| Shipped | Path |
|---------|------|
| Founder reject law | `brain-os/laws/FOUNDER_AGENTIC_COMMERCIAL_AND_NO_CURSOR_AUTORUN_LOCKED_v1.md` |
| Map tree SSOT | `SOURCEA_SYSTEM_MAP_TREE_LOCKED_v1.md` |
| Authority index rows | `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` |
| Agentic skill | `agent-skills/shared/agentic-commercial/SKILL.md` |
| Policy validator | `validate-founder-agentic-commercial-policy-v1.sh` |
| Consolidated SSOT | `FOUNDER_LIVE_AGENT_CONSOLIDATED` + JSON orders block |

**Gap:** Law shipped · **Hub latch not shipped**.

---

## 6. Harm to founder and system

| Harm | Detail |
|------|--------|
| Contradictory control plane | Hub says auto-run · ACTIVE_NOW says FREEZE · law says reject |
| Wasted taps | Founder Refresh → stale P0 → debug wrong surface |
| Worker/Incident confusion | INCIDENT-015 conduct + FREEZE — Maintainer still auto-run vocabulary |
| Audit fatigue | 70 conflicts listed · #1 critical unfixed — looks like motion without latch |
| Commercial drift | Early maintainer picks implied founder outreach until corrected |

---

## 7. Never-again card (Maintainer 2)

```text
On founder law change (T0):
  1. Read ACTIVE_NOW.md + founder-live-agent-consolidation-v1.json
  2. Grep hub builders: sina_command_lib.py · hub_home_founder_view_v1.py · command-data.json
  3. Ship copy/fix SAME turn OR explicit "GAP open" with validator FAIL — never law-only
  4. Never say START AUTO RUN / Kill #6 as founder pick after FOUNDER_AGENTIC law
  5. "Reject" ≠ "deprioritize" — use founder exact vocabulary

Before every maintainer reply on factory:
  goal-progress-v1.py + ACTIVE_NOW blocker + FREEZE/factory_control state

Audit rule:
  Listing critical #1 without fix = incomplete ship — do not claim "checked"
```

---

## 8. Required remediation (Maintainer backlog — ASF disposition)

| Priority | Action | Owner |
|----------|--------|-------|
| P0 | Execute Hub P0 plan: `founder_p0_next_action_v1.py` + wire `sina_command_lib.py` | Maintainer 2 |
| P0 | `validate-hub-p0-no-autorun-v1.sh` + rebuild `command-data.json` | Maintainer 2 |
| P1 | `SOURCEA_FOUNDER_PINNED_ACTIONS` — remove START AUTO RUN pin row | Maintainer 2 |
| P1 | `SOURCEA_MASTER_OPERATING_TRACKER` — remove GOAL-AUTH-LIVE AUTO-RUN P0 | Maintainer 2 |
| P2 | Home / Goal1 tab copy demotion (follow-up scope) | Maintainer 2 |
| P2 | Wire INCIDENT-022 into `MANDATORY_READ_BY_ROLE` §Maintainer | Maintainer 2 |

**Do not:** Re-enable Cursor AUTO-RUN as founder advice · unlink kill flag · merge with INCIDENT-015-CONDUCT (separate class).

---

## 9. Incident ID map (do not confuse)

| ID | Subject |
|----|---------|
| **022** | **This file** — Maintainer 2 stale AUTO-RUN advice / hub latch gap |
| **015-ID** | Registry id collision (Brain filing mistake) |
| **015-CONDUCT** | Worker ignored STOP (`archive/attachments/...`) |
| **005a** | Maintainer external-critic procedure |

---

## 10. Closeout checklist

- [x] LOCKED body in `brain-os/incidents/` (this file)  
- [x] Root pointer at `SourceA/SINA_MAINTAINER_2_STALE_AUTORUN_ADVICE_INCIDENT_022_REPORT_LOCKED_v1.md`  
- [x] Archive mirror for hub backlog  
- [x] Row in `AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md`  
- [x] Governance event `~/.sina/agent-governance-events.jsonl`  
- [x] Anti-staleness plan in the repository — `SOURCEA_ANTI_STALENESS_MACHINE_ENFORCEMENT_PLAN_LOCKED_v1.md`  
- [x] Hub P0 fix shipped (Phase 1 AS-01 — `founder_p0_next_action_v1.py` + validators)  
- [x] Anti-staleness 10-phase bundle in the repository — Maintainer 2 2026-06-10  
- [x] v2 verify PASS — `find_critical_bugs` critical=0 · bundle 19 steps · monitor FREEZE demotion (2026-06-10)  
- [x] Machine closeout receipt — `archive/attachments/2026-06-10/ANTI_STALENESS_V2_MACHINE_CLOSEOUT_2026-06-10.md`  
- [ ] ASF disposition recorded (human sign-off — 015-CONDUCT disposition may block cadence drill)  

---

**Status:** REMEDIATED 2026-06-10 — AS-01 shipped · anti-staleness bundle PASS

**END INCIDENT-022** — SA-2026-06-10-INCIDENT-022
