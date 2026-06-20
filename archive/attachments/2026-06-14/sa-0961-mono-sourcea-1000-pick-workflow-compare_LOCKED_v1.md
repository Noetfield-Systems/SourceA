# sa-0961 — Mono 1000 vs SourceA 1000 pick workflow compare · sync pick scripts

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Tier:** T2 research only · **No D-modules · No cross-repo implement**

## One-line verdict

> **Both packs share PLAN WITH NO ASF + 1000-grid shape, but pick order and closeout diverge.** SourceA uses **phase-first** shared lib + RUN INBOX broker; Mono uses **tier-global** inline pick + `agent-enforcement-closeout`. Sync = research + path fix — not script merge in this sa.

---

## Pack registry compare (disk truth)

| Field | SourceA (`sourcea-1000`) | Mono (`mono-1000`) |
|-------|--------------------------|---------------------|
| **REGISTRY path** | `brain-os/plan-registry/sourcea-1000/REGISTRY.json` | `os/plan-library/mono-1000/REGISTRY.json` |
| **Agent** | `AGENT-AUTO-SOURCEA` | `AGENT-AUTO-MONO` |
| **Trigger** | `PLAN WITH NO ASF` | `PLAN WITH NO ASF` |
| **Pick script** | `scripts/pick-sourcea-no-asf-plan.py` | `scripts/pick-mono-no-asf-plan.py` |
| **Run script** | `scripts/plan-no-asf-run.sh` | `scripts/plan-no-asf-run.sh` (same name, different subs) |
| **Validate** | `validate-sourcea-1000-pack.sh` | `validate-mono-1000-pack.sh` |
| **Global pack** | `~/.cursor/plans/no-asf-library` | same |
| **Cross-ref** | `mono_pack_ref` in SourceA REGISTRY | `virlux_pack_ref` in Mono REGISTRY |

**Path drift (SourceA):** `mono_pack_ref` points to `SinaaiMonoRepo/brain-os/plan-registry/mono-1000` — **missing**. Actual Mono pack: `os/plan-library/mono-1000/`.

---

## Pick algorithm compare

| Dimension | SourceA | Mono |
|-----------|---------|------|
| **Shared lib** | `sourcea_pick_lib.py` (`pick_backlog_plans`) | Inline in pick script |
| **Default order** | **phase-first** (s0→s9, T0→T3 within phase) | **tier-global** (T0→T3, first backlog in REGISTRY list order) |
| **Alt order** | `--order tier-global` | None |
| **Skip filter** | `SKIP_SNIPPETS` (Founder-only, Wire lane, etc.) | `SKIP_SNIPPETS` + `founder_only` flag + Telegram/BotFather strings |
| **Extra flags** | `--prompt` (print agent_prompt) | `--id` (resolve single mx path) |
| **Live head (2026-06-14)** | `sa-0126` (phase-s1 eval-dispatch T1) | `mx-0018` (phase-m0 verify-gates T0) |

**Why heads differ:** phase-first drains eval-dispatch before later phases; Mono tier-global stays in m0 until T0 backlog clears — **not a bug**, **order policy**.

---

## `plan-no-asf-run.sh` subs compare

| Subcommand | SourceA | Mono |
|------------|---------|------|
| `pick` | yes | yes |
| `validate-pack` | yes | yes |
| `route` | `prompt_router.py` | — |
| `l1-cycle` | yes | — |
| `verify-hub` | build panel + find_critical_bugs | — |
| `verify-stack` | — | `full-e2e-mono.sh` |
| `status` | — | queue head + last_verify from `os/plan.json` |
| `closeout` | REGISTRY + PRIORITY hints | `agent-enforcement-closeout.sh` |
| `full` | pick + route dry-run | pick + verify-stack hint |

---

## Closeout / verify authority

| Repo | Machine verify | Progress authority | Receipt |
|------|----------------|-------------------|---------|
| **SourceA** | `worker_verify_*` + broker `goal1_lane_broker.py` | Validators + receipt — not ASF | `receipts/sa-XXXX-receipt.json` |
| **Mono** | `full-e2e-mono.sh` · `agent-auto-audit.sh` | Same no-ASF law | `os/plan.json` `last_verify` + prompt `done` |

**RUN INBOX** is SourceA-only; Mono uses `plan-no-asf-run.sh status` + AGENT-AUTO-MONO chat — parallel lanes, not merged.

---

## Sync options (research — defer implement)

| # | Action | Owner | When |
|---|--------|-------|------|
| 1 | Fix SourceA `mono_pack_ref` → `os/plan-library/mono-1000` | Maintainer | Next pack REGISTRY amend |
| 2 | Extract `no_asf_pick_lib.py` (phase-first + tier-global + agent_runnable) | Maintainer | ASF orders cross-repo lib |
| 3 | Add Mono `--order phase-first` using `phase-m0`…`phase-m9` order table | Mono agent | After lib extract |
| 4 | Add SourceA `status` subcommand (mirror Mono) | SourceA maintainer | Hub Action optional |
| 5 | Document lane isolation — no pick script writes cross-repo | This doc | **Done (sa-0961)** |

**Do not:** merge Mono pick into SourceA Worker · edit Mono scripts from SourceA RUN INBOX · flip pick order without law amend.

---

## Relation to sa-0960

sa-0960 documented **no-ASF verify authority** cross-repo. This sa documents **pick workflow** divergence — complementary; both are research attachments only until VERIFY closeout.

---

## Verdict

Mono and SourceA 1000 packs are **structurally aligned** (trigger, grid, global library) but **operationally divergent** (pick order, run subs, closeout). **Sync pick scripts** means path fix + shared lib spec — **not** unifying queue heads. Factory continues RUN INBOX on SourceA; Mono stays AGENT-AUTO-MONO lane.

**One-line:** Same trigger, different drain — phase-first (SourceA) vs tier-global (Mono); fix `mono_pack_ref`, defer lib merge.
