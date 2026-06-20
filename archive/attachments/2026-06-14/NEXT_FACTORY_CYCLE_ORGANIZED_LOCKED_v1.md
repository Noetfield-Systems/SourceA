# Next factory cycle — organized plan (LOCKED v1)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Prepared:** 2026-06-14  
**Authority:** `~/.sina/phase-strict-drain-v1.json` · `SOURCEA_PHASE_STRICT_RUN_INBOX_LOCKED_v1.md`  
**Status:** Cycle 1 **COMPLETE** · Cycle 2 **STAGED** · Factory **FREEZE ON**

---

## Executive snapshot

| Metric | Value |
|--------|-------|
| Goal 1 honest | **828 / 1000** (82.8%) |
| Cycle 1 turns | **156 / 156** complete (sa-0101 → sa-1000 phase-strict) |
| Cycle 2 active pack | **s5-P1-wire-runreceipt** — 10 SAs · 30 turns |
| Next SA | **sa-0502** CHECK (RunReceipt verify-wire) |
| Factory | **FREEZE ON** · mode SINGLE_SA |
| Eval-1b | **LIVE PASS** (4/5 @ 80%) · gate_mode **shadow** |
| dispatch_ready | **false** (founder law) |
| find_critical_bugs | **2 critical** — fix before claiming green unfreeze |

---

## Cycle 1 — closed (receipt)

| Field | Receipt |
|-------|---------|
| Law | s1 OpenRouter (6) → s7 tail (3) → s9 (46) |
| Completed | 2026-06-14T11:16:19Z |
| Last SA | sa-1000 VERIFY |
| Receipt | `receipts/sa-1000-receipt.json` |
| Queue state | was 157/157 · reset for cycle 2 |

**Skipped by design:** s2, s3 (100% done), s8 (hub archived — ASF closed).

---

## Cycle 2 — phase plan

### Active now (P1 — on disk)

**Pack:** `s5-P1-wire-runreceipt`  
**Range:** sa-0502 → sa-0511  
**Turns:** 30 (CHECK → ACT → VERIFY × 10)  
**OpenRouter:** **off** (disk-only commercial lane)

| SA | Title |
|----|-------|
| sa-0502 | Run bash validate-verify-wire-v1.sh — RunReceipt artifact schema |
| sa-0503 | Cross-check TRUST_LEDGER_SCHEMA_LOCKED_v1.md FR-007 shipped signal |
| sa-0504 | Document Wire G3 attest as founder/lane step in this_week |
| sa-0505 | Validate product/RUNRECEIPT_ARTIFACT_SCHEMA_LOCKED_v1.md hub link |
| sa-0506 | Compare TrustField pilot vault note vs workspace-vault API |
| sa-0507 | Run founder_request_tracker sync on build for commercial FR rows |
| sa-0508 | Validate PROGRAM_PROGRESS parallel_plans P0 next_action honest |
| sa-0509 | Cross-check MergePack KPI trio in command center payload |
| sa-0510 | Document lane P0 revenue bottleneck in strategic one_line |
| sa-0511 | Reject fabricated G3 or Track PASS in any script grep |

### Queued after P1 (not built until P1 PASS)

| Pack | SAs | Count | Theme |
|------|-----|-------|-------|
| s5-P2 | sa-0512 → sa-0521 | 10 | commercial lane continuation |
| s5-P3 | sa-0522 → sa-0531 | 10 | commercial lane continuation |
| s5-P4 | sa-0532 → sa-0541 | 10 | commercial lane continuation |
| s5-P5 | sa-0542 → sa-0551 | 10 | commercial lane continuation |
| s5-P6 | sa-0552 → sa-0561 | 10 | commercial lane continuation |
| s5-P7 | sa-0562 → sa-0571 | 10 | commercial lane continuation |
| s5-P8 | sa-0572 → sa-0581 | 10 | commercial lane continuation |
| s5-P9 | sa-0582 → sa-0591 | 10 | commercial lane continuation |
| s5-P10 | sa-0592 → sa-0597 | 6 | s5 tail (96 backlog total) |

**After s5 complete:** reassess s8 hub-ui (76 backlog) — **still archived** per ASF no-hub latch unless explicit reopen.

---

## Disk SSOT (synced)

| Artifact | Value |
|----------|-------|
| `phase-strict-drain-v1.json` | cycle **2** · s5-P1 force_list |
| `healthy-queue-30-active.json` | 30 turns · sa-0502..0511 |
| `healthy-queue-state-v1.json` | next_pos **1** |
| `next-execution-pointer-v1.json` | **sa-0502** CHECK |
| `goal1-worker-turn-bind-v1.json` | **sa-0502** pos 1/30 |
| `worker-prompt-inbox-v1.json` | staged · pending **false** until RUN INBOX |
| `goal-progress-v1.json` | gates updated · eval live pass |

**Rebuild command (executor only):**  
`python3 ~/.sina/build-phase-strict-queue-v1.py`

---

## P0 blockers — before unfreeze

1. **Broker receipt cycle** — `validate-broker-receipt-cycle-v1.sh` · many `broker=PEND` rows (INCIDENT-007 class).
2. **phase-s0 SSOT alignment** — eval pendings assertion in validator (may be stale vs live eval pass).

**Hospital:** last receipt ok · maze passport ok · quarantine cleared.  
**Action:** executor triages P0 validators; founder does **not** run shell.

---

## Founder — one-tap sequence (when ready)

1. **Review** this attachment + Hub Goal 1 bar (828/1000).
2. **Clear FREEZE** on H1 (bounded resume — cycle 2 s5 only).
3. **RUN INBOX** once → Worker gets sa-0502 CHECK.
4. **Worker chat** executes turn → broker submit → repeat until pack PASS.
5. **After P1 PASS** — executor rebuilds P2 queue (sa-0512..0521) same pattern.

**Do not:** hub rebuild · s8 picks · batch unattended 30.

---

## Eval / OpenRouter (unchanged law)

- Eval-1b **live pass** on disk (`~/.sina/eval_packet_v1b_report.json`).
- `gate_mode_v1.txt` = **shadow** (not enforce).
- OpenRouter only on designated s1-OR turns — **not** on s5 commercial pack.
- `dispatch_ready` stays false until founder law changes.

---

## Related docs

- `SOURCEA_PHASE_PACK_PINNED_SUMMARY_LOCKED_v1.md` (refresh after P1)
- `SOURCEA_OPENROUTER_ACTIVATION_QUEUE_LOCKED_v1.md`
- `DISPATCH_POLICY_LOCKED_v1.md`
- `AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v1.md`

---

*End NEXT_FACTORY_CYCLE_ORGANIZED_LOCKED_v1*
