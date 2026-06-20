# S10 — Eternal self-heal · disk-truth audit · 100-prompt loop (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
<!--
SOURCEA-AGENT-DOC
status: LOCKED
doc_date: 2026-06-10
sequence_id: SA-2026-06-10-S10-ETERNAL
phase: phase-s10-eternal-self-heal
-->

| | |
|--|--|
| **Version** | `SOURCEA-S10-ETERNAL-2.0-LOCKED` (insight v2: `archive/attachments/2026-06-10/SOURCEA_CONVERSATION_FULL_INSIGHT_S10_SSOT_V2_LOCKED_v1.md`) |
| **Class** | Meta-phase **s10** — after s0–s9 factory drain |
| **Purpose** | Eternal daily machine loop: audit · criticize · heal · harden · skills · E2E |
| **Machine SSOT** | `~/.sina/s10-eternal-manifest-v1.json` |
| **Daily runner** | `~/.sina/bin/s10-eternal-daily` (any cwd) · repo: `scripts/s10_eternal_audit_loop_v1.py` |
| **Skill** | `agent-skills/shared/s10-eternal-self-heal/SKILL.md` |
| **Receipt** | `~/.sina/s10-eternal-receipt-v1.json` + `s10-eternal-history.jsonl` |

**Parent laws:** `AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md` §5 · `RUN_INBOX_DISK_TRUTH_EXECUTION_LOCKED_v1.md` · `SOURCEA_MONITOR_DISK_LIVE_WIRE_LOCKED_v1.md` · `factory_control_v1.py` · SH-01..10

---

## 0. One sentence

**S10 is the eternal rejuvenation engine:** 100 locked audit prompts cycle forever; **10 run every day** on machine schedule; output is disk receipts, validator hardening, skill updates, and E2E truth — not chat opinions.

---

## 1. Two lanes (never invert)

| Lane | Role | Machine? |
|------|------|----------|
| **Factory drain** (s0–s9) | `run inbox` · one SA per turn | `run-inbox-disk-truth-v1.json` |
| **S10 eternal** (s10) | System introspection · self-heal · skills · E2E audit | `s10-eternal-manifest-v1.json` |

Prompt feed 10-batch = **advisory only**. S10 prompts = **machine audit SSOT** (not OpenRouter invention).

---

## 2. 100 prompts · 10 packs · eternal rotation

| Pack | Domain | IDs | Daily duty |
|------|--------|-----|------------|
| **P1** | Disk truth wire | s10-001..010 | Monitor · hub · inbox · live_pick · partial drift |
| **P2** | Self-heal SH | s10-011..020 | SH-01..SH-10 detect/remediate |
| **P3** | Run inbox E2E | s10-021..030 | Gate · DISK TRUTH · pickup · advance · receipt |
| **P4** | Skills MD | s10-031..040 | Registry sync · SKILL.md freshness · cursor skills |
| **P5** | Validator chain | s10-041..050 | honest gate · monitor · broker · s10 validator |
| **P6** | Hub real-time | s10-051..060 | command-data age · dual pick · FREEZE UI · live read |
| **P7** | Governance | s10-061..070 | incidents · governance-events · miss disk-first |
| **P8** | Phase-strict | s10-071..080 | queue manifest · pick_floor ban · s7→s8→s9 order |
| **P9** | Deep critique | s10-081..090 | refactor candidates · laziness · poison patterns |
| **P10** | Machine enforcement | s10-091..100 | launchd · sync loops · spawn gates · eternal receipt |

**Daily:** pack = `(day_of_year % 10) + 1` → run **10 prompts** + write receipt.  
**Weekly (Sunday UTC):** run **all 100** (`--full`).  
**Law:** loop must run **≥1×/day** without founder Terminal.

---

## 3. Self-heal loop (every S10 run)

```
detect → classify → remediate → harden → verify → record → skills_patch
```

| Phase | S10 action |
|-------|------------|
| **Detect** | Run today's 10 prompts against disk + validators |
| **Classify** | PASS · WARN · FAIL · POISON per prompt |
| **Remediate** | Auto-fix only where script-owned (sync, truth patch, launchd kick) |
| **Harden** | File incident · agent-review · validator gap |
| **Verify** | `validate-s10-eternal-loop-v1.sh` + relevant gates |
| **Record** | `s10-eternal-receipt-v1.json` + `agent-governance-events.jsonl` |
| **Skills patch** | Update `agent-skills/shared/s10-eternal-self-heal/SKILL.md` + top-used skills when convinced |

---

## 4. Machine schedule (no agent babysit)

| Trigger | Action |
|---------|--------|
| **launchd** | `com.sourcea.s10-eternal-audit` — daily 06:00 local |
| **monitor_live_sync** | Once per day: `s10_eternal_audit_loop_v1.py --daily` |
| **Brain session start** | WARN if last S10 receipt >26h stale |
| **Maintainer** | `bash scripts/validate-s10-eternal-loop-v1.sh` in ecosystem safety |

---

## 5. Founder respect

- S10 runs **headless logged** — no scroll steal · no Prompt feed batch execution.
- Founder may read receipt in Hub **Track** or monitor footer when wired.
- **Execution** remains **`run inbox`** only.

---

## 6. Prompt catalog (100 — titles)

### P1 Disk truth (001–010)
001 monitor-live freshness · 002 run-inbox-truth match · 003 valid_yes vs receipts · 004 factory-now age · 005 phase-strict enabled · 006 queue cursor bind · 007 inbox DISK TRUTH block · 008 track-validate stale · 009 matrix age · 010 execution-lane json

### P2 SH (011–020)
011 SH-01 stop/kill · 012 SH-02 bind · 013 SH-03 brain_vy · 014 SH-04 silent drain · 015 SH-05 sa_mismatch · 016 SH-06 spawn gate · 017 SH-07 dual_proof · 018 SH-08 mode token · 019 SH-09 start-sourcea flag · 020 SH-10 factory-now chat

### P3 Run inbox E2E (021–030)
021 gate-pickup · 022 healthy_prompt_turn · 023 broker pickup yaml · 024 worker-submit · 025 advance queue · 026 receipt honest · 027 duplicate inject · 028 FREEZE respect · 029 phase-strict builder · 030 one-sa-per-turn

### P4 Skills (031–040)
031 agent-skills REGISTRY · 032 sync-cursor-agent-skills · 033 sourcea_worker SKILL · 034 registry-drain SKILL · 035 s10 skill itself · 036 research-intake · 037 skill-006 ask-before · 038 commercial skill · 039 brain skill · 040 maintainer skill

### P5 Validators (041–050)
041 validate-monitor-honesty · 042 validate-registry-honest-gate · 043 validate-goal1-lane-broker · 044 validate-run-inbox-disk-truth · 045 validate-s10-eternal · 046 validate-factory-conduct · 047 find_critical_bugs · 048 validate-ecosystem-safety · 049 cursor_entry_gate worker · 050 prompt_feasibility_gate

### P6 Hub real-time (051–060)
051 command-data built_at · 052 live_pick vs queue · 053 P0 next_action truth · 054 START AUTO RUN vs FREEZE · 055 hub cache TTL · 056 prompt-direction advisory · 057 goal1 tab poll · 058 hub_self_refresh agent-only · 059 command-data-shell lazy · 060 dual_proof hub card

### P7 Governance (061–070)
061 governance-events append · 062 incident open count · 063 miss disk-first · 064 external critic immunity · 065 authority index map · 066 rules in charge loop · 067 PLAN_REVOKED hygiene · 068 conduct STOP obedience · 069 registry batch fake · 070 phase-order drift 017

### P8 Phase-strict (071–080)
071 manifest s7-P1..P3 · 072 manifest s8-P1..P5 · 073 manifest s9-P1..P5 · 074 skip s2 s3 · 075 founder lanes s1 s6 · 076 pick_floor disabled · 077 resume sa-0778 · 078 119 achievable ceiling · 079 pack receipts · 080 lazy forward scan ban

### P9 Deep critique (081–090)
081 system laziness definition · 082 chat as SSOT violations · 083 built:true receipt gap · 084 validate-first quarantine · 085 orchestrator vs manual · 086 brain vs worker lane bleed · 087 overnight vs founder busy · 088 parallel roadmap duplicates · 089 hub table deletion · 090 critic reorder attempts

### P10 Machine enforcement (091–100)
091 launchd dashboard · 092 launchd s10 · 093 monitor 5s sync · 094 spawn gate JSON · 095 poison_stall auto · 096 kill flag law · 097 resume token bounded · 098 agent-governance-events · 099 eternal receipt chain · 100 S10 loop PASS day

---

## 7. Maintainer sync

When editing S10:

1. This file + `~/.sina/s10-eternal-manifest-v1.json`
2. `scripts/s10_eternal_audit_loop_v1.py`
3. `agent-skills/shared/s10-eternal-self-heal/SKILL.md`
4. `SINA_AUTHORITY_INDEX_MAP` row `S10_ETERNAL` (ASF)
5. `validate-s10-eternal-loop-v1.sh`

**LOCKED** — Eternal self-heal meta-phase. Factory drain unchanged; S10 audits the factory forever.
