# Knowledge Library Pipeline Law

**Version:** 1.0  
**Applies to:** `knowledge-library/fields/*`  
**Aligns with:** `SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md` (library = staging + teaching; locked root = source)

---

## Founder law (plain language)

We **extract** from chats and research. We **gather** what matters into one field. We **merge** only related subjects. We **unify** into one good essay. We **grow a book** from essays — one field, one book family, many fields over time.

We do **not** throw everything into one file. We do **not** fragment the same subject across SourceA. We do **not** lose purity by copying locked docs — we **point** and **teach** above them.

---

## Mandatory sequence

```
EXTRACT → GATHER → MERGE → UNIFY → BOOK
```

| Step | Agent action | Output | Stop if |
|------|--------------|--------|---------|
| **Extract** | Save manifest row + pointer to raw | `01-extracts/MANIFEST.md` entry | No raw source path |
| **Gather** | Pull key tables, quotes, verdicts | `02-gathered/GATHER_*.md` | Duplicate of locked source verbatim |
| **Merge** | Combine gathered items same topic | `03-merged/MERGE_*.md` | Unrelated subjects mixed |
| **Unify** | One essay, teachable | `04-unified/ESSAY_*.md` | Essay cites no sources |
| **Book** | Outline + chapters from essays | `05-books/BOOK_*.md` | Chapter not traced to essay |

---

## Field rules

1. **One field = one subject family** (e.g. pre-LLM gate, not “everything AI”).
2. **Cross-field link** in index only — do not merge unrelated fields.
3. **Thread tracking** — every extract tags active ASF/WTM threads.
4. **Energy** — skip gather if extract is reject/contradict; do not polish noise.

---

## Active threads (tag on every extract)

- `WTM-D5` — pre-LLM world model, gate, D5 current  
- `THREAD-FACTORY` — P0 RunReceipt  
- `THREAD-MERGEPACK` — product lane  
- `THREAD-CHAT-CONSOLIDATION` — Chat Unify → L2/L3  

---

## Relation to Chat Unify

| Tool | Stage |
|------|-------|
| Chat Unify per-chat extract | **Extract** (raw) |
| Chat Unify rollup | **Gather** across chats |
| Knowledge library merge | **Merge** same field |
| Knowledge library unified essay | **Unify** |
| Book outline | **Book** start |

Chat Unify output can land in `01-extracts/` via manifest pointer to `~/.sina/chat-unify/extracts/`.

---

## Agent training

- **Role packet** = unified essay + book chapter + locked law pointers (not essay alone).
- **Do not train** on pre-unify chat dumps.
- **Validators** = receipts for field (e.g. `validate-vector-retrieval-v1.sh` for pre-LLM field).
