# ENFORCE bypass map (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0  
**Date:** 2026-06-06  
**Authority:** Founder ASF + maintainer  
**Parent:** `COUNCIL_BRIEF_STRATEGIC_SLICE_EVAL_L0_ENFORCE_LOCKED_v1.md`  
**Hub surface:** `/api/gate-receipts-v1` · WTM gate receipts panel

---

## Purpose

ENFORCE blocks hub OpenRouter dispatch when `gate_eligible` is false. This map documents **every ingress path** so founders and agents know what is gated vs bypassed.

---

## Bypass map

| Route | ENFORCE applies? | Notes |
|-------|------------------|-------|
| `agent_loop` planner dispatch | **Yes** | Primary choke — `model_dispatch.prepare_packet` → validate → allow/block |
| Hub Advisor / OpenRouter via `loop_advisor` | **Partial** | Uses vault key; separate from planner gate receipts |
| Intelligence circle live agents | **Partial** | Per-agent session; not packet-gated today |
| Cursor IDE (local) | **No** | Direct model access outside hub — founder law |
| Spine / `execution_router` | **No** | Executes after human or planner confirm; `dispatch_ready: false` |
| Refresh / build scripts | **No** | Local validators; no model ingress |
| SEMEJ browser chain | **No** | External Chrome AIs — compare only |
| Pre-LLM D1–D16 assembly | **No** | No LLM; produces packet only |

---

## Receipt logs

| Log | Path |
|-----|------|
| ENFORCE blocks | `~/.sina/gate_enforce_v1.jsonl` |
| SHADOW would-block | `~/.sina/gate_shadow_v1.jsonl` |
| Gate SSOT | `~/.sina/model_dispatch_gate_v1.json` |
| Mode pref | `~/.sina/gate_mode_v1.txt` or `SINA_GATE_MODE` |

---

## Transparency rule

When a lane touches OpenRouter outside the planner choke, agents **must** note bypass awareness in Mind Share / Scoreboard — not claim full ENFORCE coverage.

---

## Next (after Eval-1b)

Dispatch policy assigns auto-execution classes only when behavioral proof passes — see Phase 2 in `STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md`.
