# Agent terminal closeout (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.1  
**Authority:** ASF order · **Brain owns Mac health** · all agents CART own shells  
**Wired:** `SINA_MAC_HEALTH_GUARD_LOCKED_v1.md` §Brain · `.cursor/rules/background-terminal-cart-check.mdc` · `agent-self-audit-loop` session-close

---

## Law (one sentence)

**Brain owns Mac health and machine pressure; every agent MUST CART-close terminal metadata after its own shell tasks — same turn, before final reply.**

---

## Role split

| Role | Mac health |
|------|------------|
| **Brain** | **Owner** — Mac Health Guard · CART fleet sweep · hub posture · orphan PIDs · `brain_fast_startup` |
| **Worker** | INBOX turns only · CART **own** session shells · **route** Mac health to Brain |
| **Maintainer** | Ship `mac_health_guard.py` + mini-app UI only · **route** runtime Mac health to Brain |
| **Founder** | Hub taps only — **Run full scan** · no Terminal |

---

## When (non-optional)

| Trigger | Action |
|---------|--------|
| After any `Shell` / background command completes | CART closeout |
| Before `session-close` on substantive work | CART closeout |
| User asks “what’s running?” | CART closeout first, then answer |
| UI shows terminals running 5+ min | CART closeout — never diagnose-only |

---

## Procedure — CART

| Step | Do |
|------|-----|
| **C**lose | `kill -TERM` any PID from this session’s terminal headers still alive (`kill -0`) |
| **A**ppend | Add `exit_code` footer to every terminal file from this session missing it |
| **R**econcile | Note `kill_flag` / inbox head if drain-related shells ran |
| **T**ell | One line in reply: N terminals closed · ghost vs real |

### Footer template

```
---
exit_code: 0
elapsed_ms: <actual or best estimate>
ended_at: <ISO-8601 UTC>
---
```

Use `exit_code: 1` when command output shows failure.

---

## Never

- Leave terminals without `exit_code` and move on.
- Report “stale UI” without closing in the same message.
- Stack long `brain_sync` / full `find_critical_bugs` / hospital on routine turns (`SINA_BRAIN_FAST=1`).

---

## Why

Cursor marks shells “running” until `exit_code` is written. Orphan metadata causes false “N Terminals Running”, session pressure, and founder confusion. **Close is executor duty — not founder Terminal.**

---

## Supersedes

Nothing. Complements `SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md` (founder never runs shell; **agents** must clean up after they do).
