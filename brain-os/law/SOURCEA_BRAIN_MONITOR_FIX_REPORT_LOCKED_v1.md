# Brain Monitor Fix — Full Honest Report (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
<!--
SOURCEA-AGENT-DOC
author: Maintainer-Brain-Monitor-Audit
agent_tag: SOURCEA-BRAIN-MONITOR-REPORT-20260609
doc_date: 2026-06-09
status: LOCKED
-->

| | |
|--|--|
| **Version** | `SOURCEA-BRAIN-MONITOR-REPORT-1.0-LOCKED` |
| **sequence_id** | `SA-2026-06-09-BRAIN-MONITOR-REPORT` |
| **Companions** | `SOURCEA_GOLDEN_INSIGHT_AND_SAFETY_LOCKED_v1.md` · `SOURCEA_WORKER_E2E_POSTMORTEM_LOCKED_v1.md` |
| **Locked** | 2026-06-09 · **status refreshed** 2026-06-10 |

---

## Verdict on Brain’s message

**Brain was right to push back.** The screenshot showed **real bugs**, not “refresh and it’s fine.” Fixes Brain described **did land logged**. Some numbers in Brain’s message are **already stale** because the queue moved again (including standard E2E runs).

### Brain claim vs honest check

| Brain claim | Honest check |
|-------------|--------------|
| STALE broker 67 → 0 | **TRUE** — `broker_stale: 0` logged |
| Pack 6 rolled sa-0045..sa-0054 | **TRUE** — `~/.sina/healthy-queue-30-active.json` |
| `dual_proof=True`, Brain PASS | **TRUE** — `brain_ok: true`, `dual_proof_ok: true` |
| HERE #45 sa-0045 CHECK | **Was true** when Brain wrote — queue advanced since |
| Queue tab 10 rows | **Was plausible** — drops when items DONE |
| INBOX sa-0045 pending | **Was true** — then sa-0046 delivered |
| Valid YES 113 | **Was true** — advanced with receipts |
| Hard-refresh :13021/monitor | **Problem** — monitor server often **DOWN**; hub **:13020 UP** |

---

## What the screenshot actually showed (Brain was correct)

### 1. HERE stuck on sa-0035 while Pack 5 was done

**Real bug.** Monitor `you_are_here` comes from:

- `~/.sina/healthy-queue-state-v1.json` → `next_pos`
- `~/.sina/healthy-queue-30-active.json` → queue items

When pack replay finished but `next_pos` / active pack didn’t roll, UI showed old “you are here.”

### 2. Queue tab → “No rows”

**Real bug**, not “empty backlog.” Queue filter only shows rows where `map ∈ {HERE, QUEUE}`:

```text
monitor_honesty_lib_v1.py (filter_mode == "queue"):
  rows = [r for r in rows if r["map"] in ("HERE", "QUEUE")]
```

If pointer sits on completed pack position, or `next_pos` points outside active 30-pack window, filter returns **zero rows** even though REGISTRY still has 800+ backlog tasks.

### 3. STALE broker 67

**Real integrity issue**, not harmless metadata. Orphan `WORKER_SUBMIT` events without matching receipts inflated STALE count. Permanent fix: `prune-stale-broker-backlog-events-v1.py` in `enforce-registry-hygiene-v1.sh`.

---

## What Brain fixed (verified logged)

- Pack 5 replay sa-0035..sa-0044 — broker turns completed
- Pack 6 roll sa-0045..sa-0054 — new `healthy-queue-30-active.json`
- STALE broker cleared — **0** logged
- INBOX delivered — worker path unblocked
- Brain/orchestrator aligned — `dual_proof=True`

---

## What moved since Brain’s message (expected, not regression)

Standard E2E recipe step (`validate-goal1-e2e-v1.sh`) reset orchestrator and delivered next CHECK:

| Field | Brain said | Then (post-E2E) | **Now (2026-06-10)** |
|-------|------------|-----------------|----------------------|
| HERE | #45 sa-0045 CHECK | #46 sa-0046 CHECK | **sa-0079 ACT** (queue advanced) |
| INBOX | sa-0045 pending | sa-0046 pending | **cleared** — next deliver on motion |
| Valid YES | 113 | 114 | **144** |
| sa-0045 | waiting | **DONE** — receipt logged | closed |
| Queue tab rows | 10 | 9 | varies with DONE filter |

**That is expected:** goal1 E2E resets + delivers; it advances the line after items close.

---

## Two separate problems (don’t mix them)

```text
MONITOR TRUTH BUGS          vs          REAL BACKLOG
(pointer, STALE, filter)                (REGISTRY tasks)
        ↓                                        ↓
   Brain fixed logged                    Still the actual work
   STALE=0, pack rolled                   toward 1000 Valid YES
```

Brain fixed the **first class**. The 800+ task backlog is **not** a UI bug — it’s honest remaining work.

---

## Critical finding: :13021 vs :13020

| URL | Status |
|-----|--------|
| **:13021** monitor dashboard | Often **not running** — needs `dashboard_server_v1.py` |
| **:13020** Sina Command hub | **UP** — primary founder UI |

**Use:**

- Sina Command on **:13020** + Refresh, **or**
- Start 13021 dashboard if you rely on that URL

If UI looks wrong after refresh on :13020 → payload/cache issue — **disk SSOT wins**.

---

## Factory lock orphan pattern

Factory lock may show `full_e2e` held by long-running bash after **background** `validate-sourcea-e2e-full-v1.sh`.

**Before next E2E:**

```bash
python3 ~/Desktop/SourceA/scripts/factory_validation_lock_v1.py sweep --json
python3 ~/Desktop/SourceA/scripts/factory_validation_lock_v1.py status --json
```

Don’t start second full E2E on top.

---

## How fixes fit together (full arc)

| Layer | What broke session | Fix shipped |
|-------|-------------------|-------------|
| P0 structural | FEEDBACK `built_at` drift · parallel E2E | `factory_validation_lock` · `feedback_hub_sync_assert_v1.py` |
| P1 operational | 5min E2E aborted · no ladder | fast ladder · standard recipe + tee |
| Brain monitor | pointer stale · STALE 67 | pack roll · prune STALE · INBOX deliver |
| Chain | — | `dual_proof=True` |

---

## What happens next (normal path)

1. Refresh Sina Command (**:13020**) — Valid YES, STALE 0, HERE from live payload
2. **RUN INBOX** or **▶ START AUTO RUN** on current queue head
3. Do **not** run full E2E + goal1 in parallel — `validate-sourcea-e2e-standard-v1.sh` only when re-proving
4. **Brain `activate: WAIT`** while INBOX pending = **normal**, not “Brain broken”

---

## Founder actions (ordered)

| # | Action | Why |
|---|--------|-----|
| 1 | Refresh **:13020** | Disk ahead of old screenshots |
| 2 | **START AUTO RUN** on current head (**sa-0079** as of 2026-06-10) | Real factory motion |
| 3 | Ignore sa-0035 / STALE 67 on **old** screenshots | Fixed logged |
| 4 | Don’t use :13021 without starting that server | Use :13020 |

---

## P2 ship next (small, high leverage)

| # | Item | Why |
|---|------|-----|
| 1 | Auto `--write-receipt` after worker batch close | Stops Brain column “everything PEND” panic |
| 2 | Stale factory-lock sweeper (dead PID auto-release) | Stops zombie full E2E blocking ladder — **partially shipped** (`sweep`) |
| 3 | Monitor “queue empty” guard | If filter=queue and rows=0 but `next_pos` in pack → diagnostic banner |
| 4 | Single monitor URL in docs | :13020 vs :13021 confuses everyone |

---

## Do not

- Treat STALE broker as cosmetic — it wasn’t acceptable
- Trust chat over disk for HERE / INBOX / Valid YES
- Re-run raw full E2E while auto-run or another E2E is active
- Expect :13021 to work without starting that server

---

## One-line truth

> Brain was right: monitor showed **stale pointer/filter** and **real STALE broker garbage** — fixed logged. Queue has **advanced since** (114 → **144** Valid YES). Job now: refresh **:13020** and **factory motion** — not chase sa-0035 or STALE 67 again.

If after hard refresh on :13020 you still see sa-0035 or STALE 67 → trace **live hub payload**, not rerun E2E.

---

## SAVE / LOCK / IMPLEMENT

| Item | Recommendation |
|------|----------------|
| This report | **SAVE + LOCK** |
| Monitor truth fixes | **KEEP** — hygiene after every pack |
| :13020 as primary UI | **IMPLEMENT** |
| Factory motion | **IMPLEMENT** — sa-0079+ |
| :13021 without server | **NEVER** assume it works |

---

*End SOURCEA_BRAIN_MONITOR_FIX_REPORT_LOCKED_v1*
