# World Target Model — Authority & Boundary Law (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.1 — LOCKED (governance contracts v5.1)  
**Companion:** `WORLD_TARGET_MODEL_MAP_LOCKED_v5.md`  
**Payload:** `system_roadmap.authorities` v5.1+  
**Purpose:** Zero ambiguity across Memory, Graph, Planning — critic-derived, SSOT-owned.

---

## Law (one sentence)

**Each subsystem owns one truth domain; other phases may READ, never override pre-LLM authority.**

---

## 1. Phase focus (what we optimize for)

| Phase | Focus | Optimizes for |
|-------|--------|----------------|
| **A** | Durable execution | Nothing lost — queue, run, record |
| **B** | Post-execution learning | What worked / failed / why (frozen) |
| **C** | Safe runtime control | Verify → route → repair → orchestrate (no repo semantics) |
| **D** | Pre-LLM world model | Repo meaning → ranked packet → LLM |

**Founder focus:** Understanding **before** action (D), while finishing safe runtime (C). B is complete — read-only upstream.

---

## 2. Graph taxonomy (three types — never conflate)

| Type | Owner steps | What it models | NOT |
|------|-------------|----------------|-----|
| **Execution tool graph** | **C1** | Tool/capability order for dispatch | Code AST, imports |
| **Semantic code graph** | **D1→D2→D3** | Repo structure, calls, impact | Tool routing |
| **Recovery graph** | **C4** | Failure → suggested recovery path | Pre-LLM reasoning |

**Rule:** C1 graphs **tools**. D2/D3 graphs **code**. No shared mutable graph store.

### D2 vs D3 (one sentence each)

| Step | Domain |
|------|--------|
| **D2** | Unified **semantic** fusion graph — integrates D1 indexes |
| **D3** | Structural **dependency** graph — impact simulation on fused substrate |

---

## 3. D1 bootstrap law (inside step — no new ID)

**D1 Code Intelligence** MUST begin with an internal bootstrap phase before AST/symbol indexes:

1. Repo walker first pass (file tree scan)
2. File discovery engine
3. Language detection layer
4. Module discovery seed index

**Rule:** Bootstrap completes inside D1. No D0 step. D2/D3 cannot start until D1 bootstrap + indexes are valid.

---

## 4. Memory authority matrix

| Class | Step | Plane | Role | Writes | Pre-LLM authority |
|-------|------|-------|------|--------|-------------------|
| Causal | **B2** | B | Historical truth — frozen causality | ✅ append | ❌ |
| Snapshot | **B5** | B | Historical truth snapshot (`matters_now`) | ✅ snapshot | ❌ |
| Retrieval feed | **D6** | D | Retrieval substrate — queryable representation | ❌ read-only | ❌ feed only |
| Runtime trace | **C4** | C | This-run repair trace | ✅ repair log | ❌ |
| Packet export | **D16** | D | Budget-aware memory writeback into packet | ✅ packet slice | ✅ export |

### Memory enforcement law

| Layer | Role |
|-------|------|
| **B-layer** | Historical truth — frozen causality. B2/B5 own WHY and matters_now. |
| **D-layer** | Retrieval substrate — queryable representation for pre-LLM search. |

**Rules:**
- **B** memory never defines repo truth for D — it defines **what happened**.
- **D6** reads B artifacts (`execution_memory.jsonl`, B5 snapshots) — **never writes** spine or overrides B truth.
- **D16** is the only memory merge into `llm_context_packet_v1.json` (writeback under D14 budget).

---

## 5. Planning authority matrix

| Layer | Step | Role | Authority |
|-------|------|------|-----------|
| Learning | **B4** | After execution | Learning signal only — **NOT planning truth** |
| Runtime | **C6** | During dispatch | Execution-time sequencing only — **NOT pre-LLM plan** |
| Pre-LLM | **D10** | Before execution | **ONLY SSOT** for LLM-bound pre-exec plan |

### Planning enforcement law

- **D10 wins** for pre-execution plan truth.
- **B4** may inform D10 as soft bias from history — never replace D10.
- **C6** sequences verified C1 tool graphs at runtime — orthogonal to D10 semantic decomposition.

---

## 6. Retrieval pipeline (D4–D8 — no extra step ID)

```text
D4 Intent parsed
  → D7 Query expansion (Intent → QuerySet, symbol expand, multi-query)
  → Router (inside D7): pick sources — D1 symbols / D5 vectors / D6 memory-git / D3 graph
  → D8 Graph reasoning on evidence
```

Query formulation lives in **D7**, not a separate phase letter.

---

## 7. Token budget & packet pipeline (D14–D16)

| Stage | Step | Role |
|-------|------|------|
| Compress | **D14** | Per-field token slots + summarization hierarchy — **before** assembly |
| Assemble | **D15** | Merge D14-compressed evidence into schema |
| Validate | **D15** | `validate-llm-context-packet-v1.sh` — schema gate |
| Writeback | **D16** | Budget-aware memory slots into packet — **no recomputation** |

**Packet pipeline law:** D14 compress → D15 assemble+validate → D16 writeback only. D16 must not re-rank or re-compress.

---

## 8. C ↔ D bridge (C5 scope law)

**C5 Semantic Context Fabric** is a **stateless mapping layer** only. It MUST:
- Pass handles/versions only (pointers to D1, D5 artifacts)
- Expose read APIs for runtime — **no** AST build, **no** retrieval index, **no** ranking, **no** inference

**C5 MUST NOT:** duplicate D1, D5, D7, D9, or become a shadow intelligence layer.

---

## 9. B stack frozen law

- No new B modules after **B6**.
- B outputs are **read-only** inputs for C and D.
- B does not influence pre-LLM truth after D9/D10 ship.

---

## 10. External review policy

→ `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` rows `CRITIC` + `ALIGNMENT` (canonical — not restated here).

---

**LOCKED** — boundaries enforced in hub payload `authorities` block (v5.1+).
