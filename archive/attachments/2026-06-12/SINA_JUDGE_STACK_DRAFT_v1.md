# Sina Judge Stack — Draft v1 (awaiting Form PICK)

**Saved:** 2026-06-12T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**trace_id:** `JUDGE-STACK-DRAFT-2026-06-12`  
**sequence_id:** SA-2026-06-12-JUDGE-STACK-DRAFT  
**Status:** DRAFT — **not law** until `Q-JUDGE-STACK-v1` PICK on M1 Canvas  
**Form fork:** `Q-JUDGE-STACK-v1`  
**Parents:** PACK 5 slot A/E · `SOURCEA_LIVE_FOUNDER_DECISION_FORM` · `EXECUTION_AUTHORITY_MAP` · `SINA_AGENT_CONFLICT_ROOM` · INCIDENT-029  
**ASF:** YES file 2026-06-12

---

## 0. One sentence

> **Sina PICK on Form wins all · Disk+validators prove truth · Judge Center (Audit→Lawyer→AI Judge) drafts alarms and remediation onto the Form — chat never wins alone.**

---

## 1. Outer stack (authority — constitution)

| Tier | Judge | Role | 24/7? | Creative? |
|------|-------|------|-------|-----------|
| **1** | **Human (Sina)** | Final PICK · Effect · Confirm on M1 Canvas | No (by design) | Intent |
| **2** | **Disk + Machine** | §ANSWERED · receipts · validator PASS/FAIL · alarm RIGHT/STALE/BAD | Yes | No (enforce only) |
| **3** | **AI Judge Center** | Reason · counsel · remediation prompts → **Form rows only** | Yes (batch) | Yes (bounded) |

**Precedence:** Tier 1 > Tier 2 > Tier 3. Inner AI layers **never** beat disk proof or Form PICK.

**Golden law (unchanged):** Specialists advocate · Brain routes · Validators judge · Spine remembers · **Founder overrides on Form.**

---

## 2. Inner stack (Judge Center pipeline — inside tier 3 only)

| Layer | Role | execution_authority | In → Out |
|-------|------|---------------------|----------|
| **L1 Audit Specialist** | Extract · alarm vs disk · selected chats | **false** | transcripts/machine JSON → `audit_packet.json` |
| **L2 Lawyer** | Counsel · 13-layer · settle · fork draft | **false** | audit packet → `counsel_brief.json` + Form fork draft |
| **L3 AI Judge** | Class · remediation prompt · incident stub | **false** until ASF PICK | counsel brief → judgment draft + agent remediation prompt |

### L1 — Audit Specialist

**Does:** Select chat scope (Gov · Commercial · Worker · Mono `3369d11c` · M2 `74f5ccab` · any ASF-named id) · run tier-2 alarms · cite `FOUND — path` · no verdict.

**Does not:** invent law · reorder build · founder-facing authority.

### L2 — Lawyer

**Does:** `governance_signal_regulator_v1.py` · ACE type · map to form §ANSWERED · try settlement · draft Subject·Question·4 options·Effect for Canvas.

**Does not:** SHIP disk · assign sa · override validator FAIL.

### L3 — AI Judge

**Does:** Case class RIGHT|STALE|BAD|NEEDS_PICK|INCIDENT · write **remediation prompt** for offending agent · append §OPEN_QUESTIONS text for Maintainer SHIP.

**Does not:** replace Form PICK · create LOCKED law without convince gate.

---

## 3. Flow

```text
[Selected chat output]
  → L1 AUDIT (extract + alarm vs disk)
  → L2 LAWYER (settle · fork draft)
       ├─ settled → archive
       └─ unsettled → L3 AI JUDGE (class + remediation prompt)
            → Form row on M1 Canvas
            → Tier 2 validator re-check
            → Tier 1 Sina PICK + Confirm
            → Maintainer SHIP · guilty agent runs remediation prompt
```

---

## 4. Alarm tags (tier 2 — machine)

| Tag | Meaning |
|-----|---------|
| **RIGHT** | Matches form §ANSWERED + receipt |
| **STALE** | Contradicts disk (e.g. open fork list when canvas_open=0) |
| **BAD** | INCIDENT class · scratch UI · false success · chat-only pending |
| **UNPROVEN** | No FOUND path · no validator run |

---

## 5. What Judge Center is NOT

- ❌ A new mega-chat authority  
- ❌ A replacement for M1 Canvas (slot D)  
- ❌ GPT paste reordering build (EXTERNAL_CRITIC compare only)  
- ❌ MonoRepo governance taste (PROVE lane only)

---

## 6. v1 ship plan (Maintainer 2)

| Phase | Deliverable |
|-------|-------------|
| **v1.0** | `judge_center_audit_v1.py` · counsel/bench stubs · Form category ALARM-* |
| **v1.1** | Hub Alarm strip · “Send to Judge Center” on selected chat |
| **v1.2** | Re-audit after remediation · auto INCIDENT stub |
| **v2** | Headless pipeline · Brain routes cases |

**Proposed scripts (names only):**

```bash
python3 scripts/judge_center_audit_v1.py --chats 74f5ccab,3369d11c,e54ddfa8 --json
python3 scripts/judge_center_counsel_v1.py --packet audit.json
python3 scripts/judge_center_bench_v1.py --brief counsel.json --write-form
```

---

## 7. Form PICK block (founder)

```text
ASF: FIVE-STEP — PICK: Q-JUDGE-STACK-v1 APPROVE
Effect:
  Outer: Human(Form) > Disk+Machine > AI Judge Center
  Inner: Audit → Lawyer → AI Judge → Form row only
  No judge chat authority; remediation prompts not chat law
  Maintainer ships v1 scripts + Form ALARM-RIGHT|STALE|BAD categories
```

**Options on Canvas:**

- **A — APPROVE** (recommended) — lock draft as governance attachment · ship v1.0 scripts  
- **B — APPROVE design only** — attachment locked · scripts DEFER post-W1  
- **C — REVISE** — return to Lawyer layer · amend draft before ship  
- **D — REJECT** — keep Form-only office · no Judge Center pipeline  

---

## 8. Cross-links

| Doc | Role |
|-----|------|
| `SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md` | Office ledger |
| `sourcea-system-integrity-100.canvas.tsx` | Human PICK UI |
| `SINA_AGENT_CONFLICT_ROOM_LOCKED_v1.md` | ACE triage |
| `governance_signal_regulator_v1.py` | 13-layer score |
| `MAINTAINER_2_CROSS_CHAT_GOV_COMMERCIAL_INCIDENT_SYNTHESIS_LOCKED_v1.md` | Procedure |
| `SINA_EXECUTOR_IGNORED_M1_INTEGRITY_FORM_CANVAS_INCIDENT_029_LOCKED_v1.md` | Why chat ≠ office |

---

**END DRAFT** — awaiting `Q-JUDGE-STACK-v1` PICK
