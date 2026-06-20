# Sina Knowledge Library — Master Index

**Version:** 1.0  
**Location:** `~/Desktop/SourceA/knowledge-library/`  
**Purpose:** Train agents by field — extract → gather → merge → unify → book. **Not** locked source; **not** a junk drawer.  
**Locked source stays at SourceA root.** This library **points to** and **grows from** attachments, chats, and research without replacing `*_LOCKED_vN.md`.  
**Pipeline law:** `PIPELINE_LAW.md`  
**Agent skill:** `~/.cursor/skills/sina-research-lessons/SKILL.md`

---

## Why this exists

- One essay → one book per **field** (many fields, many books over time).
- Related subjects stay **together** under one field folder.
- Content stays **pure** — originals stay in place; library uses manifests + unified layers.
- Agents learn **roles** from unified essays and book outlines, not from scattered chat.

---

## Active fields

| Field ID | Folder | Status | First essay | Book |
|----------|--------|--------|-------------|------|
| `pre-llm-world-model` | `fields/pre-llm-world-model/` | **Active** — D5 thread | `04-unified/ESSAY_v1_NO_MODEL_WITHOUT_PACKET.md` | `05-books/BOOK_OUTLINE_v1.md` |
| `context-engineering` | `fields/context-engineering/` | Planned — parent of RAG/harness patterns | — | — |
| `agent-training-roles` | `fields/agent-training-roles/` | Planned — role packets for hub agents | — | — |
| `governance-unification` | `fields/governance-unification/` | Planned — alignment + critic + unify engine | — | — |
| `commercial-governance` | `fields/commercial-governance/` | **Active** — W3 / market / 100 plans | `04-unified/ESSAY_v1_RECEIPTS_BEAT_DASHBOARDS.md` | `05-books/BOOK_OUTLINE_v1.md` |
| `execution-spine` | `fields/execution-spine/` | Planned — A1–A4, validators, queue | — | — |

---

## Pipeline stages (every field)

| Stage | Folder | What goes here | Purity rule |
|-------|--------|----------------|-------------|
| **1 Extract** | `01-extracts/` | Manifests + pointers to raw sources (chat extracts, critic pastes, attachments) | Never edit originals; add manifest row only |
| **2 Gather** | `02-gathered/` | Curated pulls — tables, quotes, one screen per source | Cite source path on every block |
| **3 Merge** | `03-merged/` | Related subjects combined (same field only) | Drop duplicates; keep provenance list |
| **4 Unify** | `04-unified/` | One essay per topic — readable, teachable, role-ready | Single voice; footnotes to merge layer |
| **5 Book** | `05-books/` | Outline → chapters → field book for agent training | Grows from unified essays only |

---

## Canonical pointers (do not duplicate)

| Artifact | Canonical path |
|----------|----------------|
| WTM map | `WORLD_TARGET_MODEL_MAP_LOCKED_v5.md` |
| Packet schema | `LLM_CONTEXT_PACKET_SCHEMA_LOCKED_v1.md` |
| Alignment law | `SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md` |
| WTM attachments | `archive/attachments/wtm/` |
| Machine roadmap | `scripts/system_roadmap.py` |
| Chat Unify extracts | `~/.sina/chat-unify/extracts/` |

---

## How agents use this

1. **Research turn** → write extract manifest → gather → merge if related → unify essay → update book outline.  
2. **Training a role** → read `04-unified/` + `05-books/` for that field; read locked source for law.  
3. **Never** replace locked docs from library prose — convince gate → sub-step → vN+1 only.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-05 | Library v1 · field `pre-llm-world-model` seeded from gate research thread |
| 2026-06-05 | Dual lineage law — Claude trigger (A) + Cursor agent synthesis (B); see `CURSOR_AGENT_POST_CLAUDE_SYNTHESIS_ATTACHMENT_v1.md` |
