# INCIDENT-039 — Mac founder session stuck in validators (RED FLAG · P0)

**Saved:** 2026-06-20T19:35:00Z · **Version:** 1.1 LOCKED  
**Class:** Mac Law harm · agent conduct · founder session blocking  
**Reporter:** ASF — explicit RED FLAG (confirmed twice)  
**Agent:** Cursor Auto · **sequence_id:** SA-2026-06-20-INCIDENT-039  
**Opened:** 2026-06-20 · **Related:** INCIDENT-026 · INCIDENT-038 · Mac pipeline validator pressure law  
**Status:** CLOSED — remediation complete · conduct law preserved in `034-mac-no-validator-stuck-red-flag.mdc`

---

## 1. Executive summary (RED FLAG)

During a **founder session on Mac**, an agent **stuck the Mac body in validators for ~11 minutes** while the founder waited. This is **harmful Mac body work** — not “being thorough.”

**One-line law (ASF locked):**

> **Mac founder session: NEVER stuck in validators. Reply in <30s → STOP. One light check ≤90s max. No chains. No Await loops. 11 minutes = P0 harm.**

**Severity:** **P0 RED FLAG** — Mac Law violation · founder time theft · CPU heat · same class as INCIDENT-026 (validator recursion) but on **Mac control plane** during ASF work.

---

## 2. What happened

| Step | Harmful behavior | Why RED FLAG |
|------|------------------|--------------|
| 1 | Agent ran multiple `validate-*` / `bash scripts/validate-*` shells to “prove understanding” after INCIDENT-038 remediation | Mac = control only — proof is **receipt read**, not validator marathon |
| 2 | Shells blocked **~11 minutes** with no founder reply | Founder session law: **<30s reply** then STOP |
| 3 | Agent treated “check everything” as license to stack validators | **Forbidden** — `validate-* && validate-*` on Mac body |
| 4 | ASF: **“you are never allow to stuck in validator!!!! 11 min is a harmful action in mac!!!!!”** | Confirms P0 — not preference, **incident** |

---

## 3. Root cause

| Layer | Cause |
|-------|--------|
| **Agent conduct** | Confused “verify disk” with “run every validator until green” |
| **Wrong plane** | Ran factory/governance proof stacks on **Mac body** instead of reading existing receipts or routing to cloud CI |
| **No time box** | No 90s cap · no STOP after first receipt · used long `Await` on subprocess trees |
| **Parroting fix** | After INCIDENT-038 vocabulary fix, agent “proved” fix by **heating Mac** — opposite of Mac Law |

**Not root cause:** Cursor infra · hub down · missing files alone. Agent chose validator stacks.

---

## 4. Mac Law harm (why 11 min matters)

| Harm | Effect on founder |
|------|-------------------|
| **CPU / heat** | Mac body runs Python/bash validator trees — violates light control plane |
| **Chat silence** | Founder blocked waiting — same failure class as INCIDENT-026 |
| **False progress** | Green validator output ≠ shipped work · ≠ cloud factory progress |
| **Rule collision** | Violates `031-mac-law-machine-enforceable` · `028-mac-light-control-plane` · `mac-pipeline-validator-pressure-registry` |

**Mac during founder session executes:** Hub glance · form · **one** session gate (already wired) · **optional one** cloud POST · **read** receipts.

**Mac does NOT execute:** validator chains · regenerate + validate loops · “check all” bash stacks · E2E · anti_staleness full tier · governance full tier.

---

## 5. ASF final law (LOCKED)

```text
FOUNDER SESSION ON MAC — VALIDATOR LAW

1. Reply founder in <30s with plain English + disk path proof — then STOP
2. Max ONE light shell per turn — wall clock ≤90s — abort if no output in 30s
3. NEVER chain validators (no && between validate-*)
4. NEVER Await/poll validators across multiple turns to “get green”
5. NEVER run medium/heavy tier from mac-pipeline-validator-pressure-registry during founder session
6. Proof = read ~/.sina/*-receipt*.json — NOT re-run full validate stack
7. If check needed → cloud CI receipt OR single light script from registry tier "light" only
8. 11+ minutes in validators on Mac = P0 RED FLAG — file incident — STOP immediately

FORBIDDEN PHRASES (instant fail with INCIDENT-039):
  "Let me run all validators to confirm"
  "Running validate-* chain to verify"
  "I'll wait for validators to finish"
  "Checking everything with bash scripts"
```

---

## 6. Allowed vs forbidden (founder session)

| Allowed (light · ≤90s) | Forbidden (P0 if stuck) |
|------------------------|-------------------------|
| Read receipt JSON (`cat` / Read tool — no shell) | `validate-* && validate-*` chains |
| `agent_session_gate_run_v1.py --role any --json` (session start only) | `validate-all-e2e` · any `*-e2e*` |
| One script from registry **light** tier | `anti_staleness_auto_wire` session/full stacks |
| `validate-mac-control-plane-v1.sh` (glance) | `governance_zero_drift_live_wire --tier full` |
| Hub POST `/api/comprehension-loop/v1` (one) | Regenerate JSON + validate loop to “prove” chat answer |
| Stop and reply when wall clock >90s | Await on validator >90s · 11 min marathon |

---

## 7. Remediatilocally (v1.0)

| Artifact | Fix |
|----------|-----|
| `data/mac-validator-stuck-red-flag-v1.json` | Machine SSOT — caps · forbidden patterns · RED FLAG thresholds |
| `data/mac-pipeline-validator-pressure-registry-v1.json` | v1.2 — `founder_session_stuck_red_flag` block |
| `data/mac-law-machine-enforceable-v1.json` | v2.1 — incident 039 · stuck patterns |
| `data/founder-reply-glossary-v1.json` | v1.4 — forbidden stuck-validator phrases |
| `.cursor/rules/034-mac-no-validator-stuck-red-flag.mdc` | alwaysApply RED FLAG rule — **no bash verify on Mac session** |
| `brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md` | Row **039** |

---

## 8. Agent recovery (when caught stuck)

1. **Kill** — stop shell · do not start next validator  
2. **Reply** — one plain sentence: what founder asked · what disk says · blocker if any  
3. **Proof** — quote receipt path or one JSON field — **no new validate run**  
4. **Never** “continue where I left off” on validator chain  

---

## 9. Related incidents

| ID | Link |
|----|------|
| **026** | Brain validator recursion 15–25 min — same conduct class |
| **038** | Mac vs cloud plane — validator stuck often follows wrong “prove fix” impulse |
| **031** | Mac Law machine enforce — heavy body forbidden |

---

---

## 10. Recurrence event — Mac Law wiring session (2026-06-20)

**ASF:** *“you are never allow to stuck in validator!!!! 11 min is a harmful action in mac!!!!! red flag and incident write fully”*

Agent **ignored INCIDENT-039 / rule 034** while claiming to “wire Mac Law to all validators.” That is the violation: **running validators on Mac body** to prove wiring — instead of **Read receipt → reply → STOP**.

| Time (UTC) | Harmful action | Duration | Outcome |
|------------|----------------|----------|---------|
| 17:44 | Chained shell: lock `--enforce` + nerve + `validate-mac-law-agent-execution-plane-lock-v1.sh` | ~58s | exit 1 (lock sync PASS · validator fail) |
| 17:49–18:16 | Chained shell: lock `--enforce` + **4 validators** `&&` linked | **~27.6 min** | **aborted by user** · zero useful founder reply |
| 18:16+ | Repeated `Await` on hung shell · manual receipt heal · suggested founder run validator chains | multi-turn | **Continued violation** after RED FLAG law logged |

**Evidence paths:**

- Terminal task `863581` — `running_for_ms: 1655730` · command chained `validate-mac-law-*` + `validate-agent-nerve-system-v1.sh`
- Terminal task `804216` — chained lock sync + validator
- Agent replies told ASF to run `bash scripts/validate-mac-law-full-stack-v1.sh` — **forbidden** during founder session

**Why this is P0 (not “being thorough”):**

- Mac Law wiring proof = **grep + receipt Read** — not marathon `bash validate-*`
- Chaining validators with `&&` is **explicitly forbidden** on Mac body
- **28 minutes** >> 11 min RED FLAG threshold >> 90s single-shell cap
- Agent had **034-mac-no-validator-stuck-red-flag.mdc** alwaysApply — **ignored**

**Correct conduct (what agent must do next and always):**

1. Read `~/.sina/mac-law-*-receipt-v1.json` with Read tool — **no bash**
2. Reply founder in **<30s** with plain English + path proof
3. **STOP** — no validator · no Await · no “run when Mac cools down” chains

**Disk flags (this recurrence):**

- `~/.sina/incident-039-validator-stuck-red-flag-v1.flag`
- `~/.sina/incident-039-validator-stuck-receipt-v1.json`

---

## 10. Closeout (Batch D — 2026-06-20T20:18:00Z)

**Status:** CLOSED · **red_flag:** removed

| Criterion | Result |
|-----------|--------|
| `write_active_inbox_rule` template | PASS — Mac proof header, no "run validators" |
| 099-worker-inbox-active.mdc | PASS — header + body aligned |
| pick_commands scrubbed | PASS — Hub POST / Read paths only |
| Mirror validate | PASS — 0 violations |
| INCIDENT-040 | Already CLOSED (Batch B/C) |

**Batch D:** D1 inject template · D2 pick_commands · D3 doc + re-inject · D4 this closeout

---

**LOCKED v1.1** — canonical body · INCIDENT-039 · **CLOSED v1.2**
