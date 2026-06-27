# Brain chatbot gap report (LOCKED v1)

**Saved:** 2026-06-27T05:30:00Z  
**Purpose:** Track public Brain failures vs Cursor parity — not narrative closeout.

---

## Baseline (2026-06-27 v2 upgrade)

| Metric | Before v1 | After v2 |
|--------|-----------|----------|
| Chunks | 31 | **371** |
| Chars | ~7k | **~179k** |
| Source files | 12 manual | **112** (68 HTML + 24 JSON + docs + manual) |
| Retrieval | keyword lite | **BM25 + intent + SQLite FTS5** |
| Database | none | `brain_knowledge_v1.sqlite` |

## Baseline (2026-06-27 v1)

| Gap | Bot before | Cursor | Fix |
|-----|------------|--------|-----|
| No RAG / manifest | Prompt-only system string | Full repo search | Manifest + bundle + hybrid retrieval |
| No health knowledge fields | `openrouter_ready` only | N/A | `knowledge.*` on GET status |
| No eval harness | 4 smoke curls in validate script | Ad-hoc | `test_brain_chat_quality_v1.py` buckets |
| Pricing drift risk | Hardcoded in prompt | Reads pricing.html | `pricing-matrix.md` distill |
| Forge vs homepage | Implicit in prompt | Any doc | `forge-runtime.md` + eval question |
| Internal leak risk | Long prompt | Rules-bound | Allowlist + secret strip in distill |

---

## Known P0 regressions to watch

| ID | Question | Required behavior |
|----|----------|-------------------|
| what-is-sourcea | What is SourceA? | Forge + execution; no lead price |
| ide-cloud | Do you have IDE cloud? | Forge Terminal path; no "we don't offer" |
| records-recovery | You just give me records?? | Acknowledge + reframe execution |
| try-without-install | Try Forge without install? | Browser demo URL; must not refuse |

---

## Stale sources flagged

- `founder-home.html` if diverges from `sourcea-positioning-v1.json` v3.2+
- Any copy still saying "book a call" as primary CTA (agentic-first law)

---

## Not in public KB (by design)

- Mac control plane ports (`:13020`, `:13027`)
- `brain-os/` incidents and governance law
- OpenRouter keys, wrangler secrets
- Factory autorun / Cloud Forge Run internals

---

## Next gaps (Phases 5–10)

| Phase | Gap | Target |
|-------|-----|--------|
| 5 | Vector RAG | pgvector + embeddings on platform |
| 6 | Widget citations UI | Show `citations[]` in chat bubble |
| 7 | 100 canonical questions | Expand eval JSON |
| 8 | Live health in KB | api status cache for "is platform up?" |
| 9 | Intent classifier | buyer vs developer routing |
| 10 | Deflection metrics | Langfuse + intake conversion |

---

## Update protocol

When founder reports "Brain got X wrong":

1. Reproduce on live worker
2. Classify: PUBLIC_SHOULD_KNOW vs INTERNAL_ONLY
3. If public — manifest + distill + sync + eval + this file
4. If internal — add anti-ICP eval question
