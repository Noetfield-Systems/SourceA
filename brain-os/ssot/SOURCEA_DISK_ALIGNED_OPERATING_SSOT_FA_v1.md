# SINGLE SOURCE OF TRUTH
# سیستم‌عامل عامل هوشمند Source-A
# سند معماری اصلی — نسخه هم‌راستا با دیسک

**نسخه:** ۱.۰ (FA) · **وضعیت:** فعال — مرجع بنیان‌گذار و مشاور  
**تاریخ:** ۲۰۲۶-۰۶-۲۴T04:30:00Z  
**شرکت‌ها:** Noetfield Systems Inc. · TrustField Technologies Inc.  
**مکان:** ونکوور، بریتیش کلمبیا  
**جایگزین نمی‌کند:** `brain-os/ssot/SOURCEA_LLM_AGENT_OPERATING_LAW_SSOT_v3.md` (قانون dispatch)  
**مکمل می‌کند:** Master Blueprint v1 · Cloud Kernel v1.3 · reconciliation map

---

> **هیچ تصمیم معماری یا dispatch بدون ارجاع به اسناد فعال روی دیسک گرفته نمی‌شود.**  
> این سند نسخهٔ فارسیِ **واقعیت دیسک + برنامه ROI** است — نه بازنویسی v1.1 قدیمی.

**امتیاز هم‌راستایی با دیسک:** ۸۵٪ روح معماری · ۴۵٪ هسته ابری به‌شکل PDF · ۱۰۰٪ قانون عامل (SSOT v3)

**وضعیت:** LOCKED برای برنامه‌ریزی · Production-Ready Thinking · Receipt-Native

---

## فهرست (۲۰ بخش — الگوی v1.1)

| § | عنوان |
|---|--------|
| ۱ | چهار ستون |
| ۲ | هسته L0 + L1–L8 |
| ۳ | سلسله‌مراتب داده |
| ۴ | طرح Blueprint (JSON — نه SQL هنوز) |
| ۵ | لایهٔ قرارداد اجرا (Execution Contract) |
| ۶ | چهار Worker منطقی (W1–W4) |
| ۷ | چرخه Chat Unify + قانون عامل v3 |
| ۸ | رسید سه‌تایی: Artifact · Evidence · Decision |
| ۹ | مسیریابی قابلیت و هزینه |
| ۱۰ | Mac L0 — میز کار (فراتر از PDF قدیمی) |
| ۱۱ | نقشهٔ فازها — واقعیت دیسک |
| ۱۲ | Master Blueprint — مسیر درآمد |
| ۱۳ | مقایسه: v1.1 قدیمی در برابر دیسک امروز |
| ۱۴ | آنچه نگه داشتیم / آنچه رد کردیم |
| ۱۵ | اولویت ارتقا (ROI) |
| ۱۶ | مشخصات سخت‌سازی Executor |
| ۱۷ | Supabase + مسیر آینده (بدون Neon زودهنگام) |
| ۱۸ | KPI و رسید اثبات |
| ۱۹ | غیراهداف صریح (LOCKED) |
| ۲۰ | قفل نهایی هسته |

---

## §۱ — چهار ستون (The 4 Pillars)

معماری Source-A روی **چهار ستون** استوار است. تفاوت با v1.1: ستون **Governance** امروز قوی‌تر از PDF قدیمی است (SSOT v3 + Mac Law).

| ستون | نام | مسئولیت | اثبات روی دیسک |
|------|-----|---------|----------------|
| **Product** | محصول | Forge، Noetfield، TrustField، WitnessBC، ویدیو تبلیغاتی | `apps/video-ad-factory/` · `sourcea.app` |
| **Governance** | حاکمیت | قانون عامل، dispatch gate، رسید، قفل Mac | `brain-os/ssot/SOURCEA_LLM_AGENT_OPERATING_LAW_SSOT_v3.md` · `brain-os/law/` |
| **Runtime** | زمان اجرا | موتور ابری قرارداد-محور؛ Mac فقط کنترل | `data/fbe_execution_contract_v1.json` · Railway FBE |
| **Factory** | کارخانه | Blueprint = کارخانه؛ یک Executor، N طرح JSON | `data/forge-real-blueprints-v01.json` (۱۰۰ ردیف) |

**قانون طلایی:**  
> Workers = عضله · Graph/Blueprint = مغز · Contract = دروازه · Receipt = حقیقت

---

## §۲ — هسته L0 + L1–L8 (Kernel Layers)

### L0 — میز کار Mac (روی دیسک — GREEN)

**در v1.1 نبود؛ شما جلوتر ساختید.**

| جزء | پورت / مسیر | وضعیت |
|-----|-------------|--------|
| Worker Hub | `:13020` · `scripts/worker_hub_v1.py` | ✅ GREEN |
| AG Routing Panel | `:8782` | ✅ GREEN |
| Mac Law | `:8781` | ✅ GREEN |
| کمربند SCAN→SHIP | session gate · next-task trigger | ✅ GREEN |
| رسیدها | `~/.sina/*-receipt*.json` (۸۰۰۰+) | ✅ GREEN |

**قانون:** Mac = control plane only · هیچ factory سنگین روی بدنه Mac.

---

### L1–L8 — موتور ابری (Hybrid — نه PDF خام)

| لایه | نام هدف (v1.3) | پیاده‌سازی امروز روی دیسک | وضعیت |
|------|----------------|---------------------------|--------|
| **L1** | UI / Interface | Hub HTML + اپ‌های macOS (Chat Unify، Cloud Workers) | 🟡 AMBER |
| **L2** | Auth & RLS | Supabase · `data/supabase-portfolio-tiers-v1.json` | ✅ GREEN |
| **L3** | State Engine | Supabase (portfolio-spine، noetfield، labs-sandbox) | 🟡 AMBER |
| **L4** | Queue | Hub Cloud Forge Run · `hub_cloud_forge_run_proceed_v1.py` | 🟡 AMBER |
| **L5** | Runtime | Railway FBE · `fbe_run_job_v1.py` | 🟡 AMBER (W3 قوی) |
| **L6** | Capability Router | `forge-scoring-ssot-v01.json` · OpenRouter ابری | 🟡 AMBER |
| **L7** | Heavy Compute | Fal · ElevenLabs · video-ad-factory | ✅ GREEN |
| **L8** | Observability | JSON receipts + Hub terminal | 🟡 AMBER |

**قانون LOCKED:** موتور را به Cloudflare Workers بازنویسی نکنید بدون پنجره ship ASF.

---

## §۳ — سلسله‌مراتب داده (Data Hierarchy)

```
بنیان‌گذار (ناظر / دروازه)
└── L0 Mac Workbench (کنترل · SCAN→SHIP)
    └── Tenant / Project (سطوح Supabase · ماژول‌های برند)
        └── Factory (قالب FBE: forge-app-factory-v1، web-product-factory-v1، …)
            └── Blueprint (۱۰۰ ردیف JSON — forge-real-blueprints-v01)
                └── Run (رسید job FBE · forge drain)
                    └── Task (صف CLOUD-SEC-* · sa-mkt-*)
                        ├── Artifact (خروجی: ویدیو · متن · فایل)
                        ├── Evidence (ردیابی · curl · زنجیره PROVE)
                        └── Decision (approved | rejected | escalated)
```

**وضعیت:** شکل JSON **ثابت و GREEN** (بلیت Phase-1). جدول SQL یکپارچه هنوز **TARGET**.

**اثبات:** `~/.sina/phase1-pevc-truth-ticket-v1.json` → `decision.verdict: "approved"` · blueprint `MAC-CTL-002` · صف `CLOUD-SEC-052` · سطح GOLD.

---

## §۴ — طرح Blueprint (JSON — الگوی v1.1 §3.1)

امروز Blueprint روی دیسک **JSON** است، نه جدول SQL.

```json
{
  "id": "MAC-CTL-002",
  "inputs": { "plane": "mac_control", "action": "..." },
  "outputs": { "artifact": "forge_drain_run_receipt", "receipt_url": null },
  "core_capability": "...",
  "validation_rule": "cloud_forge_incident_038",
  "dependencies": []
}
```

**منبع:** `data/forge-real-blueprints-v01.json` — **count: 100**

**قانون ROI:**  
> Blueprint جدید = کارخانه جدید · Worker جدید نه · کد جدید نه

**TARGET بعدی:** dual-write به Supabase پس از ۵ Proof Pack سبز متوالی.

---

## §۵ — لایه قرارداد اجرا (Execution Contract)

مغز سیستم — LLM فقط **پیشنهاد** می‌دهد؛ قرارداد **اجازه** می‌دهد.

| فیلد | نقش |
|------|-----|
| `job_id` · `factory_id` · `kernel_version` | هویت اجرا |
| `execution_mode` | `CLOUD_ONLY` (پیش‌فرض) |
| `policy_gate` | deny local وقتی FREEZE · تطابق kernel |
| `route_map` | `/api/fbe/run-forge/v1` و مسیرهای FBE |

**مسیرها:** `data/fbe_execution_contract_v1.json` · `scripts/fbe/lib/execution_contract_v1.py`

**فلسفه v1.1 حفظ شده:** deterministic kernel؛ LLM فقط planner.

---

## §۶ — چهار Worker منطقی W1–W4

| Worker | نقش PDF | پیاده‌سازی دیسک | وضعیت |
|--------|---------|-----------------|--------|
| **W1 Intake** | ورودی · ایجاد run | Hub dispatch · gate قرارداد | 🟡 |
| **W2 Planner** | DAG از blueprint | `fbe_node_graph_v1.json` · comprehension loop | 🟡 |
| **W3 Executor** | فراخوانی ابزار | `fbe_run_job_v1.py` · forge runner · Railway | ✅ |
| **W4 Memory** | تکمیل · projection | رسید · `fbe_hub_projection_v1.py` | 🟡 |

**تفاوت فنی با v1.1:** نقش‌ها **منطقی** روی Railway Python — نه ۴ Cloudflare Worker جدا.

---

## §۷ — چرخه Chat Unify + قانون عامل SSOT v3

**این بخش در v1.1 نبود — مزیت رقابتی شماست.**

```
زبان بنیان‌گذار
      │
      ▼
[Prompt Forge] ── مأموریت Cursor
      │
      ▼
   Cursor (عامل کار می‌کند)
      │
      ▼
[ORD + Truth Gate] ── PASS / BLOCK
      │ PASS
      ▼
[Founder Loop] ── یک اقدام محدود
      │
      ▼
دستور محدود به Cursor
```

### قوانین بالادست (خلاصه v3)

| # | قانون |
|---|--------|
| ۰ | جهت، نه زور — بنیان‌گذار هدف می‌دهد؛ عامل مسیر را پیدا می‌کند |
| A | یک مأموریت · یک کار · ALREADY DONE را سنجاق کن |
| B | **Disk-bound یا پیش‌نویس** · حقیقت فقط از رسید |
| C | سبز کافی است اگر نیاز را برطرف کند — بدهی را لاگ کن |
| E | هیچ dispatch بدون عبور از gate |

**مرجع کامل:** `brain-os/ssot/SOURCEA_LLM_AGENT_OPERATING_LAW_SSOT_v3.md`  
**Registry:** `data/sourcea-governance-ssot-registry-v1.json` → `llm_agent_operating_law_v3` **ACTIVE**

---

## §۸ — رسید سه‌تایی (Artifact · Evidence · Decision)

واحد محصول Source-A — یک شیء، چهار خریدار (مشتری · سرمایه‌گذار · ممیزی · خودتان).

| بخش | معنی | مثال دیسک |
|-----|------|-----------|
| **artifact** | خروجی قابل تحویل | `forge_drain_run_receipt` · ویدیو · ZIP |
| **evidence** | رد پای اثبات | curl 200 · 7/7 chains · hub receipt |
| **decision** | حکم gate | `approved` · `rejected` + rationale |

**قانون فروش (Master Blueprint):**  
> سیستم‌های قابل سرمایه‌گذاری با **رسید** اثبات می‌شوند، نه با دیاگرام.

**ماشین بعدی:** Proof Pack — تبدیل run سبز به بسته قابل فروش.

---

## §۹ — مسیریابی قابلیت و هزینه

### Mac (Cursor)

**SSOT زنده:** `data/cursor-cost-intelligence-routing-v1.json`

| نقش | مدل پیش‌فرض | هرگز |
|-----|-------------|------|
| Brain | Auto | implement sa |
| Worker | Auto → Composer | کل repo |
| Ship proof | API pool | روزمره |

### Cloud (FBE / Forge)

**SSOT:** `data/forge-scoring-ssot-v01.json` · OpenRouter روی Railway

| سطح SLA | کاربرد | وضعیت |
|---------|--------|--------|
| draft | intake · research | 🟡 جزئی |
| normal | reasoning | 🟡 |
| premium | writing | 🟡 |
| critical | governance / audit | 🟡 |

**توجه:** نام مدل‌های PDF v1.1 (Gemini 3.1 Flash-Lite و …) **TARGET** هستند — endpoint زنده از env ابری می‌آید.

---

## §۱۰ — Mac L0 میز کار (جزئیات)

| قانون | مسیر |
|-------|------|
| Mac control plane flag | `~/.sina/mac-control-plane-v1.flag` |
| CLI drain غیرفعال | `~/.sina/cli-disabled-v1.flag` |
| Factory mode FREEZE | `SOURCEA-PRIORITY.md` |
| مدل بنیان‌گذار | `data/founder-execution-model-v1.json` |

**کارخانه‌های ابری اصلی (هدف آنلاین):** fbe_railway · video_ad_factory · supabase_edge · openrouter_cloud · …

**وضعیت فعلی:** cloud factories **۸/۹ RED** — ارتقای عملیاتی U4 در اولویت، نه بازنویسی معماری.

---

## §۱۱ — نقشه فازها — واقعیت دیسک (صادقانه)

| فاز PDF | ادعای قدیمی | حقیقت دیسک ۲۰۲۶-۰۶ |
|---------|-------------|---------------------|
| Phase 1 Core | ✓ | **جزئی** — قرارداد + blueprint + Supabase؛ SQL graph نه |
| Phase 2 Execution | ✓ | **جزئی** — FBE + Cloud Forge Run؛ forge drain **GREEN** |
| Phase 3 Router | ✓ | **TARGET** |
| Phase 4 Observability | ✓ | **TARGET** — JSON receipts کافی برای T1 |

**بلیت Phase-1 PEVC:** ✅ **approved** (از رسید فقط — نه از چت)

**قانون:** JSON now · SQL later.

---

## §۱۲ — Master Blueprint — مسیر درآمد (ROI)

**مرجع:** `brain-os/roadmap/SOURCEA_MASTER_BLUEPRINT_v1.md`

### نردبان پیشنهاد (فروش از بالا به پایین)

| سطح | چیست | کی |
|-----|------|-----|
| **T1** | Done-for-you run + Proof Pack | **الان** |
| **T2** | صندلی early-access | بعد از T1 |
| **T3** | SaaS چندمستأجره | بعد از اثبات تقاضا |

### فازهای اجرا (با رسید)

| فاز | هدف | اثبات |
|-----|------|-------|
| **۰** | offer روی sourcea.app · ۱ مشتری پولی | SOW + proof-pack receipt |
| **۱** | Proof Pack machine · ۵ run سبز | ۲ مشتری |
| **۲** | ۳–۵ design partner | NRR |
| **۳** | enterprise / fundraise | audit pack پذیرفته‌شده |

**ICP پیش‌فرض:** بنیان‌گذاران و آژانس‌هایی که خروجی AI می‌فروشند و از «agent soup» سوخته‌اند.  
**عمود پیشنهادی:** تولید تبلیغ/محتوای AI — `video-ad-factory` از قبل سبز.

---

## §۱۳ — مقایسه: v1.1 قدیمی در برابر دیسک امروز

| موضوع | v1.1 (superseded) | دیسک Source-A امروز | برنده ROI |
|-------|-------------------|---------------------|-----------|
| موتور runtime | ۴ CF Worker | Railway FBE + نقش منطقی W1–W4 | **دیسک** — بدون rewrite |
| صف | Cloudflare Queues | Hub Cloud Forge Run | **دیسک** — کار می‌کند |
| DB | DDL کامل روز اول | Supabase + JSON receipts | **دیسک** — اثبات قبل از SQL |
| Neon | فاز ۳+ | ممنوع تا ASF | **دیسک** |
| Governance | SLA در PDF | SSOT v3 + ORD gate | **دیسک** — قوی‌تر |
| Mac | نبود | L0 shipped | **دیسک** — منحصربفرد |
| درآمد | implicit | T1 → T2 → T3 صریح | **دیسک** |
| Blueprint | SQL table | ۱۰۰ JSON + صف drain | **دیسک** |
| Observability | جداول token | ~/.sina receipts | **دیسک** برای T1 |

---

## §۱۴ — آنچه نگه داشتیم ✅ / آنچه رد کردیم ❌

### ✅ نگه داشتیم (روح v1.1 + قانون دیسک)

- Factory = Data Graph (Blueprint-driven)
- یک Executor · N Blueprint (نه ۵۰ Worker)
- Capability-based Router (جزئی · در حال تکمیل)
- Artifact / Evidence / Decision
- Execution Contract = مغز
- Observability از روز اول (به‌صورت JSON)
- Supabase برای spine و RLS
- Heavy compute ابری (Fal/ElevenLabs نه Mac)

### ❌ رد کردیم / به تأخیر انداختیم

- بازنویسی کامل به Cloudflare Workers
- Neon migration زودهنگام
- DDL کامل v1.1 قبل از اثبات JSON
- ۵۰ Worker اختصاصی per tool
- if premium: hardcode Claude در Router
- SaaS self-serve قبل از T1 پولی
- validator marathon روی Mac در جلسه بنیان‌گذار (INCIDENT-039)

### ⏳ در صف ROI

- Proof Pack machine
- سخت‌سازی Executor (idempotency · timeout · breaker)
- SQL dual-write پس از ۵ Proof Pack
- OTel / جداول model_calls (enterprise بعداً)

---

## §۱۵ — اولویت ارتقا (Revised Build Priority — LOCKED ROI)

| اولویت | جزء | چرا اول | باز می‌کند |
|--------|-----|---------|------------|
| **#1 NOW** | Proof Pack + T1 فروش | درآمد · اثبات بازار | بودجه برای U1–U3 |
| **#2 NOW** | سخت‌سازی Executor | گلوگاه 502 / retry | drain پایدار |
| **#3 Next** | Router + SLA روی blueprint | کنترل هزینه | حاشیه سود |
| **#4 Next** | cloud factories 9/9 GREEN | اعتبار فروش | claim = disk |
| **#5 Later** | SQL graph migration | مقیاس blueprint | Registry enterprise |
| **#6 Later** | Neon · OTel · CF Queues | فقط با فشار scale + ASF | — |

---

## §۱۶ — مشخصات سخت‌سازی Executor (§11 v1.1 — هدف دیسک)

| مکانیزم | هدف پیاده‌سازی | وضعیت |
|---------|----------------|--------|
| Idempotency keys | `execution_contract_v1.py` · همه مسیرهای FBE | 🟡 جزئی |
| Retry + backoff | `fbe_run_job_v1.py` | TARGET |
| Timeout budget | `data/fbe_timeout_budgets_v1.json` (پیشنهاد) | TARGET |
| Tool isolation | try/catch per node | TARGET |
| Snapshot input/output | evidence در هر task | 🟡 شکل Phase-1 |
| Circuit breaker | `forge-scoring-ssot-v01.json` | 🟡 fallback هست · breaker رسمی نه |

**ماشین حالت Task (هدف):**  
`PENDING → QUEUED → RUNNING → COMPLETED → ARCHIVED`  
شکست → `RETRY_WAIT` → پس از ۳ بار → `FAILED` → escalate

---

## §۱۷ — Supabase + مسیر آینده

### پروژه‌های زنده (GREEN)

| پروژه | tier | ماژول‌ها |
|-------|------|----------|
| portfolio-spine | production | witnessbc · gov · forge_factory · … |
| noetfield | production | noetfield · trustfield |
| labs-sandbox | labs | Virlux · آزمایش |

**SSOT:** `data/supabase-portfolio-tiers-v1.json`

### migration موجود (شروع truth layer — نه DDL کامل v1.1)

- `infra/supabase/portfolio-spine/migrations/001_truth_layer_cycle_receipts_v1.sql`

### جدول hybrid (قانون reconciliation)

| لایه | Supabase الان | Neon / SQL graph |
|------|---------------|------------------|
| Auth & RLS | ✅ | — |
| Realtime | ✅ | — |
| Execution graph | JSON receipts | TARGET dual-write |
| Observability SQL | — | TARGET Phase 4 |

---

## §۱۸ — KPI و رسید اثبات

| KPI | خط پایه | هدف U0 | هدف U1–U2 |
|-----|---------|--------|-----------|
| مشتری T1 پولی | ۰ | ۱ | ۳ |
| Proof Pack مهرشده | ۰ | ۱ نمونه + ۱ مشتری | ۵ متوالی |
| نرخ drain سبز | وقفه 502 | ۳ متوالی | ۱۰ |
| ORD pass rate | live | ردیابی | ≥۸۰٪ |
| cloud factories | ۸/۹ RED | ۹/۹ | ۳۰ روز پایدار |
| registry 1000-pack | ۱۰۰۰/۱۰۰۰ done | — | queue_sa head |

**خواندن روزانه:** `brain-os/plan-registry/SOURCEA-PRIORITY.md` · `~/.sina/agent-live-surfaces-v1.json`

---

## §۱۹ — غیراهداف صریح (LOCKED)

از `docs/SOURCEA_CLOUD_KERNEL_VS_DISK_RECONCILIATION_LOCKED_v1.md`:

1. **بدون Neon** تا تأیید ASF migration  
2. **بدون بازنویسی CF Worker** برای موتور  
3. **بدون IDE دوم** — Cursor سطح ویرایش می‌ماند  
4. **بدون ادغام تخت** PDF + Workbench در یک فایل SSOT  
5. **بدون factory bootstrap روی Mac** در FREEZE  
6. **بدون validator marathon** در جلسه بنیان‌گذار (≤۹۰ثانیه · یک shell)

---

## §۲۰ — قفل نهایی هسته

```
SOURCE-A KERNEL — DISK-ALIGNED FA v1.0 — LOCKED FOR PLANNING

مرجع dispatch عامل:     SSOT v3 (انگلیسی — authority)
مرجع معماری ابری:      Cloud Kernel v1.3 PDF (target)
مرجع صادقانه دیسک:      reconciliation LOCKED v1.1
مرجع درآمد:             Master Blueprint v1
کارخانه عملیاتی:       100 blueprint JSON + FBE Railway
اثبات Phase-1:          phase1-pevc-truth-ticket → approved
نسخه superseded:        Source-A-SSOT-v1.1.pdf (فقط lineage)
```

### ترتیب خواندن برای عامل / ORD / Chat Unify

1. `docs/SOURCEA_SSOT_INDEX_LOCKED_v1.md`  
2. `brain-os/ssot/SOURCEA_LLM_AGENT_OPERATING_LAW_SSOT_v3.md`  
3. `brain-os/roadmap/SOURCEA_MASTER_BLUEPRINT_v1.md`  
4. `docs/SOURCEA_CLOUD_KERNEL_VS_DISK_RECONCILIATION_LOCKED_v1.md`  
5. **این سند (FA)** — برای بنیان‌گذار و مشاور فارسی‌زبان  
6. `docs/Source-A-Cloud-Kernel-v1.3.pdf` — هنگام اجرای body کارخانه

### جملهٔ پایانی (همان closing line)

> شما نیازی به «بازگشت به v1.1» ندارید — در governance (v3) و control plane (Mac L0) از آن جلوتر رفته‌اید.  
> مسیر ارتقا: **رسید سبز را monetize کن (Proof Pack) → موتور را سخت کن → هزینه را discipline کن → SQL وقتی اثبات شد.**  
> هر حرکتی که token ذخیره کرد، rewrite را رد کرد، و رسید را جلوتر از دیاگرام گذاشت — **همان استراتژی ROI درست است.**

---

**Noetfield Systems Inc. | TrustField Technologies Inc.**  
**Vancouver, BC — ۲۰۲۶**  
**Source-A · Disk-Aligned Operating SSOT FA v1.0 · Page 20 / 20**

---

*نسخه فارسی · مسیر: `brain-os/ssot/SOURCEA_DISK_ALIGNED_OPERATING_SSOT_FA_v1.md` ·  
PDF بنیان‌گذار: `brain-os/ssot/SOURCEA_DISK_ALIGNED_OPERATING_SSOT_FA_v1.pdf` ·  
بازتولید: `python3 scripts/render_brain_os_ssot_fa_pdf_v1.py`*
