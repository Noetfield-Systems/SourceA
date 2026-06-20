# Brain disk live wire — executor mandatory CART (task-by-task)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 LOCKED  
**Date:** 2026-06-14  
**Authority:** ASF order · INCIDENT-034 · `AGENT_DISK_LIVE_WIRE_FIRST_LOCKED_v1.md`  
**Who runs this cart:** **Cursor agent in SourceA** — there is no separate executor role or team. **I** run every task below.  
**Who tracks:** Governance Specialist chat (L1 #2) · ASF confirms close.

---

## Fresh Brain chat — ASF correction (NOT a fix)

| Wrong statement (retracted) | Correct law |
|----------------------------|-------------|
| “Brain reads chat instead of disk” | **False.** Brain and Worker both read whatever the **system injects** — session gate · entry gate · active rules · broker cache · hub sync · `command-data` projection · stale JSON logged. |
| “Fresh chat = young training” | **False.** No model training. |
| “Fresh chat fixes drift after disk heal” | **Misleading.** If disk still steers Prompt feed, **new chat hits the same drift immediately** — same inject · same receipts · same stale files. |
| **What actually fixes drift** | **Disk live wire** · scrub · steer guard · subprocess sync · brain/worker live context · validators green · Maintainer hub fixes (AR-034-01/02). |

**Fresh Brain chat:** Optional UX reset only — **zero effect** on Prompt feed steer while disk is dirty. **Never** assign Brain guilt for “not reading disk.” **Never** tell founder fresh chat replaces disk heal.

---

## Ownership (RACI)

| Role | Who | Owns |
|------|-----|------|
| **ASF** | You | Final close · confirm close-line |
| **Cursor agent** | **This chat / SourceA agent** | **Run C-00–C-16** · fix disk · log events · no separate executor |
| **Governance Specialist (L1 #2)** | Governance chat | Track cart · meta-audit · INCIDENT-034 close |
| **Brain chat** | Brain workspace | Consumes disk when clean — never blamed for drift |
| **Worker chat** | Worker workspace | RUN INBOX when disk clean |
| **Maintainer 2** | SinaaiDataBase / hub | AR-034-01 · AR-034-02 only |

---

## Mandatory CART — every task

Run order: **C-00 → C-01 … C-12** on Brain-touching sessions. **C-13** every substantive ship. **C-14** when dashboard/hub restarted.

---

### C-00 — Session identity

| Field | Value |
|-------|--------|
| **Owner** | **Cursor agent (me)** |
| **Tracker** | Governance |
| **When** | Start of every Brain/Worker/Governance executor session |
| **Action** | `python3 scripts/agent_rules_loop_orchestrator.py --phase session_start` OR read `/api/agent-rules-in-charge-v1` |
| **Verify** | Rules banner loaded · no parallel duplicate `.mdc` for same topic |
| **Receipt** | Session ledger / rules loop stdout |
| **Fail** | Stop · do not ship vocabulary or hub law until rules in charge confirmed |

---

### C-01 — Anti-staleness auto wire (L0.5→L1→L2)

| Field | Value |
|-------|--------|
| **Owner** | **Cursor agent (me)** |
| **Tracker** | Governance · `anti-staleness-auto-wire-v1.json` |
| **When** | Brain session start · Brain-touching ship · after queue/factory change |
| **Action** | `python3 scripts/anti_staleness_auto_wire_v1.py --role brain --tier session --json` |
| **Verify** | `"ok": true` · `factory_now_line` present · `queue_sa` non-empty when `mode=SINGLE_SA` |
| **Receipt** | `~/.sina/anti-staleness-auto-wire-v1.json` |
| **Fail** | Run `queue_ssot_unify_v1.py --json` · heal queue · re-run C-01 · **no PASS report to founder** |

---

### C-02 — Disk live wire sync

| Field | Value |
|-------|--------|
| **Owner** | **Cursor agent (me)** |
| **Tracker** | Governance |
| **When** | Inside C-01 · or standalone after any truth/factory change |
| **Action** | `python3 scripts/disk_live_wire_sync_v1.py --role brain --json` |
| **Verify** | Steps: truth_bundle · agent_live_surfaces · brain_live_surfaces · memory_mirror · worker_live_context · brain_live_context |
| **Receipt** | `~/.sina/disk-live-wire-receipt-v1.json` |
| **Fail** | Fix failing step source · re-run C-02 |

---

### C-03 — Brain live context (Brain SSOT block)

| Field | Value |
|-------|--------|
| **Owner** | **Cursor agent (me)** |
| **Tracker** | Governance · Brain session gate |
| **When** | Every Brain session · after C-02 · before Brain founder-facing reply |
| **Action** | `python3 scripts/brain_live_context_v1.py --json` |
| **Verify** | File exists · `text_block` contains `RUN INBOX` · **no** `Prompt feed` · **no** `Confirm auto-send` · `mandatory_next` like `Worker chat → RUN INBOX — sa-XXXX ROLE` |
| **Receipt** | `~/.sina/brain-live-context-v1.json` |
| **Fail** | Run C-04 scrub · re-run C-03 · Brain must read this file before close-line |

---

### C-04 — Brain stale scrub

| Field | Value |
|-------|--------|
| **Owner** | **Cursor agent (me)** |
| **Tracker** | Governance |
| **When** | After C-03 if drift suspected · inside anti-staleness · after hub/dashboard sync |
| **Action** | `python3 scripts/brain_stale_prompt_scrub_v1.py --json` |
| **Verify** | `actions[]` logged · brain-current-action · brain-goal1-validation founder lines clean |
| **Receipt** | Scrub stdout · updated JSON mtimes |
| **Fail** | Hand-fix named file in `actions` · re-run C-04 |

---

### C-05 — Worker stale scrub (paired)

| Field | Value |
|-------|--------|
| **Owner** | **Cursor agent (me)** |
| **Tracker** | Governance |
| **When** | Same as C-04 · every session tier worker or session |
| **Action** | `python3 scripts/worker_stale_prompt_scrub_v1.py --json` |
| **Verify** | `execution-lane-v1.json` advisory=`live_next10_mirror` · no `prompt_feed_lane` key in run-inbox truth |
| **Receipt** | Scrub stdout |
| **Fail** | `python3 scripts/run_inbox_disk_truth_v1.py --write --json` · re-run C-05 |

---

### C-06 — Brain session gate

| Field | Value |
|-------|--------|
| **Owner** | **Cursor agent (me)** |
| **Tracker** | Governance |
| **When** | Brain chat session start (mandatory before substantive Brain work) |
| **Action** | `python3 scripts/agent_session_gate_run_v1.py --role brain --json` |
| **Verify** | Receipt has `brain_live_context` block · `founder_close_line` has RUN INBOX · `inject` has no Prompt feed steer |
| **Receipt** | `~/.sina/agent_session_gate_receipt_v1.json` |
| **Fail** | Fix failing step in `steps[]` · re-run from C-01 |

---

### C-07 — Brain entry gate

| Field | Value |
|-------|--------|
| **Owner** | **Cursor agent (me)** |
| **Tracker** | Governance |
| **When** | Brain turn after session gate · pre-ship with `--scan-text` on draft close-line |
| **Action** | `python3 scripts/cursor_entry_gate.py --role brain --json` |
| **Verify** | Payload includes `read_first` → brain-live-context · `founder_close_line` positive path |
| **Receipt** | `~/.sina/cursor_entry_gate_receipt_v1.json` |
| **Fail** | If `--scan-text` hits stale: `GATE_FAILED founder_close_line` — rewrite draft · never ship |

---

### C-08 — Brain fast startup (route only)

| Field | Value |
|-------|--------|
| **Owner** | **Cursor agent (me)** |
| **Tracker** | Brain receipt |
| **When** | `brain-session-start.sh` path · broker brain_sync fast |
| **Action** | `python3 scripts/brain_fast_startup_v1.py --json` |
| **Verify** | `mandatory_next` = RUN INBOX route · no E2E/hospital on session start |
| **Receipt** | `~/.sina/brain-fast-startup-v1.json` |
| **Fail** | Do not run full validator bundle — fix bind/queue · re-run fast tick |

---

### C-09 — Brain governance wire

| Field | Value |
|-------|--------|
| **Owner** | **Cursor agent (me)** |
| **Tracker** | Governance · L1 pipeline |
| **When** | After factory/queue change · L1 mesh refresh |
| **Action** | `python3 scripts/brain_governance_wire_v1.py --json` |
| **Verify** | `active_decisions[]` includes next_steps_rename · `queue_head.sa_id` matches factory-now |
| **Receipt** | `~/.sina/governance-brain-wire-v1.json` |
| **Fail** | Reconcile stale `reconciled_decision` · obey `active_decisions[]` not archaeology |

---

### C-10 — Brain disk validator (Prompt feed steer)

| Field | Value |
|-------|--------|
| **Owner** | **Cursor agent (me)** |
| **Tracker** | Governance |
| **When** | **Every** Brain-touching session end · before telling founder “fixed” |
| **Action** | `bash scripts/validate-brain-disk-no-prompt-feed-v1.sh` |
| **Verify** | Exit 0 · brain-live-context · brain-current-action · brain-goal1-validation clean |
| **Receipt** | Validator stdout `OK: validate-brain-disk-no-prompt-feed-v1` |
| **Fail** | Back to C-03–C-05 · **do not** add prohibition rules |

---

### C-11 — Worker disk validator (paired)

| Field | Value |
|-------|--------|
| **Owner** | **Cursor agent (me)** |
| **Tracker** | Governance |
| **When** | Same as C-10 when Worker spine touched |
| **Action** | `bash scripts/validate-worker-disk-no-prompt-feed-v1.sh` |
| **Verify** | Exit 0 |
| **Receipt** | Validator stdout |
| **Fail** | C-05 · worker steer guard path |

---

### C-12 — Unified live wire validator

| Field | Value |
|-------|--------|
| **Owner** | **Cursor agent (me)** |
| **Tracker** | Governance · INCIDENT-034 P4 |
| **When** | Pre-ship · after C-10/C-11 · ~45s fast path (not full E2E) |
| **Action** | `bash scripts/validate-disk-live-wire-v1.sh` |
| **Verify** | Mirror inject positive-only · both brain+worker context files exist |
| **Receipt** | Validator stdout |
| **Fail** | Trace failing sub-check · fix disk source · re-run C-01 |

---

### C-13 — Pre-ship founder close-line scan

| Field | Value |
|-------|--------|
| **Owner** | **Cursor agent (me)** |
| **Tracker** | Governance |
| **When** | Before any founder-facing paragraph in Brain/Worker/Governance chat |
| **Action** | `python3 scripts/founder_close_line_gate_v1.py --text "<draft>" --json` |
| **Verify** | `"ok": true` · no F03/F10–F13 hits |
| **Receipt** | Gate JSON stdout |
| **Fail** | Replace with disk close-line from C-03 `founder_close_line` |

---

### C-14 — Background sync processes (reversion guard)

| Field | Value |
|-------|--------|
| **Owner** | **Cursor agent (me)** |
| **Tracker** | Governance |
| **When** | After hub/dashboard restart · if C-12 fails after 12s stability |
| **Action** | Ensure `dashboard_server_v1.py` + hub restarted with **fresh Python** (not stale PID from before script fixes) |
| **Verify** | 12s test: `execution-lane` stays `live_next10_mirror` · no `prompt_feed_lane` key returns |
| **Receipt** | Stability test log in session report |
| **Fail** | Kill stale dashboard PID · `serve-sina-command.sh` · re-run C-01 |

---

### C-15 — Governance event log

| Field | Value |
|-------|--------|
| **Owner** | **Cursor agent (me)** |
| **Tracker** | Governance |
| **When** | After any material heal (scrub · wire · validator fix · hub restart) |
| **Action** | Append JSON line to `~/.sina/agent-governance-events.jsonl` |
| **Verify** | Line has `detect → classify → remediate → harden → verify → record` |
| **Receipt** | jsonl tail |
| **Fail** | N/A — always log material fixes |

---

### C-16 — Stale inject source hunt (when drift persists after C-01–C-12)

| Field | Value |
|-------|--------|
| **Owner** | **Cursor agent (me)** |
| **Tracker** | Governance |
| **When** | Brain **or** Worker still steers Prompt feed after validators PASS once then fail · or validator FAIL |
| **Action** | Trace inject chain: `agent_session_gate_receipt` → `brain-live-context` / `worker-live-context` → `goal1-lane-broker` cache → `099-worker-inbox-active.mdc` → `prompt-queue.mdc` → hub `command-data*.json` → dashboard background sync PID age |
| **Verify** | Identify **file + writer script** that re-poisoned disk · fix writer · subprocess scrub · 12s stability (C-14) |
| **Receipt** | Governance event log with root writer named |
| **Fail** | **Never** blame Brain/Worker · **never** recommend fresh chat as fix · heal the writer |

**Retracted:** “Fresh Brain chat last resort” — ASF: new chat does not bypass dirty disk.

---

## Open items (not executor hub code)

| ID | Owner | Task | Track |
|----|-------|------|-------|
| AR-034-01 | Maintainer 2 | Stop prompt-direction embedding command-data | Governance meta-audit |
| AR-034-02 | Maintainer 2 | H1 museum hero link (INCIDENT-032) | Founder visual confirm |
| AR-034-03 | **Cursor agent** | Bulk sync/archive stale `~/.sina/brain/*.md` | `rg Prompt\ feed ~/.sina/brain/` |

---

## Fast path (~45s) — I run this every Brain/Worker session

```bash
cd ~/Desktop/SourceA
python3 scripts/anti_staleness_auto_wire_v1.py --role brain --tier session --json
python3 scripts/brain_live_context_v1.py --json
python3 scripts/brain_stale_prompt_scrub_v1.py --json
python3 scripts/agent_session_gate_run_v1.py --role brain --json
bash scripts/validate-brain-disk-no-prompt-feed-v1.sh
bash scripts/validate-disk-live-wire-v1.sh
```

**Do NOT run** full E2E bundle unless ASF explicitly asks.

---

## Brain founder close-line (canonical — from disk)

> Worker chat: **RUN INBOX** one sa/turn. Optional: Worker Hub http://127.0.0.1:13020/ → **Next steps** · Safety. Museum: http://127.0.0.1:13020/legacy/. Quote **factory_now_line** from truth bundle.

---

## INCIDENT-034 close (Governance tracks)

- [ ] C-03 through C-12 green on 3 consecutive sessions (Brain **and** Worker)
- [ ] C-16 root writer identified if drift recurs (no “blame chat” closeout)
- [ ] AR-034-01 + AR-034-02 shipped (Maintainer)
- [ ] ASF confirms close-line without Prompt feed steer **with disk proof** (validators + live context files)
- [ ] **No close criterion** “founder opens fresh Brain chat” — disk-only proof

**END CART**
