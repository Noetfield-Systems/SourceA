# SourceA E2E Debugger Playbook (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
> **Note 2026-06-10:** Rules 0–7 remain valid for E2E proof only. Do **not** use this playbook to promote Cursor AUTO-RUN as founder P0 under FREEZE.

<!--
SOURCEA-AGENT-DOC
author: Maintainer-E2E-Recipe
agent_tag: SOURCEA-E2E-PLAYBOOK-LOCK-20260609
doc_date: 2026-06-09
status: LOCKED
-->

| | |
|--|--|
| **Version** | `SOURCEA-E2E-PLAYBOOK-1.0-LOCKED` |
| **Status** | **LOCKED** — edits require founder unlock + new version suffix (`_v2`) |
| **Locked** | 2026-06-09 (formal seal — validator `validate-sourcea-e2e-playbook-locked-v1.sh`) |
| **sequence_id** | `SA-2026-06-09-E2E-PLAYBOOK` |
| **Canonical path** | `/Users/sinakazemnezhad/Desktop/SourceA/SOURCEA_E2E_DEBUGGER_PLAYBOOK_LOCKED_v1.md` |
| **Lock receipt** | `~/.sina/sourcea-e2e-playbook-lock-v1.json` |
| **Validator** | `scripts/validate-sourcea-e2e-playbook-locked-v1.sh` |
| **For roles** | Worker · Brain · Maintainer · Founder · any E2E debugger |
| **Authority** | Subordinate to `SINA_OS_SSOT_LOCKED.md` · complements `brain-os/law/enforcement/BRAIN_NO_FULL_E2E_SHELL_LOCKED_v1.md` |
| **Chat origin** | Cursor session `a53f3fa1` — hub safety UX + cache cleanup + E2E hardening handoff |

**When lost:** open this file first. Do **not** re-derive process from chat memory.

**Lock rule:** Do not edit body in place. Fork → `_v2` → re-run validator → update sequence registry.

---

## Find me again (index hooks)

| Where | Pointer |
|-------|---------|
| Document sequence | `SOURCE_A_DOCUMENT_SEQUENCE_REGISTRY_LOCKED_v1.md` → `SA-2026-06-09-E2E-PLAYBOOK` |
| Program threads | `ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md` → `THREAD-ECOSYSTEM` hook row |
| Factory priority | `brain-os/plan-registry/SOURCEA-PRIORITY.md` → playbook row 2026-06-09 |
| Brain law | `brain-os/law/enforcement/BRAIN_NO_FULL_E2E_SHELL_LOCKED_v1.md` |
| Hub Actions | 🛡 Safety check · 🔁 Fix ecosystem · Restart hub |
| Scripts (recipe) | `scripts/validate-sourcea-e2e-standard-v1.sh` |
| Scripts (fast) | `scripts/validate-e2e-fast-ladder-v1.sh` |
| Scripts (repair) | `scripts/fix-ecosystem-all-v1.sh` |

---

## Golden recommendation (system + team + products)

| Lane | Success model | Motion |
|------|---------------|--------|
| **FACTORY** | 144 → 1000 **Valid YES** (one `sa`/turn, receipts, no chat fiction) | Hub **▶ START AUTO RUN** or Worker `run inbox once` |
| **PRODUCT** | 3 TrustField demos (parallel track, ASF calendar — **not** Worker queue) | Founder calendar / demo calls |
| **AGENT** | 9s repro → targeted fix → ~3m verify → **one** ~6m standard E2E | This playbook |
| **NEVER AGAIN** | 40 min re-proving strict build for a 9s late-check flake | Rules 0–7 below |

---

## Rule 0 — Parse the failure section first

| Section failed | Re-run? |
|----------------|---------|
| Gates / pack | Only that script (~1s) |
| Strict build | Only build (~70s) **if** gates passed |
| `find_critical_bugs` / phase-s0 | Standalone phase-s0 (~9–90s) |
| Full chain | **Once**, after above green |

---

## Rule 1 — Standalone repro (seconds)

```bash
cd ~/Desktop/SourceA/scripts
bash validate-phase-s0-ssot-alignment-v1.sh          # ~9–90s
bash validate-feedback-aggregate-hub-sync-v1.sh      # isolates sa-0042
bash validate-hub-built-at-sync-contract-v1.sh       # contract PASS
```

Read the **line number** in `AssertionError` — **sa-0017** vs **sa-0042** are different fixes.

---

## Rule 2 — One fix, two verifies, one full E2E

1. Fix the **proven** validator only  
2. `bash validate-phase-s0-ssot-alignment-v1.sh`  
3. `python3 find_critical_bugs.py` (~3 min)  
4. **One** `bash validate-sourcea-e2e-standard-v1.sh` — not 3× raw full E2E

---

## Rule 3 — Logging (never hide failures)

```bash
# NEVER:
bash full_e2e.sh 2>&1 | tail -25

# ALWAYS:
bash scripts/validate-sourcea-e2e-standard-v1.sh   # has tee built-in
# or:
bash scripts/validate-sourcea-e2e-full-v1.sh > /tmp/e2e.log 2>&1
echo EXIT:$?
tail -30 /tmp/e2e.log
```

Debug JSONL only when needed: `SINA_E2E_DEBUG_LOG=1` (`scripts/_debug_e2e_log_v1.py`).

---

## Rule 4 — New `hub_built_at` checks

Must use **`scripts/feedback_hub_sync_assert_v1.py`** — never copy a single-read assert into a new `sa-00xx`.

Contract validator: `bash scripts/validate-hub-built-at-sync-contract-v1.sh`

---

## Rule 5 — “Intermittent” with 3–10s timestamp gap

→ **Concurrent shell write**, not corrupt JSON.  
→ **Resync at check site** (`sync_feedback_aggregate_hub_built_at_v1.py` + retries), not rebuild entire panel.

---

## Rule 6 — Transient pack / gatekeeper flake

Re-run `bash validate-sourcea-1000-pack.sh` **once**.  
If PASS → queue noise or ACTIVE_NOW drift — run gatekeeper pre-sync (see Fixes shipped).  
Stay on phase-s0 line; do not jump to full E2E.

---

## Rule 7 — Preflight before any E2E session

```bash
bash scripts/validate-ecosystem-safety-v1.sh   # lock, monitor, INBOX, contracts
bash scripts/validate-e2e-fast-ladder-v1.sh    # ~90s
# then only if needed:
bash scripts/validate-sourcea-e2e-standard-v1.sh
```

---

## Accurate status (snapshot 2026-06-10T00:16Z)

| Check | Status |
|-------|--------|
| Root cause (sa-0042 `hub_built_at` flake) | **Identified and fixed** — shared `feedback_hub_sync_assert_v1.py` |
| sa-0017 / sa-0042 same contract | **Yes** |
| Debug noise in production | **Gated** (`SINA_E2E_DEBUG_LOG=1` only) |
| phase-s0 / `find_critical_bugs` | **Green** when run standalone |
| Full E2E sign-off | Use **standard recipe once** — do not stack parallel full E2E shells |
| Factory queue | **sa-0079 ACT** — INBOX cleared; Worker motion, not E2E |
| Valid YES (honest) | **143** (`~/.sina/last-hygiene-pass-v1.json`) |
| REGISTRY done | **144** (receipt-only enforced) |
| `dual_proof` | **True** |

---

## What you should do now (founder)

| Priority | Action |
|----------|--------|
| 1 | **Don’t re-run E2E** unless you want proof — factory is structurally fixed |
| 2 | Refresh **http://127.0.0.1:13020** → **▶ START AUTO RUN** or Worker `run inbox once` on **sa-0079** |
| 3 | Close old debug Canvas/tabs — separate from Worker chat |
| 4 | If E2E again: Rule 7 chain only **once** |
| 5 | **🛡 Safety** = top bar or blue Home panel — **not** red ⛔ Emergency |

---

## Session threads captured (so nothing is lost)

This playbook consolidates **multiple Cursor arcs** from session `a53f3fa1` and prior E2E hardening work:

| Thread / topic | What was done | Where on disk |
|----------------|---------------|---------------|
| Hub Safety button invisible | Blue Factory safety panel + top bar 🛡 Safety + numbered steps | `hub_home_founder_view_v1.py`, `app.js`, `shell.html` |
| Hub buttons dead | `/api/action` `UnboundLocalError` fix | `sina-command-server.py` |
| Prompt feed stale Home | `renderDirectionBigPicture()` restored | `app.js` |
| Restart hub noop | `SINA_FORCE_RESTART=1` honored | `serve-sina-command.sh` |
| Gatekeeper QUEUE_POS_DRIFT | ACTIVE_NOW sync before gatekeeper | `validate-gatekeeper-v1.sh` |
| sa-0042 flake class | Shared retry assert module | `feedback_hub_sync_assert_v1.py` |
| E2E recipe P1 | Fast ladder + standard recipe + factory lock preflight | `validate-e2e-*-v1.sh` |
| Brain full E2E ban | Routing-only law | `BRAIN_NO_FULL_E2E_SHELL_LOCKED_v1.md` |
| Mac cache cleanup | pip, playwright, Cursor logs, retrieval cache (~4GB freed) | Ops only — not a repo script |
| 1000-pack specialist audit | Phase-first drain s0→s2; don’t use full E2E as debugger | Analysis in chat — motion = factory queue |

**Not lost — still authoritative elsewhere:**

- `ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md` — all program threads  
- `ASF_FULL_DAY_EXECUTION_PLAYBOOK_LOCKED_v1.md` — hour-by-hour day execute  
- `brain-os/plan-registry/SOURCEA-PRIORITY.md` — sa receipt rows  
- `~/.sina/brain-current-action-v1.json` — Brain disk SSOT each turn  

---

## Fixes shipped (implement — already on disk)

| Fix | File / script | Lock recommendation |
|-----|---------------|----------------------|
| Shared `hub_built_at` assert | `scripts/feedback_hub_sync_assert_v1.py` | **LOCKED** — Rule 4 |
| Contract validator | `scripts/validate-hub-built-at-sync-contract-v1.sh` | Wire in ecosystem safety |
| Gatekeeper pre-sync | `scripts/validate-gatekeeper-v1.sh` | Keep — prevents E2E flake |
| Standard E2E recipe | `scripts/validate-sourcea-e2e-standard-v1.sh` | **Canonical** sign-off path |
| Fast ladder | `scripts/validate-e2e-fast-ladder-v1.sh` | Pre-full-E2E only |
| Factory lock | `scripts/factory_validation_lock_v1.py` | No parallel full E2E |
| Hub force restart | `scripts/serve-sina-command.sh` | `SINA_FORCE_RESTART=1` |
| Hub safety UX | `agent-control-panel/` | Hard refresh after panel rebuild |

---

## Cache / Mac heaviness (ops playbook)

Safe to clear periodically (session 2026-06-09):

```bash
pip3 cache purge
rm -rf ~/Library/Caches/ms-playwright ~/Library/Caches/node-gyp ~/Library/Caches/typescript
rm -rf ~/Library/Application\ Support/Cursor/logs/*
rm -rf ~/Library/Application\ Support/Cursor/User/globalStorage/anysphere.cursor-retrieval/*
rm -f /tmp/e2e-*.log
cd ~/Desktop/SourceA/scripts && python3 cleanup-goal1-leftovers-v1.py --json
```

**Do not delete:** `~/.sina/events/`, receipts, REGISTRY, INBOX law files.

**Heavy but keep:** `Cursor/User/globalStorage/state.vscdb` (~19GB chat state) — vacuum only with Cursor quit if needed.

**One-shot repair:**

```bash
bash ~/Desktop/SourceA/scripts/fix-ecosystem-all-v1.sh
```

---

## Agent role cheatsheet

| Role | May run | Must not |
|------|---------|----------|
| **Brain** | guard, safety, fast ladder, receipt write | full E2E, strict build (see Brain law) |
| **Worker** | one sa turn, inbox, targeted validator | 3× full E2E debugging |
| **Maintainer** | standard E2E **once** for sign-off | parallel full E2E shells |
| **Founder** | Hub Safety · START AUTO RUN · Refresh | Emergency stop unless real emergency |

---

## Proof command (when founder says “RUN STANDARD E2E ONCE”)

```bash
cd ~/Desktop/SourceA/scripts
python3 factory_validation_lock_v1.py sweep --json
bash validate-ecosystem-safety-v1.sh
bash validate-sourcea-e2e-standard-v1.sh 2>&1 | tee /tmp/e2e-standard-$(date +%Y%m%d-%H%M%S).log
```

Report only: `PASS`/`FAIL`, log path, `critical` count, `dual_proof` line.

---

## Recommendation: SAVE / LOCK / IMPLEMENT

| Item | Recommendation |
|------|----------------|
| **This playbook** | **SAVE + LOCK** — canonical debugger SSOT (this file) |
| `feedback_hub_sync_assert_v1.py` | **LOCK** — no new one-off hub_built_at asserts |
| E2E standard recipe | **IMPLEMENT** as only full sign-off path |
| Hub safety UX | **KEEP** — rebuild panel after UI changes |
| Factory motion | **IMPLEMENT** — drain queue (sa-0079+), not more E2E |
| Product demos | **PARALLEL** — TrustField track, not Worker |
| Chat-only process | **NEVER** — always write playbook row like this session |

---

## Lock seal (machine)

| Field | Value |
|-------|-------|
| `locked` | `true` |
| `schema` | `sourcea-e2e-playbook-lock-v1` |
| `validator` | `validate-sourcea-e2e-playbook-locked-v1.sh` |
| `ecosystem_safety` | wired step 4b |
| `e2e_recipe_p1` | wired |
| `important_docs_index` | `ecosystem_law` bucket |

Run check anytime:

```bash
bash ~/Desktop/SourceA/scripts/validate-sourcea-e2e-playbook-locked-v1.sh
```

---

*End SOURCEA_E2E_DEBUGGER_PLAYBOOK_LOCKED_v1 · LOCKED — do not edit in place*
