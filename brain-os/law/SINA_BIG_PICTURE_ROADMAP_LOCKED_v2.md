# Sina System — Big Picture Roadmap (Locked)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 2.0 — LOCKED  
**Supersedes:** `archive/superseded/wtm/v1/SINA_BIG_PICTURE_ROADMAP_LOCKED_v1.md`  
**sequence_id:** SA-2026-06-05-BIG-PICTURE-ROADMAP-v2  
**Hub:** `http://127.0.0.1:13020/?tab=system-roadmap`  
**Master map:** `WORLD_TARGET_MODEL_MAP_LOCKED_v5.md` (FINAL)  
**Law:** `WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v2.md`

**Companions:** `SINA_EXECUTION_INTELLIGENCE_STACK_LOCKED_v1.md` (Phase B) · `SINA_RUNTIME_STACK_LOCKED_v1.md` (Phase C) · `SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2.md` (Phase D)

---

## 0. One-page truth

| System | Question | Hub phase | Status |
|---
**Canonical WTM map:** `brain-os/wtm/WORLD_TARGET_MODEL_MAP_LOCKED_v5.md`
-----|----------|-----------|--------|
| **Execution Spine** | Durable queue + worker + memory? | **A** | ✅ DONE (`D1`–`D4`) |
| **Execution Intelligence OS** | What happened? What to prefer next? | **B** | ✅ FROZEN (`C1`–`C6`) |
| **Runtime Stack** | Verified plan → safe dispatch? | **C** | 🔄 `B4` active |
| **Pre-LLM World Model** | Repo meaning before LLM? | **D** | ❌ `A1.1` next |

**Build order on founder UI:** **A → B → C → D** (first built → final target).

**Step IDs** (`D1`, `C1`, `B4`, `A1.1`) are stable artifact names — see INCIDENT-003.

---

## 0.5 Session origin (2026-06-05)

Trigger: *major upgrade today*. Spine + intelligence + runtime + pre-LLM map = **World Target Model tab only** — not RunReceipt, factory, or Roadmaps & goals.

| Built in session | Hub phase | Step IDs |
|------------------|-----------|----------|
| Execution Spine | **A** | D1–D4 |
| Intelligence stack | **B** | C1–C6 |
| Tool graph → verify → router | **C** | B1–B3 ✅ |
| Pre-LLM roadmap locked | **D** | A1.1–A5.3 |

---

## 1. Stack diagram (target)

```text
USER → [Phase D: Pre-LLM world model] → LLM packet → LLM
         ↓
       [Phase C: Runtime stack] → founder confirm
         ↓
       [Phase A: Execution spine]
         ↓
       [Phase B: Post-exec intelligence — frozen, read-only upstream]
```

---

## 2. Phase map (hub-aligned)

```text
PHASE A — EXECUTION SPINE              ✅ DONE
PHASE B — EXECUTION INTELLIGENCE OS    ✅ FROZEN
PHASE C — RUNTIME STACK                🔄 B4 NEXT
PHASE D — PRE-LLM WORLD MODEL          ❌ A1.1 NEXT
```

---

# PHASE A — EXECUTION SPINE ✅

Steps **D1–D4** · queue · worker · memory · artifacts · `validate-execution-spine.sh`

---

# PHASE B — EXECUTION INTELLIGENCE OS ✅ FROZEN

Steps **C1–C6** · patterns · decisions · feedback · planner · context · self-optimization  
Detail: `SINA_EXECUTION_INTELLIGENCE_STACK_LOCKED_v1.md`

---

# PHASE C — RUNTIME STACK 🔄

Steps **B1–B7** · tool graph · verification · router · **B4 repair** · fabric · planner · orchestrator  
Detail: `SINA_RUNTIME_STACK_LOCKED_v1.md`

| Step | Status |
|------|--------|
| B1–B3 | ✅ |
| B4 | ● NOW |
| B5–B7 | ahead |

---

# PHASE D — PRE-LLM WORLD MODEL ❌

Steps **A1.1–A5.3** (12 gated builds · sub-phases A1–A5)  
Detail: `SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2.md`

**Next:** A1.1 Code Intelligence Layer v1

---

## 3. Status dashboard

| Domain | Status |
|--------|--------|
| Spine (Phase A) | ✅ |
| Intelligence (Phase B) | ✅ frozen |
| Runtime B1–B3 | ✅ |
| Runtime B4–B7 | 🔄 |
| Pre-LLM (Phase D) | ❌ |
| Code intelligence | ❌ **START A1.1** |

---

## Archive

v1 (reverse phase letters D→C→B→A in prose): `archive/superseded/wtm/v1/SINA_BIG_PICTURE_ROADMAP_LOCKED_v1.md`
