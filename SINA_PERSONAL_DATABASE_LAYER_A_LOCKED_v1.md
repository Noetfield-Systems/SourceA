# Personal Database (Layer A) — locked law

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Status:** LOCKED · **Thread:** `THREAD-SUPERBRAIN` · **Hub tab:** `personal-db`

## Purpose

**Sina AI Personal Database** is the final source of truth for agents that copy and learn from the founder. Sina Command sits on top and reads Layer A — it does not replace it.

| Path | Role |
|------|------|
| `~/Desktop/SinaaiMonoRepo/SinaaiDataBase/data/` | Layer A markdown SSOT (L0–L4) |
| `~/Desktop/SinaaiMonoRepo/SinaaiDataBase/imports/raw/` | Drop raw exports |
| `~/Desktop/SinaaiMonoRepo/SinaaiDataBase/pipeline/staging/` | Parsed staging |
| `~/Desktop/SinaaiMonoRepo/SinaaiDataBase/data/L4-agents/` | Agent mandate templates |

## Conflict rule

On conflict between Source A law, Prompt OS, or UI copy vs a **promoted active** Layer A entry: **Layer A wins** for identity, mandates, and personal knowledge. Source A governs ops and app behavior.

## Layers

| Layer | Folder | Use |
|-------|--------|-----|
| L0-meta | `data/L0-meta/` | Architecture, ingestion, SoT registry |
| L1-identity | `data/L1-identity/` | Who you are, non-negotiables |
| L2-knowledge | `data/L2-knowledge/` | Stable knowledge entries |
| L3-process | `data/L3-process/` | Processes and playbooks |
| L4-agents | `data/L4-agents/` | Per-agent mandates for copy agents |

## Required frontmatter (every `data/**/*.md` entry)

```yaml
id: "unique-id"
title: "Human title"
layer: L2-knowledge   # or L0-meta … L4-agents
access: [owner, agent]   # owner | agent | public
status: active          # draft | active | archived
```

Optional: `category`, `tags`, `summary`, `related`, `sources`, `lang`, `created`, `updated`.

## Access

| Value | Meaning |
|-------|---------|
| `owner` | Founder-only sensitive |
| `agent` | Copy agents may read when training |
| `public` | Safe to cite externally (rare) |

## Ingestion (Phase 0)

1. Drop file in `imports/raw/`
2. Hub **Personal DB** → **Scan imports** (or `POST /api/personal-db` action `scan`)
3. Review staging under `pipeline/staging/`
4. Promote draft to `L2-knowledge/` or `L3-process/` via app (action `promote_draft`)

## Agents

- Copy agents **must** cite Layer A `id` when stating founder truth.
- Forbidden: inventing founder biography not in Layer A.
- Training path: read this law → Personal DB tab → one private-agent loop round citing `data/L4-agents/`.

## Maintainer

- Layer A files: founder + designated mono maintainer chat.
- Hub ingestion API: `scripts/personal_db_ops.py` — `sinaai_maintainer` only for code changes.
