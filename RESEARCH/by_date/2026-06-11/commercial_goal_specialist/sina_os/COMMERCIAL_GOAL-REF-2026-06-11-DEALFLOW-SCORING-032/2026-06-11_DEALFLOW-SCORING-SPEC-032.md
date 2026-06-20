# Dealflow Scoring Engine — Spec (Option C · future)

**Saved:** 2026-06-11T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**trace_id:** `COMMERCIAL_GOAL-REF-2026-06-11-DEALFLOW-SCORING-032`  
**parent:** `ACCELERATION-GTM-032`  
**execution_authority:** false · **status:** spec only — **not** 6MO SourceA P0  
**not_same_as:** API code scout (`sidecar_scout_api_v1.py`)

---

## Purpose

Future **portfolio discovery** funnel: score inbound startups/projects for studio PoC or SPV — separate from SourceA factory queue.

**Target funnel (monthly):** 200 → 20 qualified → 5 demo → 1 PoC → 1 paying pilot

---

## Minimal SQL schema

```sql
-- dealflow_v1.sql (Postgres / Supabase when lane activates)

CREATE TABLE dealflow_source (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name          TEXT NOT NULL,
  url           TEXT,
  source_type   TEXT CHECK (source_type IN ('product_hunt','github','rss','referral','manual')),
  ingested_at   TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE dealflow_company (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id     UUID REFERENCES dealflow_source(id),
  name          TEXT NOT NULL,
  website       TEXT,
  sector        TEXT,
  stage         TEXT,
  team_score    SMALLINT,   -- 0-100
  tech_score    SMALLINT,
  traction_score SMALLINT,
  governance_fit SMALLINT, -- alignment with SourceA proof story
  total_score   SMALLINT GENERATED ALWAYS AS (
    (COALESCE(team_score,0)*0.25 +
     COALESCE(tech_score,0)*0.25 +
     COALESCE(traction_score,0)*0.30 +
     COALESCE(governance_fit,0)*0.20)::SMALLINT
  ) STORED,
  status        TEXT DEFAULT 'new' CHECK (status IN (
    'new','qualified','demo','poc','pilot','pass','archive'
  )),
  lane_hint     TEXT CHECK (lane_hint IN ('noetfield','trustfield','virlux','777','none')),
  notes         TEXT,
  updated_at    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE dealflow_event (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id    UUID REFERENCES dealflow_company(id),
  event_type    TEXT NOT NULL,
  actor         TEXT DEFAULT 'agent',
  payload       JSONB,
  created_at    TIMESTAMPTZ DEFAULT now()
);
```

---

## Scoring weights (v1)

| Dimension | Weight | Signals |
|-----------|--------|---------|
| **Team** | 25% | founder prior exit · domain years · Canada presence |
| **Tech** | 25% | OSS stars · API quality · agent-native architecture |
| **Traction** | 30% | revenue · pilots · waitlist · production agents |
| **Governance fit** | 20% | regulated vertical · audit need · Copilot/MSB adjacency |

**Qualified threshold:** `total_score >= 65` AND `governance_fit >= 50`

---

## Agentic workflow (when activated)

```text
Crawler (PH/GitHub/RSS) → ingest dealflow_source
→ Scout agent scores → CRM row
→ Commercial Goal weekly review → ASF PICK top 5
→ Lane worker builds PoC in mandatory chat
→ Case study + PR if pilot pays
```

**Firewall:** newsroom scoring agent ≠ investment decision — ASF PICK required for PoC spend.

---

## Activation gate

| Gate | PASS when |
|------|-----------|
| **G1** | W1+W2 SourceA demo shipped |
| **G2** | At least one W3 pilot closed |
| **G3** | ASF explicit yes to external dealflow studio |

Until G3: use **manual ICP lists** in `NOETFIELD-LANE-029` / `TRUSTFIELD-LANE-030`.

**execution_authority:** false
