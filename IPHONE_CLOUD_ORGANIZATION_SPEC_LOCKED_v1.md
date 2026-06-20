# iPhone Cloud — organization spec (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
| | |
|--|--|
| **Version** | `IPHONE-CLOUD-ORG-1.0-LOCKED` |
| **Locked** | 2026-06-04 |
| **Source dump** | `~/Desktop/iphone Cloud/` (~1,900 files, 366 top entries) |
| **Parent pipeline** | `SinaaiMonoRepo/.../data/L0-meta/011-chat-consolidation-pipeline.md` |
| **Rule** | **Classify before move.** Staging stays on Desktop until ASF approves each batch. |

---

## 1. What you have today (inventory)

| Area | Files (approx) | Quality |
|------|----------------|---------|
| **Sina Business/** | 905 | Richest — Noetfield, Oracle, Primepath, 777, Agent AI, corporate |
| **Next Steps 777/** | 256 | 777 Foundation ops |
| **The 777 Foundation/** | 196 | Board, fundraising, landing |
| **Prompt Pack 777/** | 68 | Prompts / kits |
| **Root loose files** | 333 | **Problem** — duplicates, mixed entities |
| **Witness / Token / lexre / Bridge** | 50+ | Trust / product code fragments |
| **untitled folder*** | 10+ | **Inbox** — classify first |

**File types:** docx (1130), pdf (436), zip (107), html (74), xlsx/csv/pptx, some tsx (lexre).

**Naming signal:** Many files already encode **subject + doc type + version** (e.g. `noetfield_gate_protocol_procurement_ready_v1_1.docx`).

---

## 2. Three-level taxonomy (use on every file)

Every document gets **one row** in `iphone-cloud-manifest.jsonl`:

| Level | Key | Meaning | Example values |
|-------|-----|---------|----------------|
| **Subject** | `subject` | *Who / which program* | `noetfield`, `777`, `trustfield`, `virlux`, `witness`, `sina_os`, `personal`, `contractor` |
| **Field** | `field` | *What kind of work* | `legal`, `spec`, `product`, `marketing`, `finance`, `ops`, `prompt`, `code`, `hr`, `research` |
| **Spec tier** | `spec_tier` | *Authority level* | `locked`, `active`, `draft`, `archive`, `raw` |

**Optional tags:** `lang` (en|fa|mixed), `audience` (investor|partner|internal|public), `version` (v1.0), `thread_id` (from ASF registry).

### Field definitions

| Field | Put here | Not here |
|-------|----------|----------|
| **spec** | Product behavior, routing, governance, APIs, intake | Marketing one-pagers |
| **product** | SKUs, packs, catalogs, deliverable samples | Legal bylaws |
| **legal** | Corp records, resolutions, contracts, charter | Landing HTML |
| **marketing** | Decks, one-pagers, LinkedIn, landing copy | Bank void cheque |
| **finance** | Bank, insurance, unit economics models | Python code |
| **ops** | Checklists, SOP, handoff, procurement packs | Founder bio |
| **prompt** | Agent prompts, n8n, Prompt Pack | Locked SSOT |
| **code** | html, tsx, zip kits with src | Random PDF scan |
| **research** | Market maps, , capital gap | Final locked spec |
| **personal** | Passport, rental, resume, photos | Noetfield investor pack |

### Spec tier definitions

| Tier | Meaning | Destination |
|------|---------|-------------|
| **locked** | Canonical — don’t edit without version bump | `SourceA/` or repo `docs/*_LOCKED_*` |
| **active** | Current working truth | Repo `docs/` or `product/` |
| **draft** | Superseded soon or WIP | `imports/iphone-cloud/drafts/` |
| **archive** | Historical only | `imports/iphone-cloud/archive/` |
| **raw** | Unclassified / scan / duplicate | Stay in staging until classified |

---

## 3. Subject → thread → desktop home (canonical map)

| Subject code | Human name | ASF thread | Promote copies to |
|--------------|------------|------------|-------------------|
| `noetfield` | Noetfield Systems | THREAD-PORTFOLIO | `~/Desktop/Noetfield/docs/` |
| `777` | 777 Foundation | THREAD-PORTFOLIO | `~/Desktop/The 777 Foundation/` |
| `trustfield` | TrustField / Witness BC | THREAD-PORTFOLIO | `~/Desktop/TrustField Technologies/docs/` |
| `virlux` | VIRLUX / Primepath | THREAD-PORTFOLIO | `~/Desktop/VIRLUX/docs/` |
| `witness` | Witness product line | THREAD-PORTFOLIO | `TrustField` or `Noetfield` per content |
| `sina_os` | SinaPromptOS / DevBridge / PAIOS | THREAD-PROMPTOS + WIRE + SUPERBRAIN | `SourceA/`, `SinaPromptOS/`, `SinaaiMonoRepo/` |
| `investor` | Decks / bio / connector | THREAD-INVESTOR | `Sina-Investor-Package-FINAL/` |
| `factory` | MergePack / utilities | THREAD-MERGEPACK (parked) | `~/Desktop/mergepack/docs/` |
| `personal` | Career, banking, rental | *(none — private)* | `iphone Cloud/_organized/personal/` only |
| `contractor` | Contractor Business | personal ops | `iphone Cloud/_organized/contractor/` |
| `lexre` | lexre code WIP | THREAD-PORTFOLIO or archive | Repo if active else archive |

---

## 4. Current folder → subject (migration map)

Use this to **rename mentally** before physical moves:

| Current path under `iphone Cloud` | → Subject | Notes |
|-----------------------------------|-----------|--------|
| `Sina Business/Noetfield/` | `noetfield` | Split by **field** inside (Sales→marketing, Code→code, *spec* in filename→spec) |
| `Sina Business/Go /777`, `Oracle`, `Primepath` | `777` / `virlux` / mixed | Read filename; Oracle may be Noetfield product line |
| `Sina Business/ Noetfield Systems Inc – Corporate Records` | `noetfield` + **legal** | Never merge into marketing |
| `The 777 Foundation/`, `Next Steps 777/`, `Board 777/` | `777` | ops + legal + marketing |
| `Prompt Pack 777/`, `Prompts/` | `777` or `sina_os` | **field=prompt** |
| `Witness/`, `Token/` | `trustfield` / `witness` | compliance + product |
| `Bridge Parallel/`, `Witnex–landing/` | `witness` or `noetfield` | marketing/code |
| `lexre/` | `lexre` | **field=code** |
| `Sina Business/Agent AI/`, `Codex/`, `Python/` | `sina_os` | prompts + experiments |
| `Career/`, `Resume/`, `RBC/`, root passport/rental | `personal` | Do not ingest to public repos |
| `Contractor Business/` | `contractor` | |
| `untitled folder*` | `raw` | Inbox — classify each file |
| Root 333 files | **split** | Use filename tokens: `Noetfield_`, `777_`, `Witness`, `Sina_` |

---

## 5. Target folder shape (after organize)

**Done 2026-06-04:** all files under flat `_organized/{subject}/` only (**10 subjects** + `_INBOX` for unclassified).

```text
~/Desktop/iphone Cloud/
  _organized/
    777/           (146 active in `_TOPICS/` + `_archive/` — see `README_777_MERGED.md`)
    noetfield/     (723)
    personal/      (390)
    trustfield/    (137)
    witness/       (85)
    sina_os/       (22)
    investor/      (22)
    lexre/         (18)
    virlux/        (17)
    contractor/    (13)
  _INBOX/          (only if still-unclassified raw drops)
```

**Flatten:** `python3 ~/Desktop/SourceA/scripts/iphone-cloud-flatten.py`  
Legacy empty folders (`Sina Business`, etc.) may remain — delete manually in Finder.

**Promoted copies** (second step) go to repo `docs/` only when `spec_tier=locked|active` and subject matches.

---

## 6. Manifest schema (`iphone-cloud-manifest.jsonl`)

One JSON object per line:

```json
{
  "id": "ic-00001",
  "source_path": "iphone Cloud/Sina Business/Noetfield/noetfield_gate_protocol_procurement_ready_v1_1.docx",
  "subject": "noetfield",
  "field": "spec",
  "spec_tier": "active",
  "title": "Gate protocol procurement ready",
  "version": "v1.1",
  "lang": "en",
  "audience": "partner",
  "thread_id": "THREAD-PORTFOLIO",
  "promote_to": "~/Desktop/Noetfield/docs/specs/",
  "status": "classified",
  "notes": ""
}
```

**Statuses:** `unclassified` → `classified` → `promoted` → `duplicate_skip`

---

## 7. Pipeline (4 steps — same spirit as chat consolidation)

| Step | Action | Output |
|------|--------|--------|
| **1 Inventory** | Scan tree + root loose files | `iphone-cloud-inventory.csv` |
| **2 Classify** | Rule + filename + folder → subject/field/tier | `iphone-cloud-manifest.jsonl` |
| **3 Stage** | Copy (not move) into `_organized/{subject}/{field}/{tier}/` | Sorted staging |
| **4 Promote** | ASF approves batch → copy to repo + optional L2 markdown extract | Repo docs + SoT |

**Do not** auto-promote **personal** or **finance** to GitHub repos.

---

## 8. Classification rules (automatable heuristics)

| Signal | Subject | Field |
|--------|---------|-------|
| Path contains `Noetfield` | noetfield | from subfolder (Sales→marketing, Code→code) |
| Filename `*spec*`, `*protocol*`, `*routing*`, `*governance*` | infer subject | **spec** |
| Filename `*OnePager*`, `*Deck*`, `*LinkedIn*` | infer subject | **marketing** |
| Filename `*Resolution*`, `*Corporate*`, `*Charter*`, `*Application*` | infer subject | **legal** |
| Filename `*Unit_Economics*`, `*Capital*Gap*` | infer subject | **finance** or **research** |
| Filename `*checklist*`, `*SOP*`, `*handoff*` | infer subject | **ops** |
| `.html`, `.tsx`, `.zip` kit | infer subject | **code** |
| `*prompt*`, `n8n`, `Agent AI` | sina_os | **prompt** |
| Duplicate `(2)`, `(3)` in name | mark `duplicate_skip` | keep newest date |

---

## 9. Link to program command center

| Plan ID | Action |
|---------|--------|
| `SUPERBRAIN-P0` | Add todo: run Step 1 inventory on `iphone Cloud` |
| Manifest lives | `~/Desktop/SourceA/imports/iphone-cloud/` (create on first run) |

---

## 10. What agents should do

1. Read this spec before moving any file out of `iphone Cloud`.
2. Never bulk-delete or bulk-move without manifest row.
3. Prefer **copy** to `_organized/` then **promote** to repo.
4. Extract **spec** docx/pdf to markdown for L2 only when ASF requests.

---

---

## Same pattern — MergePack product repo

| | |
|--|--|
| Spec | `~/Desktop/mergepack/docs/MERGEPACK_ORGANIZATION_LOCKED_v1.md` |
| Topics | `mergepack/docs/_TOPICS/` (01-product … 06-sourcea-locks) |
| Progress | `mergepack/PROGRAM_PROGRESS.json` |
| Scripts | `mergepack/scripts/organize-mergepack-docs.py`, `update-mergepack-progress.py` |

MergePack uses **canon merge** (not 560 files) — scattered `DAY*.md` archived; read `CANON_*.md` per topic.

---

**LOCKED.** Changes → `IPHONE-CLOUD-ORG-2.0` + ASF.
