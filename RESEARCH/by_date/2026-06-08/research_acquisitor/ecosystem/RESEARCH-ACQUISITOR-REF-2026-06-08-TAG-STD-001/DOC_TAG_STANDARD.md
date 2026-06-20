# Doc tag standard — Research Acquisitor

**Saved:** 2026-06-08T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
```
[RESEARCH ACQUISITOR_REF · Research Acquisitor · RESEARCH-ACQUISITOR-REF-2026-06-08-TAG-STD-001]
```

| agent_name | Research Acquisitor |
| trace_id | `RESEARCH-ACQUISITOR-REF-2026-06-08-TAG-STD-001` |
| ref_tag | `RESEARCH-ACQUISITOR-TAG-STD-001` |

| Field | Value |
|-------|-------|
| **agent_name** | `Research Acquisitor` |
| **agent_id** | `research_acquisitor` |
| **trace_id** | `RESEARCH-ACQUISITOR-REF-YYYY-MM-DD-{TOPIC}-{NNN}` |
| **ref_tag** | `RESEARCH-ACQUISITOR-{TOPIC}-{NNN}` |
| **registry_id** | `rr-YYYYMMDD-{hash}` from `research_root_sync.py register` |
| **canonical** | `false` — vault briefs are evidence input, not LOCKED law |

## Law

Every YAML/MD saved by **Research Acquisitor** must carry the agent name in the tag.  
**Forbidden:** generic `RA-REF`, `TF-COMM-REF`, `NF-COMM-REF` without `RESEARCH-ACQUISITOR` prefix.

## Required YAML header

```yaml
# [Research Acquisitor · RESEARCH-ACQUISITOR-REF-2026-06-07-EXAMPLE-001] rr-20260607-xxxxxxxx
trace:
  agent_name: Research Acquisitor
  agent_id: research_acquisitor
  trace_id: RESEARCH-ACQUISITOR-REF-2026-06-07-EXAMPLE-001
  ref_tag: RESEARCH-ACQUISITOR-EXAMPLE-001
  registry_id: rr-20260607-xxxxxxxx
  session_transcript: 85dd7cd4-0977-4cfc-9449-ea278ea0baee
  canonical: false
```

## Required MD header

```markdown
[RESEARCH ACQUISITOR_REF · Research Acquisitor · RESEARCH-ACQUISITOR-REF-...]

| agent_name | Research Acquisitor |
| trace_id | `RESEARCH-ACQUISITOR-REF-...` |
| ref_tag | `RESEARCH-ACQUISITOR-...` |
```

## Lookup

Master index: `~/.sina/agent-workspaces/research-acquisitor/TRACE_REGISTRY.yaml`
