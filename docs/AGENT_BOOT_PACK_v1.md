# Agent Boot Pack v1

**Schema:** `agent-boot-pack-v1`  
**Saved at (UTC):** 2026-07-02T22:30:00Z  
**Law:** L17 · tool-agnostic by construction — any IDE/agent loads this manifest before work

---

## One line

> Load **laws v3 → role → orient → registries → boot contract** in order; route work at lowest plausible cost tier (L17).

---

## Mandatory load order (every session)

| Order | Artifact | Path | Why |
|------:|----------|------|-----|
| 1 | **Laws v3** | `docs/GOVERNED_AUTORUN_LAWS_v3.md` | L1–L17 operating system |
| 2 | **Role routing** | `.cursor/rules/000-entry-gate.mdc` + role from session gate `--role` | Brain vs Worker vs governance |
| 3 | **Orient SSOT** | `data/sourcea_orient_routing_v1.json` · human: `docs/SOURCEA_ORIENTATION_AND_ROUTING_LOCKED_v1.md` | Pipeline nodes · graph tiers |
| 4 | **Registries** | See §Registries below | Triggers, missions, cost-tier queue |
| 5 | **Boot ledger** | `data/cursor-bootstrap-ledger-v1.json` | Structural GPS — read before structural edits |
| 6 | **Session gate** | `python3 scripts/agent_session_gate_run_v1.py --role <role> --json` | Spine + cost receipt (L16 + L17) |

**Do not** mega-paste context — use `docs/CURSOR_CONTEXT_INDEX_LOCKED_v1.md` as router only.

---

## Registries (machine SSOT)

| Registry | Path | Law |
|----------|------|-----|
| Trigger registry | `data/trigger-registry-v1.json` | L14 T-REG |
| Mission registry | `data/mission-registry-v1.json` | P3 mission_id on receipts |
| Cost-tier queue | `data/worker-cost-tier-queue-v1.json` | L17 routing |
| Mac spine contract | `data/mac-spine-bridge-contract-v1.json` | L16 |
| Session cost contract | `data/agent-session-cost-contract-v1.json` | L17 |
| Cursor cost routing | `data/cursor-cost-intelligence-routing-v1.json` | 045 pool law |
| NOETFIELD spec | `docs/NOETFIELD_COHERENT_SYSTEM_SPEC_v1.md` | Cross-repo coherence |
| Machine process loops | `data/machine-process-loops-v1.json` | 8 loops · no founder routing |
| Founder trigger retirement | `data/founder-trigger-retirement-registry-v1.json` | Earned autonomy · receipt count |

---

## Cost tiers (L17 — lowest plausible first)

| Tier | Worker | Use when |
|------|--------|----------|
| **T0** | Scripts only | grep, sweep, registry/doc sync, vocab pass |
| **T1** | Copilot pilot | Kaizen `machine_safe` PRs (after founder P4 fences) |
| **T2** | Cursor Auto/Composer | Branch builds · scoped sa on branches |
| **T3** | Cloud Loop Specialist | Integration / merge to `main` (L15) |

Escalation requires `TIER_ESCALATION` receipt: `{from_tier, to_tier, reason, evidence}` via `scripts/agent_session_cost_v1.py escalate`.

---

## Role boot snippets

### Brain

- Entry: `bash scripts/brain-session-start.sh` (once per chat)
- Execute: route only — never implement sa on Brain chat
- INBOX: `~/.sina/worker-prompt-inbox-v1.json` / spine `worker_inbox`
- Digest input: `data/brain-digest-cost-tier-latest-v1.json`

### Worker

- Entry: `python3 scripts/cursor_entry_gate.py --role worker`
- Execute: RUN INBOX head only · one W-LBA item per session when assigned
- Tier default: **T2** unless task maps to T0 in `worker-cost-tier-queue-v1.json`

### Cloud Loop Specialist (integrator)

- Tier: **T3** always for merge to `main`
- Law: L15 — branches only for local agents; integrator merges

---

## Session receipts (mirror + spine)

| Receipt | Path | Spine event |
|---------|------|-------------|
| Session gate | `~/.sina/agent_session_gate_receipt_v1.json` | `MAC_SESSION_GATE` |
| Session cost | `~/.sina/agent-session-cost-receipt-v1.json` | `AGENT_SESSION_COST` |
| Fresh main | `~/.sina/mac-fresh-main-sync-receipt-v1.json` | `MAC_FRESH_MAIN_SYNC` |
| Heartbeat | `~/.sina/mac-spine-heartbeat-receipt-v1.json` | `MAC_AGENT_HEARTBEAT` |

---

## Tool-agnostic rule

This pack lists **paths and contracts only** — no Cursor-specific hooks required. Any agent (Cursor, Copilot, cloud worker) that loads the manifest + runs session gate is boot-compliant.

**Validator (ship window):** confirm manifest paths exist on disk before merge.

---

## Related

- Corporate bootstrap: `docs/CURSOR_CORPORATE_BOOTSTRAP_PACK_LOCKED_v1.md`
- Governed autorun skill: `.cursor/skills/governed-autorun/SKILL.md`
- Agent boot pack contract: this file is the canonical manifest (`docs/AGENT_BOOT_PACK_v1.md`)
