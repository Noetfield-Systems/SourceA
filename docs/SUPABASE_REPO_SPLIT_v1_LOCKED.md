# Supabase repo split — LOCKED v1

**Saved:** 2026-06-27T10:55:00Z  
**Authority:** ASF  
**Machine registry:** `data/supabase-portfolio-tiers-v1.json` → key `supabase_repo_split_v1`  
**Extended routing:** `docs/SUPABASE_REPO_SPLIT_RULE_SHORT_YAML_HANDOFF_NOTICE_LOCKED_v1.md`  
**Org / pause law:** `docs/SUPABASE_ORG_SPLIT_FOUNDER_STEPS_LOCKED_v1.md`

---

## One sentence

SourceA/Forge lives on **portfolio-spine**; Noetfield/TrustField on **noetfield**; Labs/Virlux on **labs-sandbox** — integrate by **async signed events only**; never cross-project joins; secrets stay in `~/.sourcea-secrets/`.

---

## Canonical YAML (paste-ready)

```yaml
supabase_repo_split_v1:
  rule: "SourceA/Forge = portfolio-spine; Noetfield/TrustField = noetfield; labs/Virlux = labs-sandbox."
  registry: "data/supabase-portfolio-tiers-v1.json"
  sourcea:
    project: "portfolio-spine"
    ref: "ldfruywifqnfpwsfgmdl"
    owns: ["sourcea", "forge_factory", "gov", "foundation", "audit"]
    secrets: "~/.sourcea-secrets/portfolio-spine.env"
    db_secrets: "~/.sourcea-secrets/portfolio-spine-db.env"
  noetfield:
    project: "noetfield"
    ref: "tkgpapowwplupyekpivy"
    owns: ["noetfield", "trustfield"]
    secrets: "~/.sourcea-secrets/noetfield.env"
    db_secrets: "~/.sourcea-secrets/noetfield-db.env"
  labs:
    project: "labs-sandbox"
    ref: "bueoakgiisvufxfbdvoa"
    owns: ["virlux", "labs", "research", "experiments"]
    secrets: "~/.sourcea-secrets/labs-sandbox.env"
    db_secrets: "~/.sourcea-secrets/labs-sandbox-db.env"
  integration: "async_only"
  allowed_integration: ["signed_webhook", "signed_event_row", "status_token"]
  forbidden:
    - "cross-project joins"
    - "TrustField tables in portfolio-spine"
    - "SourceA plan registry in noetfield"
    - "Virlux payment or FINTRAC data in labs"
    - "Supabase secrets in repo"
```

---

## Ultra-short handoff

```yaml
supabase_split: "SourceA/Forge→portfolio-spine; Noetfield/TrustField→noetfield; Labs/Virlux→labs-sandbox; async events only; no cross-project joins; no secrets in repo."
```

---

## Agent checklist (before any Supabase work)

1. Identify product owner → pick **one** project from the YAML block.
2. Load secrets: `source infra/scripts/load-supabase-secrets-v1.sh <portfolio-spine|noetfield|labs-sandbox>`.
3. Run migrations only under that project's `infra/supabase/<tier>/migrations/`.
4. If another tier needs data → design webhook / signed event row — **never** SQL JOIN across projects.

---

## Tables placed this session (2026-06-27)

| Table | Correct project | Status |
|-------|-----------------|--------|
| `public.sourcea_plan_registry` | portfolio-spine | ✅ 23,485 rows |
| `public.cloud_forge_run_rows` | portfolio-spine | ✅ 1,766 rows |
| `noetfield.*` (migrations 0001–0008) | noetfield | ✅ applied |
