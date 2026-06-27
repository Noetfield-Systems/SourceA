# Supabase repo split rule + short YAML handoff notice (LOCKED v1)

**Saved:** 2026-06-27T10:52:00Z  
**Authority:** ASF explicit edit — 2026-06-27  
**Registry:** `data/supabase-portfolio-tiers-v1.json` → `supabase_repo_split_v1`  
**Canonical law:** `docs/SUPABASE_REPO_SPLIT_v1_LOCKED.md`  
**Account map:** `data/portfolio-account-structure-v1.json`  
**Noetfield project rule:** `infra/supabase/noetfield/README.md`  
**Purpose:** Prevent permanent confusion between SourceA, Noetfield, TrustField, and labs Supabase ownership.

---

## One Sentence Law

**SourceA is the platform spine; Noetfield owns the Canada / TrustField operating database; Labs is disposable. Integration crosses by signed events, never by shared tables.**

---

## Canonical Split

| Product / module | Supabase project | Ref | Schemas / ownership | Secrets file |
|---|---|---|---|---|
| SourceA | `portfolio-spine` | `ldfruywifqnfpwsfgmdl` | `gov`, `foundation`, `audit`, `forge_factory` | `~/.sourcea-secrets/portfolio-spine.env` |
| Forge / Forge Factory / WTM | `portfolio-spine` | `ldfruywifqnfpwsfgmdl` | `forge_factory` | `~/.sourcea-secrets/portfolio-spine.env` |
| Noetfield | `noetfield` | `tkgpapowwplupyekpivy` | `noetfield` | `~/.sourcea-secrets/noetfield.env` |
| TrustField | `noetfield` | `tkgpapowwplupyekpivy` | `trustfield` | `~/.sourcea-secrets/noetfield.env` |
| VIRLUX / labs / research | `labs-sandbox` | `bueoakgiisvufxfbdvoa` | `virlux_ops`, `labs`, `research` | `~/.sourcea-secrets/labs-sandbox.env` |

---

## Rule

1. **SourceA / Forge / Brain / Hub plan registry** goes to `portfolio-spine`.
2. **Noetfield + TrustField / Canada operating data** goes to the dedicated `noetfield` project.
3. **VIRLUX / labs / experiments** goes to `labs-sandbox`.
4. **No cross-project JOINs, foreign keys, or views.**
5. **Cross-project integration is async only:** signed webhook, signed event row, or status token.
6. **Secrets never enter the repo.** Use only `~/.sourcea-secrets/*.env`.

---

## Why TrustField Sits With Noetfield

TrustField is the Canada / operational trust product lane, not the SourceA / Forge platform spine. It shares the `noetfield` Supabase project but stays in its own schema:

- `noetfield.*` — Noetfield intelligence, decision audit, drift, copilot pilot
- `trustfield.*` — TrustField operational data and plan registry lane

This keeps TrustField operating data out of the SourceA platform database while still placing TrustField under the Noetfield business/account lane.

---

## Forbidden

- TrustField tables in `portfolio-spine`
- SourceA plan registry in `noetfield`
- VIRLUX payment / FINTRAC data in labs or SourceA
- Cross-project DB JOINs
- Supabase keys in repo `.env`, docs, prompts, or code
- Autonomous agents using production service-role keys directly

---

## Required Integration Pattern

If SourceA needs TrustField status:

```text
TrustField / Noetfield Supabase
→ signed event / webhook / status token
→ portfolio-spine audit or status table
→ Brain / Hub / Chat Unify reads public-safe status
```

Never:

```sql
SELECT *
FROM portfolio_spine...
JOIN noetfield...
```

---

## Agent Routing Checklist

Before any Supabase migration, API, dashboard, or secret work:

1. Identify product owner:
   - SourceA / Forge / Brain / Hub → `portfolio-spine`
   - Noetfield / TrustField / Canada trust ops → `noetfield`
   - VIRLUX / labs / experiments → `labs-sandbox`
2. Identify schema:
   - SourceA platform → `forge_factory`, `gov`, `audit`, `foundation`
   - Noetfield → `noetfield`
   - TrustField → `trustfield`
   - Labs → `virlux_ops`, `labs`, `research`
3. Load only the matching local secret file.
4. If another project needs data, design async event integration only.
5. Update `data/supabase-portfolio-tiers-v1.json` before changing ownership.

---

## Governance Specialist Machine Pipeline

Machine key: `data/supabase-portfolio-tiers-v1.json` → `supabase_repo_split_v1.governance_specialist_pipeline`

```yaml
pipeline: supabase_repo_split_rollout_governance_v1
owner_role: governance_specialist
authority_order:
  - SourceA data/supabase-portfolio-tiers-v1.json
  - SourceA docs/SUPABASE_REPO_SPLIT_RULE_SHORT_YAML_HANDOFF_NOTICE_LOCKED_v1.md
  - target repo local handoff
steps:
  - confirm_target_repo_lane
  - paste_short_yaml
  - add_sourcea_authority_pointer
  - search_stale_ownership_language
  - commit_only_rollout_files_per_repo
commit_policy: "one governance commit per repo; never git add -A in dirty trees"
```

---

## Paste-Ready YAML Handoff

Use this exact short block in other repos:

```yaml
supabase_repo_split_v1:
  rule: "SourceA/Forge = portfolio-spine; Noetfield/TrustField = noetfield; labs/Virlux = labs-sandbox."
  registry: "data/supabase-portfolio-tiers-v1.json"
  sourcea:
    project: "portfolio-spine"
    ref: "ldfruywifqnfpwsfgmdl"
    owns: ["sourcea", "forge_factory", "gov", "foundation", "audit"]
    secrets: "~/.sourcea-secrets/portfolio-spine.env"
  noetfield:
    project: "noetfield"
    ref: "tkgpapowwplupyekpivy"
    owns: ["noetfield", "trustfield"]
    secrets: "~/.sourcea-secrets/noetfield.env"
  labs:
    project: "labs-sandbox"
    ref: "bueoakgiisvufxfbdvoa"
    owns: ["virlux", "labs", "research", "experiments"]
    secrets: "~/.sourcea-secrets/labs-sandbox.env"
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

## Ultra-Short Handoff

```yaml
supabase_split: "SourceA/Forge→portfolio-spine; Noetfield/TrustField→noetfield; Labs/Virlux→labs-sandbox; async events only; no cross-project joins; no secrets in repo."
```

