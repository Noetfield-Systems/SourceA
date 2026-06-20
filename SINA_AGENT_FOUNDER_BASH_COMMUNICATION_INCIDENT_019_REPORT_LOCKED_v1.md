# INCIDENT-019 pointer — Agent-founder bash communication

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Canonical body:** `brain-os/incidents/SINA_AGENT_FOUNDER_BASH_COMMUNICATION_INCIDENT_019_LOCKED_v1.md`  
**Law:** `AGENT_FOUNDER_BASH_COMMUNICATION_LOCKED_v1.md`  
**Related:** INCIDENT-020 · INCIDENT-021

## One-line

Agent gave repo-relative `scripts/...` without `cd`; ASF ran from `~` → ENOENT. Topic = **communication**, not S10. Fix: cwd-safe bash law + `~/.sina/bin/` wrappers.

**Status:** REMEDIATED
