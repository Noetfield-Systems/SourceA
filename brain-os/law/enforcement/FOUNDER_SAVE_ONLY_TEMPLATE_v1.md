# Founder SAVE ONLY template (reference v1)

**Locked:** 2026-06-09 · **Incident:** CIR-COSPRO-RESEARCH-SAVE-2026-06-07  
**Law:** `AGENT_VERBS_SAVE_WORK_EDIT_LOCKED_v1.md`

---

## Paste this when you want a report kept

```text
SAVE ONLY: docs/research/<filename>
FORBIDDEN: everything else
```

Agent writes **that one file** → **STOP**.

For pathless `SAVE`, `SAVE AND LOCK`, `LOCK`, or `FILE`, do **not** ask ASF for an exact path. Run:

```bash
python3 scripts/agent_filing_registry_gate_v1.py resolve --agent <id> --intent "<founder message>" --json
```

Use the resolved `route_id`, `path`, and `next_steps[]`; ask only category/scope on no-match or ambiguity.

---

## What SAVE means

- One physical file in docs (or lane vault)
- Stable for future reference
- **No** SSOT · AGENTS · roadmap · registry · sync · other agents' files
- Exception: pathless filing uses the filing registry only to choose the one physical target.

## What SAVE does not mean

- Wire ecosystem
- Update read chains
- Register/sync unless you order that separately

## Other verbs

| Verb | When |
|------|------|
| **WORK** | Worker INBOX / Product build — full speed, no extra ask |
| **EDIT ALLOWED** | Cross-desk — `EDIT ALLOWED: <path>` + `ACTION:` same message |

---

## Monitor

```bash
tail -5 ~/.sina/governance-events.jsonl
bash ~/Desktop/SourceA/scripts/validate-governance-agent-verbs-v1.sh
```

Closure: `~/.sina/governance/CIR-COSPRO-FINALIZED-v1.yaml`
