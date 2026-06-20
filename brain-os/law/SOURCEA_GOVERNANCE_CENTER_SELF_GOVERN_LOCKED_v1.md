# SourceA — Governance Center & Self-Govern (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-13-GOV-CENTER-SELF-GOVERN  
**Router:** `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md` §0q  
**Index:** `GOVERNANCE_CENTER`  
**Machine:** `scripts/governance_center_run_v1.py` · `~/.sina/governance-center-receipt-v1.json`

---

## Law (one sentence)

**The system governs itself permanently — Governance Center runs heal · drift · cascade · stairlift · planner · judge · lawyer · thread on machine cadence; founder sees receipts and next-10, not fights in chat.**

---

## 1. Governance Center (three roles — one office)

| Role | Machine | Job | Output |
|------|---------|-----|--------|
| **Planner** | `live_ongoing_prompts_v1.py` | **What to do next** — next 10 queue turns from disk | `~/.sina/live-ongoing-prompts-next-10-v1.json` |
| **Judge** | `judge_center_bench_v1.py` (L3) | RIGHT / STALE / BAD · resolution | `~/.sina/judge-center/latest-resolution-v1.json` |
| **Lawyer** | `judge_center_counsel_v1.py` (L2) | Settle · KEEP/IGNORE · escalate INCIDENT class | `~/.sina/judge-center/latest-counsel-v1.json` |
| **Thread curator** | `thread_room_run_v1.py` | Map THREAD-* arcs · nothing lost T30 | `~/.sina/thread-room/latest-curation-v1.json` |

**Orchestrator:** `python3 scripts/governance_center_run_v1.py --tier fast|full`

**Without Stairlift:** law never reaches Worker · Vinny · fleet — **Stairlift is the broadcast layer** (`governance_stairlift_sync_v1.py` → `~/.sina/governance-stairlift-v1.json`).

---

## 2. Permanent auto-heal (minimum human observation)

| Layer | Script | Cadence |
|-------|--------|---------|
| **G7 self-heal** | `governance_self_heal_daemon_v1.py --heal` | **Hourly** launchd `com.sourcea.g7-governance-self-heal` |
| **Worker turn** | `worker_anti_staleness_heal_v1.py --force` | Every Worker turn entry |
| **Founder intake** | `founder_input_cascade_v1.py` | Every ASF message → 6 layers + receipt |
| **Brain → Governance wire** | `brain_governance_wire_v1.py` | Every Governance Center run + specialist session start |
| **Stairlift HOT** | `governance_stairlift_sync_v1.py --if-stale --tier hot` | Every turn entry (~50ms skip) |
| **Drift score** | `governance_drift_engine.py` | On center run + hub Refresh |
| **Governance Center** | `governance_center_run_v1.py` | Specialist session start · `--tier full` weekly |

**Founder observes:** alarm strip P0–P3 · `governance-center-receipt-v1.json` ok · next-10 head — **not** Terminal.

---

## 3. Raw OpenRouter AI → controlled specialists

```text
OPENROUTER (raw model)
    ↓
model_dispatch.py          ← single choke (off | shadow | enforce)
    ↓
Classify L1                ← ASF order vs EXTERNAL_CRITIC (never auto-build critic)
    ↓
agent-research pipeline    ← intake → brainstorm → evaluate (≥65) → promote
    ↓
Promote target             ← skill_draft | council_topic | deferred
    ↓
agent-skills/<id>/SKILL.md ← specialist contract (governance · coding · search · …)
    ↓
Stairlift + rules loop     ← every surface loads role + mandatory laws
    ↓
Judge Center               ← conflicting chat outputs → Form rows only (Tier 3)
```

| Specialist type | Skill home | Gate |
|-----------------|------------|------|
| Governance | `governance-specialist-in-charge.mdc` + this law | cascade receipt required |
| Coding / Worker | `agent-skills/sourcea_worker/SKILL.md` | broker + receipt VERIFY |
| Search / research | `sina-research-intake` + pipeline | evaluate before promote |
| Brain / route | `agent-skills/sourcea_brain/SKILL.md` | no sa closeout |

**Law:** OpenRouter **never** owns order — `live-ongoing-prompts-next-10-v1.json` and healthy queue do. Next steps direction commentary is optional (L1 input only).

---

## 4. 100-step governance horizon (machine-owned phases)

| Phase | Steps | Owner | Proof |
|-------|-------|-------|-------|
| **G0** | 1–10 | Center | cascade + stairlift + self-heal PASS |
| **G1** | 11–25 | Judge + Lawyer | alarm strip 0 ACTIVE_STALE on hot paths |
| **G2** | 26–45 | Thread + Planner | next-10 always ≤10s stale · THREAD map complete |
| **G3** | 46–65 | Drift engine | aggregate score ≥90 sustained 7d |
| **G4** | 66–85 | Specialist pipeline | every role has SKILL + stairlift surface |
| **G5** | 86–100 | OpenRouter gate | enforce mode + zero bypass on planner ingress |

Detail rows live in `brain-os/plan-registry/` — **Governance Specialist advances G-phase only with validator PASS**, not chat approval.

---

## 5. Forbidden

- Founder fights agent every turn for drift fix  
- “Done” without `governance-center-receipt-v1.json` or cascade receipt  
- New judge **chat** as authority (Judge Center disk only)  
- OpenRouter 10-pack as execution SSOT  
- Chat-only law sync to Worker / Vinny / fleet  

---

**END LOCKED** — authority index `GOVERNANCE_CENTER`
