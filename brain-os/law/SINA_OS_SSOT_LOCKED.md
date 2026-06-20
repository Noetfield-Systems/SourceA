# Sina OS — Master Source of Truth

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
## INTERNAL ONLY — MacBook local agents — NOT for GitHub / NOT public online

**Version:** 3.1 — FINAL LOCKED  
**Status:** Phase 0 — Declaration only. Nothing here is a build instruction.  
**Authority:** ASF (human founder) → Sina OS governance stack  
**Visibility:** `INTERNAL_LOCAL_ONLY` — never commit this file to git, never push to remote  
**Canonical location:** `brain-os/law/SINA_OS_SSOT_LOCKED.md` (repo-relative)  
**Locked:** 2026-05-31
**Phase 1 work plan (read-only, future):** `/Users/sinakazemnezhad/Desktop/SourceA/PHASE1_UNIFIED_BLUEPRINT_v2_3.md`

---

> **What this document is.**
> The single, non-overlapping, non-ambiguous reference for the entire Sina MonoRepo ecosystem.
> Every session, every agent, every contributor reads this first — before touching code, before reading README, before continuing any prior thread.
> It is not a build plan. It is not a product spec. It is the declared structure of the system.

---

## SSOT Lock Statement

The single Source of Truth for the entire Sina MonoRepo ecosystem is **this file on the MacBook Desktop**, plus optional local mirrors under `SinaaiMonoRepo/SinaaiDataBase/governance/` when working in the monorepo (`system_registry.json`, `ANNOUNCEMENT_BOARD.md`). **This master file lives in `Desktop/SourceA/` — internal only — never commit to git or publish online.** Sina OS is governance-only — declarative, building, not a runtime. ASF is the only human override. SinaaiDataBase stores truth but does not govern or execute. SinaaiRuntime executes on `:8000` only and may not invent structure. UI observes and controls without being authoritative. Noetfield is a future isolated product — docs only today. All other products are declared entities, not executable until announced. Legacy paths (`backend/`, `cacos/`, extra Telegram stacks) are frozen and not authoritative. Golden Edge is an optional scoring tool, not a governance layer. Git is the future integrity and enforcement layer — not a second SSOT — activated in Phase 2. No agent, session, or contributor may treat the codebase, README, or prior agent designs as structural truth without reading this stack first.

---

## 1. The Locked Core Model

```
ASF              → final human authority for all registry and conflict decisions
Sina OS          → declares structure (governance only — not a runtime)
SinaaiDataBase   → stores truth (no authority, no execution)
SinaaiRuntime    → executes what has been declared (:8000 only)
UI               → observes and surfaces control (:3000)
Git              → makes truth durable (Phase 2 — not yet active)
Noetfield        → future isolated product (docs only today — not a Runtime submodule)
```

**One sentence:**
Sina OS declares → DataBase stores → Runtime executes → UI observes → Git preserves → Noetfield (when built) runs isolated.

---

## 2. Authority Hierarchy

One hierarchy. No ties. No parallel authorities.

```
1. ASF (human founder)            ← only override; approves structural changes
2. Sina OS governance stack       ← declarative structural authority
3. L0-law tier                    ← wins identity and boundary disputes
4. All other documents            ← subordinate; must align to the above
```

**LAW PURITY (alive SSOT):** `SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md` §**LAW PURITY POLICY** — law=law 100% · no fragmentation · no duplication · no mixing unrelated subjects · ask ASF if unknown. Router §11 points here; do not restate.

**AGENT CONDUCT (alive SSOT):** `SOURCEA_NO_FAKE_PROGRESS_ENTERPRISE_SHIP_LOCKED_v1.md` — **no fake progress** · proven evidence · meaningful effect · result-driven acts/plans · enterprise-grade ship only. UI green ≠ done. Valid YES / form 0 open / chat claims without disk receipt = **NOT progress**.

**What is never a structural authority:**
- The codebase (code reflects declared structure; it does not define it)
- README or ROADMAP (narrative documents — subordinate to registry)
- Agent memory or prior session outputs (must re-read SSOT at session start)
- Git history (integrity layer, not author of truth)
- Golden Edge `:8001` (optional scoring tool — not governance)
- Layer A docs (`data/L0–L4`) (identity and mandates — subordinate to `governance/`)

---

## 3. System Registry — Locked

### Meta layer

| ID | Name | Role | Status |
|---|---|---|---|
| `asf` | ASF | Human founder — final authority for registry changes and conflict resolution | Active |
| `sina_os` | Sina OS | Governance authority — declares structure, naming, status | Building |

### Core systems

| ID | Name | Path | Port | Exactly one role | Status |
|---|---|---|---|---|---|
| `sinaai_database` | SinaaiDataBase | `SinaaiDataBase/` | none | Truth storage | Active |
| `sinaai_runtime` | SinaaiRuntime | `SinaaiRuntime/` | `:8000` | Execution engine — primary spine | Active |
| `ui` | UI Dashboard | `ui/` | `:3000` | Observation and human control surface | Active |
| `scripts` | System Operations | `scripts/` | none | Host and ops automation | Active |
| `github_triggers` | GitHub Workflows | `.github/workflows/` | none | External event triggers | Active |
| `golden_edge` | Golden Edge | `SinaaiDataBase/governance/golden_edge/` | `:8001` | Optional scoring tool (subordinate utility) | Optional |
| `backend` | Backend | `backend/` | `:8010` | Legacy execution | Frozen |
| `cacos` | CACOS-N | `SinaaiRuntime/cacos/` | `:8020` | Legacy parallel OS | Deprecated |

### Product entities

| ID | Name | Path | Status | Executable now |
|---|---|---|---|---|
| `noetfield` | Noetfield | `SinaaiDataBase/noetfield/` | Docs only | No |
| `trustfield` | TrustField Technologies | `Desktop/TrustField Technologies/` (external) | Separate company — active delivery; may collaborate or overlap with Noetfield | Yes (delivery repo) |
| `virelux` | Virelux | — | Not implemented | No |
| `loadfield` | LoadField | — | Removed from scope | No |
| `seven_system` | 777 / Seven System | — | Runtime cycle signal only | No |

**Rule:** A product entity becomes executable only when Sina OS publishes a registry status change and an ANNOUNCEMENT_BOARD entry. Documentation is not activation.

---

## 4. Authority Table — One Role Per System

| System | Exactly one role | May decide structure? | May execute? | Is SSOT? |
|---|---|---|---|---|
| ASF | Human meta-control | Yes — final | No | Approves changes |
| Sina OS | Governance — declares structure | Yes — declarative | No | Yes — author |
| SinaaiDataBase | Truth storage | No | No | Stores SSOT files |
| SinaaiRuntime | Execution engine | No | Yes | No |
| UI | Observation + human control surface | No | No (display/trigger only) | No |
| scripts | Host ops automation | No | Yes (host only) | No |
| GitHub workflows | External event triggers | No | Triggers Runtime | No |
| Golden Edge | Optional scoring tool | No | Yes (scoring API only) | No |
| backend | Legacy execution | No | Legacy only | No |
| cacos | Legacy parallel OS | No | Isolated legacy | No |
| Noetfield | Future product spec | No | No (yet) | Product specs only |
| TrustField Technologies | Separate company — external delivery; optional collaboration/overlap with Noetfield | No | Yes (own repo/stack) | Own SOT in delivery repo |
| Virelux | Placeholder product | No | No | No |
| 777 | Runtime signal concept | No | No | No |
| Git | Integrity and enforcement (Phase 2) | No | No | Verifies SSOT |

---

## 5. Port Map — Locked

| Port | System | Role | Status |
|---|---|---|---|
| `:8000` | SinaaiRuntime | Primary execution spine | **Active — canonical** |
| `:3000` | UI | Observation and control dashboard | Active |
| `:8001` | Golden Edge | Optional scoring tool (subordinate) | Optional |
| `:8010` | backend | Legacy | Frozen — no new work |
| `:8020` | cacos | Legacy parallel OS | Deprecated — no new work |

**Rule R4 (locked):** Primary spine is `:8000` only. `:8010` and `:8020` are not valid execution paths.

No port: Sina OS (governance only), SinaaiDataBase (file-based), scripts, GitHub workflows.

---

## 6. SSOT File Stack — Read Order

When any question about structure arises, read these files in this order. Higher entries win on conflict.

```
1. /Users/sinakazemnezhad/Desktop/SourceA/SINA_OS_SSOT_LOCKED.md   ← this file — master SSOT (INTERNAL)
2. SinaaiMonoRepo/SinaaiDataBase/governance/system_registry.json
3. SinaaiMonoRepo/SinaaiDataBase/governance/ANNOUNCEMENT_BOARD.md
4. SinaaiMonoRepo/SinaaiDataBase/governance/boundaries.json
5. SinaaiMonoRepo/SinaaiDataBase/L0-law/three-system-boundary.md
6. SinaaiMonoRepo/SinaaiDataBase/data/L0-meta/002-sot-hierarchy-registry.md
7. SinaaiMonoRepo/SinaaiDataBase/data/L1-identity/001-sina-core.md
8. SinaaiMonoRepo/AGENTS.md
```

**Layer A** (`data/L0–L4`) = identity and agent mandates. Subordinate to `governance/`. Must align with the registry — not the other way around.

**Git** = integrity layer (Phase 2, private repo only). **This Desktop master SSOT is never pushed to public git.** Local monorepo governance files may be committed later — this Desktop file may not.

---

## 7. Governance Rules — Locked

**G1 — Sina OS is the only naming authority.**
No system, subsystem, or product entity may be added, renamed, or removed without a registry update and an ANNOUNCEMENT_BOARD entry.

**G2 — SinaaiDataBase stores truth. It does not execute and does not govern.**
DataBase files define structure and rules. They do not run processes. Golden Edge at `:8001` is an optional scoring tool — it is located inside `SinaaiDataBase/governance/` by path only, not by role.

**G3 — SinaaiRuntime executes only what has been declared.**
No new subsystems without a registry entry. Undeclared modules currently running (loop_engine, civilization, etc.) are tolerated in Phase 0 as existing debt. They must be declared or frozen before Phase 1 closes.

**G4 — Primary spine is `:8000` only.**
No new routing to `:8010` or `:8020`.

**G5 — Products evolve only via Sina OS announcement.**
A product moving from `docs_only` to executable requires an explicit registry status change and an ANNOUNCEMENT_BOARD entry.

**G6 — Conflicts resolve at the LAW tier, then registry order.**
`SinaaiDataBase/L0-law/` wins on identity and boundary disputes. After that, Section 6 read order determines precedence.

**G7 — Phase 0 is declaration. Phase 1 is consolidation. Phase 2 is enforcement.**
Phase 0: write and agree governance files. No enforcement. No building.
Phase 1: close declared gaps, freeze legacy, scaffold Noetfield as isolated greenfield.
Phase 2: git enforcement, CI gates (was "Phase B") — not active until declared.

**G8 — Cloud-first LLM default.**
`OLLAMA_ENABLED=false` is current operational truth. Not Phase-gated.

**G9 — No agent or session invents structure.**
Every session reads this SSOT before acting. Prior thread outputs, code comments, and README narratives are not structural authority.

---

## 8. System Boundaries — Locked

**Sina OS** — governance only
- May: update registry, publish announcements, declare status changes
- May not: run as a process, own runtime state, be a dependency of any running system

**SinaaiDataBase** — truth storage only
- May: hold governance and identity documents, define structure in files
- May not: execute processes, be a runtime dependency

**SinaaiRuntime** — execution only
- May: run agents, process requests, manage declared loops, integrate Telegram and GitHub Lab
- May not: redefine system structure, act as governance authority, create product entities without registry entry

**UI** — observation and control surface only
- May: display state, surface metrics, send commands to Runtime APIs
- May not: be authoritative for any system state

**Noetfield** — future isolated product
- Today: documentation and specification only
- When built: standalone system with its own database, its own API, its own tenant model
- Must operate with SinaaiRuntime fully offline — not a Runtime submodule, ever
- Has no current runtime dependency on SinaaiOS because no Noetfield code exists

**TrustField Technologies** — separate external company
- Not a submodule, corpus, or child of Noetfield
- Live delivery: `Desktop/TrustField Technologies/` + `trustfield.ca` (own repo and SOT)
- May collaborate with Noetfield or compete/overlap on similar services — explicit commercial agreements only; no structural merge without ASF + registry + ANNOUNCEMENT_BOARD
- SinaaiDataBase `noetfield/corpus/` may reference TrustField for research only — path is not ownership

**Golden Edge** — optional scoring tool
- Subordinate to Sina OS governance
- Located inside `SinaaiDataBase/governance/` by path; classified as tool, not governance authority
- Optional: system operates correctly without it running

---

## 9. Conflicts — Resolved

All conflicts identified across the three source documents. Each has one resolution. None are open.

| # | Conflict | Resolution |
|---|---|---|
| C1 | Phase 0/1 vs Phase A/B vs blueprint exit | Collapsed: Phase 0 = declaration · Phase 1 = consolidation · Phase 2 = git enforcement |
| C2 | Dual SSOT: governance/ vs Layer A meta | Single stack: `governance/` wins; Layer A is subordinate identity layer |
| C3 | Dual governance: `SinaaiDataBase/governance/` vs `SinaaiRuntime/governance/` vs Golden Edge | One authority: Sina OS governance stack only. Runtime/governance = undeclared code debt. Golden Edge = tool. |
| C4 | Sina OS "decides" vs loops starting without registry gate | Sina OS = declarative authority. Undeclared loops = tolerated debt in Phase 0; must be declared in Phase 1. |
| C5 | SinaaiDataBase "does not execute" vs Golden Edge FastAPI inside DataBase tree | Golden Edge reclassified: optional scoring tool. Location in DataBase tree is path only, not role. |
| C6 | Git as second SSOT domain | Rejected. Git = integrity layer only. Truth is authored in `governance/`. |
| C7 | Sina OS vs sinaai_os vs SinaaiOS vs CACOS-N naming | Canonical name: **Sina OS** (two words, no camel case after "Sina"). CACOS-N = deprecated legacy name. |
| C8 | Noetfield: registry entity vs standalone product vs zero code | Noetfield = docs-only product entity today. Future: standalone isolated product. Never a Runtime submodule. |
| C9 | TrustField as sibling vs corpus inside Noetfield | **Superseded v3.1 (ASF):** TrustField Technologies = **separate company**, external to mono. Not owned by or inside Noetfield. May collaborate with Noetfield or offer similar/overlapping services — commercial boundary only. Mono `noetfield/corpus/` may hold cross-reference material only. |
| C10 | Telegram canonical: v4 vs fintech vs v2/v3 | One canonical path: `telegram_fintech` or `v4` (whichever is declared active in Phase 1). Others frozen. |
| C11 | UI role: observation only vs tenant SaaS routes | UI role locked: observation + human control surface. Not SSOT. May send API commands to Runtime. |
| C12 | Undeclared Runtime loops vs G3 | Tolerated as Phase 0 debt. Must be declared or frozen in Phase 1 registry sweep. |

---

## 10. Known Gaps — Declared

These are the known gaps between declared structure and actual disk state. Listed so they are not lost. They are not Phase 0 action items.

| Gap | Declared | Actual | Phase |
|---|---|---|---|
| SSOT in git | SSOT must be committed | `SinaaiDataBase/.git` = 0 commits | Phase 0 exit act |
| Sina OS control plane | Sina OS declares structure | No `sina_os/` module | Accepted — building |
| Multiple FastAPI stacks | `:8000` canonical | `:8001/:8010/:8020` on disk | `:8010/:8020` frozen; `:8001` optional |
| Telegram fragmentation | One canonical path | Five trees on disk | Phase 1 — declare one, freeze others |
| Noetfield code | Future standalone product | 0 `.py` files | Accepted — Phase 1+ |
| Runtime reads Layer A | Runtime informed by identity | Registry read is informational only | Phase 1+ |
| Undeclared Runtime modules | All modules declared | `loop_engine`, `civilization`, etc. undeclared | Phase 1 registry sweep |
| PM2 naming | App name matches function | "cacos-api" runs `run_api.py` | Phase 1 — cosmetic |

---

## 11. Phase Definitions — Locked

| Phase | Name | Purpose | Allowed | Forbidden | Exit criterion |
|---|---|---|---|---|---|
| **Phase 0** | Governance / Declaration | Lock SSOT; agree structure | Write governance files; align registry | New subsystems; Noetfield code; enforcement CI; treating code as structural authority | This document + registry + board agreed and consistent |
| **Phase 1** | Consolidation + Foundation | Close declared gaps; subtract chaos; scaffold Noetfield greenfield | Freeze legacy; declare canonical Telegram; commit SSOT to git; Noetfield standalone scaffold | New meta layers; parallel FastAPI; Noetfield inside Runtime; dual SSOT | Git commit of SSOT; all gaps in §10 either closed or formally deferred |
| **Phase 2** | Integrity / Enforcement | Git-backed truth; CI gates | `validate-registry.yml` blocking; path guards | Enforcement before Phase 0–1 stable | Not started |

**You are in Phase 0 now.**
Local agreement on **this Desktop file** = Phase 0 locked. Git commit of monorepo governance mirrors is optional and **must not include this Desktop file**.

---

## 12. How Truth Is Updated

**Only valid path:**

1. ASF identifies or approves the change
2. Update `system_registry.json` (and this file if structural)
3. Add dated entry to `ANNOUNCEMENT_BOARD.md` and `governance/announcements/YYYY-MM-DD-*.md`
4. Align Layer A / product docs after registry — never before

**Invalid updates** (these do not change the SSOT):
- Editing README, ROADMAP, code comments, or agent prompts without a registry change
- A session or agent "deciding" a new structure without an ASF-approved registry entry
- Committing code that implies a new system role not reflected in the registry

**Phase 0:** Local agreement on governance files is sufficient for work to proceed.
**Phase 2:** Git commit is required; CI advisory transitions to blocking when activated.

---

## 13. Reading Order for Any New Session

```
1. /Users/sinakazemnezhad/Desktop/SourceA/SINA_OS_SSOT_LOCKED.md    ← this file (INTERNAL)
2. SinaaiMonoRepo/SinaaiDataBase/governance/system_registry.json
3. SinaaiMonoRepo/SinaaiDataBase/governance/ANNOUNCEMENT_BOARD.md
4. SinaaiMonoRepo/SinaaiDataBase/governance/boundaries.json
5. SinaaiMonoRepo/AGENTS.md
```

Do not read the codebase to understand structure.
Do not resume a prior thread without reading this first.
Do not treat any prior agent output as structural authority.

---

## Document Control

**This is the master SSOT. It supersedes:**
- `SINA_OS_SSOT_LOCKED.md` v1.0
- `PHASE1_UNIFIED_BLUEPRINT.md` v1 (conceptual, pre-audit)
- `PHASE1_UNIFIED_BLUEPRINT_v2.md` (forensic, pre-unification)

**The Phase 1 build plan** (`PHASE1_UNIFIED_BLUEPRINT_v2.md` or successor) is a work plan document — subordinate to this file. It is not SSOT.

**Version history:**
- v1.0 — 2026-05-31 — Initial SSOT from concept briefs
- v2.0 — 2026-05-31 — Forensic rewrite (reality-based)
- v3.0 — 2026-05-31 — Final unification: all conflicts resolved, single authority table, phase vocabulary collapsed
- v3.1 — 2026-05-31 — ASF: TrustField = separate company (not Noetfield corpus); collaboration/overlap allowed at commercial layer
