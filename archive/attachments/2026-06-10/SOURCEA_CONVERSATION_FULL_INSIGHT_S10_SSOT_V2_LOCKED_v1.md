> **ARCHIVE ONLY — not canonical law.** Authority: `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` · `brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md`.

# SourceA — Full conversation insight · disk-truth E2E map · S10 SSOT v2

**Saved:** 2026-06-10T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 2.0 — FINAL LOCKED  
**Date:** 2026-06-10  
**Supersedes:** S10 v1 sections on enforcement (now `factory_control_v1.py`)  
**Parent index:** `SOURCEA_MASTER_INDEX_ALL_SUBJECTS_LOCKED_v1.md`  
**Machine SSOT:** `SOURCEA_S10_ETERNAL_SELF_HEAL_AUDIT_LOCKED_v1.md` + `~/.sina/s10-eternal-manifest-v1.json`

---

## 0. Your ask — reframed (founder)

You want **one eternal machine loop** that:

1. Finds every place the system is **not real-time with disk truth** (E2E, from scratch).
2. **Self-heals, criticizes, hardens** validators and skills — daily, forever.
3. Runs **alongside** factory drain (s0–s9), **never instead of it**.
4. Keeps **100 audit prompts** on rotation — 10/day, 100/week — with disk receipts.

**S10 is that loop.** Factory execution stays `run inbox`. S10 audits the factory forever.

---

## 1. Conversation arc — threads & patterns

| Thread | What happened | Core pattern | Insight |
|--------|---------------|--------------|---------|
| **A — Stuck / trust** | Batch drain after STOP; +69 honest while frozen | **Conduct** (plan todo > ASF) | Green validators ≠ safe to batch |
| **B — Display lies** | Brain said “healed”; monitor lag | **Projection** (chat ≠ disk) | Cite `factory-now` line only |
| **C — Root cause** | Fixes don’t stick across incidents 001–015 | **Two OS**: factory law vs Cursor optimizer | Ship **4 invariants**, not more architecture |
| **D — Machine fix** | spawn gate · factory-now · stop receipts | **Control plane** must block spawn | `factory_control_v1.py` = one module |
| **E — History** | Jun 9 smooth (23 manual) vs Jun 10 fast (596 batch) | **Cadence** beats raw count | Replay one-sa rhythm |
| **F — Disposition** | Packs 41–45 (+69) pending founder call | **Trust debt** separate from gates | accept / audit / rollback |
| **G — S10 eternal** | 100 prompts · 10 packs · daily launchd | **Rejuvenation lane** | Audit factory without touching inbox execution |
| **H — Disk truth ask** | “What is not real-time with disk?” | **Dual SSOT** confusion | Hub snapshot ≠ execution truth |
| **I — Portfolio** | TrustField outreach 0/15 · prompt-direction | **Separate lane** | Agentic commercial ≠ SourceA factory drain |

**Master pattern:** *Chat and hub are fast; disk is slow but honest. Eternal loops close the gap.*

---

## 2. Three lanes (never invert)

| Lane | SSOT file | Role | Founder action |
|------|-----------|------|----------------|
| **Factory s0–s9** | `~/.sina/run-inbox-disk-truth-v1.json` | Execute one SA via `run inbox` | Resume bounded only |
| **Conduct plane** | `factory_control_v1.py` → `factory-now-v1.json` | FREEZE · spawn gate · STOP | Hub Stop · read factory-now |
| **S10 eternal** | `~/.sina/s10-eternal-manifest-v1.json` | Audit · heal · skills · E2E | Read receipt — no Terminal |

**Prompt feed 10-batch** + `curl …/api/prompt-direction` = **advisory only** — not execution SSOT.

---

## 3. Disk truth vs real-time — full E2E table (from scratch)

> **PROMOTED TO ROOT LAW (2026-06-10):** Canonical copy is `SOURCEA_DISK_TRUTH_E2E_MATRIX_LOCKED_v1.md` at repo root (`DISK_TRUTH_E2E` authority). This section is a **historical snapshot** only — edit the root matrix, not this duplicate.


Legend: **RT** = real-time with disk · **LAG** = stale/cache/build snapshot · **GAP** = known wrong · **S10** = pack that watches · **Heal** = script can auto-fix

| # | Layer | Disk SSOT (truth) | UI / chat reads | Sync | Status | S10 | Heal |
|---|-------|-------------------|-----------------|------|--------|-----|------|
| 1 | Honest progress | `receipts/sa-*-receipt.json` + REGISTRY | monitor · factory-now · hub cards | On closeout + brain_sync | **RT** (±1 receipt lag OK) | P1·P5 | brain_sync |
| 2 | Valid YES count | `monitor_honesty_lib` audit | monitor.html · command-data | `monitor_live_sync` ~5s | **RT** | P1 | sync_disk |
| 3 | Brain column | `brain-goal1-validation-v1.json` | Brain chat · hub brain card | `brain_sync_lib` on honest change | **RT** after 014 fix | P2·P5 | brain_sync |
| 4 | Queue cursor | `healthy-queue-state-v1.json` | run-inbox-truth · INBOX meta | On advance / deliver | **RT** | P1·P3 | bind heal |
| 5 | Run inbox truth | `run-inbox-disk-truth-v1.json` | INBOX DISK TRUTH block | `run_inbox_disk_truth_v1` | **RT** | P1·P3 | ensure_inbox_truth |
| 6 | Inbox pending SA | `worker-prompt-inbox-v1.json` | Worker session | Broker deliver | **RT** (bind OK today) | P1 | patch block |
| 7 | Factory now line | `factory-now-v1.json` (5s cache) | cursor_entry_gate · chat | rebuild on stop/sync | **LAG** (TTL by design) | P2 | rebuild |
| 8 | FREEZE / kill flag | `auto-run-disabled-v1.flag` + stop receipt | Hub START button · next_action text | Partial | **GAP** — UI shows START under FREEZE | P2·P6 | panel lane |
| 9 | Spawn gate | `factory_control_v1` in-process + flag | Hub autorun · Shell | At spawn entry | **RT** (machine) | P2·P10 | N/A |
| 10 | Hub command-data | `command-data.json` `built_at` | Sina Command panel | Panel build / poll | **LAG** (minutes) | P6 | build panel |
| 11 | Hub shell preload | `command-data-shell.json` | First paint | Build time snapshot | **LAG** | P6 | rebuild |
| 12 | P0 next_action string | Built from goal1 + live_pick | Founder hero line | Panel build | **GAP** — “sa-0778 … pick sa-0101” dual text | P6 | panel lane |
| 13 | live_pick vs queue | Queue = sa-0778; pick text = sa-0101 | goal1 tab · next_action | Stale pick_floor legacy | **GAP** | P6 | SinaaiDataBase panel |
| 14 | START AUTO RUN CTA | Should hide when FREEZE | Visible in next_action | Not wired to factory-now | **GAP** | P6 | panel lane |
| 15 | Monitor live pulse | `monitor-live-v1.json` | monitor.html iframe | 5s sync thread | **RT** | P1·P10 | sync_disk |
| 16 | Broker cycle | `goal1-lane-broker-events.jsonl` | batch log · brain validate | Per submit | **RT** at closeout | P3·P5 | hygiene |
| 17 | Pack receipts | `pack-drain-receipts/pack-*.json` | Worker audit | Per pack turn | **RT** when drain runs | P8 | N/A |
| 18 | Phase-strict queue | `phase-strict-drain-v1.json` + manifests | run-inbox-truth | Builder script | **RT** | P8 | build-phase-strict |
| 19 | S10 receipt | `s10-eternal-receipt-v1.json` | Not in hub yet | Daily 06:00 + monitor | **RT** on disk | P10 | launchd |
| 20 | Prompt feed batch | OpenRouter propose | Prompt feed UI | Advisory curl | **Not execution** | — | — |
| 21 | TrustField tracker | `TrustField…/plan.json` | Portfolio thread | Separate repo | **Separate lane** | P7 | agent lane |
| 22 | Cursor plan todos | IDE state | Cursor runtime | None | **GAP** — survives STOP | P7·P9 | manual cancel |
| 23 | Chat memory | None (forbidden) | Agent replies | None | **GAP** if used | P9 | factory-now law |
| 24 | dual_proof | monitor + brain receipt | validators | ecosystem safety | **RT** (595/595) | P2·P5 | — |
| 25 | Governance events | `agent-governance-events.jsonl` | Maintainer | S10 + incidents | **RT** | P7 | append |

**Summary:** Execution path (rows 1–6, 9, 15–18) is **mostly RT**. **Hub hero UX** (rows 8, 10–14) is where founder *feels* stuck — not because factory gates fail, but because **panel snapshot ≠ factory-now**.

---

## 4. S10 SSOT v2 — upgraded eternal engine

### 4.1 What S10 is

```
detect → classify → remediate → harden → verify → record → skills_patch
```

| Asset | Path |
|-------|------|
| Law v1 | `SOURCEA_S10_ETERNAL_SELF_HEAL_AUDIT_LOCKED_v1.md` |
| Law v2 insight (this file) | `archive/attachments/2026-06-10/SOURCEA_CONVERSATION_FULL_INSIGHT_S10_SSOT_V2_LOCKED_v1.md` |
| 100 prompts | `~/.sina/s10-eternal-manifest-v1.json` |
| Daily runner | `scripts/s10_eternal_audit_loop_v1.py` |
| Validator | `scripts/validate-s10-eternal-loop-v1.sh` |
| Skill | `agent-skills/shared/s10-eternal-self-heal/SKILL.md` |
| Schedule | `scripts/com.sourcea.s10-eternal-audit.plist` (06:00) |
| Receipt | `~/.sina/s10-eternal-receipt-v1.json` + `s10-eternal-history.jsonl` |

### 4.2 Rotation (eternal)

| Schedule | Prompts |
|----------|---------|
| **Daily** | pack = `(day_of_year % 10) + 1` → **10 prompts** |
| **Weekly** | Sunday UTC `--full` → **100 prompts** |
| **Monitor** | `monitor_live_sync` → once/day if receipt missing |

### 4.3 Ten packs

| Pack | Domain | Eternal duty |
|------|--------|--------------|
| P1 | Disk truth wire | monitor · inbox · queue · partial drift |
| P2 | Self-heal SH-01..10 | stop · bind · brain · spawn · factory-now |
| P3 | Run inbox E2E | gate-pickup · broker · advance · one-sa |
| P4 | Skills MD | registry · cursor sync · top-used skills |
| P5 | Validator chain | honest · monitor · broker · factory-conduct |
| P6 | Hub real-time | built_at · dual pick · FREEZE UI |
| P7 | Governance | incidents · STOP obedience · events |
| P8 | Phase-strict | s7→s8→s9 · pack receipts |
| P9 | Deep critique | laziness · chat-as-SSOT · poison |
| P10 | Machine enforcement | launchd · sync · spawn · eternal receipt |

### 4.4 v2 upgrades (this session)

| Upgrade | From | To |
|---------|------|-----|
| Conduct plane | 4 fragmented modules | **`factory_control_v1.py`** single SSOT |
| CI validators | 3 separate scripts | **`validate-factory-conduct-v1.sh`** unified |
| factory-now | Rebuild storm | **5s TTL cache** + event-driven rebuild |
| Spawn gate | Hub + script triple-check | **Once at spawn entry** |
| S10 P2 checks | Partial | Must map `factory_control` + `drain_spawn_allowed` |

### 4.5 Proof on disk (2026-06-10)

| Run | Result |
|-----|--------|
| Pack 1 (disk truth) | **10/10 PASS** (Worker report) |
| Pack 2 (SH) | **5 PASS / 5 WARN** — honest (FREEZE, unmapped SH-03..05 checks) |
| factory-now | `Valid YES 595 · brain 595 · dual_proof True · mode FREEZE · queue sa-0778` |
| run-inbox-disk-truth | queue=inbox=sa-0778 · truth_match=true |
| Hub next_action | **GAP**: shows START + pick sa-0101 while queue sa-0778 |

```bash
python3 scripts/s10_eternal_audit_loop_v1.py --daily --json
bash scripts/validate-s10-eternal-loop-v1.sh
python3 scripts/factory_control_v1.py now
```

### 4.6 S10 will keep flagging until panel lane fixes

| Item | Owner | Why S10 cannot auto-heal |
|------|-------|--------------------------|
| Dual pick sa-0101 vs sa-0778 | Sina Command panel | `command-data` build logic |
| START visible under FREEZE | Hub UI | Needs read `factory-now.kill_flag` |
| Hub cache TTL | Panel poll/build | Needs FROZEN banner + hide CTA |
| Unmapped SH checks s10-013..015 | Maintainer | Wire checks in `s10_eternal_audit_loop_v1.py` |

---

## 5. Four invariants (conversation conclusion)

1. **ONE mode** — FREEZE default (`factory-mode-v1.json`)
2. **ONE now** — `factory-now-v1.json` line in every status reply
3. **ONE visibility** — pack receipt or factory-now ≤60s when running
4. **ONE spawn gate** — `drain_spawn_allowed()` at every drain entry

**Fifth (S10): ONE audit lane** — 100 prompts eternal; never conflate with `run inbox`.

---

## 6. Founder card (this conversation)

| ✅ Do | ❌ Don’t |
|------|---------|
| Stay **FREEZE** until bounded resume | Trust “healed” without factory-now |
| `run inbox` one sa · stop · look | Batch autodrain / complete-all-todos |
| Read **S10 receipt** daily (disk) | Run Prompt feed batch as execution |
| Disposition packs 41–45 | Merge 015-CONDUCT with 015-ID |
| Let S10 + launchd audit headless | Use Terminal for eternal loops |

**Resume one step:**
```bash
python3 scripts/factory_control_v1.py resume --max-turns 1
```

---

## 7. Maintainer next (S10 + panel)

| Priority | Ship |
|----------|------|
| P0 | Wire S10 checks s10-013..015 to `factory_control` + `dual_proof` |
| P1 | Hub: hide START when `factory-now.kill_flag` |
| P1 | Hub: single pick — drop sa-0101 from next_action when queue sa-0778 |
| P2 | Hub Track tab: show `s10-eternal-receipt-v1.json` summary |
| P2 | Map `validate-s10-eternal` into `find_critical_bugs` critical |

---

## 8. Add to master list — file registry

| # | Subject | File |
|---|---------|------|
| **14** | **Full conversation insight + S10 SSOT v2** | `SOURCEA_CONVERSATION_FULL_INSIGHT_S10_SSOT_V2_LOCKED_v1.md` |
| **15** | **S10 eternal law** | `SOURCEA_S10_ETERNAL_SELF_HEAL_AUDIT_LOCKED_v1.md` |
| **16** | **factory_control plane (optimized)** | `scripts/factory_control_v1.py` |
| **17** | **Disk truth execution law** | `brain-os/laws/RUN_INBOX_DISK_TRUTH_EXECUTION_LOCKED_v1.md` |
| **18** | **S10 skill** | `agent-skills/shared/s10-eternal-self-heal/SKILL.md` |

---

**END** — Conversation synthesized · disk-truth E2E mapped · S10 v2 locked.
