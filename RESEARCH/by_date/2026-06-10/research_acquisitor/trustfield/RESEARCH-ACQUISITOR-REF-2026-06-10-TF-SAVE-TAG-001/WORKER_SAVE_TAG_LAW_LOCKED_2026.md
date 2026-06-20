
**Saved:** 2026-06-10T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
<!--
trace_id: RESEARCH-ACQUISITOR-REF-2026-06-10-TF-SAVE-TAG-001
worker_id: research_acquisitor
subject: trustfield
execution_authority: false
repo: TrustField Technologies
chat: MANDATORY_TRUSTFIELD_CHAT_LOCKED_v1
-->

# [AUTO] TrustField worker — save tag law (LOCKED)

**[AUTO]** · 2026-06-10 · **Mandatory founder rule**

---

## Rule (non-negotiable)

**Save everything for this repo and this chat ONLY under the TrustField tag namespace.**

| Field | Value (use exactly) |
|-------|---------------------|
| **worker_id** | `research_acquisitor` (advise/research) or `worker` (build receipt cites parent blueprint) |
| **subject** | `trustfield` |
| **trace_id** | `RESEARCH-ACQUISITOR-REF-YYYY-MM-DD-TF-*` or `RESEARCH-ACQUISITOR-YYYYMMDD-TF-*` |
| **Parent blueprint** | `RESEARCH-ACQUISITOR-20260608-TF-001` |
| **Repo** | `/Users/sinakazemnezhad/Desktop/TrustField Technologies` |
| **execution_authority** | `false` on every `_META.yaml` |

## Forbidden

- Saving under `noetfield`, `virlux`, `seven77`, `sina_os`, `dual_brand` (unless Brain routes dual-brand — then still mirror **trustfield slice** separately)
- Superseded prefixes: `RA-MKT-*`, `GOVGS-*`, `TF-COMM`, `NF-COMM`
- Chat-only decisions · random SourceA folders · `~/.sina/` writes from Portfolio Worker
- Mixing Noetfield/Virlux content into TrustField trace folders

## Mandatory save path (Tier 1 mirror)

```
~/Desktop/SourceA/RESEARCH/by_date/{date}/research_acquisitor/trustfield/{trace_id}/
  ├── [artifact].md or .yaml
  └── _META.yaml   # execution_authority: false
```

Vault staging: `~/.sina/agent-workspaces/trustfield/`

## Closeout (every session with research/decisions)

```bash
python3 ~/Desktop/SourceA/RESEARCH/_GOVERNANCE/research_save_enforcer.py save \
  --path <vault_file> --worker research_acquisitor --subject trustfield --trace-id <trace_id>
python3 ~/Desktop/SourceA/RESEARCH/_GOVERNANCE/research_save_enforcer.py verify --trace-id <trace_id>
```

**Blocked closeout if `enforcer_verify != PASS`.**

---

**[AUTO]** · LOCKED · G7 in `GLOBAL_RULES_LOCKED_2026.md`
