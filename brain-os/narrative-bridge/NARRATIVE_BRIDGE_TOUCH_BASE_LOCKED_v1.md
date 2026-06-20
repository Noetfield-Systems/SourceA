# Narrative Bridge — Touch Base (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-11-NARRATIVE-BRIDGE  
**Authority:** ASF · **human comfort layer** — megachat translator → disk → any new chat  
**Parent:** `SOURCEA_TODAY_SESSION_UNIFIED_CLOSEOUT_RECEIPT_2026-06-11_LOCKED_v1.md` §1 row 10 · `TERMINOLOGY_DICT`  
**Skill:** `agent-skills/shared/narrative-translator/SKILL.md` · `@sina-narrative-translator`  
**Living snapshot:** `brain-os/narrative-bridge/LATEST_TOUCH_BASE_LOCKED_v1.md` (update on touch-base)  
**Megachat anchor:** `a53f3fa1` · workspace `SinaaiDataBase` · `ecosystem_master_catalog_v1.py` → `mega_chat_anchors`

---

## 0. One sentence

> **Megachat translates founder narrative; disk bridge copies that translator into every light chat; Brain/Worker enforce with validators — you need both layers, not one.**

---

## 1. Two brains (both required)

| Layer | Feels like | Canonical | Does |
|-------|------------|-----------|------|
| **Narrative / library** | Human · thread · “gets me” | Megachat `a53f3fa1` + this bridge | Extract intent · compare · touch base |
| **Machine / courthouse** | Cold · enforceable · proof | SourceA Brain + spine G1–G7 | Route · gate · validator PASS |

**Rule:** Megachat = **LENS** (extract). SourceA = **BUILDER** (implement). Never invert.

---

## 2. Files (SSOT)

| File | Role |
|------|------|
| **This doc** | Law — ritual · reply shape · handoff |
| `LATEST_TOUCH_BASE_LOCKED_v1.md` | **Living** — last founder intent snapshot (~15–40 lines) |
| `SOURCEA_FOUNDER_MACHINE_TERMINOLOGY_DICTIONARY_LOCKED_v1.md` | Human word ↔ machine row |
| `agent-skills/shared/narrative-translator/SKILL.md` | Translator reply contract |
| `agent-skills/shared/conscious-recovery/SKILL.md` | Transcript + disk recovery (pair always) |

---

## 3. Touch-base ritual

### A — In megachat (extract — 5 min)

Founder or agent ends a heavy stretch with:

```text
TOUCH BASE — update bridge
```

Agent must:

1. Read `LATEST_TOUCH_BASE` + search transcript `a53f3fa1` for disputed topics.
2. Rewrite `LATEST_TOUCH_BASE_LOCKED_v1.md` using §4 template.
3. **Machine propagate:** `python3 scripts/megachat_bridge_touch_v1.py --propagate --json` (skills · validators · ACTIVE_NOW · anchors RT).
4. Log broker event optional; **must** run `session-close` summary if disk work touched.

### B — In new light chat (consume — 2 min)

**Workspace:** `~/Desktop/SourceA` (Brain/Worker) — not SinaaiDataBase for builds.

First message:

```text
MANDATORY READ:
1. @brain-os/narrative-bridge/LATEST_TOUCH_BASE_LOCKED_v1.md
2. @sina-narrative-translator
3. @sina-conscious-recovery
4. @SOURCEA_FOUNDER_MACHINE_TERMINOLOGY_DICTIONARY_LOCKED_v1.md

TASK: <one sentence>
PROOF: <one validate-*.sh>
```

Brain also: `bash scripts/brain-session-start.sh`

### C — Proof touch-base worked

Light chat reply must:

1. **TRANSLATE** — one plain sentence of founder intent.
2. **MAP** — one authority row or `*_LOCKED` path.
3. **PROVE** — one validator command (or honest OPEN).

If only “I remember megachat” with no path → **FAIL** — rerun conscious-recovery.

---

## 4. LATEST template (copy into living file)

```markdown
# Latest Touch Base (LOCKED — living)

**Updated:** YYYY-MM-DDTHH:MM:SSZ
**From:** megachat a53f3fa1 | maintainer extract
**For:** Brain · Worker · light chats

## MEANT (founder voice)
- …

## MAPS_TO (disk)
| Theme | Row / path |
|-------|------------|
| … | … |

## NOT (misreads to avoid)
- …

## NEXT_MACHINE
- Brain: …
- Worker: …

## PROOF
- `bash scripts/…`

## ANCHOR_SEARCH
- transcript: a53f3fa1 — keywords: …
```

---

## 5. Translator reply shape (every governance turn)

```text
TRANSLATE — <founder intent in plain words>
MAP — <row or LOCKED path>
MACHINE — <task · gate · proof command>
OPEN — <honest gaps only>
```

Pair with conscious-recovery **FOUND** format when recovering threads.

---

## 6. Assignment law (unchanged)

| Chat | Workspace | Job |
|------|-----------|-----|
| Megachat ECOSYSTEM | `SinaaiDataBase` | Touch base · bridge extract · narrative compare |
| Brain | `SourceA` | Route · pick · spawn |
| Worker | `SourceA` | Build · receipts |

See `brain-os/lanes/MANDATORY_CHAT_HANDOFF_INDEX_LOCKED_v1.md`.

---

## 7. Proof scripts

```bash
cd ~/Desktop/SourceA
bash scripts/validate-narrative-bridge-v1.sh
bash scripts/sync-cursor-agent-skills.sh
python3 scripts/ecosystem_master_catalog_v1.py --json
```

---

*End NARRATIVE_BRIDGE_TOUCH_BASE*
