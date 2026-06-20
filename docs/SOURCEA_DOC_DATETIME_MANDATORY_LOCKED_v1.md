# SourceA Doc Datetime Mandatory — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-16T05:47:17Z · **Authority:** Founder order — mandatory for all agents and humans writing docs  
**Path:** `~/Desktop/SourceA/docs/SOURCEA_DOC_DATETIME_MANDATORY_LOCKED_v1.md`  
**Enforcement:** `.cursor/rules/019-doc-datetime-mandatory.mdc` (alwaysApply)  
**Validator:** `bash scripts/validate-doc-datetime-header-v1.sh [path]`

---

## 0. One sentence

> **Every doc logged must declare when it was written or last saved — date and exact UTC time — in the header; date-only headers are invalid.**

---

## 1. Required header field

| Field | Format | Example |
|-------|--------|---------|
| **Saved:** | `YYYY-MM-DDTHH:MM:SSZ` | `2026-06-16T05:47:17Z` |

- **Seconds required** — `T05:47Z` without seconds is **FAIL**
- **UTC only** on the `Saved:` line (suffix `Z`)
- Optional local line: `**Saved at (local):** 2026-06-16 01:47:17 EDT`

---

## 2. Placement

- Within the **first 12 lines** of the file
- Same metadata block as `Version`, `Path`, `Authority`
- On every **material edit**, update `Saved:` to write-time UTC

---

## 3. Scope (mandatory)

| Path pattern | Required |
|--------------|----------|
| `docs/**/*_LOCKED*.md` | Yes |
| `docs/**/*.md` (new SAVE TO) | Yes |
| `brain-os/**/*_LOCKED*.md` | Yes |
| `archive/attachments/**/*.md` | Yes |
| `RESEARCH/**/*.md` | Yes |
| Agent chat replies | No (disk docs only) |

---

## 4. Forbidden

| Pattern | Status |
|---------|--------|
| `**Saved:** 2026-06-16` | FAIL — date only |
| No Saved line on new LOCKED doc | FAIL |
| Stale Saved after material edit | FAIL — update on save |

---

## 5. Agent workflow

1. Before writing doc → note UTC: `date -u +"%Y-%m-%dT%H:%M:%SZ"`
2. Put `**Saved:** <iso>Z` in header
3. Run `bash scripts/validate-doc-datetime-header-v1.sh <path>`
4. FAIL → fix header before claiming SAVE complete

---

## 6. Acceptance

- [ ] `.cursor/rules/019-doc-datetime-mandatory.mdc` exists · alwaysApply true  
- [ ] Validator PASS on all docs touched in same SAVE session  
- [ ] No new date-only `Saved:` headers in `docs/`  

**END LOCKED v1.0.0**
