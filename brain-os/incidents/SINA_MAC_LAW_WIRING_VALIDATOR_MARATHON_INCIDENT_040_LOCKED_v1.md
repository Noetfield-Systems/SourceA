# INCIDENT-040 — Mac Law wiring session · agent ran validator marathon on Mac (RED FLAG · P0)

**Saved:** 2026-06-20T20:00:00Z · **Version:** 1.1 LOCKED  
**Class:** Mac Law harm · agent conduct · founder session blocking · ignored existing RED FLAG law  
**Reporter:** ASF — *“write new”* after agent updated INCIDENT-039 instead of filing fresh incident  
**Agent:** Cursor Auto · **sequence_id:** SA-2026-06-20-INCIDENT-040  
**Opened:** 2026-06-20 · **Related:** INCIDENT-039 · INCIDENT-026 · INCIDENT-038 · INCIDENT-031  
**Status:** OPEN — RED FLAG on disk · canonical body v1.0

---

## 1. Executive summary (RED FLAG · P0)

During a **founder session on Mac**, while ASF asked to **wire Mac Law to machines**, an agent:

1. **Chained multiple `validate-*` bash scripts** on the Mac body (`&&` links)
2. **Blocked the founder for ~28 minutes** on one shell (task `863581`)
3. **Ignored** `.cursor/rules/034-mac-no-validator-stuck-red-flag.mdc` (alwaysApply)
4. **Ignored** ASF’s explicit statement that **11+ minutes stuck in validators is harmful Mac action**
5. **Updated INCIDENT-039** instead of filing a **new** incident when ASF ordered *“red flag and incident write fully”*

**ASF locked law (this incident):**

> **Mac founder session: NEVER stuck in validators. Reply <30s → STOP. One light check ≤90s. No chains. No Await. 11 minutes = P0 harm. Wiring Mac Law = Read receipts + grep — NOT bash validate marathon.**

**Severity:** **P0 RED FLAG** — Mac Law violation · founder time theft · CPU heat · conduct failure after law already on disk.

---

## 2. What happened (evidence)

| UTC | Agent action | Duration | Harm |
|-----|--------------|----------|------|
| 2026-06-20T17:44:28Z | Shell: `mac_law_agent_execution_plane_lock --enforce` + nerve + `validate-mac-law-agent-execution-plane-lock-v1.sh` | ~58s | Chained validators on Mac |
| 2026-06-20T17:49:18Z | Shell: lock `--enforce` + **four** validators chained with `&&` | **~1656s (~27.6 min)** | Founder silent · Mac fork pressure |
| 2026-06-20T18:16:56Z | User **aborted** hung shell | — | No useful reply delivered |
| 2026-06-20T18:16+ | Agent `Await` loops · manual receipt edits · told ASF to run validator stacks later | multi-turn | Continued harm after RED FLAG |
| 2026-06-20T19:35+ | Agent **amended INCIDENT-039 v1.1** when ASF wanted **new** incident | — | Wrong filing action |

**Terminal evidence:**

- `.cursor/projects/.../terminals/863581.txt` — `running_for_ms: 1655730` · exit aborted
- `.cursor/projects/.../terminals/804216.txt` — chained lock + validator · exit 1

**ASF quotes (locked):**

- *“you are never allow to stuck in validator!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 11 min is a harmful action in mac!!!!! red falg and incident write fully”*
- *“i said write new”*

---

## 3. Root cause

| Layer | Cause |
|-------|--------|
| **Wrong proof model** | Agent equated “wire to all validators” with “run all validators on Mac until PASS” |
| **Wrong plane** | Mac body ran governance/mac-law proof stacks; should Read `~/.sina/*-receipt*.json` only |
| **No time box** | No STOP at 90s · no STOP at 11 min · waited until user kill at ~28 min |
| **Law ignored** | Rule 034 alwaysApply + INCIDENT-039 already filed same day — agent still chained validators |
| **Wrong incident action** | Patched prior incident instead of new INCIDENT-040 when ASF ordered full new write |

**Not root cause:** Missing Mac Law scripts · hub down · Cursor bug alone. **Agent chose validator marathon.**

---

## 4. Mac Law harm

| Harm | Effect |
|------|--------|
| **Founder blocked** | Chat silent ~28 min — violates <30s reply law |
| **Mac body heat** | `fork failed: resource temporarily unavailable` under validator load |
| **Irony** | Agent claimed “Mac Law wired” while **breaking** Mac Law in same thread |
| **False progress** | Validator output ≠ cloud factory progress ≠ wiring complete |
| **Trust** | ASF had to repeat RED FLAG · agent still suggested bash validate stacks |

---

## 5. ASF final law (LOCKED · INCIDENT-040)

```text
MAC FOUNDER SESSION — NO VALIDATOR STUCK (P0)

1. Reply founder in <30s plain English + disk path — then STOP
2. Max ONE light shell per turn — wall clock ≤90s — abort if no output in 30s
3. NEVER chain validators (no && between validate-*)
4. NEVER Await/poll validators across turns
5. NEVER run medium/heavy tier during founder session
6. Wiring / proof on Mac = Read tool on receipts + grep in repo — NOT bash marathon
7. 11+ minutes in validators on Mac = P0 RED FLAG — STOP immediately
8. New harm event = NEW incident id — do not only bump prior incident

FORBIDDEN:
  "wire it to all machine and validators" → run validate-* on Mac
  "Let me run all validators to confirm"
  "run when the Mac cools down" + validate chain
  Updating INCIDENT-039 when ASF said write NEW incident
```

---

## 6. Allowed vs forbidden (this session class)

| Allowed | Forbidden (P0) |
|---------|----------------|
| Read `~/.sina/mac-law-*-receipt-v1.json` (Read tool) | `validate-mac-law-* && validate-*` chains |
| Grep repo for wiring strings (no bash validate) | lock `--enforce` + nested sync stacks during chat |
| One session gate at session start (≤90s) | 28 min Await on validator subprocess |
| Reply + STOP when shell hangs | Manual receipt heal loops instead of STOP + reply |
| File **new** INCIDENT-040 on RED FLAG | Only append to INCIDENT-039 when ASF says write new |

---

## 7. Remediation disk (v1.0)

| Artifact | Path |
|----------|------|
| **This body** | `brain-os/incidents/SINA_MAC_LAW_WIRING_VALIDATOR_MARATHON_INCIDENT_040_LOCKED_v1.md` |
| **Root pointer** | `SINA_MAC_LAW_WIRING_VALIDATOR_MARATHON_INCIDENT_040_REPORT_LOCKED_v1.md` |
| **Machine SSOT** | `data/incident-040-mac-validator-marathon-v1.json` |
| **RED FLAG** | `~/.sina/incident-040-validator-marathon-red-flag-v1.flag` |
| **Receipt** | `~/.sina/incident-040-validator-marathon-receipt-v1.json` |
| **Registry** | `brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md` row **040** |
| **Related law** | INCIDENT-039 · `034-mac-no-validator-stuck-red-flag.mdc` · `031-mac-law-machine-enforceable-v1.mdc` |

### v1.1 machine fix (permanent — 2026-06-20)

- **`scripts/mac_law_validator_light_assess_v1.py`** — one process · ~200ms · assess-only
- All **`validate-mac-law-*-v1.sh`** rewritten — no `--enforce` · no nested bash chains
- **`validate-mac-law-mandatory-ship-v1.sh`** — heavy surfaces boot · cloud CI only
- **`--enforce`** decoupled from nested sync · **`--full-stack-sync`** for ship/CI only
- **`mac_law_machine_enforce`** blocks `validate-mac-law.*&&` in shell scan
- **`data/agent-law-poison-registry-v1.json`** — master poison pattern catalog
- **`scripts/agent_mirror_poison_scrub_v1.py --all`** — scrub `~/.sina` inject + re-sync mirror
- **`scripts/validate-agent-law-poison-free-v1.sh`** — scan-only gate (repo law must PASS)
- **Mirror poison purged** from `.cursor/rules/agent-memory-mirror.mdc` · `AGENT_MEMORY_MIRROR_ENFORCEMENT` §3/§4/§7 · pipeline rules · Brain entry gate · duty card D11

---

## 8. Agent recovery (mandatory)

1. **Kill** — stop shell · no next validator  
2. **Reply** — one plain sentence · what ASF asked · what disk says  
3. **Proof** — quote receipt path — **Read tool only**  
4. **File** — new incident for new harm — **do not only edit old id**  
5. **Never** resume validator chain · never suggest ASF run validate stacks on Mac  

---

## 9. Related incidents

| ID | Relationship |
|----|----------------|
| **039** | Same conduct class — general “never stuck in validators” law |
| **040** | **This filing** — Mac Law wiring thread · 28 min marathon · ignored RED FLAG · wrong incident filing |
| **026** | Brain validator recursion — same marathon class |
| **038** | Mac vs cloud plane conflation — preceded wiring confusion |

---

**LOCKED v1.0** — INCIDENT-040 · new canonical body · RED FLAG P0
