# INCIDENT-041 — Agent held open Cursor terminal for Hub server (RED FLAG · P0)

**Saved:** 2026-06-20T22:43:46Z · **Version:** 1.0 LOCKED  
**Class:** Mac Law harm · agent conduct · founder never Terminal · session pollution  
**Reporter:** ASF — *“NO OPEN TERMINAL”* · *“CLEAR THE TERMINAL IF YOU DONT USE IT”*  
**Agent:** Cursor Auto · **sequence_id:** SA-2026-06-20-INCIDENT-041  
**Opened:** 2026-06-20 · **Related:** INCIDENT-039 · INCIDENT-040 · Batch E Hub proof · Mac control plane law  
**Status:** OPEN — **RED FLAG ACTIVE** · canonical body v1.0

---

## 1. Executive summary (RED FLAG · P0)

During **Batch E (Hub live proof)**, after `serve-sina-command.sh` failed to keep Hub alive via nohup, an agent **started `python3 scripts/sina-command-server.py` as a long-running foreground process in a Cursor agent terminal** and **left that terminal open** so Hub would stay up.

ASF **aborted** the task (`terminated_by_user`). ASF then ordered: **never leave an open terminal** — Hub must daemonize; **clear the terminal when done**.

**ASF locked law (this incident):**

> **Agents MUST NOT hold open Cursor/shell terminals with long-running servers. Founder never Terminal. Hub boot = one-shot script or launchctl — script exits, terminal closes. If Hub dies after Ready, fix launchctl/nohup in the repository — do NOT pin a terminal open.**

**Severity:** **P0 RED FLAG** — violates Mac control plane · pollutes founder session · repeats “Mac body does work” pattern in a new form (terminal babysitting instead of validator marathon).

---

## 2. What happened (evidence)

| Step | Agent action | Harm |
|------|--------------|------|
| 1 | `enter-mac-control-plane-v1.sh` — Hub still `down` after kickstart | ~20s · no useful Hub |
| 2 | `serve-sina-command.sh` — prints **Ready** then exits | nohup child **dead** within seconds · port :13020 empty |
| 3 | Retries (nohup, background `serve-sina-command`) | **~1m34s+ retry tax** · founder sees terminal churn |
| 4 | **`block_until_ms: 0`** + `python3 scripts/sina-command-server.py` in **persistent agent terminal** | **Open terminal left running** — wrong architecture |
| 5 | Batch E POSTs succeeded while terminal held | Proof valid but **method forbidden** |
| 6 | ASF **aborted** terminal task `957617` | Hub down again — expected when terminal killed |
| 7 | ASF: *“THIS SHOULD BE LIKE THIS!!! NEVER USING TERMINAL AND LEAVE IT”* | **New incident required** |

**Terminal evidence:**

- `.cursor/projects/.../terminals/957617.txt` — `Run Hub server in persistent background process` · **`terminated_by_user`**
- `.cursor/projects/.../terminals/521646.txt` · `266927.txt` — `serve-sina-command.sh` Ready then exit; Hub not durable

**Batch context:** Batch A–D remediated inject poison; Batch E goal was Hub POST proof for W-CLOUD-001/002. Proof receipt exists at `~/.sina/sourcea-worker-cloud-assignment-receipt-v1.json` — **method of obtaining it was harmful conduct**.

---

## 3. Root cause

| Layer | Cause |
|-------|--------|
| **Agent conduct** | Treated “Hub must be up for curl” as license to **hold a shell open** with the server process |
| **Wrong workaround** | Foreground server in agent terminal instead of fixing **why nohup/launchctl Hub exits** |
| **Mac Law drift** | Same class as INCIDENT-039/040 — **Mac body executes** instead of control-plane one-shot + Read receipts |
| **Cursor tool misuse** | `block_until_ms: 0` for **long-lived daemons** — forbidden for Hub/factory |

---

## 4. Allowed vs forbidden (all agents)

| Allowed | Forbidden (P0) |
|---------|----------------|
| **One-shot:** `bash scripts/serve-sina-command.sh` — script exits after spawning nohup | **`python3 scripts/sina-command-server.py` in agent terminal** left running |
| **One-shot:** `enter-mac-control-plane-v1.sh` — kickstart launchctl, exit | **`block_until_ms: 0`** to keep Hub/factory/server alive in agent shell |
| Read `~/.sina/mac-control-plane-receipt-v1.json` · report `hub: down` + blocker | Leaving terminal open “so POST works” |
| Hub POST **once** if Hub already up via **founder/launchctl daemon** | Retry loops >90s without replying to founder |
| Document blocker: *Hub down — fix com.sourcea.hub* · STOP | Pin terminal · Await forever · tell founder to run bash |

---

## 5. Tips for other agents (mandatory read)

### 5.1 Terminal hygiene

1. **Every shell command must exit.** Agent turns are not daemons.
2. **Never** start `sina-command-server.py`, `fbe_motor_delegate`, film render, or validator stacks in a **background agent terminal** and walk away.
3. If you used `block_until_ms: 0`, the process must be **short** (<90s) or you must **not** use that pattern for servers.
4. When a task completes or fails, **do not leave orphan terminals** — founder had to abort task `957617`.

### 5.2 Hub boot (correct order)

```text
1. bash scripts/enter-mac-control-plane-v1.sh          # one-shot · kickstart com.sourcea.hub
2. Read ~/.sina/mac-control-plane-receipt-v1.json      # hub field
3. If down: bash scripts/serve-sina-command.sh       # one-shot · nohup · script EXITS
4. curl -sf -m 5 http://127.0.0.1:13020/health       # single check
5. If still down: STOP · tell founder Hub daemon broken · cite log tail — DO NOT hold terminal
```

### 5.3 Batch E / W-CLOUD proof without open terminal

- **If Hub up:** one `curl` POST to `/api/fbe/forge-competitor-run/v1` (dry_run) · update proof receipt · **STOP**.
- **If Hub down:** write receipt with `hub_post.blocker: hub_not_reachable` · **STOP** — proof partial is honest; **do not** open terminal to force it.

### 5.4 Related incidents (read together)

| ID | Lesson |
|----|--------|
| **039** | Never validator marathon on Mac |
| **040** | Never chained `validate-*` while wiring Mac Law |
| **041** | **Never open terminal to babysit Hub/server** |

### 5.5 Reply shape when Hub is down

One plain sentence + path:

> “Hub :13020 is down after one-shot boot. Batch E mac_proof Read PASS; Hub POST deferred. Fix: launchctl `com.sourcea.hub` or `serve-sina-command.sh` from Hub Actions — not an agent-held terminal.”

---

## 6. Remediatilocally (v1.0)

| Artifact | Path |
|----------|------|
| **This body** | `brain-os/incidents/SINA_AGENT_OPEN_TERMINAL_HUB_HOLD_INCIDENT_041_LOCKED_v1.md` |
| **Report pointer** | `brain-os/incidents/SINA_AGENT_OPEN_TERMINAL_HUB_HOLD_INCIDENT_041_REPORT_LOCKED_v1.md` |
| **Machine SSOT** | `data/incident-041-agent-open-terminal-hub-hold-v1.json` |
| **RED FLAG** | `~/.sina/incident-041-open-terminal-red-flag-v1.flag` |
| **Receipt** | `~/.sina/incident-041-open-terminal-receipt-v1.json` |
| **Registry** | `brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md` row **041** |
| **Related law** | `~/Desktop/MacLaw/MAC_CONTROL_PLANE_LOCKED.md` · `.cursor/rules/mac-control-plane.mdc` · `.cursor/rules/031-mac-law-machine-enforceable-v1.mdc` |

### v1.1 machine fix (follow-up — not done in this filing)

- Investigate why `serve-sina-command.sh` nohup exits immediately after Ready (pid dead, :13020 empty)
- Ensure `com.sourcea.hub` launchd plist keeps Hub without Cursor terminal
- Optional: Hub health gate in `mac_control_plane_v1.py --enter` with **actionable** one-line founder message (no agent terminal)

---

## 7. Agent recovery (mandatory)

1. **Kill** — do not leave Hub/server in agent terminal; founder abort = immediate stop  
2. **Reply** — one sentence: what ASF asked · Hub status · receipt path  
3. **Proof** — Read tool on JSON receipts only  
4. **File** — **new** incident for **new** harm (this document)  
5. **Never** resume with “persistent background process” for Hub  

---

## 8. Related incidents

| ID | Relationship |
|----|----------------|
| **039** | Validator marathon — same “Mac body blocks founder” class |
| **040** | Validator marathon during Mac Law wiring |
| **041** | **This filing** — open terminal Hub hold · Batch E · ASF abort |
| **038** | Mac vs cloud — control plane must not run factory body |

---

**LOCKED v1.0** — INCIDENT-041 · RED FLAG P0 · open terminal Hub hold forbidden
