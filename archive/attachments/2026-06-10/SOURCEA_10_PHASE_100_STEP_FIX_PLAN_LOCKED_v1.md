> **ARCHIVE ONLY — not canonical law.** Authority: `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` · `brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md`.

# SourceA — 10-phase · 100-step fix plan (LOCKED v1)

**Saved:** 2026-06-10T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0  
**Date:** 2026-06-10  
**Parent:** `SOURCEA_MASTER_INDEX_ALL_SUBJECTS_LOCKED_v1.md`  
**Audience:** ASF Founder · Worker · Maintainer · External advisor (read-only)  
**Scope:** All subjects #1–#18 · incidents 001–021 · 015-CONDUCT · S10 · hub gaps

---

## Big-picture threads (map every step to one)

| Thread | Code | What “done” looks like |
|--------|------|------------------------|
| **T1 — Founder sovereignty** | `SOVEREIGN` | FREEZE default · STOP wins · bounded resume only |
| **T2 — Conduct plane** | `CONDUCT` | Spawn blocked when frozen · stop receipt chain |
| **T3 — Disk truth** | `DISK` | run-inbox-truth · factory-now · receipts = progress |
| **T4 — Projection** | `DISPLAY` | Brain/hub/chat cite same line as disk |
| **T5 — Hub visibility** | `HUB` | No START under FREEZE · one pick · FROZEN banner |
| **T6 — Factory cadence** | `CADENCE` | One sa · stop · look — not batch autodrain |
| **T7 — Disposition & trust** | `TRUST` | Packs 41–45 decided · 015-CONDUCT closed |
| **T8 — Incident governance** | `GOV` | Registry + subject index · 022 filed for STOP |
| **T9 — Eternal audit (S10)** | `S10` | 100 prompts cycling · daily receipt · skills patch |
| **T10 — Advisor lane** | `ADVISE` | External critic only · no stealth architecture |

**Tiers:** **P0** = safety/trust now · **P1** = visibility + closeout · **P2** = hardening + eternal

---

## Phase 1 — FREEZE & founder law (T1 · P0)

| Step | Action | Owner | Tier |
|------|--------|-------|------|
| 1.1 | Confirm kill flag ON · no drain PIDs · void “complete all todos” plans | Founder | P0 |
| 1.2 | Hub Stop once · verify `founder-stop-receipt-v1.json` written | Founder | P0 |
| 1.3 | Read `factory-now` line: `python3 scripts/factory_control_v1.py now` | Founder | P0 |
| 1.4 | Cancel Cursor plan todos that conflict with FREEZE | Founder | P0 |
| 1.5 | Law: no resume without `ASF: resume drain — max N — receipt required` | Founder | P0 |
| 1.6 | Do **not** remove kill flag via start-sourcea or install-autorun hints | Maintainer | P0 |
| 1.7 | Wire founder card in Hub home (FREEZE = default mode text) | Panel | P1 |
| 1.8 | Telegram/bot STOP routes to `stop_goal1_auto_run_v1.py` only | Maintainer | P1 |
| 1.9 | Pre-sleep handoff always touches kill flag | Maintainer | P2 |
| 1.10 | Document resume one-liner in `ACTIVE_NOW.md` heartbeat | Worker | P2 |

---

## Phase 2 — Disposition & trust debt (T7 · P0)

| Step | Action | Owner | Tier |
|------|--------|-------|------|
| 2.1 | Open 015-CONDUCT report · note packs **41–45** window | Founder | P0 |
| 2.2 | Pick disposition: **accept** · **audit sample (3 sa)** · or **rollback** | Founder | P0 |
| 2.3 | If audit sample: spot-check pack 44 range receipts on disk | Worker | P0 |
| 2.4 | Write disposition note to `agent-governance-events.jsonl` | Maintainer | P0 |
| 2.5 | If rollback: run bounded revert script · receipt per sa | Maintainer | P1 |
| 2.6 | If accept: lock honest count · no re-litigate +69 in chat | Brain | P1 |
| 2.7 | Close 015-CONDUCT only after disposition + spawn gate proof | Maintainer | P1 |
| 2.8 | Never merge 015-CONDUCT with 015-ID or 011 in speech | All agents | P0 |
| 2.9 | File **INCIDENT-022** (SUBJ-FACTORY · CONDUCT) for STOP spawn if not in registry | Maintainer | P1 |
| 2.10 | Advisor brief updated with disposition outcome | Founder | P2 |

---

## Phase 3 — Conduct plane hardening (T2 · P0)

| Step | Action | Owner | Tier |
|------|--------|-------|------|
| 3.1 | Verify `factory_control_v1.py` on disk · validators PASS | Maintainer | P0 |
| 3.2 | Smoke: kill flag blocks autodrain JSON `reason=kill_flag` | Maintainer | P0 |
| 3.3 | Smoke: resume token allows exactly one bounded turn | Maintainer | P0 |
| 3.4 | `validate-factory-conduct-v1.sh` in `find_critical_bugs` critical | Maintainer | P0 |
| 3.5 | Wire S10 checks s10-013..015 to `factory_control` (unmapped → PASS) | Maintainer | P1 |
| 3.6 | Per-turn re-read kill flag inside autodrain loop | Maintainer | P1 |
| 3.7 | `consume_resume_turn` called at end of each allowed turn | Maintainer | P1 |
| 3.8 | poison_stall writes on sa_mismatch · blocks spawn | Maintainer | P1 |
| 3.9 | Cursor rule `factory-stop-supremacy-locked-v1.mdc` alwaysApply | Maintainer | P2 |
| 3.10 | SH-06 spawn gate row green in S10 pack 2+ | S10 | P2 |

---

## Phase 4 — Disk truth & factory-now (T3 · P0)

| Step | Action | Owner | Tier |
|------|--------|-------|------|
| 4.1 | SSOT chain: receipts → registry honest → monitor valid_yes | Maintainer | P0 |
| 4.2 | `run-inbox-disk-truth-v1.json` fresh before every `run inbox` | Worker | P0 |
| 4.3 | INBOX contains DISK TRUTH block when pending | Worker | P0 |
| 4.4 | `factory-now-v1.json` rebuilt on stop · brain_sync · mode change | Maintainer | P0 |
| 4.5 | All status replies quote factory-now same turn (Brain + Worker) | Brain/Worker | P0 |
| 4.6 | Ban chat-memory progress (“596” from recall without disk read) | All agents | P0 |
| 4.7 | `validate-run-inbox-disk-truth-v1.sh` PASS in ecosystem safety | Maintainer | P1 |
| 4.8 | dual_proof 595/595 monitored daily (S10 P5) | S10 | P1 |
| 4.9 | Bind triple align queue=inbox=bind (sa-0778 today) | Worker | P1 |
| 4.10 | Pack receipts visible ≤60s when drain runs (SH-04) | Maintainer | P2 |

---

## Phase 5 — Hub & panel visibility (T5 · P1)

| Step | Action | Owner | Tier |
|------|--------|-------|------|
| 5.1 | Read `factory-now.kill_flag` in panel build | Panel | P1 |
| 5.2 | Hide **START AUTO RUN** when FREEZE | Panel | P1 |
| 5.3 | Show **FROZEN** banner + stop receipt id | Panel | P1 |
| 5.4 | Fix dual pick: drop sa-0101 from next_action when queue sa-0778 | Panel | P1 |
| 5.5 | Progress card reads `factory-now-v1.json` only — not stale built_at | Panel | P1 |
| 5.6 | command-data rebuild on hub_self_refresh (agent-only) | Maintainer | P1 |
| 5.7 | goal1 tab poll respects FREEZE (no hero START) | Panel | P1 |
| 5.8 | S10 receipt summary on Hub Track tab | Panel | P2 |
| 5.9 | Monitor footer: factory-now one-liner | Panel | P2 |
| 5.10 | S10 P6 prompts 051–060 WARN → PASS after panel ship | S10 | P2 |

---

## Phase 6 — Brain & monitor projection (T4 · P1)

| Step | Action | Owner | Tier |
|------|--------|-------|------|
| 6.1 | Close INCIDENT-014: brain_sync on every honest-count change | Maintainer | P1 |
| 6.2 | `validate-brain-sync-hooks` + snapshot-sync in find_critical_bugs | Maintainer | P1 |
| 6.3 | Brain never says “healed” without factory-now + dual_proof | Brain | P0 |
| 6.4 | Close INCIDENT-013 pattern: no stale goal_progress parrot | Brain | P1 |
| 6.5 | monitor_live_sync ≤120s freshness (S10 P1) | S10 | P1 |
| 6.6 | Scroll respect — no autoscroll steal (018) | Panel | P2 |
| 6.7 | Brain routes only — no Worker disk edits | Brain | P0 |
| 6.8 | Worker routes only — no Brain-style status sermons | Worker | P0 |
| 6.9 | INCIDENT-012 tombstone — cite 013 only | All | P1 |
| 6.10 | DISPLAY thread: hub brain column = live_vy | Maintainer | P2 |

---

## Phase 7 — Factory cadence replay (T6 · P1)

| Step | Action | Owner | Tier |
|------|--------|-------|------|
| 7.1 | After disposition: `factory_control_v1.py resume --max-turns 1` | Founder | P1 |
| 7.2 | Manual **`run inbox`** one sa only | Worker | P1 |
| 7.3 | STOP · look · read factory-now · read pack receipt | Founder | P1 |
| 7.4 | No `worker_healthy_pack_loop` until spawn gate + ASF token | Worker | P0 |
| 7.5 | No autodrain 25 · no 972 chase | All | P0 |
| 7.6 | Phase-strict queue s7→s8→s9 order honored (017 healed) | Maintainer | P1 |
| 7.7 | One open turn at a time — broker chain visible | Worker | P1 |
| 7.8 | Jun 9 playbook doc in Worker skill footnote | Maintainer | P2 |
| 7.9 | Checkpoint only every 5 turns if batch ever re-enabled | Worker | P2 |
| 7.10 | CADENCE thread: trust metric = founder saw receipt same turn | Founder | P2 |

---

## Phase 8 — Incident governance (T8 · P1)

| Step | Action | Owner | Tier |
|------|--------|-------|------|
| 8.1 | Session start: read `AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md` | All agents | P1 |
| 8.2 | Use `INCIDENT_SUBJECT_INDEX` for subject queries | All agents | P1 |
| 8.3 | File 022 for 015-CONDUCT STOP spawn (SUBJ-FACTORY · CONDUCT) | Maintainer | P1 |
| 8.4 | File 016 plan-todo ghost linked to spawn gate regression test | Maintainer | P2 |
| 8.5 | No new bodies in `archive/attachments/` as canonical | Maintainer | P0 |
| 8.6 | Root pointer + brain-os body for every new id | Maintainer | P1 |
| 8.7 | validate-incident-filing-v1.sh PASS | Maintainer | P2 |
| 8.8 | Hub ecosystem_incidents tab shows paths not bodies | Panel | P2 |
| 8.9 | INCIDENT-020 law: subject ≠ script name | All | P1 |
| 8.10 | Quarterly compendium append for 011–021 lessons | Maintainer | P2 |

---

## Phase 9 — S10 eternal loop (T9 · P2)

| Step | Action | Owner | Tier |
|------|--------|-------|------|
| 9.1 | Confirm `s10-eternal-manifest-v1.json` 100 prompts | Maintainer | P2 |
| 9.2 | launchd `com.sourcea.s10-eternal-audit` loaded 06:00 | Maintainer | P2 |
| 9.3 | `monitor_live_sync` triggers daily S10 if receipt missing | Maintainer | P2 |
| 9.4 | `validate-s10-eternal-loop-v1.sh` in ecosystem safety | Maintainer | P2 |
| 9.5 | Map all unmapped S10 checks in `s10_eternal_audit_loop_v1.py` | Maintainer | P1 |
| 9.6 | Sunday UTC `--full` 100-prompt run scheduled | Maintainer | P2 |
| 9.7 | S10 FAIL → governance-events · no silent ignore | S10 | P1 |
| 9.8 | Skills patch: top-used SKILL.md after convinced FAIL class | Maintainer | P2 |
| 9.9 | S10 pack rotation: founder reads receipt not Terminal | Founder | P2 |
| 9.10 | S10 ≠ execution — never replaces `run inbox` | All | P0 |

---

## Phase 10 — Steady state & advisor lane (T10 · P2)

| Step | Action | Owner | Tier |
|------|--------|-------|------|
| 10.1 | External advisors: EXTERNAL_CRITIC only · attach pack #2–5,7–9,14 | Founder | P1 |
| 10.2 | Forbid advisor batch drain · 972 · new D-modules in brief | Founder | P0 |
| 10.3 | Four invariants checklist in every advisor reply | Advisor | P1 |
| 10.4 | Portfolio TrustField lane separate from factory drain | Founder | P1 |
| 10.5 | prompt-direction API = advisory only — not execution | All | P0 |
| 10.6 | find_critical_bugs green before “factory healed” claim | Maintainer | P1 |
| 10.7 | Monthly: replay Phase 7 cadence drill (one sa) | Founder | P2 |
| 10.8 | Master index #1–#18 + this plan = advisor onboarding | Founder | P2 |
| 10.9 | Success metric: 0 spawn with flag ON · 0 STOP→drain transcripts | Maintainer | P1 |
| 10.10 | **DONE:** frozen by default · visible truth · eternal S10 audit | ASF | P2 |

---

## Phase × thread matrix

| Phase | Primary thread | Tier focus |
|-------|----------------|------------|
| 1 | T1 SOVEREIGN | P0 |
| 2 | T7 TRUST | P0 |
| 3 | T2 CONDUCT | P0→P1 |
| 4 | T3 DISK | P0 |
| 5 | T5 HUB | P1 |
| 6 | T4 DISPLAY | P1 |
| 7 | T6 CADENCE | P1 |
| 8 | T8 GOV | P1 |
| 9 | T9 S10 | P2 |
| 10 | T10 ADVISE | P2 |

---

## Founder week-1 minimum (P0 only — 10 steps)

1. Stay FREEZE  
2. Disposition packs 41–45  
3. Read factory-now daily  
4. Void plan todos  
5. No batch drain  
6. Hub Stop if unsure  
7. Send advisor pack (critic only)  
8. Confirm spawn gate blocks (Maintainer smoke)  
9. Read S10 receipt (not Terminal)  
10. Resume one sa only when ready  

---

## File map (this plan ↔ master list)

| Phase | Master # |
|-------|----------|
| 1–3 | #2, #3, #12, #16 |
| 2, 8 | #7, #12, incident registry |
| 4–6 | #10, #11, #14 |
| 5 | #14 § disk-truth E2E |
| 7 | #9, #12 |
| 9 | #15, #17, #18 |
| 10 | #4, #14 |

**END** — 10 phases · 100 steps · 10 threads · 3 tiers
