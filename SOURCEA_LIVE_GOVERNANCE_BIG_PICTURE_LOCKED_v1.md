# SourceA Live Governance — Big Picture (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-11-LIVE-GOV-BP  
**Authority:** ASF · **need vs noise · tier priority · zero-latency propagation target**  
**Parent:** `SINA_OS_SSOT_LOCKED.md` · `TERMINOLOGY_DICT` · `LAW PURITY` · `DISK_TRUTH_E2E`  
**Machine:** `governance_propagation_cascade_v1.py` · `validate-governance-propagation-live-v1.sh`

---

## 0. One sentence

> **Know what we want and reject what we don’t — P0 SSOT at the top, smaller P1–P7 below — and every G0 change or worker completion cascades to monitor/hub without another agent checking.**

---

## 1. Theory vs proven (honest)

| State | Meaning | Today |
|-------|---------|-------|
| **Theory** | On paper · validators exist · agents *should* obey | Most of 2026 governance build |
| **Proven** | Machine-enforceable · live projection · **no governance latency** on critical path | **Partial** — see §6 |

**Proven criterion (your bar):** Complete policy on disk **and** worker says “file done” → machine updates monitor + inbox + factory-now **in one cascade** — no founder refresh · no second agent audit.

---

## 2. Organizational tiers P0–P7 (one vocabulary — do not mix)

**Rule:** This **P0–P7** is **governance stack depth** — NOT hub founder P0 · NOT doc-library P0 · NOT pack P0 (Cross-doc §12.3 systems A–G).

| Tier | Role | What belongs | Change propagates to |
|------|------|--------------|----------------------|
| **P0** | **SSOT apex** | `SINA_OS_SSOT` · LAW PURITY · ecosystem shape | P1–P4 within **5s** (monitor) · hub light align |
| **P1** | **Registry + resolution** | Authority index · Governance entry · TERMINOLOGY_DICT · Cross-doc · GOV_UNIFY | Coverage audit · agent_rules charge · hub essentials |
| **P2** | **Topic law** | One LOCKED file per topic at row path | Validators for that topic · incident corpus if report |
| **P3** | **Enforcers** | `validate-*` · `find_critical_bugs` · AS-01..19 · ACE planes | FAIL loud · Safety red |
| **P4** | **Live projection** | Hub command-data · monitor :13021 · ACTIVE_NOW · factory-now | RT or labeled LAG · dual-pick gate |
| **P5** | **Process machines** | Five-step · Fork · Result · 100-step · Batch 2 | Boot prompts · Canvas UI |
| **P6** | **Staging / input** | RESEARCH · attachments · chat · advisor paste | Never auto-promote to law |
| **P7** | **Noise — reject** | Duplicate POSA copies · examples · superseded archive · chat summaries | Do not load · do not cite |

**P0 is SSOT.** Everything else must be **smaller** and **subordinate** — noise is fragmentation.

---

## 2b. Truth tree — thorn → root → branch → leaf (down only)

Founder model: keep the **thorn** healthy and the whole tree stays green. Truth **never climbs** from leaf to root — it **descends** from the thorn.

```text
THORN (P0)     ASF will · SINA_OS_SSOT · LAW PURITY — apex; finds the root
  ↓
TRUNK (P1)     Authority index · Governance entry · TERMINOLOGY · Cross-doc
  ↓
BRANCH (P2)    One LOCKED file per topic at row path
  ↓
BARK (P3)      Validators · enforcers — FAIL loud if leaf tries to override thorn
  ↓
LEAF (P4–P6)   Hub · monitor · ACTIVE_NOW · RESEARCH · chat — projection & input only
  ↓
FALLEN (P7)    Archive · superseded · duplicate POSA — must not re-enter trunk
```

| Direction | Allowed | Forbidden |
|-----------|---------|-----------|
| **Down** | P0 edit → cascade → monitor/hub/inbox | — |
| **Up** | — | Leaf/chat/archive → new law without GOV_UNIFY + row |
| **Sideways** | Pointer-only between peers | Duplicate prose competing as law |

**If an untruth enters a leaf (chat, stale hub, attachment essay):** it **does not enter the original system** while enforcers hold — `validate-no-archive-as-law` · LAW PURITY · `authority_root_coverage_audit` T3_ORPHAN=0 · cascade from **G0 mtime only**.

**MonoRepo mirror (Layer A):** LAW → OPERATIONAL → ARCHIVE — same down-only rule (`002-sot-hierarchy-registry`).

---

## 3. What we NEED vs what we DON’T (big picture inventory)

### 3.1 NEED — keep and wire

| Cluster | Artifacts | Why |
|---------|-----------|-----|
| **SSOT + purity** | OS SSOT · Authority index · LAW PURITY · Governance entry | Topic → path → act |
| **Dictionary** | TERMINOLOGY_DICT | Human ↔ machine one voice |
| **Integrity pack** | Five-step · Fork · Result · 100-step · Batch 2 · Cross-doc | Daily + deep audit |
| **Resolution** | Alignment 12-order · GOV_UNIFY · Phase receipts · FR tracker | Merge · don’t forget |
| **ACE** | `AUTO_CONFLICT_ENGINE_V3` · Conflict room · Council | DESIGN / EXECUTION / DELIVERY |
| **Enforcers** | Anti-staleness AS · root coverage · completion backlog · ecosystem safety | Machine proof |
| **Live wire** | Monitor 5s · broker worker-submit · propagation cascade | Zero-latency path |
| **Disk truth** | E2E matrix · run-inbox truth · dual-pick | Projection = control |

### 3.2 DON’T NEED — noise (P7)

| Item | Action |
|------|--------|
| Second copy of same rule prose | Archive · pointer only |
| Newest file wins | Forbidden — index row wins |
| Chat / GPT as structural SSOT | Input only |
| Cursor plan todos as mission | Cancel on STOP (GAP) |
| Noetfield POSA v3 as ecosystem apex | Historical product L0 — SourceA OS SSOT wins |
| 285 duplicate validate scripts without AS bundle | Run bundle + critical rollup only |
| Manual “refresh monitor” agent step | Forbidden — disk wired |

---

## 4. Collected stack (integrity · ACE · resolution · result)

```text
P0  SINA_OS_SSOT + LAW PURITY
 └─ P1  Authority index · Governance entry · TERMINOLOGY_DICT
      ├─ P2  Topic LOCKED laws (105+ rows)
      ├─ P3  Enforcers (AS-01..19 · coverage · backlog · safety)
      ├─ ACE  AUTO_CONFLICT v3 → Conflict room → Council (parallel triage)
      └─ P5  Process: Five-step → Fork → Result → 100-step → Batch 2
            Resolution: Alignment · GOV_UNIFY · receipts · FR-tracker
            Live: propagation_cascade · monitor · broker · hub
```

---

## 5. Propagation ladder (G0 word change → machine labels)

**Law:** Edit at **P0/P1** → machine runs cascade — **not** manual hub copy · **not** second agent “please rebuild.”

| Trigger | Machine action | Target tier |
|---------|----------------|-------------|
| `SINA_AUTHORITY_INDEX_MAP` mtime change | `monitor_live_sync` signature + optional `governance_propagation_cascade` | P1→P4 |
| `PROGRAM_PROGRESS.json` change | cascade `reason=progress` | P1→P4 |
| Worker `worker-submit` VERIFY | cascade `reason=worker_round_complete` | P4 RT |
| ASF founder PICK receipt written | cascade `reason=founder_pick` + strict hub if law touched | P0→P4 |
| Maintainer law SAVE/LOCK | `governance_propagation_cascade --strict-hub` | Full panel |

**Receipt:** `~/.sina/governance-propagation-receipt-v1.json`

**Worker prompt line (mandatory close):**

```text
After WORKER_ROUND_REPORT + broker worker-submit — machine runs propagation cascade; do not ask founder to refresh monitor.
```

---

## 6. Zero-latency status (E2E honest — from DISK_TRUTH matrix)

| Layer | Status today | Target |
|-------|--------------|--------|
| Receipts · broker · monitor pulse | **RT** (~5s) | Keep |
| Factory-now line | **LAG** 5s TTL | Event-driven on cascade |
| Hub command-data | **LAG** minutes | Light align on cascade · strict build on law |
| P0 hero dual-pick text | **GAP** if misaligned | dual-pick FAIL |
| Chat memory | **GAP** | Forbidden |
| G0 law → hub labels | **LAG** until cascade | **Cascade on mtime + worker-submit** |

**Not yet proven:** “Change one P0 word → every label in hub updates instantly” — **hub full rebuild** still minutes; **monitor + factory-now + inbox** hit RT via cascade.

---

## 7. Implementation checklist (this task)

| # | Item | Status |
|---|------|--------|
| 1 | P0–P7 tier vocabulary (this doc) | **DONE** |
| 2 | Need / don’t inventory (§3) | **DONE** |
| 3 | `governance_propagation_cascade_v1.py` | **DONE** |
| 4 | Broker worker-submit → cascade hook | **DONE** (maintainer wire) |
| 5 | G0 paths in monitor watch signature | **DONE** (maintainer wire) |
| 6 | `validate-governance-propagation-live-v1.sh` | **DONE** |
| 7 | Phase 1.10 + integrity Phases 3–10 | **OPEN** (backlog enforcer) |
| 8 | Hub Today “big picture” card | **P2** |
| 9 | Full strict hub on every P0 token edit | **P2** — event debounce |

---

## 8. How agents stay in the spirit of law

1. Read **TERMINOLOGY_DICT** + this doc §3 before multi-file edits  
2. Run **completion backlog** before SHIP — SAY open items  
3. Never promote P6→P2 without GOV_UNIFY + authority row  
4. Worker ends with broker submit — **not** “please check monitor”  
5. ACE triage on conflict — winning law from index row  

---

*End live governance big picture*
