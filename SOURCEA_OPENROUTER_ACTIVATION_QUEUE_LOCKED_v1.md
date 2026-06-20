# SourceA — OpenRouter Activation Queue (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-13-OPENROUTER-ACTIVATION-QUEUE  
**Parent:** `SOURCEA_PHASE_STRICT_RUN_INBOX_LOCKED_v1.md` · `DISPATCH_POLICY_LOCKED_v1.md`  
**Machine:** `~/.sina/build-phase-strict-queue-v1.py` · `~/.sina/phase-strict-drain-v1.json`

---

## Law (one sentence)

**Phase-strict queue runs s1 OpenRouter activation first, then s7 tail, then s9 — ACT turns on s1 pack may use live eval; all other packs stay disk-only.**

---

## Order (headless drain)

| # | Pack | SAs | OpenRouter on ACT? |
|---|------|-----|-------------------|
| 1 | **s1-OR-P1** | sa-0101 · 0102 · 0104 · 0106 · 0110 · 0115 | **YES** (live eval / gate proof) |
| 2 | **s7-P3 tail** | sa-0798 … sa-0800 | NO |
| 3 | **s9-P1…P5** | sa-0951 … sa-1000 (minus blocked) | NO (research defer) |

**Skip unchanged:** s2 · s3 · s8 hub · s4/s5/s6 founder lanes.

---

## Activation definition (not hub dispatch_ready)

| Step | Proof |
|------|--------|
| Live eval PASS | `validate-eval-packet-v1b-live.sh` |
| Policy gate | `eval_1b_gate_ok` in `/api/dispatch-policy-v1` |
| Model gate | `~/.sina/gate_mode_v1.txt` — shadow → enforce only after live PASS |
| Orchestrator | `dispatch_ready` = **`orchestrator_dispatch_ready()`** when eval live + enforce + tier pass |

---

## Chat context (governance)

When founder references **yesterday / this thread / fragmentation fix**, Governance Specialist reads:

`~/.sina/governance-chat-context-v1.json` → transcript pointer — **input only**, not authority.

---

**END LOCKED**
