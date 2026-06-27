# Vocabulary Intelligence Machine (VIM) — Blueprint v1.1

**Saved:** 2026-06-24T21:30:00Z  
**Unified spine:** `data/sourcea-vocabulary-unified-index-v1.json` · `brain-os/law/enforcement/SOURCEA_VOCABULARY_UNIFIED_LOCKED_v1.md`  
**Machine SSOT:** `data/vocabulary-intelligence-registry-v1.json`  
**Chat Unify:** tab **Vocabulary Intel** · `scripts/chat_unify_vocabulary_intelligence_v1.py`  
**Scanner:** `scripts/vocabulary_intelligence_scan_v1.py`  
**Receipt:** `~/.sina/chat-unify-vocabulary-intelligence-v1.json`

---

## One law

> **Scan every surface → classify tier + subject → suggest display word with reason → receipt. Apply only Tier 1–2 when a campaign is armed. Tier 3 and poison governance never get casual renames.**

---

## Problem (resolved by unified index)

Vocabulary **was** in six fragmented places. **Now:** `data/sourcea-vocabulary-unified-index-v1.json` is the spine — all layers defer to it. VIM scans surfaces; unified index defines subjects, tiers, and display names.

---

## Three tiers

| Tier | Name | Who sees it | Change? |
|------|------|-------------|---------|
| **1** | Founder-facing | Hub UI, landing status, agent close lines, emails | **Yes** — display text |
| **2** | Ops display | `one_law`, boot.json, CLI help, `show_this` | **Yes** — copy not keys |
| **3** | Machine frozen | `/api/cloud-forge-run/*`, `cloud_forge_run_head`, batch JSON keys, filenames | **No** — migration campaign only |

---

## Subject tags (never mix)

| Subject | Example words | Policy |
|---------|---------------|--------|
| `motor_cloud` | drain, Cloud Forge Run, Auto Runtime, Cloud Forge Run | → **Cloud Forge Run** / **Auto Runtime** |
| `product_loop` | scoped loop, loop build, `/sourcea/loops/` | **Keep** — commercial SKU |
| `chat_unify_loop` | founder loop, ORD loop, verify pipeline | **Keep** — Chat Unify machines |
| `governance_poison` | poison, anti-poison, mirror scrub | **Governance only** — not motor display |
| `forge_product` | Forge, ICP compile, machine prove | `data/sourcea-forge-vocabulary-disambiguation-v1.json` |

---

## Architecture

```text
VIM Control Plane (goal / campaign / approve)
        │
        ├── vocabulary_intelligence_scan_v1.py     (scan + classify + suggest)
        ├── vocabulary_intelligence_apply_v1.py    (Phase 2 — tier 1–2 patch)
        ├── vocabulary_intelligence_live_v1.py       (Phase 3 — curl landing + Railway)
        └── validate-vocabulary-intelligence-v1.sh (no Tier-1 stale after campaign)
```

**Scan profiles** (registry `scan_profiles`):

| Profile | Roots |
|---------|-------|
| `sourcea_repo` | `~/Desktop/SourceA` |
| `founder_disk` | `~/.sina/*.json` receipts |
| `websites` | `SourceA-landing/`, `sites/SourceA-landing/` |

---

## Campaign shape

First campaign: **`motor-rename-v1`**

- **Goal:** Cloud motor display = **Cloud Forge Run** + **Auto Runtime**
- **Apply tiers:** 1, 2 only
- **Skip:** `secondary-cloud-forge-run-batch-*`, API paths, product loop pages

---

## Scanner usage (Phase 1 — shipped)

```bash
cd ~/Desktop/SourceA
python3 scripts/vocabulary_intelligence_scan_v1.py \
  --campaign motor-rename-v1 \
  --profile sourcea_repo \
  --write-receipt \
  --json
```

Optional profiles:

```bash
python3 scripts/vocabulary_intelligence_scan_v1.py \
  --campaign motor-rename-v1 \
  --profile founder_disk \
  --profile websites \
  --write-receipt \
  --json
```

**Output:** hits with `tier`, `subject`, `match`, `suggestion`, `reason`, `action` (`patch` | `skip` | `glossary_only`).

---

## Classifier rules (machine)

1. Path matches `tier3_path_globs` or line matches `tier3_line_patterns` → **Tier 3** · `action: skip`
2. Path matches `tier2_path_globs` or key `one_law` / `show_this` / `for_founder` → **Tier 2**
3. `.html` / hub UI / `brain_live_context` close lines → **Tier 1**
4. Line matches `product_loop.keep_patterns` or path `/sourcea/loops/` → **subject: product_loop** · `action: skip`
5. Line matches `chat_unify_loop.keep_patterns` → **subject: chat_unify_loop** · `action: skip`
6. Else motor retired pattern → **subject: motor_cloud** · suggest from `display_map`

---

## Phase roadmap

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 0 | Registry + blueprint + scanner dry-run | **shipped** |
| 0.5 | Unified vocabulary index + law | **shipped v1.0** |
| 1 | Chat Unify VIM (repo · URL · paste · file) | **shipped** |
| 2 | `motor-rename-v1` apply script + validator | Next |
| 3 | Live wire landing + Railway `for_founder` | Ship window |
| 4 | Windows profile (`%USERPROFILE%\.sina`) | Later |

---

## Related SSOT (all defer to unified index)

- `data/sourcea-vocabulary-unified-index-v1.json` **← read first**
- `brain-os/law/enforcement/SOURCEA_VOCABULARY_UNIFIED_LOCKED_v1.md`
- `data/cloud-motor-founder-vocabulary-v1.json`
- `data/founder-reply-glossary-v1.json`
- `data/cloud-forge-run-hundred-rows-per-turn-vocabulary-v1.json`
- `brain-os/law/enforcement/SOURCEA_POISON_AND_REALTIME_BLOCKER_TERMINOLOGY_LOCKED_v1.md`
- `data/sourcea-forge-vocabulary-disambiguation-v1.json`
- `scripts/founder_reply_translator_v1.py`

---

*VIM Blueprint v1 · scan-first · tier-safe · subject-aware · receipt-native.*
