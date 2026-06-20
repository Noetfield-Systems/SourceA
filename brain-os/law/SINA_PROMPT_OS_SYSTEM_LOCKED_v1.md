# Sina Prompt OS — System Definition (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
## Multi-project parallel execution under Sina OS

**Version:** 1.0 — FINAL LOCKED  
**Status:** ACTIVE — MVP delivered on Mac (`Desktop/SinaPromptOS/`)  
**Authority:** Subordinate to `SINA_OS_SSOT_LOCKED.md` v3 (structural law)  
**Visibility:** `INTERNAL_LOCAL_ONLY` — never commit to public git, never push online  
**Canonical location:** `/Users/sinakazemnezhad/Desktop/sourceA/SINA_PROMPT_OS_SYSTEM_LOCKED_v1.md`  
**Implementation:** `/Users/sinakazemnezhad/Desktop/SinaPromptOS/`  
**Launcher:** `/Users/sinakazemnezhad/Desktop/Sina Prompt OS.command`  
**Locked:** 2026-06-02  
**Maintainer:** ASF

---

> **Lock statement.**  
> This document is the **canonical reference** for how Sina Prompt OS works with Sina OS, ASF, Cursor, and parallel product repos.  
> Narrative examples (including Persian) in §4 are **approved for future reference** after validation in §3.  
> If this file conflicts with `SINA_OS_SSOT_LOCKED.md` v3 on **structure** → **SSOT wins**.  
> If SSOT product table (TrustField = corpus only) conflicts with **operational reality** → treat this file + `TRUSTFIELD_DELIVERY_ALIGNMENT` as execution truth until ASF updates registry.

**Superseded for full doctrine by:** `SINAAI_AGENTS_AND_AUTOMATION_UNIFIED_BLUEPRINT_LOCKED_v1.md` (§5)  
**This file retains:** Farsi narrative §4 + validation audit §3  
**Index:** `SINA_PROMPT_OS_CORE_v1.md`

---

## 1. One-sentence definition (locked)

> **Sina Prompt OS** is a local **AI-assisted execution router**: it reads Sina OS law, every project’s `os/plan.json`, and recent Cursor chats, then outputs **one Cursor prompt per chosen project** — so ASF never has to re-read six repos to remember what matters.

**Not:** a second SSOT, a structural governor, or a replacement for ASF.

---

## 2. Locked hierarchy

```text
ASF (human)
  → approves structural changes only ASF may authorize
Sina OS — Source A SSOT v3
  → law: phases, freeze, registry intent, forbidden architecture
Sina Prompt OS — this system
  → operational priority + next-task prompt (no structural authority)
Per-repo os/
  → plan.json + strategy.md (project memory queue)
Cursor
  → executes exactly one prompted task per session
Product repos
  → code, UI, API, deploy [DELIVERY] or governance [DESIGN]
```

### Locked formula

```text
Prompt(repo) = f(Source A, RepoContext(repo), GlobalPriority)
```

| Input | Source |
|--------|--------|
| Source A | `Desktop/sourceA/SINA_OS_SSOT_LOCKED.md` |
| RepoContext | `{repo}/os/plan.json`, `strategy.md`, delivery SOT if any |
| GlobalPriority | `SinaPromptOS/config/projects.json` → `global_priority` + `weight` |

---

## 3. Validation of ASF narrative example (accuracy audit)

ASF provided a Persian “what the system is now” narrative. Below: **keep**, **correct**, or **reject** each claim.

| Claim in example | Verdict | Correction for Source A |
|------------------|---------|-------------------------|
| Multi-project **parallel** AI execution system | ✅ Accurate | Matches delivered `SinaPromptOS` + per-repo `os/` |
| Central brain decides, multiple projects execute | ✅ Accurate | “Brain” = **Prompt OS router**, not Sina OS runtime |
| **Sina OS** = law (important / forbidden / priority / structure) | ✅ Accurate | Sina OS does **not** pick “which line of code today” |
| **Prompt OS** = reads all projects, next step, Cursor command | ✅ Accurate | Implemented: snapshot + router + UI :8765 |
| Examples: “add login endpoint”, “Virelux dashboard UI” | ⚠️ Partially | Must respect **feature freeze** (TrustField) and **phase** (Noetfield = docs-first). Prompt OS suggests **queued** `next_tasks[0]`, not random features |
| **Projects** = TrustField, Noetfield, Virelux, MonoRepo | ⚠️ Incomplete | Locked registry has **6**: + **777 Foundation**, + **SinaPromptOS** tool itself |
| **plan.json** = memory of done / next | ✅ Accurate | Plus SQLite history in `SinaPromptOS/data/` |
| **Cursor** = arms only, no decisions | ✅ Accurate *if* ASF uses one-task prompts |
| **ASF** = gate for structural change | ✅ Accurate | Registry, new core project, Prompt OS schema, “live” definition |
| Prompt OS = suggestion, ASF = structure approval, Sina OS = law | ✅ Accurate | **Critical** — prevents AI self-destruction |
| Daily loop: read → decide → prompt → execute → update | ✅ Accurate (target) | MVP: **manual** UI/CLI; `scripts/daily-snapshot.sh` ready, not yet cron |
| “Factory that decides and moves alone” | ⚠️ Aspirational | Today: **strong suggestions** + copy-paste prompts; ASF still opens Cursor and approves structural changes |
| TrustField > Virelux in importance | ✅ Accurate | `global_priority`: trustfield #1; weights 10 vs 7 |
| Noetfield = MVP | ⚠️ Wording | More precise: **docs-only product entity** (0 `.py`); MVP **spec**, not live SaaS |
| Sina OS “does not think what code to write” | ✅ Accurate | |
| Prompt OS “execution planner” | ✅ Accurate | Not “architecture planner” |

**Rejected if interpreted wrongly:**

- Prompt OS may **not** redesign Sina OS, registry, or product boundaries.
- Prompt OS may **not** treat TrustField as sandbox to migrate into Noetfield.
- “Parallel” does **not** mean new FastAPI stacks inside `SinaaiRuntime :8000`.

---

## 4. Canonical narrative — فارسی (تأییدشده برای مرجع آینده)

> نسخهٔ زیر همان محتوای مثال ASF است، با اصلاحات دقیق §3.  
> این بخش برای **مرجع انسانی** است؛ قانون فنی انگلیسی در §2 و SSOT v3.

---

### سیستم تو الان دقیقاً چی شده؟

تو یک **سیستم اجرای چندپروژه‌ای مبتنی بر AI** ساخته‌ای — نه یک چت‌بات:

> **یک مغز مرکزی اجرایی (Prompt OS)** که زیر قانون **Sina OS** کار می‌کند، **چند پروژه موازی** را جلو می‌برد، و **حلقهٔ** «بخوان → پیشنهاد بده → اجرا در Cursor → به‌روز state» را تکرار می‌کند.

---

### اجزای واقعی (قفل‌شده)

#### 1) Sina OS — قانون (نه برنامه‌نویس روزانه)

- چه چیزی مهم، ممنوع، و در چه فازی هستیم
- ساختار اکوسیستم و freezeها
- **نمی‌گوید** امروز کدام خط کد — **می‌گوید** جهت و حدود مجاز

مثال: Noetfield داخل Runtime نباشد؛ TrustField در فاز DELIVERY ممکن است ops داشته باشد ولی feature freeze.

#### 2) Sina Prompt OS — برنامه‌ریز لحظه‌ای اجرا (نه قانون‌گذار)

- `plan.json` همه repoها + چت‌های Cursor + اولویت سراسری
- خروجی: **یک پرامپت Cursor** برای **یک تسک**
- UI: `Sina Prompt OS.command` → `localhost:8765`

مثال خروجی واقعی امروز: «Render Postgres + Redis را وصل کن و production readiness را PASS کن» — از صف TrustField، نه اختراع تصادفی.

**محدودیت:** اگر تسک با Source A یا freeze در تضاد باشد — تسک رد می‌شود؛ ASF باید صف را عوض کند.

#### 3) پروژه‌ها — بدن (۶ مورد ثبت‌شده)

| ID | نقش |
|----|-----|
| trustfield | DELIVERY — درآمد / gates |
| sinaai_mono | DESIGN — PAIOS / governance / Runtime spine |
| virlux | DELIVERY — پلتفرم / staging |
| noetfield | DESIGN — spec و corpus (فعلاً بدون کد) |
| seven77 | DELIVERY — وب بنیاد 777 |
| sina_prompt_os | ابزار router خودت |

#### 4) Plan / State — حافظه

- هر repo: `os/plan.json` (`next_tasks`, `done`, `blocked`)
- مرکزی: SQLite در `SinaPromptOS/data/sina_prompt_os.db`

#### 4b) Execution Truth — واقعیت (قفل 2026-06-02)

- **گزارش وضعیت** (intent): `SourceA/REPO_STATUS_REPORTS/`
- **لاگ اجرا** (evidence): `SourceA/REPO_EXECUTION_LOGS/`
- قانون: `SINAAI_EXECUTION_TRUTH_LAYER_LOCKED_v1.md`
- بعد از VERIFY: `submit-execution-log.sh` → `mark-done-verified.sh` → `run-feedback-cycle.sh`
- سیستم بدون `verify_passed: true` به «done» اعتماد نمی‌کند

#### 5) Cursor — بازو

- فقط اجرا — **اگر** یک پرامپت، یک workspace، یک تسک رعایت شود

---

### ASF چیست؟

**ASF = تنها انسانی که اجازهٔ تغییر ساختار را می‌دهد.**

| ASF مجاز است | Prompt OS مجاز است |
|--------------|-------------------|
| عوض کردن Source A / رجیستری | پیشنهاد تسک بعدی |
| اضافه کردن پروژه به `projects.json` | تولید پرامپت |
| برداشتن feature freeze | خواندن state |
| انتخاب Track فاز ۱ | به‌روز history محلی |

```text
Sina OS      = قانون
Prompt OS    = پیشنهاد اجرای لحظه‌ای
ASF          = اجازه تغییر ساختار
Cursor       = اجرای یک تسک
Repo         = محصول
```

---

### حلقه روزانه (هدف — بخشی خودکار امروز)

**صبح:** snapshot همه پروژه‌ها → Sina OS در پرامپت embed می‌شود → بهترین تسک / یا تسک هر پروژه.

**روز:** Prompt → Cursor → `plan.json` update → تکرار.

**شب:** snapshot شبانه (اسکریپت آماده؛ cron اختیاری) → اولویت فردا در `projects.json` یا یادداشت UI.

```text
Read state → Decide (router) → Prompt → Execute (Cursor) → Update (plan.json)
```

---

### جملهٔ نهایی (قفل)

> کارخانهٔ نرم‌افزار: **پیشنهاد و حافظه خودکار** — **قانون و ساختار با ASF**.

Prompt OS سرعت را کم نمی‌کند؛ **drift و redesign تصادفی** را کم می‌کند.

---

## 5. English — execution loop (agents)

| Step | Actor | Action |
|------|-------|--------|
| 1 | SinaPromptOS | `build_full_snapshot()` — all `os/plan.json`, Cursor transcript tails |
| 2 | Router | `rank_projects()` — score = priority + blocked + next_tasks + weight |
| 3 | Output | One `CURSOR PROMPT` block for top project (or ASF picks another) |
| 4 | Human | Open correct Cursor workspace; paste prompt |
| 5 | Cursor | Single task; VERIFY script; update `os/plan.json` |
| 6 | Optional | `python -m core.cli suggest --copy` again |

**CLI:** `cd ~/Desktop/SinaPromptOS && .venv/bin/python -m core.cli suggest --copy`  
**UI:** `~/Desktop/Sina Prompt OS.command`

---

## 6. Two planes (do not confuse)

| Plane | Examples | Prompt OS may suggest |
|-------|----------|---------------------|
| **[DESIGN]** | MonoRepo governance, Noetfield spec | Consolidation, registry, docs |
| **[DELIVERY]** | TrustField, VIRLUX, 777 | Ops, gates, E2E, reliability — not new features if frozen |

Registry sync **after** delivery burst — ledger does not block ship.

---

## 7. Never-do (locked)

1. Prompt OS overrides Source A or changes registry without ASF  
2. Cursor session invents new architecture without registry announcement  
3. Treat TrustField as temporary sandbox for Noetfield migration  
4. Suggest new TrustField user-facing features while engineering freeze ON  
5. Run Noetfield Python inside `SinaaiRuntime :8000`  
6. Commit `Desktop/sourceA/` or this tool’s DB to public git  

---

## 8. File map (Source A + tool)

| File | Role |
|------|------|
| `SINA_OS_SSOT_LOCKED.md` | Master law |
| `SINA_PROMPT_OS_SYSTEM_LOCKED_v1.md` | **This file** |
| `SINA_PROMPT_OS_CORE_v1.md` | Short index → this file |
| `SINAAI_MASTER_BLUEPRINT_END_TO_END_v1.md` | Roadmap |
| `sourceB/TRUSTFIELD_PROMPT_OS_ADAPTER_v1.md` | TrustField line-by-line map |
| `SinaPromptOS/config/projects.json` | Live project registry |
| `SinaPromptOS/START_FA.md` | Operator quick start (Farsi) |

---

## 9. ASF sign-off

| Field | Value |
|-------|--------|
| Narrative example (§4) approved for Source A | ☐ ASF |
| Sina Prompt OS MVP accepted as parallel execution layer | ☐ ASF |
| Date | __________ |

---

## Document control

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-06-02 | Initial LOCK: validation + Farsi canonical narrative + delivery binding |

**Supersedes:** informal chat summaries; `SINA_PROMPT_OS_CORE_v1.md` as standalone authority.
