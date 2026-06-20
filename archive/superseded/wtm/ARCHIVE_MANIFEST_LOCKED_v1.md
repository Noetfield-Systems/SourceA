# WTM superseded docs — archive manifest (LOCKED)

**Saved:** 2026-06-06T18:42:41Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0  
**Policy:** When hub map / roadmap upgrades, **vN** moves here; **vN+1** is canonical at SourceA root.  
**Archive root:** `archive/superseded/wtm/`  
**Maintainer:** ASF · executor moves files + updates manifest before hub rebuild  

---

## Supersession log

| Date | Superseded (archive path) | Canonical replacement | Evidence |
|------|---------------------------|----------------------|----------|
| 2026-06-05 | `v1/WORLD_TARGET_MODEL_MAP_LOCKED_v1.md` | `WORLD_TARGET_MODEL_MAP_LOCKED_v2.md` | Hub payload v2.6 · phases A→B→C→D · 12-step journey A1.1–A5.3 · Future panel lists all Phase D steps · INCIDENT-003 phase naming law |
| 2026-06-05 | `v1/WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v1.md` | `WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v2.md` | Law table still said D→C→B→A; hub UI canonical A→B→C→D |
| 2026-06-05 | `v1/SINA_BIG_PICTURE_ROADMAP_LOCKED_v1.md` | `SINA_BIG_PICTURE_ROADMAP_LOCKED_v2.md` | §0.5/§2 used reverse phase letters (A=pre-LLM, D=spine); contradicted hub swimlanes |
| 2026-06-05 | `v1/SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v1.md` | `SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2.md` | Cross-links to v1 big picture; build order unchanged but phase labels + hub alignment required |
| 2026-05-27 | `v2/WORLD_TARGET_MODEL_MAP_LOCKED_v2.md` | `WORLD_TARGET_MODEL_MAP_LOCKED_v3.md` | Hub payload v3.0 · alignment law Orders 7–12 · 4 sub-steps: A1.1.1, A2.1.1, A2.1b, A5.3.1 · 16 Phase D steps |
| 2026-06-05 | `v3/WORLD_TARGET_MODEL_MAP_LOCKED_v3.md` | `WORLD_TARGET_MODEL_MAP_LOCKED_v4.md` | INCIDENT-004 · step IDs aligned to phase letters · payload v4.0 · A1–A4, B1–B6, C1–C7, D1–D16 |
| 2026-06-05 | `v4/WORLD_TARGET_MODEL_MAP_LOCKED_v4.md` | `WORLD_TARGET_MODEL_MAP_LOCKED_v5.md` | FINAL roadmap v5.0 · authority law · graph/memory/planning matrices · retrieval pipeline D4→D7→sources |
| 2026-05-27 | — (same MAP v5 file) | MAP v5.2 header + payload v5.2 | Governance unification · `SINA_GOVERNANCE_ENTRY` + `SINA_AUTHORITY_INDEX_MAP` · duplicate rule tables → pointers |

---

## Not archived (still canonical v1)

| Doc | Why kept |
|-----|----------|
| `WORLD_TARGET_MODEL_ARCHITECTURE_DIAGRAM_LOCKED_v1.md` | Blueprint still matches hub `architecture_blueprint`; cross-links updated to MAP v2 |
| `WORLD_TARGET_MODEL_UI_RESEARCH_LOCKED_v1.md` | UI shell spec; historical D→C→B→A prose flagged agent-only |
| `WORLD_TARGET_MODEL_UI_INCIDENT_REPORT_LOCKED_v1.md` | Incident record — never delete |
| `WORLD_TARGET_MODEL_PHASE_NAMING_INCIDENT_REPORT_LOCKED_v1.md` | Incident record — never delete |
| `SINA_EXECUTION_INTELLIGENCE_STACK_LOCKED_v1.md` | Phase B detail — content still valid |
| `SINA_RUNTIME_STACK_LOCKED_v1.md` | Phase C detail — content still valid |

---

## Attachments (not version bumps)

Beneficial extras from analyzed suggestions → `archive/attachments/<track>/`  
Do **not** merge attachments into master map as competing step lists.  
See `SINA_SOURCE_ALIGNMENT_LAW_LOCKED_v1.md`.

| Date | Example (not source) | Parent source |
|------|----------------------|---------------|
| 2026-06-05 | `archive/attachments/examples/wtm/CHATGPT_13STEP_WTM_REVIEW_EXAMPLE_LOCKED_v1.md` | MAP v2 · 12-step order kept |
| 2026-05-27 | (same example file) | MAP v3 · extras promoted to sub-steps per law §7.3 |

---

## Upgrade procedure (executor)

1. Rebuild hub payload; confirm `system_roadmap.version` + `phase_order` + step list.
2. Write new `*_LOCKED_v{N+1}.md` at SourceA root.
3. `mv` old `*_LOCKED_vN.md` → `archive/superseded/wtm/vN/`.
4. Append row to this manifest with evidence (hub version, incident ID, diff summary).
5. Update `scripts/system_roadmap.py` `MAP_DOC`, `LAW_DOC`, `WTM_LOCKED_DOCS`.
6. Run `python3 scripts/build-sina-command-panel.py`.
7. Grep SourceA for old `*_vN.md` paths; fix cross-links.

**Script:** `scripts/archive-superseded-wtm-doc.py`

---

## Step ID stability law (all versions)

Phase **letters** on founder UI = **A→B→C→D** (build order).  
Step **IDs** stay historical: `D1` (spine), `C1` (intel), `B4` (runtime), `A1.1` (pre-LLM) — do not rename without migration plan.
