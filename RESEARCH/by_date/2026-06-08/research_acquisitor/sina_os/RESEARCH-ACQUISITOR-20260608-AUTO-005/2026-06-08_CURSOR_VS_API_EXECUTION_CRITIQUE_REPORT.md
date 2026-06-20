# SourceA Execution Surface — External Critic Verdict Report

**Saved:** 2026-06-08T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**trace_id:** `RESEARCH-ACQUISITOR-20260608-AUTO-005`  
**input_class:** EXTERNAL_CRITIC (Claude advisor)  
**worker:** Research Acquisitor · **execution_authority:** false  
**date:** 2026-06-08 · **subject:** sina_os

---

## Executive summary

Claude argues that SourceA failures trace to **Cursor UI clipboard injection** and recommends **Claude API → n8n → cloud Hub** in that order.

**Verdict:** The observation is **partially true** for manual/visible lanes and portfolio workers. It is **overstated** for **Goal 1 Rail A**, which already runs **headless** via `agent -p -f`. The real remaining dependency is **local Cursor agent CLI + Mac availability + governance gates** — not paste alone.

**ASF P0 per Master Operating Tracker:** prove **GOAL-AUTH-LIVE** on existing Rail A before any platform migration ordered by external critic.

---

## What Claude claimed

| # | Claim |
|---|--------|
| 1 | Root problem = clipboard paste into Cursor chat — never fully automatic |
| 2 | Fix #1 (this week) = Claude API Python SDK replaces Cursor turns |
| 3 | Fix #2 (next week) = n8n for schedule/retry/webhooks |
| 4 | Fix #3 (month 1) = Cloud Hub on Railway/Fly for phone access |
| 5 | Stop building Cursor scripts — move execution off Cursor entirely |

---

## What disk actually shows

### Rail A is already headless (default)

**Law:** `GOAL1_EXECUTION_SOLUTION_LOCKED_v1.md`

```text
INJECT → VALIDATE → ACTIVATE (agent -p -f) → SYNC (orchestrator/broker)
```

**Entry:** Hub **▶ AUTO-RUN** → `goal1_auto_loop_v1.py` → `start_goal1_worker_turn_v1.py` → **`agent -p -f`**

**Founder law:** `TODAY_AUTORUN_50_PLAN_LOCKED_v1.md` — no Worker paste for autorun.

### Clipboard path still exists (non-default)

Used for: manual fallback, **visible Worker chat lane**, TrustField/Noetfield portfolio site builds.

### Documented failure layers (not paste-only)

1. Wrong mental model — watching Worker chat while headless runs in batch log  
2. Prepare ≠ execute — INBOX delivered ≠ agent running  
3. Fragile launch — detached processes required  
4. Preflight / Mac awake / agent binary  
5. `broker=no`, one-sa gate, YAML shape errors  
6. Brain tracker STALE → INBOX blocked  

---

## Verdict matrix

| Claude claim | Verdict | Notes |
|--------------|---------|-------|
| Everything is clipboard injection | **Reject** | Rail A default is CLI headless |
| Cursor as automation runtime is root cause | **Accept partial** | Still Cursor agent on Mac — vendor + local dependency |
| Claude API this week replaces Worker | **Reject as P0** | No file/validator/git surface; critic cannot reorder roadmap |
| n8n for orchestration | **Accept** | After Rail A proof — wraps existing scripts |
| Cloud Hub for phone | **Accept partial** | Monitor/control yes; full cloud workers = larger scope |
| Rip out Cursor this week | **Reject timing** | GOAL-AUTH-LIVE ~90%; blocker = observed live chain |

---

## Alignment with your system (not generic automation)

| Your requirement | Implication |
|------------------|-------------|
| ASF → Brain → Broker → Worker → Disk | Swap LLM vendor ≠ swap architecture |
| Semi-auto L1 | Not unsupervised 24/7 Level 3 yet |
| Hub only for founder | n8n/cloud behind Hub — not Terminal |
| WORKER_ROUND_REPORT + broker=yes | Any new runner must match contract |
| GOAL-AUTH-LIVE P0 | Prove existing chain before replatform |
| TrustField / Noetfield revenue | Portfolio Cursor workers = separate lane |
| Disk wins over chat | RESEARCH + tracker + REGISTRY are SSOT |

---

## Recommended order (ASF system)

### P0 — now

- Hub → Goal 1 loop → **EXECUTE TURN / AUTO-RUN**
- Confirm events in `~/.sina/events/YYYY-MM-DD.jsonl`
- Close **GOAL-AUTH-LIVE** when full chain observed once

### P1 — harden without replatform

- Audit remaining clipboard paths on Rail A  
- Stabilize preflight, launchd, broker=no handling  
- **n8n:** schedule AUTO-RUN, retry, phone notify  

### P2 — only if ASF orders explicitly

- API runner for bounded turns (CHECK, research, copy) — same receipt shape  
- Register in `EXECUTION_AUTHORITY_MAP` — no parallel spine  

### Parallel (never blocked on spine)

- TrustField / Noetfield V3 worker execution  
- Founder GTM outreach — **revenue blocker is sales execution, not automation architecture**

---

## API wrapper — hold until ASF asks

If ordered, minimum spec:

- Same INBOX in / WORKER_ROUND_REPORT out  
- Brain still routes sa_id  
- Explicit read-only vs write tool policy  
- Events append to `~/.sina/events/`  
- New LOCKED doc + validator — not critic overwrite  

**Brain decision memo candidate:** `DEC-AUTO-SURFACE-001`

---

## One line for ASF

**Your system wants governed semi-auto proof on Rail A first; Claude wants platform swap first.** Disk agrees with you — next move is **Hub AUTO-RUN**, not Anthropic SDK alone.

---

## Vault paths

| Artifact | Path |
|----------|------|
| YAML SSOT | `~/.sina/agent-workspaces/research-acquisitor/briefs/2026-06-08_CURSOR_VS_API_EXECUTION_CRITIQUE_REPORT.yaml` |
| This report | `~/.sina/agent-workspaces/research-acquisitor/briefs/2026-06-08_CURSOR_VS_API_EXECUTION_CRITIQUE_REPORT.md` |
| Mirror | `~/Desktop/SourceA/RESEARCH/by_date/2026-06-08/research_acquisitor/sina_os/RESEARCH-ACQUISITOR-20260608-AUTO-005/` |
