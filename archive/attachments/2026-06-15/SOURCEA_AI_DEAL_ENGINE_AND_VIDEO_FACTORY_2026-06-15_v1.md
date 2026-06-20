# SourceA AI Deal Engine + Programmatic Video Factory (June 2026)

**Saved:** 2026-06-15T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Schema:** `sourcea-ai-deal-engine-v1`  
**Generated:** 2026-06-15  
**Trace:** SOURCEA-DEAL-ENGINE-VIDEO-20260615  
**Authority:** `SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md` · `commercial_pipeline_v1.py` · `commercial-video-factory/` · `SOURCEA_DEMO_VIDEO_100_UPGRADE_PLAN_2026-06-15_v1.md`  
**Law:** Optimize **pipeline state**, not emails sent. Video/page/proposal are **generated artifacts** — but proof must be **≥70% real UI** (`commercial_short_film_v1.py`), never mock terminals on outbound.

---

## 0. What GPT got right (and what you already built)

GPT’s framing matches disk more than chat suggests:

| GPT stage | SourceA today (disk) | Gap |
|-----------|----------------------|-----|
| Market Scanner | Manual / research skills | No autonomous scanner agent |
| Opportunity Ranker | `icp_score` on pipeline rows | No 500/day ranker |
| ICP Matcher | `SOURCEA_ICP_MARKET_IDENTITY_LOCKED_v1.md` | Not wired to auto-ingest |
| Research Agent | `sina-research-lessons` · Worker | Not per-prospect at scale |
| Personalization Agent | `commercial_eval_booking_agent_v1.py` bodies | Per-row, not 100/day |
| **Video/Page Generator** | **`commercial-video-factory/` (Remotion)** · `commercial_short_film_v1.py` | Not wired to pipeline row_id |
| Outreach Agent | `commercial_mail_draft_v1.py` · outbound packs | Founder send click — by design |
| Follow-up Agent | `commercial_reply_qualification_agent_v1.py` | Watches replies, not autonomous Mail |
| Objection Agent | — | **Missing** |
| Proposal Agent | `attach/procurement-pack.html` static | Not generated per deal |
| Legal/Contract Agent | — | **Missing** |
| Negotiation Agent | — | **Missing** |
| Close Agent | `pilot_deposit` · `close` pipeline states | No autonomous close |
| **Human approval only** | `hello@sourcea.com` send policy · hub taps | **Correct** |

**KPI GPT proposed → already in `commercial_pipeline_v1.py`:**

```python
TARGETS = {
    "researched": 500,
    "personalized_sent": 100,
    "replied": 30,
    "proof_viewed": 20,
    "eval_scheduled": 10,
    "pilot_deposit": 5,
    "close": 1,
}
```

Headline on factory live: `0 sent · 3 active · 0 close — optimize pipeline state` — that **is** the Deal Engine KPI, not activity vanity.

**Current honest counts (2026-06-15):** 3 active · 2 proof_viewed · 1 eval_scheduled · 0 sent · 0 close.

---

## 1. One autonomous commercial OS (not five websites)

GPT: *website · message · video · pricing · proposal = generated artifacts.*

SourceA architecture logged:

```text
~/.sina/commercial-pipeline-v1.jsonl     ← deal state SSOT (append-only)
~/.sina/commercial-pipeline-glance-v1.json ← simultaneous conversations glance
scripts/commercial_agents_wire_v1.py     ← routes next agent per row status
scripts/commercial_pipeline_repair_v1.py   ← heal + sync + pack refresh
commercial-video-factory/                  ← JSON prospect in → MP4 out (Remotion)
SourceA-landing/green-unified/             ← canonical site shell (not per-prospect yet)
~/.sina/outbound/eval-booking-*/           ← per-row artifact packs
```

**North star:** `commercial_pipeline_v1.py --glance` is the **Deal Engine dashboard**. Worker Hub `commercial_agents` payload is the **orchestration layer**. Brain routes; agents advance **state**; founder approves **send** and **close**.

---

## 2. Deal Engine — full agent map (build order)

### Layer 1 — State machine (DONE)

Funnel: `researched → personalized_sent → replied → proof_viewed → eval_scheduled → pilot_deposit → close`

Scripts: `commercial_pipeline_v1.py` · `commercial_agents_wire_v1.py` · hub wire in `worker_hub_v1.py`

**Optimization target:** maximize rows in `eval_scheduled` + `pilot_deposit` **simultaneously**, not sends/day.

### Layer 2 — Artifact generators (PARTIAL)

| Artifact | Generator | Input | Output |
|----------|-----------|-------|--------|
| Eval email pack | `commercial_eval_booking_agent_v1.py` | `row_id` | `~/.sina/outbound/eval-booking-{id}/` |
| Reply follow-up | `commercial_reply_qualification_agent_v1.py` | inbound text | `reply-followup-{id}/` |
| **Prospect reel (30s)** | **`commercial-video-factory`** | `remotion-prospect-reel-v1.json` | `out/{company}-reel.mp4` |
| **Short film (90s)** | `commercial_short_film_v1.py` | `commercial-short-film-beats-v1.json` | Playwright b-roll + narration |
| Landing page | Static green-unified | — | Per-prospect page **not yet** |
| AEG proof URL | `inject_landing_aeg_proof_v1.py` | factory repository | `proof/live.html` |

### Layer 3 — Missing agents (GPT list — honest backlog)

| Agent | Priority | First script stub |
|-------|----------|-------------------|
| Market intelligence | P2 | `commercial_market_scan_v1.py` |
| ICP scoring at ingest | P1 | extend `add_row()` with auto-score |
| Narrative optimization | P1 | critic agent on pack body before send |
| Objection handling | P1 | `commercial_objection_agent_v1.py` |
| Pricing optimization | P2 | lane-specific from SSOT pricing |
| Contract drafting | P3 | template from procurement pack |
| Manager/Critic | **P0** | session gate + `critic_boot` on every artifact |

### Layer 4 — Human gates (NON-NEGOTIABLE)

- Outbound send: `hello@sourcea.com` only (`commercial_recipient_guard_v1.py`)
- Mail open: `--open-mail` requires real `--to`
- Close: `pilot_deposit` transition manual until Stripe/contract wired
- Video ship: no mock-only reels in AB1 packs (see §4)

---

## 3. Gemini Remotion stack — already present

**FOUND:** `commercial-video-factory/` — description: *"JSON prospect in, MP4 proof reel out"*

```bash
cd commercial-video-factory
npm run studio          # preview ProspectReel
npm run render:sample   # render sample JSON → MP4
```

**Stack matches Gemini recommendation:**

| Gemini | SourceA |
|--------|---------|
| Remotion (React/TS) | ✅ `src/ProspectReel.tsx` |
| JSON scenario in | ✅ `data/sample-prospect-reel-v1.json` |
| Spring text pop-in | ✅ `PopText` component |
| `npx remotion render` | ✅ `npm run render` |
| ElevenLabs voice | 🔶 `commercial_short_film_v1.py` reads `secrets.env` — not wired to Remotion yet |
| Flux backgrounds | 🔶 Not wired — CSS gradients today |

**Props schema (`remotion-prospect-reel-v1`):**

- `company` · `lane` (AB1/NW1/AEG/WBC) · `hook` · `pain` · `proof_line`
- `scenario` · `verdict` · `receipt_hash` · `proof_url` · `cta`
- `duration_seconds` (default 30) · `pipeline_row_id` (optional)

### Gemini "Build MVP Fast" 30s structure → maps to ProspectReel beats

| Gemini section | ProspectReel `kind` | Seconds (30s total) |
|----------------|-------------------|---------------------|
| Hook 0–5s | `hook` | 0–17% (~5s) |
| Pain 5–15s | `pain` | 17–40% (~7s) |
| Value 15–25s | `proof` | 40–78% (~11s) |
| CTA 25–30s | `cta` | 78–100% (~7s) |

For **SourceA AB1**, replace MVP Fast copy with governance pain:

- Hook: *"Can you prove what your agents executed last night?"*
- Pain: *"Logs aren't receipts. Counsel can't file a chat transcript."*
- Proof: **real** `sourcea-boot` terminal or `proof/live.html` b-roll — not mock
- CTA: *Book 15-min live proof*

---

## 4. Critical fix — weak proof in Remotion today

**Problem:** `ProspectReel.tsx` `TerminalMock` draws **fake** CLI lines (`witness-ai proof`). That violates:

- `commercial_short_film_v1.py` law: **≥70% real product UI**
- Founder law: **never ship weak proof online**
- SSOT: SourceA brand on AB1 — sample JSON still says `Witness AI` / `witnessbc.com`

**Upgrade path (Gemini + DEMO plans unified):**

```text
1. Playwright capture clips per beat → public/broll/{row_id}/*.mp4
2. Remotion <Video> component replaces TerminalMock for proof beat
3. pipeline row → JSON props via commercial_video_factory_v1.py
4. ElevenLabs audio → public/voice.mp3 (optional beat)
5. render → attach to eval-booking pack + proof_url
```

**Hybrid stack (best of Gemini + Screen Studio + Remotion):**

| Layer | Tool |
|-------|------|
| Real UI capture | Playwright (`commercial_short_film_v1.py`) or Screen Studio |
| Motion/template | Remotion (`commercial-video-factory`) |
| Voice | ElevenLabs API |
| Ship gate | `validate-demo-film-quality-v1.sh` (DEMO-500) |

---

## 5. Wire Deal Engine → Video Factory (concrete)

### New script (proposed): `scripts/commercial_video_factory_v1.py`

```text
INPUT:  --row-id cp-a0c7c6c607
READ:   commercial-pipeline row · aeg-live · trust-signals · public-urls
WRITE:  commercial-video-factory/data/prospect-{row_id}-v1.json
RUN:    cd commercial-video-factory && npm run render -- --props=...
OUTPUT: ~/.sina/outbound/eval-booking-{suffix}/prospect-reel.mp4
PATCH:  pack.json proof_video_path · body.txt link
```

### Pipeline transition hook

When row hits `proof_viewed` → auto-queue:

1. `commercial_eval_booking_agent_v1.py` (pack)
2. `commercial_video_factory_v1.py` (30s reel)
3. Optional: `commercial_short_film_v1.py` (90s master — weekly, not per prospect)

### Per-prospect landing (GPT "generated website")

**Phase 1 (now):** query param `proof/live.html?prospect=` + dynamic headline from JSON  
**Phase 2:** Remotion still frame + Hub SSR slice — not five full sites  
**Phase 3:** Navattic-style interactive embed from same Playwright capture

---

## 6. 50 high-leverage ENGINE plans (subset of 100)

| ID | Title | Grade | Motion |
|----|-------|-------|--------|
| ENGINE-401 | Pipeline TARGETS = Deal Engine KPI dashboard | A | Already in glance — expose in Hub hero |
| ENGINE-402 | Bottleneck agent from `commercial_agents_wire_v1` | A | Show `reply_qualification` vs `eval_booking` |
| ENGINE-403 | Wire `pipeline_row_id` on every outbound pack | A | `pack.json` field |
| ENGINE-404 | `commercial_video_factory_v1.py` row → JSON | A | New script |
| ENGINE-405 | Replace TerminalMock with `<Video>` b-roll | A | Edit ProspectReel.tsx |
| ENGINE-406 | AB1 sample JSON → SourceA brand | A | Fix sample-prospect-reel-v1.json |
| ENGINE-407 | Render reel on eval pack create | B | repair script hook |
| ENGINE-408 | Attach `prospect-reel.mp4` to eval body | B | pack template |
| ENGINE-409 | ElevenLabs wire in factory | B | secrets.env + render pipeline |
| ENGINE-410 | Critic agent blocks mock-only renders | A | critic_boot on render receipt |
| ENGINE-411 | Market scan stub → researched rows | D | 500/day aspirational |
| ENGINE-412 | ICP auto-score on `add_row` | B | extend pipeline |
| ENGINE-413 | Objection agent from reply patterns | B | new script |
| ENGINE-414 | Narrative critic on pack body | B | pre-send gate |
| ENGINE-415 | Per-prospect proof URL in JSON props | A | `resolve_aeg_proof_url()` |
| ENGINE-416 | 9:16 render profile for LinkedIn | B | second Remotion composition |
| ENGINE-417 | Instagram reel composition (Gemini) | C | `ProspectReelVertical.tsx` |
| ENGINE-418 | Word-level captions from Descript export | B | SRT → Remotion |
| ENGINE-419 | Short film master → clip library | B | ffmpeg slice beats |
| ENGINE-420 | Gate K URL in every video CTA | C | durable host |
| ENGINE-421–450 | Extend DEMO-401–430 with ENGINE prefix cross-refs | B | see DEMO doc |
| ENGINE-451 | Hub Action: Render prospect reel | B | `run_commercial_action` |
| ENGINE-452 | Simultaneous conversation metric | A | `active_conversations` in glance |
| ENGINE-453 | State downgrade guard | A | already in pipeline sync |
| ENGINE-454 | CRM memory JSONL per row | B | append touchpoints |
| ENGINE-455 | Follow-up timing agent | B | days-since-status |
| ENGINE-456 | Proposal PDF per row | D | generated artifact |
| ENGINE-457 | Pricing band from lane | B | AB1 $3–10K in video CTA |
| ENGINE-458 | Contract template agent | D | post-pilot |
| ENGINE-459 | Close agent → pilot_deposit receipt | D | founder only |
| ENGINE-460 | Deal Engine receipt daily | A | `deal-engine-daily-v1.json` |
| ENGINE-461–500 | Mirror DEMO-461–500 distribution/refresh/integration | B | unified registry |

Full DEMO-401–500 remains in `SOURCEA_DEMO_VIDEO_100_UPGRADE_PLAN_2026-06-15_v1.md`. ENGINE-421–450 are **cross-refs**, not duplicates.

---

## 7. Success models applied to SourceA Deal Engine

| Model | Application |
|-------|-------------|
| **Linear** | Reel hook = instant product, no logo splash |
| **Arcade** | One capture → MP4 + interactive + eval URL |
| **GPT simultaneous deals** | `TARGETS` funnel widths = conversation capacity |
| **Gemini Remotion** | Template once · 100 prospects = 100 JSON files · `npm run render` |
| **SourceA wedge** | BLOCK beat must be **real** AEG/boot — moat |

**Wrong optimization (ignore):**

- Emails sent/day without reply rate
- Demos booked without eval_scheduled conversion
- Instagram volume without AB1 lane discipline

**Right optimization:**

```text
maximize Σ rows where status ∈ {proof_viewed, eval_scheduled, pilot_deposit}
subject to: founder_send_clicks ≤ human_capacity
subject to: every artifact passes critic_boot + real UI ≥70%
```

---

## 8. Build MVP Fast vs SourceA AB1 (lane clarity)

Gemini's Persian MVP Fast script is a **different product** (14-day MVP shop). **Do not paste** into SourceA AB1 reels.

| | Build MVP Fast (Gemini example) | SourceA AB1 |
|--|--------------------------------|-------------|
| Pain | 6 months wasted | Can't prove agents overnight |
| Proof | UI mockups | `sourcea-boot` PASS/BLOCK |
| CTA | DM "MVP" | Book 15-min eval + live proof URL |
| Video style | 9:16 text pop | 16:9 terminal + command center |
| Lane | Consumer Instagram | Enterprise/agency controlled automation |

Use Gemini's **technical workflow** (Remotion + JSON + render). Use SourceA **copy** from `commercial-short-film-beats-v1.json` and eval packs.

---

## 9. One next tap

```bash
cd ~/Desktop/SourceA/commercial-video-factory && npm run render:sample
```

Watch `out/sample-prospect-reel.mp4`. If the proof beat feels fake (it will — `TerminalMock`), that's ENGINE-405: replace with Playwright b-roll from `http://127.0.0.1:5180/sourcea/proof/live.html`.

Then say **wire ENGINE-404** and I'll add `commercial_video_factory_v1.py` to generate JSON from `cp-a0c7c6c607` and attach the reel to the AB1 eval pack.

---

## 10. Lessons learned

1. **GPT and Gemini are describing the same company** — orchestration layer + programmatic artifacts — SourceA already started both logged.  
2. **The gap is wiring**, not philosophy: pipeline row → Remotion props → outbound pack.  
3. **Remotion without real UI is still weak proof** — worse than Screen Studio alone.  
4. **Human send gate is a feature**, not a bug, for controlled commercial lane.  
5. **KPI = pipeline state** is implemented; Hub should headline `eval_scheduled / TARGET` not email counts.

---

*End of SOURCEA_AI_DEAL_ENGINE_AND_VIDEO_FACTORY_2026-06-15_v1.md*
