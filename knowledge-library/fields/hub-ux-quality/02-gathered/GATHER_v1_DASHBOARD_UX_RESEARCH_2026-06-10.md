# GATHER v1 — Dashboard UX for Sina Command

**Field:** hub-ux-quality  
**Stage:** 02-gathered  
**Date:** 2026-06-10  
**Sources:** Grotol SaaS dashboard UX · Orbix perceived performance 2026 · HUB_UNIFY_AND_PROOF_MASTER_v1.md · disk audit

## Golden rules (apply to every hub change)

1. Shell paints first; heavy data streams per tab.
2. Skeleton layout matches final UI — no generic spinner for tabs.
3. One live writer for queue/proof; UI reads slices only.
4. No poll unless tab is visible.
5. Empty state always offers one-tap next action.

## Sina-specific

- Founder never Terminal — actions must work from Home §3.
- Proof counter from `PROGRAM_1000_HONEST_STATUS.json` only.
- Worker lane truth from `run-inbox-disk-truth-v1.json`.

**Report:** `archive/attachments/2026-06-10/hub-app-quality-research-report_LOCKED_v1.md`
