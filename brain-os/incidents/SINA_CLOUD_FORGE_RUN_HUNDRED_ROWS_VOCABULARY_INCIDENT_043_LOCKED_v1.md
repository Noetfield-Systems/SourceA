# INCIDENT-043 — Cloud Forge Run “100 rows per turn” · agent vocabulary split · ASF order disobedience

> **SUPERSEDED 2026-07-05 (INCIDENT-045)** for mandatory 100-row quota. Turn/batch/full_pack vocabulary below remains reference. Active motor law: `SOURCEA_CLOUD_FORGE_RUN_REALISTIC_MOTOR_LOCKED_v1.md`.

**Saved:** 2026-06-24T07:15:00Z · **Version:** 1.0 LOCKED  
**Class:** Agent conduct · ASF vocabulary · Cloud Forge Run semantics · cross-agent inconsistency  
**Reporter:** Founder — “some agents get it, some not — annoying”  
**Agent:** Cursor Auto · **sequence_id:** SA-2026-06-24-INCIDENT-043  
**Opened:** 2026-06-24 · **Related:** INCIDENT-042 · INCIDENT-020 (topic conflation) · INCIDENT-039  
**Status:** **OPEN — law locked · agents must read before any cloud-forge-run reply**

---

## 1. Executive summary (founder language)

**ASF order (unchanged since batch 2, clarified v1.1 2026-06-24):** Every **10 minutes**, automation must move **exactly 100 queue rows down** — **100 is the mandatory minimum quota per turn**, not “up to 100.” Not one row, not one row per cron, not a vague “pack running” story.

**The frustration:** Multiple Cursor agents in the same week gave **contradictory explanations** of the same live system. Some correctly described **one CF cron → one Railway request → 100 internal row steps (mandatory)**. Others softened ASF to **“up to 100”** or talked as if:

- only **one plan** runs per 10-minute tick,
- **`full_pack` is a long-running background job** still executing across turns,
- **`skipped`** means the turn did not run (it did — rows still moved),
- **`batch`** (locked JSON file logged) equals **`turn`** (10-minute cron trigger).

Founder time was burned reconciling agents who cited the **same law files** but interpreted them differently. That is **conduct failure**, not a Railway bug.

**This incident locks vocabulary and forbids the wrong readings.** INCIDENT-042 fixed Dockerfile and pattern drift; INCIDENT-043 fixes **agent mouth**.

---

## 2. ASF locked semantics (plain English)

| Word | Means | Does NOT mean |
|------|--------|----------------|
| **Turn** (also: tick, trigger) | One external event: CF cron `*/10` **or** one Cloud Workers Proceed tap | 100 separate crons; a background daemon |
| **Row** | One CLOUD-SEC slot in the active drain queue (e.g. `CLOUD-SEC-1042`) | The whole batch JSON file; “one pack” |
| **100 rows per turn** | **Mandatory minimum** — `run_auto_runtime_pack` must consume **100 rows** (`processed === 100`) when batch has ≥100 cloud rows left | “Up to 100” · “some rows” · optional quota |
| **`full_pack: true`** | Mode flag: “use internal 100-row loop in this HTTP request” | A noun: “the full pack is running”; a second scheduler |
| **`max_advance: 100`** | **Row quota per turn — 100 is the quantity ASF ordered** | “Maximum allowed” · “up to 100” |
| **Batch** (e.g. batch 11) | Locked file `secondary-cloud-forge-run-batch-11-locked-v1.json` (~100 cloud rows + 10 Mac control rows) | One 10-minute turn |
| **processed N/100** | Rows consumed this turn (shipped **plus** skipped) | N crons fired |
| **shipped** | Row passed motor + `advance_on_pass` | The only kind of progress |
| **skipped** | Motor failed; self-heal moved head (`pack_self_heal_motor_fail`) | Turn did not run; fake progress |

**Cadence law:**

```text
Every ~10 minutes (CF cron */10):
  ONE POST auto-tick { full_pack: true, max_advance: 100 }
  → MUST process 100 rows DOWN in that single request (batch tail excepted)
  → ONE observer row for that trigger
  → wait for next cron (not 100 more POSTs)
```

**Forbidden agent phrase:** “up to 100” — instant fail (founder correction v1.1).

---

## 3. What agents got wrong (documented splits)

### Split F — “up to 100” softening poison (founder correction v1.1)

**Wrong:** “Each cron moves **up to 100** rows.”  
**Right:** Each cron **must move 100 rows** — `max_advance: 100` is the **mandatory quota**, not a ceiling.

**Why harmful:** Agents treat 15/100 or 0/100 as acceptable. ASF order is **100 rows per turn** when the batch has capacity.

### Split A — “one row per cron” poison

**Wrong:** “Cloudflare cron processes **one plan** every 10 minutes.”  
**Right:** One cron fires **one Railway request** that internally loops **100 plans** (mandatory when batch has ≥100 rows left).

**Why harmful:** Founder thinks 5000 plans = 5000 × 10 min = months. ASF intent is **50 turns per batch** (100 rows × 50 batches), not 5000 turns.

### Split B — “100 pack running” poison

**Wrong:** “The **100 pack is still running** — wait for it to finish.”  
**Right:** The pack loop **starts and finishes inside one HTTP request** (seconds to minutes). Between crons, **nothing is “pack running”** unless `pack_in_progress` gate is stuck (INCIDENT-042 R4 — heal, not reinterpret).

**Why harmful:** Founder waits across 10-minute boundaries for a phantom job. Agents sound competent but describe a **different architecture**.

### Split C — “skipped = idle turn” poison

**Wrong:** “Automation **skipped** the batch so nothing happened.”  
**Right:** Observer `processed 100/100 · skipped 97 · shipped 3` = turn **ran fully**; motor failed on 97 rows and self-heal advanced head anyway.

**Why harmful:** Confuses **motor outcome** with **turn outcome**. Turn succeeded; evidence motor needs fix (see dispatch URL — separate engineering).

### Split D — batch file vs turn conflation

**Wrong:** “Batch 11 will take 100 days because each row is one day.”  
**Right:** Batch 11 has ~100 cloud rows. At ASF cadence, **~1 turn** drains an active batch if motor passes (or **1 turn** burns 100 skip slots if motor fails).

### Split E — redeploy ≠ drain

**Wrong:** “Redeploy Railway again to make the 100 rows run.”  
**Right:** Redeploy replaces container image. Drain cadence is **CF cron → auto-tick**. Extra `railway up` churn marks old deploys **REMOVED** — does not substitute for rows down.

---

## 4. Timeline (2026-06-23 — 2026-06-24 UTC)

| When | Event | Agent mistake class |
|------|--------|---------------------|
| 06-23 | INCIDENT-042 locks full_pack pattern | Some agents still parrot “single cycle” in side chats |
| 06-23 night | Multiple `railway up` in 30 min | Explained as failure; actually **normal REMOVED** supersession |
| 06-24 06:10 | Observer `0/100` idle on batch 10 complete | Correct — no rows to drain; some agents called it “pack not running” |
| 06-24 06:40 | Observer `100/100` · shipped 15 · skipped 85 | Some agents said “skipped batch”; founder frustration peaks |
| 06-24 | Founder: “100 per row per 10 min — not 100 pack running” | **INCIDENT-043 filed** |

---

## 5. Root cause

| ID | Cause |
|----|--------|
| R1 | **`full_pack` reads as noun** (“pack”) not **mode flag** — English ambiguity |
| R2 | **`skipped` overloaded** — queue skip vs turn skip vs batch skip |
| R3 | **No mandatory vocabulary SSOT** before INCIDENT-043 — agents read code comments at different depths |
| R4 | **Shipped vs processed** not in founder-facing agent training — mirror inject missing |
| R5 | **Batch (file) vs turn (cron)** never isolated in one table until this incident |

---

## 6. Locked remediation (law — not suggestions)

| # | Action | Path |
|---|--------|------|
| 1 | **Hundred-rows terminology law** | `brain-os/law/enforcement/SOURCEA_CLOUD_FORGE_RUN_HUNDRED_ROWS_PER_TURN_TERMINOLOGY_LOCKED_v1.md` |
| 2 | **Machine vocabulary SSOT** | `data/cloud-forge-run-hundred-rows-per-turn-vocabulary-v1.json` |
| 3 | **Cursor rule (requestable)** | `.cursor/rules/037-cloud-forge-run-hundred-rows-per-turn-v1.mdc` |
| 4 | **Pair INCIDENT-042 law** | cross-links in full-pack pattern law + `data/cloud-forge-run-full-pack-pattern-v1.json` |
| 5 | **Registry row** | this incident · **043** |

**Agents MUST** read items 1–2 before any reply that mentions: Cloud Forge Run, full_pack, cron, batch N, skipped, shipped, Railway deploy REMOVED, or “100”.

---

## 7. Mandatory agent reply shape (Cloud Forge Run questions)

Every agent answer that touches automation **must** include these three lines (plain English):

1. **Turn cadence:** “One CF cron (~10 min) = one Railway request = **100 rows down** (mandatory quota).”
2. **Proof:** Quote `cloud_forge_run_head` before/after or observer `processed N/100` (not “pack running”).
3. **Batch vs turn:** Name active **batch_id** from queue API separately from **rows consumed this turn**.

**Forbidden reply patterns (instant fail — re-read law):**

- “one plan per cron”
- “the 100 pack is still running” (without `pack_in_progress` gate proof)
- “skipped means the turn didn’t run”
- “up to 100” / “up to 100 rows”

---

## 8. Proof commands (read-only · Mac founder session)

```bash
# Queue head + batch (realtime)
curl -sS "https://sourcea-fbe-runner-production.up.railway.app/api/cloud-forge-run/queue/v1"

# Last turns — look for pack.processed and pack.max_advance
curl -sS "https://sourcea-fbe-runner-production.up.railway.app/api/cloud-forge-run/observer/v1"
```

- “redeploy to advance the queue”

---

## 9. Close criteria

- [ ] All agents cite INCIDENT-043 vocabulary in cloud-forge-run threads (founder spot-check)
- [ ] Zero new chats recommending “one row per cron” for ASF drain
- [ ] `validate-cloud-forge-run-hundred-rows-vocabulary-v1.sh` PASS in ship window
- [ ]  5000 drain: head advances ~100 rows per cron turn (motor fix separate)

---

## 11. Founder display names (anti-poison · 2026-06-24)

| Poison (retired) | Say |
|------------------|-----|
| drain · Cloud Forge Run | **Cloud Forge Run** |
| loop · drain loop · Cloud Forge Run | **Auto Runtime** |

**Law:** `SOURCEA_CLOUD_FORGE_RUN_AUTO_RUNTIME_VOCABULARY_LOCKED_v1.md` · **SSOT:** `data/cloud-motor-founder-vocabulary-v1.json` · **Rule:** `038-cloud-forge-run-vocabulary-v1.mdc`

Internal API paths (`/api/cloud-forge-run/*`) unchanged.

---

## 10. Related

- `brain-os/law/enforcement/SOURCEA_CLOUD_FORGE_RUN_FULL_PACK_PATTERN_LOCKED_v1.md`
- `brain-os/incidents/SINA_CLOUD_FORGE_RUN_BATCH3_RAILWAY_CHAIN_INCIDENT_042_LOCKED_v1.md`
- `brain-os/law/enforcement/SOURCEA_POISON_AND_REALTIME_BLOCKER_TERMINOLOGY_LOCKED_v1.md`
- `scripts/cloud_auto_runtime_v1.py` → `run_auto_runtime_pack`
- `data/cloud-auto-runtime-v1.json`

**LOCKED v1.0 — INCIDENT-043**
