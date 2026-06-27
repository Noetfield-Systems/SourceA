# Cursor observer — Forge Mission (LOCKED v1)

**Saved at:** 2026-06-25T11:00:00Z  
**Mission:** `docs/FORGE_MISSION_6000_PLANS_LOCKED_v1.md`  
**6000 plans:** site spine + Forge Terminal + Chat Unify

---

## One law

> **Cursor agents OBSERVE and FACILITATE the Forge Mission. Pre-LLM Mac RAW AI is the worker. Cursor does not implement the 6000-plan body.**

---

## Cursor MAY

- Read REGISTRY.json and pick next plan
- Paste `RAW AI WORK — ft-score-NNNN` into Forge Terminal or Chat Unify
- Run light checks ≤90s (`forge_terminal_living_ui_e2e_verify_v1.py`, curl health)
- Update plan `status: done` when RAW AI receipt exists in the repository
- Explain to founder what shipped vs what is blocked
- Route cloud dispatch to `:13027` when Mac law requires

---

## Cursor MUST NOT

- Implement multi-file UI upgrades as Cursor worker body
- Chain validators across turns (INCIDENT-039)
- Pretend chat edits equal factory ship without receipt
- Bypass pre-LLM pipeline (session gate · prompt forge · quality gate)
- Bootstrap heavy factory on Mac without ASF

---

## Worker definition

| Worker | Entry | Output |
|--------|-------|--------|
| **Pre-LLM Mac RAW AI** | `POST /api/forge-terminal/v1` · `POST /api/chat-unify` | File edits + receipt JSON |
| **Cloud body** | `:13027` dispatch · Railway | Factory runs |
| **Founder** | Taste · approve · one-tap | Ship decision |

---

## Facilitator loop (every turn)

1. `python3 scripts/pick_forge_mission_plan_v1.py --surface forge --phase NOW --json`
2. Paste plan title + bounded paths into RAW AI chat
3. Wait for receipt (`~/.sina/forge-plan-receipt-v1.json` or thread meta)
4. Mark REGISTRY done · note `built_by: pre-llm-mac`
5. Reply founder one line: what built · disk path · next plan id

---

## Surfaces in scope

- https://sourcea.app/sourcea/forge/terminal (online)
- http://127.0.0.1:13029/ (Forge Terminal Connect)
- http://127.0.0.1:13023/ (Chat Unify)
- Shared spine: sourcea.app pulse · proof · segments
