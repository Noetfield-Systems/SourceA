# Orchestra reactivation — post s5 (LOCKED v1)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14  
**ASF intent:** Finish **s5 commercial** first · then reactivate **orchestra + OpenRouter + n8n**  
**Authority:** `~/.sina/phase-strict-drain-v1.json` · `SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md`

---

## Now vs after s5

| Layer | Now (during s5) | After s5 complete |
|-------|-----------------|-------------------|
| Factory drain | **s5-P1..P10** (95 backlog) | Pause registry drain · switch to orchestra mode |
| OpenRouter gate | **enforce** (live) | Same — planner choke active |
| Eval-1b / dispatch policy | **gate_ok** · spine bridge ready | Founder spine Action + low-risk enqueue |
| Runtime orchestrator | idle · `dispatch_ready=false` | Refresh stack · bounded loop activation |
| n8n | **standby** (not blocking s5) | Hub **Start n8n** → starter test |
| Goal1 orchestrator | healthy-drain · SINGLE_SA | **activate loop** with SYNC chain |

---

## Phase gate — do not start orchestra until

- [ ] **s5 commercial:** 100/100 done (currently **5/100**)
- [ ] **critical_count:** 0 (`find_critical_bugs`)
- [ ] **broker cycle:** PASS on honest done rows
- [ ] **FREEZE:** cleared on H1 for bounded resume

---

## Cycle 3 sequence (founder one-tap)

### Step 1 — Commercial closeout proof
- Valid YES reflects s5 receipts
- RunReceipt / TrustField / MergePack validators green
- `goal-progress-v1.json` shows s5 **100%**

### Step 2 — OpenRouter (already armed)
| Check | Disk |
|-------|------|
| Gate mode | `~/.sina/gate_mode_v1.txt` = **enforce** |
| Eval live | `eval_packet_v1b_report.json` · 5/5 @ 100% |
| Policy | `dispatch_policy_v1.json` · `eval_1b_gate_ok: true` |

No flip needed — verify only after s5.

### Step 3 — Orchestra (runtime + Goal1)
1. Hub **Refresh** (build) — orchestrator + graph_executor payloads refresh
2. **Spine bridge Action** — eval proof via `spine-smoke-echo` (founder confirm)
3. **Activate loop** or bounded **RUN INBOX** — Brain poll · Worker · orchestrator SYNC

**Law:** `orchestrator dispatch_ready` stays **false** at hub top-level until Phase 3 council brief — bridges run via graph_executor + founder confirm, not silent auto.

### Step 4 — n8n glue
Per `SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md`:

1. Hub → **Automation & n8n** → **Start n8n** (`http://127.0.0.1:5678`)
2. **Run n8n starter test** (hub API alive · runtime :8000 · liaison status)
3. Import workflow: `~/Desktop/SinaaiMonoRepo/n8n/workflows/sinaai-telegram-agents.json`
4. **One Telegram listener only** — disable built-in bot before n8n Telegram path

n8n = **external glue** · never SSOT for SourceA law or Cursor prompts.

### Step 5 — Smoke proof
- `validate-spine-bridge-proof-matrix-v1.sh` PASS
- n8n starter test PASS
- One full Goal1 loop round: INJECT → ACTIVATE → VALIDATE → SYNC

---

## What stays forbidden (even after s5)

- n8n as brain for five-repo ranking or prompt SSOT
- `dispatch_ready: true` at orchestrator without council brief update
- Parallel Telegram listeners (n8n + runtime bot)
- s8 hub-ui drain while hub archived (no-hub latch)
- 24×7 unattended factory without bounded founder resume

---

## s5 remaining work (current focus)

| Pack | SAs | Status |
|------|-----|--------|
| P1 | sa-0502–0511 | **in progress** (sa-0502 done) |
| P2–P10 | sa-0512–0597 | queued after each pack PASS |

**Head:** sa-0503 CHECK (TrustField FR-007) · **829/1000** honest

---

## Related docs

- `SOURCEA_PHASE_PLAN_REANALYSIS_LOCKED_v1.md`
- `NEXT_FACTORY_CYCLE_ORGANIZED_LOCKED_v1.md`
- `DISPATCH_POLICY_LOCKED_v1.md` Phase 2b
- `GOAL1_LOOP_ACTIVATION_CHAIN_LOCKED_v1.md`

---

*End ORCHESTRA_REACTIVATION_POST_S5_LOCKED_v1*
