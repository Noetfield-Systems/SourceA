# SourceA Founder Message Normalization (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-11-FOUNDER-MSG-NORM  
**Authority:** ASF · **parse ASF orders without case friction**  
**Parent:** `SOURCEA_LIVE_FOUNDER_DECISION_FORM_LOCKED_v1.md` · `TERMINOLOGY_DICT`  
**Machine:** `scripts/live_founder_decision_form_v1.py` · `normalize_founder_text()`  
**Row ID:** `FOUNDER_MSG_NORM`

---

## 0. One sentence

> **Founder text in ALL-CAPS is 100% equivalent to the same text in mixed or lowercase — agents normalize before matching ASF orders, PICK keys, and Track titles.**

---

## 1. Locked rules

| ID | Rule | Effect |
|----|------|--------|
| **NORM-CAPS** | **CAPS = non-caps** for intent equivalence | `PICK`, `FIVE-STEP`, `WTM`, `TRUSTFIELD` = `pick`, `five-step`, `wtm`, `trustfield` after normalize |
| **NORM-TRIM** | Strip leading/trailing whitespace | Before compare |
| **NORM-COLLAPSE** | Collapse internal runs of spaces to one | Before compare |
| **NORM-ASF-PREFIX** | `ASF:` prefix optional case-insensitive | `asf: five-step — pick:` matches canonical |
| **NORM-KEY** | Option keys **A–D** case-insensitive | `a` = `A` for PICK lines |

**Forbidden:** Rejecting or re-asking because founder used caps. **Forbidden:** Treating CAPS as anger signal for governance (conduct is separate).

---

## 2. Where machines apply

| Consumer | Apply on |
|----------|----------|
| `live_founder_decision_form_v1.py` | PICK parse · question match |
| Five-step SAY/PICK | Founder reply templates |
| `founder_request_tracker.py` | Title dedupe key (`title_key`) |
| Future: `cursor_entry_gate.py` scan_text | Order detection |

---

## 3. Evidence

| Source | Statement |
|--------|-----------|
| ASF directive | Writing in capital letters is **100% equal** to non-capital letters for labels and orders |
| Form row | `LIVE_DECISION_FORM` §2 **NORM-CAPS** |

---

## 4. Examples

| Founder writes | Machine reads |
|----------------|---------------|
| `ASF: FIVE-STEP — PICK: 2.05 B` | `asf: five-step — pick: 2.05 b` → step 2.05 key B |
| `CONTINUE PLAYBOOK` | `continue playbook` |
| `TRUSTFIELD IS EQUAL` | `trustfield is equal` → matches ECO-EQUAL |

---

*End founder message normalization*
