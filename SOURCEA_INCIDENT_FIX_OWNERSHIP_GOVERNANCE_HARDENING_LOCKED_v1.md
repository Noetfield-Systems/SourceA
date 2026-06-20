# SourceA — Incident Fix Ownership & Governance Hardening (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-13-INCIDENT-FIX-OWNERSHIP  
**Authority:** ASF — commercial ship · zero governance drift · zero stasis  
**Router:** `SINA_GOVERNANCE_ENTRY_LOCKED_v1.md` §0p  
**Index:** `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` row `INCIDENT_FIX_OWNERSHIP`  
**Related:** `SOURCEA_NO_FAKE_PROGRESS_ENTERPRISE_SHIP_LOCKED_v1.md` · `SOURCEA_RESULT_DRIVEN_DISCUSSION_POLICY_LOCKED_v1.md` · `AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md` · `WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md` · INCIDENT-030

---

## Law (one sentence)

**No incident closes on narrative; every gap gets a law-audit (PASS/FAIL per clause), a fix matrix (role → ship obligation → artifact → validator PASS), and stairlift propagation to every agent before status = remediated.**

---

## 0. ASF imperative (non-negotiable)

| Rule | Law |
|------|-----|
| **No partial blame + move on** | “Worker partly, system partly” without fix rows = **FORBIDDEN closeout** |
| **Law first** | Every incident: table of **LOCKED clauses → PASS or FAIL** — no “partially compliant” |
| **Everyone fixes** | Worker · Maintainer · Specialist · Brain · Machine each get **ship obligations** — not advice |
| **Maintainer is not A** | Maintainer does **not** execute sa turns — Maintainer **wires gates** so Worker cannot bypass law |
| **Result-driven** | Fix = disk artifact + validator PASS — chat acknowledgment = **zero progress** |
| **Commercial** | Buyer must replay proof — same factory law we sell |
| **Zero drift / zero stasis** | Law change → **stairlift** updates all agents in **&lt;5s fast path** — no manual “tell everyone in chat” |
| **Lightest hardening** | Prefer **fail-closed gate** on hot path over new prose |

---

## 1. Stairlift (governance propagation — mandatory)

**Stairlift** = machine path that pushes new/changed law to **every agent surface** without founder Terminal.

| Step | Machine | When |
|------|---------|------|
| 1 | G0 law mtime change detected | Any `*_LOCKED_v1.md` in stairlift watch list |
| 2 | `scripts/governance_stairlift_sync_v1.py --if-stale` | **Every Worker turn entry** · broker submit · governance preflight |
| 3 | `~/.sina/governance-stairlift-v1.json` | Agent banner SSOT — roles + mandatory laws |
| 4 | `agent_rules_loop_orchestrator.py` `phase=founder_rule_change` | Rules-in-charge refresh |
| 5 | `governance_propagation_cascade_v1.py --fast` | Hub cache invalidate + inbox truth (already on Worker closeout) |

**Forbidden:** Announcing law in chat only · updating LOCKED doc without running stairlift · expecting Maintainer to verbally sync Worker.

### 1.1 Agent surfaces (everyone — mandatory recipients)

Stairlift payload **`~/.sina/governance-stairlift-v1.json`** must list every surface below. **No surface may rely on chat to learn law.**

| Surface | Machine id | How law arrives |
|---------|------------|-----------------|
| **Worker** | `worker` · `sourcea_worker` | Turn entry stairlift + rules loop banner + broker gate |
| **Governance specialist** | `governance_specialist` | Preflight stairlift + validator wiring + law audit |
| **Brain** | `brain` · `sourcea_brain` | INBOX route only · stairlift on pickup |
| **Executor** | `executor` | Cursor session · `.cursor/rules/incident-fix-ownership.mdc` + stairlift SSOT |
| **Advisor** | `advisor` | Sina Command Advisor · hub Rules tab cache invalidate |
| **Vinny** | `vinny` | **Named operator surface** — same stairlift payload as fleet; zero chat-only sync |
| **SEMEJ** | `semej` | Chrome chain · read-only law from stairlift SSOT |
| **Portfolio fleet** | trustfield · virlux · ai_dev_bridge_os · noetfield_* · seven77 | Scoreboard agents · session gate reads stairlift |

**Drift = FAIL:** Any surface executing factory work without fresh stairlift fingerprint within the current Worker turn window.

### 1.3 Founder input cascade (ONE intake — mandatory)

**When ASF sends input** (chat · directive · stop phrase) → **one machine path** updates **all layers** — agents do **not** manually apply rules in 10 places.

| Step | Machine | Proof |
|------|---------|-------|
| 1 | `scripts/founder_input_cascade_v1.py` | `--text "…"` or entry gate auto |
| 2 | Latch detect + `sync_all_layers` + INBOX patch | receipt `~/.sina/founder-input-cascade-receipt-v1.json` |
| 3 | `verify_layers()` — latch · stairlift · routing · truth · INBOX · rail | `validate-founder-input-cascade-v1.sh` **PASS** |

**Forbidden:** Founder order in chat only · agent “I updated my rules” without cascade receipt · 10 parallel rule files as SSOT.

### 1.2 Balance tiers (one system — not fragmented)

**One stairlift script, three speeds.** Heavy governance on cold path; sub-second on hot path. No parallel validators for the same truth.

| Tier | When | Budget | What runs |
|------|------|--------|-----------|
| **HOT** | Every Worker turn entry (`--if-stale --tier hot`) | **&lt;200ms** stale · **&lt;50ms** skip | Fingerprint · write payload if law changed |
| **WARM** | Worker closeout cascade on law change | **&lt;10s** once per fingerprint | HOT + rules-in-charge refresh |
| **FULL** | Maintainer preflight · `--deep` validator · law ship | **&lt;20s** once per fingerprint | WARM + hub cascade + standing validators |

**Receipt cache:** Deep validators may reuse PASS from `~/.sina/governance-validator-receipt-v1.json` for **1h** — no re-run broker/factory if wiring unchanged.

**Future (no new docs):** Hub + scoreboard agents read `governance-stairlift-v1.json` on tab open; Maintainer schedules `--deep` weekly; law bumps auto-invalidate receipt via fingerprint.

**Forbidden:** `--force --tier full` on turn entry · stacking duplicate grep validators · 3-minute waits for unchanged law.

---

## 2. Incident response protocol (mandatory)

### 2.1 Open

1. File LOCKED body in `brain-os/incidents/` + row in `AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md`  
2. **Law audit table** — each violated clause: **FAIL** until remediated  
3. **Fix matrix** (§3 template) — one row per role with open obligation  

### 2.2 Remediate

Each fix row moves: `open` → `shipped` only when **artifact path + validator command PASS** logged.

### 2.3 Close

Incident status **`remediated`** only when:

- All law-audit rows **PASS**  
- All fix-matrix rows **`shipped`** with validator evidence  
- `bash scripts/validate-incident-fix-ownership-v1.sh` **PASS**  
- ASF accepts (founder gate for Critical/P0)

**Forbidden:** `remediated` from narrative · backfill-only broker events without hot-path gate · “we learned” without validator.

---

## 3. Fix matrix template (copy into every incident LOCKED body § remediation)

| Row | Role | Ship obligation (law-based) | Artifact / script | Validator (must PASS) | Status |
|-----|------|---------------------------|-------------------|------------------------|--------|
| F1 | **Worker** | VERIFY only via broker + receipt; never hand-edit REGISTRY | `goal1_lane_broker.py` behavior | live submit + `receipts/sa-XXXX-receipt.json` | open/shipped |
| F2 | **Machine / Broker** | VERIFY without receipt = **FAIL** | `goal1_lane_broker.py` · `worker_factory_heal_v1.py` | `validate-broker-receipt-cycle-v1.sh` | open/shipped |
| F3 | **Maintainer** | Wire gates on turn entry + verify shell + hygiene | `worker_turn_entry_v1.sh` · `enforce-registry-hygiene-v1.sh` | `validate-worker-factory-heal-v1.sh` | open/shipped |
| F4 | **Specialist** | Document gap only — **no** REGISTRY closeout | RESEARCH / advisory YAML | `execution_authority: false` | open/shipped |
| F5 | **Brain** | Route Worker INBOX — **no** substitute execution | `SINA_BRAIN_INBOX_PROCESS_LOCKED_v1.md` | broker pickup only | open/shipped |
| F6 | **Stairlift** | Propagate law to all agents | `governance_stairlift_sync_v1.py` | `validate-incident-fix-ownership-v1.sh` | open/shipped |

---

## 4. Role fix obligations (standing law — not optional)

| Role | Must ship when law/incident touches factory | Must never |
|------|---------------------------------------------|------------|
| **Governance Specialist** | Own all governance fixes · cascade + proof · law audit · fix matrix · validators on hot path | Say “fixed” without receipt · passive reports · delegate propagation to agents |
| **Worker** | One sa · broker submit every turn · RECIPE·VALIDATION·EVIDENCE·BUILT on VERIFY | Hand-edit REGISTRY · YAML-only done · skip broker |
| **Maintainer** | Validators on hot path · hygiene batch · stairlift on law touch | Close sa · pretend to be Worker |
| **Specialist** | Law gap analysis → RESEARCH · fix row F4 only | Edit product SSOT · mark sa done |
| **Brain** | Deliver/route INBOX · reconcile pointer | Implement sa · claim progress without receipt |
| **Executor** | Ship disk artifacts · rules loop each session | Reorder roadmap · skip validators |
| **Advisor** | Strategic coach · EXTERNAL_CRITIC classify | Close sa · change active step |
| **Vinny** | Load stairlift SSOT before operator action | Chat-only law sync · bypass gates |
| **Machine** | Fail-closed gates · auto-revert unproven done | Silent `ok: true` on failed VERIFY |
| **ASF** | Close Critical incidents · accept remediated | Terminal for routine ops |

---

## 5. INCIDENT-030 standing fix matrix (reference — must stay shipped)

| Row | Status | Proof |
|-----|--------|-------|
| F1 Worker broker path | **shipped** | broker rejects chat closeout · INCIDENT-030 §7 |
| F2 Broker receipt gate | **shipped** | `validate-broker-receipt-cycle-v1.sh` PASS |
| F3 Maintainer turn entry | **shipped** | `worker_factory_heal_v1` + validator PASS |
| F6 Stairlift | **shipped** | this law + `governance_stairlift_sync_v1.py` |

---

## 6. Machine SSOT

| Item | Path |
|------|------|
| Stairlift payload | `~/.sina/governance-stairlift-v1.json` |
| Fix matrix lib | `scripts/incident_fix_ownership_lib_v1.py` |
| Stairlift sync | `scripts/governance_stairlift_sync_v1.py` |
| Founder input cascade | `scripts/founder_input_cascade_v1.py` · `~/.sina/founder-input-cascade-receipt-v1.json` |
| Validator | `scripts/validate-incident-fix-ownership-v1.sh` · `scripts/validate-founder-directive-propagation-v1.sh` · `scripts/validate-founder-input-cascade-v1.sh` |
| Cursor rule | `.cursor/rules/incident-fix-ownership.mdc` |

---

## 7. Commercial line

**We sell controlled execution.** Drift and stasis are inventory risk. Stairlift + fix matrix = **hardening in the lightest form**: fail closed on the hot path, propagate law in milliseconds, close incidents only with validator proof.

---

*End SOURCEA_INCIDENT_FIX_OWNERSHIP_GOVERNANCE_HARDENING_LOCKED_v1*
