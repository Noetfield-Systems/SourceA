# Council Brief — Strategic Slice (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0  
**Issued:** 2026-05-27  
**Authority:** Founder professional verdict (ASF)  
**Hub (archive):** legacy `/legacy/` Council Room · Track — **not daily**  
**Daily:** Cursor Worker chat RUN INBOX · optional Worker Hub `http://127.0.0.1:13020/`  
**Scope:** Founder · **TrustField Technologies** · **AI Dev Bridge OS**  
**Supersedes:** Ad-hoc GPT/Claude architecture paste as operational law

---

## 0. One-line verdict

**GPT and Claude are aligned and mostly correct on architecture and gaps; they are unreliable on operational state and silent on governance/rules (half the system).**  
**Next move is NOT another D-module** — ship **Eval-1 + L0/L1 slice + ENFORCE coverage transparency**, while keeping the **rules-in-charge loop** so agents never invent parallel law from critic paste.

---

## 1. What external critics got right (trust architecture)

| Claim | Physical evidence | Verdict |
|-------|-------------------|---------|
| Pre-LLM packet compiler (D1–D16) is real | `pre_llm/context_assembly/assembly_engine.py`, `~/.sina/llm_context_packet_v1.json` | **Correct** |
| Runtime C1–C7 exists but dispatch is disabled | `dispatch_ready: False` in `orchestrator_engine.py`, `router_engine.py` | **Correct** |
| D5 retrieval is token overlap, not embeddings | `pre_llm/vector_retrieval/query_engine.py` line 1 | **Correct** |
| Eval-1 is structural only | `eval_packet_v1/runner.py` — no live LLM | **Correct** |
| No physical `event_bus.py` | 0 files in repo; docs only | **Correct** |
| Execution is host subprocess, not sandbox | `execution_spine/executor.py` | **Correct** |

---

## 2. What external critics got wrong or omitted (do NOT paste as law)

| Gap | Reality in SourceA |
|-----|-------------------|
| **Operational state** | Gate mode, L0/L1 done status, Eval-1 report, WTM `do_now` live in `system_roadmap.py` + hub Refresh — critics often stale |
| **Governance / rules (≈50% of system)** | Council Room brief, rules-in-charge (`agent_rules_in_charge.py`), supersession law (`AGENT_RULES_IN_CHARGE_LOCKED_v1.md`), 8-agent fleet policy, edit lock, critic law |
| **Founder never uses Terminal** | Spine + Actions + maintainer agent run shell; hub Refresh is founder control plane |
| **Phase B frozen** | Post-exec intelligence capstone at B6 — learning bias only, not planning truth |
| **Cursor IDE bypasses ENFORCE** | `model_dispatch` chokes hub OpenRouter paths; direct Cursor API is outside gate today |

**Law:** `CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md` — external paste = **compare only**, never new `.mdc` rules without supersession check.

**SSOT trust order:** ~/.sina + validators > hub Refresh > external chat (GPT/Claude paste = compare only — `CHATGPT_EXTERNAL_CRITIC_LAW_LOCKED_v1.md`).

---

## 3. Strategic slice — the only approved next build (not L8, not new D17)

### Workstream A — Eval-1 (structural sustain)

- **Now:** `validate-eval-packet-v1.sh` PASS; `~/.sina/eval_packet_v1_report.json`; hub **Eval-1 panel** (`/api/eval-packet-v1`)
- **Maintain:** ≥80% packet wins on readiness_score / gate_eligible — **no live LLM**
- **Does not unlock dispatch:** structural proof only; critics must not treat Eval-1 pass as behavioral outcome proof

### Workstream A2 — Eval-1b (behavioral proof)

- **Now:** `validate-eval-packet-v1b.sh` PASS (scaffold arm); `~/.sina/eval_packet_v1b_report.json`; hub **Eval-1b panel** (`/api/eval-packet-v1b`)
- **Scaffold arm:** keyword + grounding + composite proxy — runs on every strict build (no OpenRouter)
- **Live arm:** LLM A/B on `live_pilot` tasks — `eval_1b_gate_ok=true` only when live ≥80% **and** scaffold_ok; blocked today on OpenRouter HTTP 402 (structural CI honest)
- **Unlocks:** dispatch policy gate receipt — **not** hub `dispatch_ready` (founder law stays false until Phase 3 council update)

### Eval-1 vs Eval-1b — comparison (do not conflate)

| Dimension | **Eval-1** (structural) | **Eval-1b** (behavioral) |
|-----------|-------------------------|---------------------------|
| **Question** | Does assembled packet beat empty template on gate readiness? | Does packet context beat raw prompt on task outcome (scaffold proxy + live LLM)? |
| **Runner** | `scripts/eval_packet_v1/runner.py` | `scripts/eval_packet_v1b/runner.py` |
| **Live LLM** | **Never** — scores `validate_packet` / assembly only | Scaffold: no · Live arm: OpenRouter on pilot tasks |
| **Win metric** | `readiness_score`, `gate_eligible` | Scaffold: `composite` (keywords + grounding + actionability) · Live: pilot A/B wins |
| **Threshold** | 80% packet wins | Scaffold: 70% · Live pilots: 80% |
| **Report** | `~/.sina/eval_packet_v1_report.json` | `~/.sina/eval_packet_v1b_report.json` |
| **Validators** | `validate-eval-packet-v1.sh` | `validate-eval-packet-v1b.sh` + `validate-eval-packet-v1b-grounding.sh` + `validate-eval-packet-v1b-live.sh` (skip honest on 402) |
| **Dispatch gate** | Informational — sustains slice | `eval_1b_gate_ok` from `policy_engine.eval_1b_gate_status()` |
| **Hub `dispatch_ready`** | N/A — always false at hub | N/A — always false at hub (Phase 3) |

**Law:** Eval-1 PASS does not substitute for Eval-1b live pass. Both run on build; hub shows both panels. Machine truth: `/api/dispatch-policy-v1` + `SOURCEA-PRIORITY.md`.

### Workstream B — L0/L1 (user + workspace signals)

- **Now:** `pre_llm/user_signals/`; hub touch → `user_signals_v1.json` + `workspace_state_v1.json`; wired into `packet.workspace`
- **Slice goal:** Deepen MVP — richer hub Refresh signals, stable SSOT, panel green on WTM
- **Explicitly NOT in slice:** Full editor cursor/keystroke telemetry (L0-full) — backlog

### Workstream C — ENFORCE coverage transparency

- **Now:** Gate mode = machine `~/.sina/gate_mode_v1.txt` + `/api/dispatch-policy-v1` `gate_mode` (shadow today); `model_dispatch.dispatch_chat` blocks ineligible packets when enforce
- **Slice goal:** Published **bypass map** — which ingress paths are gated vs bypassed (hub planner, advisor, Cursor IDE, maintainer scripts)
- **Artifacts:** `gate_receipts_hub.py`, `/api/gate-receipts-v1`, WTM gate receipts panel
- **Law:** ENFORCE does not mean "every LLM call everywhere" — honesty in hub UI

### Workstream D — Rules-in-charge loop (parallel, never dropped)

- **Every agent round:** `agent_rules_loop_orchestrator.py` → `validate-agent-rules-in-charge-v1.sh`
- **Before ship:** pre_ship phase + no duplicate `.mdc` without supersession
- **Receipts:** `~/.sina/agent_rules_loop_receipt_v1.jsonl`
- **Agents must NOT:** Convert GPT/Claude architecture essays into new locked law without maintainer + ASF review

---

## 4. Lane obligations (TrustField · AI Dev Bridge · Hub edit)

| Agent | Lane | Obligation under this brief |
|-------|------|------------------------------|
| **Founder (ASF)** | All | Read Council brief once per session; Track cards stay open until hub projection proves done |
| **TrustField** | THREAD-PORTFOLIO | Align lane work to infra/law truth (B-001, GLOBAL_BLOCKERS) — **no** SourceA D-module builds; attest council brief on Scoreboard |
| **AI Dev Bridge OS** | THREAD-WIRE | Wire G1/G2/G3 evidence via Actions/spine — **no** new pre-LLM modules; report gate bypass awareness in Mind Share if wire touches models |
| **SinaaiDataBase workspace** | SourceA hub code | Ship slice validators + hub panels + this brief; run shell; rebuild hub; **never** ask founder for Terminal — **not** a scoreboard agent |

---

## 5. Acceptance criteria (slice = done)

1. Eval-1 validator PASS + report artifact present + hub panel shows latest run  
1b. Eval-1b scaffold validator PASS + `scaffold_ok=true` + hub Eval-1b panel; live arm honest when 402 (`eval_1b_gate_ok=false`)  
2. L0/L1 validator PASS + user/workspace SSOT present + hub panel shows touch/live state  
3. Gate receipts API + panel show enforce mode + shadow/enforce log counts  
4. ENFORCE bypass map doc section live in hub (gate receipts or WTM attachment)  
5. Rules-in-charge validator PASS + loop receipt appended on maintainer preflight  
6. WTM `do_now` reflects **Strategic slice** (not L8 embeddings as primary)  
7. Council topic advisory vote open; Mind Share procedure posted by maintainer  

---

## 6. Explicitly deferred (do not start until slice closes)

- L8 full embedding index + hybrid D9 ranking  
- New D-modules (D17+)  
- C7 auto-dispatch / `dispatch_ready: true`  
- Eval-1b **live** pass (`eval_1b_gate_ok=true`) — scaffold CI shipped; blocked on OpenRouter credits until restored  
- `event_bus.py` implementation  

---

## 7. Hub surfaces (founder — Refresh only)

| Tab | What to check |
|-----|----------------|
| **Council Room** | This brief + whole-system copy brief + rules in charge (gold) |
| **Command → WTM** | `do_now` = Strategic slice; Eval-1 + Eval-1b / L0 / Gate panels |
| **Track** | Three commitment cards pinned for slice |
| **Agent hub** | Private page → vault → Scoreboard attest **Council brief read** |

---

## 8. Copy block for agents (paste once per chat)

```
STRATEGIC SLICE (LOCKED) — Founder verdict 2026-05-27
Next: Eval-1 structural sustain + Eval-1b behavioral scaffold/live + L0/L1 deepen + ENFORCE bypass transparency.
NOT: new D-module, NOT L8 primary.
Governance: rules-in-charge loop every round; GPT/Claude arch = compare only.
Lanes: TrustField + AI Dev Bridge align lane work; maintainer ships hub-side.
Hub: Council Room → this brief · Track → commitment cards · Refresh.
Doc: COUNCIL_BRIEF_STRATEGIC_SLICE_EVAL_L0_ENFORCE_LOCKED_v1.md
```

---

**END — LOCKED v1**
