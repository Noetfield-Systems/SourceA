# Wire lane progress — single checklist (ASF)

**ASF daily routine:** `founder/ASF_DAILY_CARD.md` (5 commands) · index `founder/README.md`

**FORCE MAJEURE:** `SINAAI_FAST_TRACK_FORCE_MAJEURE_LOCKED_v1.md` — **NO WAIT. NO BLOCK. GO.**

**Law:** Repo blockers do **not** stop this list.

**Ports:** `PORT_NOTICE_BOARD.md` — desk **3004+** only.

---

## Done

- [x] G1 — `npm run verify:g1` → probe only (no Cursor spam)
- [x] Desktop G2 wire — `npm run smoke:g2:iphone` PASS
- [x] Physical iPhone G2 smoke — RUN SYSTEM PASS + recorded
- [x] Ports — 3000–3003 blocked for DevBridge
- [x] `wire.record_physical_g2` + Record on Mac one tap
- [x] `full_m8` lane in orchestrator + desk lane picker
- [x] `cursor.dispatch_repo` (M8 per-repo Agent)
- [x] Desktop `full_m8` proxy — `npm run smoke:g2:full-m8` PASS
- [x] `npm run wire:preflight` — code checklist

## Open (wire — ASF only)

- [ ] **full_m8 on iPhone** — `npm run proof:iphone-production` → RUN SYSTEM → log NOT `smoke: complete` only
- [ ] Record full_m8: `--lane full_m8` or one tap after full_m8 PASS
- [x] **G3 Tailscale** — `run_2026-06-04T00-16-55Z` on `100.85.10.79` → `record:g3` pass (2026-06-15)

## Not required for P2 (parallel)

- VIRLUX Railway deploy
- Mono Phase 0 exit
- 777 Supabase SERVICE_ROLE
- Noetfield spec section 3
- TrustField postgres (helpful but **does not** gate wire)

---

**Health:** `cd ~/Desktop/AI\ Dev\ Bridge\ OS && npm run verify:health`  
**Preflight:** `npm run wire:preflight`  
**Production URL:** `npm run proof:iphone-production`  
**M8 UI paste:** LOCKED — read `SinaPromptOS/docs/M8_INCIDENT_2026-06-03_LOCKED.md`  
**Safe:** `dispatch-day` manual paste · phone `full_m8` · `m8-paste-one-repo.sh` (one repo only)  
**G3:** `npm run proof:g3` (after Tailscale on Mac + iPhone)  
**M6 (optional, after wire green):** `cd ~/Desktop/SinaPromptOS && ./scripts/install-m6-launchd.sh`
