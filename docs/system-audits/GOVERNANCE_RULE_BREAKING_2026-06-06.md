# Governance — rule breaking diagnosis and T0+T1 enforcement

**Saved:** 2026-06-06T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit @ 2026-06-16T05:49:57Z  

---

## Why rules break every chat

| # | Root cause | Mechanism |
|---|------------|-----------|
| 1 | Law without enforcement | 138 LOCKED docs — nothing blocks a bad reply pre-send |
| 2 | Contradictory founder docs | ASF_DAILY_CARD vs No Terminal (fixed T0+T1) |
| 3 | Chat ≠ memory | Each session re-derives; no persistent agent law injection |
| 4 | Law surface area | 141+ LOCKED files — search miss = violation |
| 5 | Tool reflex | Cursor default: run bash when user says "fix" |
| 6 | Archive vs ops confusion | SinaaiDataBase used for ops instead of SourceA worker |
| 7 | Three loops confusion | plan-no-asf vs dispatch-day vs agent_loop |

**Path to near-zero:** Pre-reply block hook + single machine truth chain + hub-only founder UX.

---

## T0+T1 zero-breaking enforcement pack — DONE

| Item | Deliverable | Status |
|------|-------------|--------|
| F1 | `founder/ASF_DAILY_CARD.md` hub-only | DONE |
| F2 | `validate-founder-docs-no-terminal-v1.sh` CRITICAL in FCB | DONE |
| M2 | `strategic_synthesis_hub.py` honest gates | DONE |
| M4 | `~/.cursor/hooks.json` + `founder-reply-lint.sh` | PARTIAL — **warn only** |
| PRIORITY | Evidence row `T0+T1 zero rule-breaking enforcement` | DONE |

**Autonomy stack also closed:** sa-0123–sa-0201 per PRIORITY (prompt_router, execution_kernel, runtime spine).

---

## M4 hook gap

- **Current:** `founder-reply-lint.sh` warns on Terminal patterns in assistant reply  
- **Missing:** Block / reject send — founder can still receive Terminal instructions  
- **P1 fix:** Upgrade hook to hard block or require hub-only phrasing

---

## No Terminal law chain

```
SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md
  → validate-founder-docs-no-terminal-v1.sh
  → find_critical_bugs.py (CRITICAL)
  → founder/ASF_DAILY_CARD.md (aligned)
```

---

## Brain routing rules (not new law)

1. Search `BRAIN_RULES_AUTHORITY_INDEX_LOCKED_v1.md` first  
2. Read live pick — one `sa-XXXX` per worker  
3. Never parallel rules invented in chat  
4. SinaaiDataBase = archive; SourceA = ops  
5. `do_not_redo` list is authoritative for closed tasks  

---

## Remaining governance gaps

| Gap | Priority |
|-----|----------|
| M4 block (not warn) | P1 |
| Hub sa-queue tab | P1 |
| important_docs_index Canada AI | P2 |
| ARCHITECT rejected YAML cleanup | P2 |

---

## Verdict

**Disk law is now aligned** post T0+T1. **Runtime enforcement** still depends on founder discipline + warn-only hook. Near-zero requires **block hook** + **hub queue UX** so founder never needs Terminal for pick/closeout visibility.
