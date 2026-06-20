# Healthy Drain — Prompt Feasibility / OpenRouter Step-2 Incident (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — FINAL LOCKED  
**sequence_id:** SA-2026-06-07-INCIDENT-002  
**Classification:** INTERNAL — MANDATORY READ for Brain · Worker · executor autoloop  
**Canonical location:** `/Users/sinakazemnezhad/Desktop/SourceA/SINA_HEALTHY_DRAIN_PROMPT_FEASIBILITY_INCIDENT_REPORT_LOCKED_v1.md`  
**Incident window:** 2026-06-07 (founder: “why is step 2 OpenRouter when we don’t have it?”)  
**Maintainer:** ASF · Brain executor documents; founder is law editor  

---

## 1. Executive summary

Brain injected **Goal 1 healthy drain step 2 (ACT)** bound to **sa-0129**: “Verify `eval_1b_gate_ok` true in `/api/dispatch-policy-v1`”. That requires **live Eval-1b / OpenRouter credits**, which the founder **does not have**. Step 2 was therefore **impossible** — Worker correctly stopped; founder lost trust in the loop.

**Severity:** **High** — breaks semi-auto REGISTRY drain; wastes turns; feels like Brain “not thinking.”

---

## 2. Root causes

| # | Cause |
|---|--------|
| 1 | `generate-healthy-prompt-pack-v1.py` built queue from **live pick order** without **feasibility filter**. |
| 2 | Brain treated “REGISTRY pick 1” = “runnable step 2” without checking **commercial blockers**. |
| 3 | Executor autoloop preamble **mentioned OpenRouter** on ACT turns instead of **excluding** blocked sa. |
| 4 | No mechanical gate at **front door** (entry gate / mandatory handoff) before inject. |

---

## 3. Founder expectation violated

- **Step 2 must be doable on disk** with validators the repo already has.
- **Never inject** OpenRouter, live eval, or `eval_1b_gate_ok: true` as an ACT requirement when credits are absent.
- If a sa is commercial-blocked, **skip or defer** — do not stop the loop on impossible work.

---

## 4. Fixes shipped (2026-06-07)

| Layer | Fix |
|-------|-----|
| Mechanical gate | `scripts/prompt_feasibility_gate.py` — blocks impossible prompt text |
| Entry gate | `cursor_entry_gate.py` runs feasibility; prints `FEASIBILITY_BLOCKED` on ACT/inject |
| Front door | `.cursor/rules/000-entry-gate.mdc` — feasibility mandatory before reply/inject |
| Worker mandatory | `MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md` §PROMPT FEASIBILITY GATE |
| Brain mandatory | `MANDATORY_BRAIN_CHAT_LOCKED_v1.md` — feasibility before Worker handoff/inject |
| Achievable pack | `~/.sina/build-achievable-healthy-queue.py` — skips OpenRouter/live-eval sa |
| Autoloop | `~/.sina/healthy-drain-autoloop.py` — uses achievable queue; forbids live-eval in paste |

---

## 5. Mandatory rule (never again)

**Before every inject, handoff, or ACT turn:**

1. Run `python3 scripts/prompt_feasibility_gate.py --role worker --strict`
2. If `action: STOP_INJECT` → rebuild achievable pack or advance pick — **do not paste**
3. ACT step must pass feasibility on **queue item + live pick** title/instruction/verify
4. VERIFY may document honest `eval_1b_gate_ok: false` — must not require live pass to proceed pack

**Line test:** Would a Worker with **no OpenRouter** finish this step with disk validators only? If no → **not injectable**.

---

## 6. Status

| Item | Status |
|------|--------|
| Incident documented | LOCKED |
| Gate wired | ACTIVE |
| sa-0129 defer | done — pick advanced to sa-0130 |
| Achievable 30-pack | ACTIVE at `~/.sina/healthy-queue-30-active.json` |

---

*End incident report*
