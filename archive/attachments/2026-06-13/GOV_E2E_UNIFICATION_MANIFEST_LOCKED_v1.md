# Governance E2E unification manifest (LOCKED v1)

**Saved:** 2026-06-13T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-13 · **Authority:** ASF order — search · check · organize · unify  
**Supersedes attachment:** `archive/attachments/2026-06-12/GOV_E2E_UNIFICATION_MANIFEST_LOCKED_v1.md` (status only)  
**Router:** `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md` · **Engine:** `GOVERNANCE_UNIFICATION_ENGINE_LOCKED_v1.md`

---

## 0. One sentence

> **Router + authority index row + truth bundle · skills from registry · plans from disk truth · hub is projection · chat is never SSOT.**

---

## 1. Truth stack (read order — nothing else first)

| Tier | Read once | Never substitute |
|------|-----------|------------------|
| **P0** | `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md` | Chat summaries |
| **P0** | `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` | Newest file in folder |
| **P0** | `python3 scripts/agent_truth_bundle_v1.py --json` | Hub hero / stale SOURCEA-PRIORITY header |
| **P1** | `SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md` | M1 canvas lag |
| **P1** | `SOURCEA_CURSOR_RULES_AND_SKILLS_MAP_LOCKED_v2.md` | Random `~/.cursor/skills` |
| **P2** | Role handoff `brain-os/lanes/MANDATORY_CHAT_HANDOFF_INDEX_LOCKED_v1.md` | Megachat memory |
| **Brain tree** | `brain-os/INDEX_LOCKED_v1.md` | Root duplicates / `os/chat-handoffs/` stubs |
| **Plans** | `brain-os/plan-registry/SOURCEA-PRIORITY.md` + `factory-now` line | `os/plan-library/` (MOVED) |

**213 root LOCKED files:** Topic law + incidents. Load **one index row** per task — never bulk-read root.

---

## 2. Skills (unified — one registry)

| SSOT | Path |
|------|------|
| Registry | `agent-skills/REGISTRY_LOCKED_v1.json` (v1.3) |
| Role map | `SOURCEA_CURSOR_RULES_AND_SKILLS_MAP_LOCKED_v2.md` |
| Sync | `bash scripts/sync-cursor-agent-skills.sh` |
| Worker load | `sourcea_worker/SKILL.md` + shared: conscious-recovery · narrative-translator · registry-drain · truth-projection · founder-freeze-conduct |

**Rule:** Cursor install under `~/.cursor/skills/sina-*` is **projection**. Registry wins on conflict.

---

## 3. Memory (unified — three layers only)

| Layer | Path | Job |
|-------|------|-----|
| Hard rules | `.cursor/agent-memory/ECOSYSTEM_HARD_RULES.yaml` | R-007–R-010 · ask-first · conflict ladder |
| Session inject | `~/.sina/agent-memory-mirror-v1.json` | Forbidden patterns · inject block |
| Brain load list | `brain-os/memory/BRAIN_KNOWLEDGE_INDEX_LOCKED_v1.md` | What Brain transfers — not Worker daily |
| Events | `~/.sina/governance-event-spine-v1.jsonl` | Spine SSOT |
| Rules in charge | `GET /api/agent-rules-in-charge-v1` | Founder live + `.mdc` banner |

**Do not mirror laws in chat.** `~/.sina/brain/` = projection · `brain-os/` wins.

---

## 4. Goals & plans (unified — disk truth wins)

| Signal | Live (2026-06-13T10:27Z) | Source |
|--------|--------------------------|--------|
| honest_done | **616 / 1000** (61.6%) | `agent_truth_bundle_v1.py` |
| factory_mode | **FREEZE** · kill_flag ON | `factory-now-v1.json` |
| queue_sa | **sa-0798** (pos 2/297) | `run-inbox-disk-truth-v1.json` |
| founder_p0 | STRATEGIC-SLICE | rules-in-charge |
| form open rows | **0** | `live_founder_decision_form_v1.py --json` |
| WTM now | PHASE D COMPLETE — ENFORCE gate when ready | rules-in-charge |

**Dual-pick law:** `queue_sa` from disk truth **>** phase-first REGISTRY head.

**6mo wedge:** `ENFORCEMENT_6MO_INVESTOR_WIN_LOCKED_v1.md` — W1 film · W2 validators · W3 commercial.

---

## 5. Machines (E2E — run, don't read)

| Machine | Command / tap |
|---------|---------------|
| Session truth | `python3 scripts/agent_truth_bundle_v1.py --json` |
| Rules banner | `python3 scripts/agent_rules_loop_orchestrator.py --phase session_start` |
| Worker gate | `python3 scripts/cursor_entry_gate.py --role worker` |
| Full hygiene | Hub → **Safety check** |
| Anti-staleness | `bash scripts/validate-anti-staleness-bundle-v1.sh` |
| Propagation | `bash scripts/validate-governance-propagation-live-v1.sh` |
| Hub sync | `python3 scripts/hub_self_refresh_v1.py --json` |
| Critical rollup | `python3 scripts/find_critical_bugs.py` (slow ~60–120s) |

---

## 6. E2E status (2026-06-13 recheck — 10:48Z)

| Check | Status | Notes |
|-------|--------|-------|
| Anti-staleness bundle | **42/42 PASS** | full green |
| S10 eternal loop | **PASS** | receipt FAIL=0 |
| Ecosystem safety | **PASS** | includes anti-staleness + S10 |
| Prompt feed no-autosend | **PASS** | INCIDENT-028 surfaces clean |
| Agent memory mirror | **PASS** | violations=0 · F09 pattern added |
| Session gate (worker) | **PASS** | ASG-20260613 |
| Form integrity | **PASS** | 0 open |
| Root LOCKED sprawl | **DEFERRED** | GOV_UNIFY batch A–F · Maintainer |

---

## 7. Fragmentation batches (unchanged — Maintainer / Brain)

| Batch | Action | Owner |
|-------|--------|-------|
| A | Root incident reports → attachment index only | Maintainer 2 |
| B | Root ↔ `brain-os/` twins → MOVED stubs | GOV_UNIFY MERGE |
| C | `SINA_BRAIN_JOB_TITLES_*` ×3 → one canonical | Brain |
| D | `os/plan-library/` enforce MOVED | Maintainer 2 |
| E | `~/.sina/brain/` mirror → pointer-only | G7 heal |
| F | S10 broker/inbox timeout validators | Worker (infra) |

**Worker this turn:** manifest refresh + truth proof — **no** mass archive · **no** hub law edits.

---

## 8. Agent session start (light — 30s)

```bash
cd ~/Desktop/SourceA
python3 scripts/cursor_entry_gate.py --role worker
python3 scripts/agent_truth_bundle_v1.py --json
python3 scripts/live_founder_decision_form_v1.py --json
```

Then: governance entry §0 branch · one authority index row · role SKILL from registry · **STOP** if FREEZE unless Brain `sa` ACT.

---

## 9. Stale vs right (anti-repeat)

| Stale (reject in chat) | Right (cite disk) |
|------------------------|-------------------|
| "33 open form rows" | **0** — form v2 filled |
| "Confirm → auto-send 10 prompts" | **FORBIDDEN** — INCIDENT-028 · live next-10 SSOT only |
| AUTO-RUN as P0 | Factory background · FREEZE · sa-0798 |
| SOURCEA-PRIORITY header sa-0779 | Truth bundle queue_sa **sa-0798** |
| Hub hero pending list | Form JSON + §ANSWERED |

---

*End GOV_E2E_UNIFICATION_MANIFEST_LOCKED_v1 — 2026-06-13*
