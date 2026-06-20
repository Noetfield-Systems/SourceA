# Sina Ecosystem — Source Alignment Law (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.1 — COMPLETE RULE ORDER · FINAL LOCKED  
**sequence_id:** SA-2026-06-05-SOURCE-ALIGNMENT-LAW  
**Scope:** **Whole system** — SourceA, hub, all locked plans, roadmaps, Layer A, factory, WTM, products  
**Authority:** ASF · subordinate only to `SINA_OS_SSOT_LOCKED.md` for ecosystem structure  
**Canonical location:** `/Users/sinakazemnezhad/Desktop/SourceA/SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md`  
**Hub:** Essentials read chain · Doc library · WTM law strip  
**Router:** `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md` §3 · **Index:** `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` row `ALIGNMENT`

---

## 0. Founder law (plain language — LOCKED)

When we **lock** docs, the **last locked version is our SOURCE**.

When we align a **new suggestion** (roadmap, next step, ChatGPT paste, advisor opinion) against **our map, system, or roadmap**, we must:

1. **Analyze fully** — similarities, repetition, beneficial extras.  
2. **Keep our plan** — locked source is not replaced by the new opinion.  
3. **Never let** chat cause **drift, mixing, or mess**.  
4. **First** file extras as a **small attachment** (not in source yet).  
5. **After we are convinced** an extra is helpful — analyze **where it sits** in the **current** roadmap (which phase, which step family).  
6. **If convinced** it belongs in build order — insert as a **sub-step** (e.g. **Step 2.1** under Step 2), then **upgrade** locked map **vN → vN+1** — never replace unrelated steps.

**Chat is input. Locked source is truth. Sub-steps extend; they do not rewrite.**

---
**Canonical WTM map:** `brain-os/wtm/WORLD_TARGET_MODEL_MAP_LOCKED_v5.md`


## 1. Law (one sentence)

**Locked vN = SOURCE → compare → keep plan → attach extras → convince → place under related step → sub-step insert → vN+1 upgrade with archive.**

---

## 2. Source hierarchy (never invert)

| Rank | What | Role |
|------|------|------|
| **1** | Latest `*_LOCKED_vN.md` at SourceA root | **SOURCE** |
| **2** | Hub / app payload from those docs | Live mirror of source |
| **3** | `archive/attachments/` (pre-convince notes) | Staging — not source |
| **4** | `archive/attachments/examples/` | Worked cases — not source |
| **5** | Chat / ChatGPT / advisor paste | **Input only** — see `CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md` |

**Agent smart judgment (rank 3)** sits between machine SSOT and attachments — see `AGENT_DECISION_STACK_AND_SMART_JUDGMENT_LOCKED_v1.md`. It may harden contracts and prevent repeat incidents; it may **not** replace Orders 1–4 or skip the convince gate.

---

## 3. Complete rule order (mandatory sequence)

Execute **in order**. Do not skip a step.

| Order | Name | Action | Output |
|-------|------|--------|--------|
| **1** | **Identify source** | Find latest locked `*_LOCKED_vN.md` + hub payload for that track | Source version N |
| **2** | **Line-by-line compare** | Map every new item to existing step/rule/phase | Compare table |
| **3** | **Classify each row** | Same · rename · extra · repeat · contradict · replace | Per-row verdict |
| **4** | **Keep the plan** | Do not rewrite master map, SSOT, or hub to match chat | Unchanged steps 1…N |
| **5** | **Reject drift** | Drop contradicts, replaces, renumbers, omissions of locked steps | Rejected log |
| **6** | **Attachment (staging)** | Beneficial extras → `archive/attachments/<track>/` — **not** source yet | Attachment file |
| **7** | **Convince gate** | Founder/ASF agrees extra is worth building (not just interesting) | Explicit yes/no per extra |
| **8** | **Placement analysis** | For each convinced extra: which **phase**, which **parent step**, before/after which sibling | Placement memo |
| **9** | **Sub-step insert** | Add as child of related step — e.g. Rule 6 → **Step 2.1** under Step 2 — stable parent IDs unchanged | New ID only for insert |
| **10** | **Upgrade source vN+1** | New `*_LOCKED_v{N+1}.md` · update payload/hub · archive vN to `archive/superseded/` | Manifest evidence row |
| **11** | **Retire attachment** | Move staging attachment to `examples/` or merge one-line pointer into map § Attachments | No parallel roadmap left |
| **12** | **Verify** | Hub step count, IDs, phase order, read chain — match vN+1 only | Checklist §12 |

**Rule:** Orders **1–6** happen on **every** new suggestion. Orders **7–12** happen **only** when convinced to build the extra.

---

## 4. Classify every delta (Order 3)

| Class | Action |
|-------|--------|
| **Same** | No change |
| **Rename only** | Alias in attachment — **do not** rename stable step IDs |
| **Beneficial extra (unconvinced)** | Order 6 attachment only |
| **Beneficial extra (convinced)** | Orders 7–12 — placement + sub-step + vN+1 |
| **Repeat / already built** | Reject — cite existing step |
| **Contradicts order** | Reject |
| **Replaces locked plan** | Reject — violates §0 |

---

## 5. Convince gate (Order 7)

Before **any** sub-step or vN+1:

- [ ] Extra is **not** duplicate of existing step or architecture zone already assigned  
- [ ] Extra improves **build order** or **gate clarity** — not cosmetic rename  
- [ ] **Founder/ASF explicit yes** (chat enthusiasm is not approval)  
- [ ] Placement analysis (Order 8) written — not “add somewhere in Phase D”  

**No convince → stays attachment only. No hub change.**

---

## 6. Placement analysis (Order 8)

For each convinced extra, answer:

| Question | Required answer |
|----------|-----------------|
| Which **hub phase**? | A / B / C / D (or factory track equivalent) |
| Which **parent step** is it most related to? | e.g. “mostly Step 2” |
| **Before or after** which sibling? | e.g. after A2.1, before A2.2 |
| **Cross-cutting?** | If yes — split into sub-steps under **each** parent (e.g. A2.1.1 + A5.3.1) |
| **New top-level step?** | Only if no parent fits — rare; needs stronger convince |

**Default:** insert under related parent as **sub-step**, not new top-level phase.

---

## 7. Sub-step insert rules (Order 9)

### 7.1 Pattern (Rules 1–5 same, Rule 6 new)

```text
Locked source:     Step 1 · Step 2 · Step 3 · Step 4 · Step 5
New suggestion:    Rule 1–5 align · Rule 6 new (mostly related to Step 2)

After convince + placement:
                   Step 1 · Step 2 · Step 2.1 (NEW) · Step 3 · Step 4 · Step 5
```

Parent steps **keep IDs and content**. Only the **insert** gets a new ID.

### 7.2 ID conventions (WTM / technical tracks)

| Pattern | When | Example |
|---------|------|---------|
| **`X.Y.Z`** (third level) | Sub-step **inside** build gate of X.Y | A2.1.1 under A2.1 |
| **`X.Yb` / `X.Y.1`** | Sibling **between** X.Y and X.{Y+1} | A2.1b between A2.1 and A2.2 |
| **`X.{n+1}` new letter block** | New sub-phase under same hub phase only if many inserts | A2.3 after A2.2 (full gate, not sub-module) |

**Stable law:** Existing `D1`, `C1`, `B4`, `A1.1` etc. **never renamed** to “match” phase letters.

### 7.3 Three locked placement examples (WTM)

**Example A — Query Expansion (chat Rule 6 → mostly Step A2.1/A2.2)**

```text
Before:  A2.1 Vector Retrieval → A2.2 Graph Reasoning
Placed:  A2.1 → A2.1b Query Expansion v1 → A2.2
Why:     Same sub-phase A2; expands retrieval before graph queries
```

**Example B — Memory + Logs + Git (cross-cutting)**

```text
Before:  A2.1 … A5.3 only as architecture zones
Placed:  A2.1.1 memory/git read bridge (under A2.1)
         A5.3.1 unified memory into packet (under A5.3)
Why:     Feeds retrieval and assembly — not step 11 between A4.2 and A5.1
Alt:     If one gate needed: A4.3 sibling — only with founder v3 lock
```

**Example C — Graph Fusion (architecture extra → mostly Step A1.1/A1.2)**

```text
Before:  A1.1 Code Intelligence → A1.2 Dependency Graph
Placed:  A1.1 → A1.1.1 Graph Fusion v1 → A1.2
Why:     Unified AST+call+import substrate before dependency impact graph
```

Full worked compare (13 vs 12): `archive/attachments/examples/wtm/CHATGPT_13STEP_WTM_REVIEW_EXAMPLE_LOCKED_v1.md`

---

## 8. Upgrade source vN+1 (Order 10)

When Orders 7–9 complete:

1. Draft `*_LOCKED_v{N+1}.md` with inserted sub-steps in build order table  
2. Update builders (`system_roadmap.py`, etc.) — `STEP_CATALOG`, journey, hub strings  
3. `mv` vN → `archive/superseded/<track>/vN/`  
4. Append `ARCHIVE_MANIFEST` row — evidence: convince date, placement memo, new IDs  
5. `python3 scripts/build-sina-command-panel.py`  
6. Verify hub Future column / swimlanes show new sub-step in **correct parent column**

**Attachments alone never trigger Order 10.**

---

## 9. Attachments vs sub-steps

| Stage | Location | Canonical? |
|-------|----------|------------|
| Unconvinced extra | `archive/attachments/<track>/` | No |
| Convinced, placement draft | Same attachment + placement memo | No |
| After vN+1 lock | Master map vN+1 + hub payload | **Yes** |
| Learning record | `archive/attachments/examples/` | No |

---

## 10. Agent forbidden (whole system)

| Forbidden | Why |
|-----------|-----|
| Chat paste as SOURCE | Inversion |
| Replace Step 2 with Rule 6 | Drift — use Step 2.1 |
| Skip convince gate → hub insert | Unauthorized build order |
| Top-level step from chat without placement | Messy phases |
| Rename stable step IDs for aesthetics | INCIDENT-003 |
| Agent analysis tables in founder UI | INCIDENT-002 |
| vN+1 without archive vN | No evidence trail |

---

## 11. Checklist (Order 12 — verify)

- [ ] Source vN identified  
- [ ] Compare + classify complete  
- [ ] Plan kept; drift rejected  
- [ ] Unconvinced extras → attachment only  
- [ ] Convinced extras → placement memo + sub-step IDs defined  
- [ ] Parent steps unchanged  
- [ ] vN archived; vN+1 at root  
- [ ] `scripts/system_roadmap.py` + `PAYLOAD_VERSION` updated  
- [ ] `python3 scripts/build-sina-command-panel.py` → `audit_hub_source_alignment.py` **OK**  
- [ ] Hub matches vN+1 (see `HUB_SOURCE_UI_ALIGNMENT_PROCEDURE_LOCKED_v1.md`)  
- [ ] Example/analysis in `examples/` if useful  

---

## 12. Track pointers (today)

| Track | Current SOURCE | Manifest |
|-------|----------------|----------|
| World Target Model | `WORLD_TARGET_MODEL_MAP_LOCKED_v5.md` | `archive/superseded/wtm/ARCHIVE_MANIFEST_LOCKED_v1.md` |
| WTM separation | `WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v2.md` | — |
| This law | **This file** | — |
| External critic handling | `CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md` | — |
| Governance router | `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md` | — |
| Authority index | `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` | — |

---

**LOCKED — COMPLETE RULE ORDER:**  
**Compare → Keep → Attach → Convince → Place → Sub-step → Upgrade → Verify.**  
Whole system. Never drift.
