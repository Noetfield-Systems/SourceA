---
name: sourcea-cursor-agent-knowledge-audit
description: >-
  Cursor agent (Composer) knowledge audit — compare private agent answers vs public
  Brain chatbot parity. SSOT read chain, gap report, eval regression. Use when founder
  asks "why did Cursor know X but Brain didn't?" or before agent prompt/knowledge edits.
---

# SourceA Cursor agent knowledge audit skill

**Saved:** 2026-06-27T05:30:00Z  
**Sibling skill:** `.cursor/skills/sourcea-brain-chatbot-audit/SKILL.md`  
**Brain index (internal routing):** `brain-os/memory/BRAIN_KNOWLEDGE_INDEX_LOCKED_v1.md`  
**Public chat index:** `data/CHATBOT_KNOWLEDGE_MANIFEST.json`

---

## Purpose

Cursor agents have **private repo context** (4,600+ files). Public Brain has **manifest allowlist only**. This skill audits **parity gaps** — what strangers should get vs what only Cursor knows.

---

## Two knowledge planes

| Plane | Audience | SSOT | Size |
|-------|----------|------|------|
| **Cursor agent** | Founder + workers in IDE | Brain index, rules, live wire | Full repo (bounded WORK) |
| **Public Brain** | Strangers on sourcea.app | CHATBOT_KNOWLEDGE_MANIFEST | ~30 chunks, public lanes |

**Law:** Never leak internal-only paths, Mac ports, governance incidents, or secrets into public bundle.

---

## Gap audit workflow

1. **Reproduce** — ask same question in Cursor and live Brain worker
2. **Classify gap**
   - `PUBLIC_SHOULD_KNOW` → add to manifest + distill
   - `INTERNAL_ONLY` → keep out of bundle; Brain should redirect politely
   - `STALE_PUBLIC` → re-run distill from www HTML
3. **Log** in `docs/BRAIN_CHATBOT_GAP_REPORT_LOCKED_v1.md`
4. **Regression** — add to `data/brain-chat-eval-canonical-v1.json` if P0

```bash
python3 scripts/test_brain_chat_quality_v1.py --bucket p0_positioning --write-report --json
```

---

## Cursor agent read chain (before public-facing edits)

When editing Brain prompt, landing copy, or knowledge corpus:

| # | File | Why |
|---|------|-----|
| 1 | `data/CHATBOT_KNOWLEDGE_MANIFEST.json` | Public source map |
| 2 | `docs/SOURCEA_POSITIONING_ONE_LINE_LOCKED_v1.md` | Positioning law |
| 3 | `sites/.../data/sourcea-positioning-v1.json` | Machine SSOT |
| 4 | `docs/BRAIN_CHATBOT_GAP_REPORT_LOCKED_v1.md` | Known failures |
| 5 | `reports/chat_eval_last_run.json` | Last eval scores |

**Do not** inject Brain index (`brain-os/memory/`) into public worker.

---

## Parity checklist (founder question → both surfaces)

| Question type | Cursor may use | Brain may use |
|---------------|----------------|---------------|
| What is SourceA? | Full architecture | positioning-public + forge-runtime |
| Pricing | Internal bands + SSOT | pricing-matrix distilled from /pricing |
| Forge vs homepage | Any doc | forge-runtime + site-map |
| Mac Hub ports | Yes (founder) | **Forbidden** — redirect to public demo |
| OpenRouter key | Yes (ops) | **Forbidden** |
| PyPI / npm packages | If shipped + public | Only if in manifest www_url |

---

## Agent self-audit (this chat)

Before claiming "Brain should know X":

1. Is X in manifest `sources[]` with `public: true`?
2. Is distilled output newer than source? (`sync --check-only`)
3. Did eval bucket pass after last sync?
4. Was worker redeployed after bundle change?

If any NO → gap is **pipeline**, not model intelligence.

---

## Fix order (always)

```text
Edit SSOT (positioning JSON / www HTML)
  → distill_www / distill_docs
  → sync_brain_chat_knowledge
  → redeploy worker
  → test_brain_chat_quality
  → append gap report
```

---

## Mac founder session

- One light eval OK (`test_brain_chat_quality_v1.py --bucket p0_positioning`)
- No validator marathon — see INCIDENT-039
- Proof = `reports/chat_eval_last_run.json` + worker health JSON

---

## Exit

Cursor agent and public Brain agree on **P0 canonical questions** at 90%+ — Cursor may still know more internally, but strangers get cited, grounded public answers.
