# Forge Mission — 6000 plans + Cursor observer law (LOCKED v1)

**Saved at:** 2026-06-25T11:00:00Z  
**Master:** `brain-os/plan-registry/FORGE_MISSION_6000_MASTER_v1.json`  
**Visual contract:** `data/forge-visual-parity-contract-v1.json`  
**Online demo:** https://sourcea.app/sourcea/forge/terminal  
**Local desk:** `http://127.0.0.1:13029/` · Chat Unify `http://127.0.0.1:13023/`

---

## One law

> **6000 plans build Forge Terminal (local + online) and Chat Unify to sourcea.app visual grade. Pre-LLM Mac RAW AI executes. Cursor observes and facilitates — never the worker body.**

---

## 6000 pack map

| Pack | Plans | Prefix | Path | Role |
|------|------:|--------|------|------|
| **Shared spine** | 2000 | `sa-score` + `sa-score2` | `sourcea-site-score-up-1000*` | Site · proof · pulse · routing — **both apps inherit** |
| **Forge Terminal** | 2000 | `ft-score` | `forge-terminal-score-up-1000/` | Local `:13029` + online `/sourcea/forge/terminal` |
| **Chat Unify** | 2000 | `cu-score` | `chat-unify-score-up-1000/` | Mac `:13023` + DMG shell |
| **Total** | **6000** | | | |

Shared spine = proof-native GTM + receipts + pulse. App packs = **visual parity + living UI + pre-LLM pipeline**.

---

## Three surfaces · one spine

```
                    ┌─────────────────────────────────────┐
                    │  Shared spine (2000 sa-score*)      │
                    │  proof · pulse · vocabulary · SEO   │
                    └──────────────┬──────────────────────┘
           ┌───────────────────────┼───────────────────────┐
           ▼                       ▼                       ▼
   sourcea.app              Forge Terminal            Chat Unify
   /forge/terminal          :13029 + apps/            :13023 + standalone
   (public demo)            forge-terminal-v1/        scripts/chat-unify-*
```

**Rule:** Any spine plan that touches Forge MUST ship on **both** local IDE and online demo in the same release train.

---

## Who builds (non-negotiable)

| Role | Actor | May do |
|------|-------|--------|
| **Worker** | Pre-LLM Mac RAW AI | `POST /api/forge-terminal/v1` · `POST /api/chat-unify` · cloud `:13027` dispatch · file edits via controlled run |
| **Observer** | Cursor agent | Read disk · pick plan · paste WORK order · verify receipt · unblock founder · **no implement body** |
| **Facilitator** | Cursor agent | Route plan → RAW AI · sync REGISTRY status · run light E2E ≤90s · update mission manifest |
| **Founder** | Human | Approve scope · one-tap dispatch · taste judgment |

Cursor **forbidden:** multi-file implement loops · validator marathons · pretending to be the factory body.

---

## Visual parity target

Both apps must match **sourcea.app** v2 design system:

- Fonts: Plus Jakarta Sans + Inter + JetBrains Mono (see `sourcea.css`)
- Header: `ar-header` · `ar-btn` · `sa-btn-glow` patterns
- Dark shell: `--ft-*` tokens aligned to site `--sa-*`
- Proof CTA: **See live receipt** primary · Cal = fallback only
- Online demo must not look like a separate product skin

Contract: `data/forge-visual-parity-contract-v1.json`

---

## Execution loop (smooth)

1. `python3 scripts/pick_forge_mission_plan_v1.py --surface forge --phase NOW --json`
2. Facilitator pastes plan into Forge Terminal / Chat Unify (RAW AI turn)
3. RAW AI implements bounded path · returns receipt
4. Facilitator marks `status: done` + `built_by: pre-llm-mac`
5. Light verify: `python3 scripts/forge_terminal_living_ui_e2e_verify_v1.py` (≤90s)
6. Deploy online: build script → `wrangler pages deploy` for `/forge/terminal` only when plan tags `surface: online`

---

## Phase law (all 6000)

| Phase | Per pack ranks | Mission focus |
|-------|----------------|---------------|
| NOW | 1–60 | Visual parity P0 · online/local sync · kill mailto on forge demo |
| NEXT | 61–220 | Living UI · quality gate · mesh · integrations |
| LATER | 221–550 | Swarm · civilization · enterprise |
| MOONSHOT | 551–1000 | Moat · research |

---

## Score target

| Surface | Now | After NOW packs | After full 2000 |
|---------|-----|-----------------|---------------|
| Online Forge Terminal | ~58 | ~78 | ~92 |
| Local Forge IDE | ~62 | ~80 | ~93 |
| Chat Unify | ~55 | ~75 | ~90 |
| Site + apps combined | 78 | ~88 | **93+** |

---

## Commands

```bash
# Generate all app packs
python3 scripts/generate_forge_terminal_score_up_1000_plans_v1.py
python3 scripts/generate_chat_unify_score_up_1000_plans_v1.py
bash scripts/validate-forge-mission-6000-v1.sh

# Pick next work
python3 scripts/pick_forge_mission_plan_v1.py --surface forge --phase NOW
python3 scripts/pick_forge_mission_plan_v1.py --surface chat-unify --phase NOW
python3 scripts/pick_forge_mission_plan_v1.py --surface spine --phase NOW
```

---

## Priority NOW (first 5 across packs)

1. `ft-score-0001` — Shared `forge-visual-parity-contract-v1.json` wired into local + online CSS
2. `ft-score-0002` — Online demo header matches `founder-home` ar-header
3. `cu-score-0001` — Chat Unify shell imports site design tokens
4. `sa-score-0001` — Stranger proof run API (spine)
5. `ft-score-0031` — Online feedback form → pulse not mailto
