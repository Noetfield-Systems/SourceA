
**Saved:** 2026-06-07T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
[COMMERCIAL_GOAL_AGENT_REF · commercial_goal_specialist · COMMERCIAL_GOAL-REF-TAG-STD-000]

| Field | Value |
|-------|-------|
| **agent_name** | Commercial Goal Specialist |
| **agent_id** | `commercial_goal_specialist` |
| **ref_tag** | `COMMERCIAL_GOAL-REF-{TOPIC}-{NNN}` |
| **trace_id** | `COMMERCIAL_GOAL-REF-{YYYY-MM-DD}-{TOPIC}-{NNN}` |
| **registry_id** | `rr-YYYYMMDD-{8hex}` |
| **vault** | `~/.sina/agent-workspaces/trustfield/commercial-goal/` |
| **manifest** | `COMMERCIAL_GOAL-REF-MANIFEST-009` |
| **canonical** | `false` |

## Law

Every document this agent saves **must** carry line-1 agent ref under **Commercial Goal Specialist** — not TrustField, Commercial Goal Specialist, or Executor tags.

## Required header (YAML)

```yaml
# [COMMERCIAL_GOAL_AGENT_REF · commercial_goal_specialist · COMMERCIAL_GOAL-REF-YYYY-MM-DD-TOPIC-NNN] rr-YYYYMMDD-xxxxxxxx
trace:
  agent_ref: COMMERCIAL_GOAL_AGENT_REF
  agent_name: Commercial Goal Specialist
  agent_id: commercial_goal_specialist
  trace_id: COMMERCIAL_GOAL-REF-YYYY-MM-DD-TOPIC-NNN
  ref_tag: COMMERCIAL_GOAL-REF-TOPIC-NNN
  registry_id: rr-YYYYMMDD-xxxxxxxx
```

## Required header (Markdown)

```markdown
[COMMERCIAL_GOAL_AGENT_REF · commercial_goal_specialist · COMMERCIAL_GOAL-REF-YYYY-MM-DD-TOPIC-NNN]

| agent_name | Commercial Goal Specialist |
| agent_id | `commercial_goal_specialist` |
| ref_tag | `COMMERCIAL_GOAL-REF-TOPIC-NNN` |
| trace_id | `COMMERCIAL_GOAL-REF-YYYY-MM-DD-TOPIC-NNN` |
| registry_id | `rr-YYYYMMDD-xxxxxxxx` |
```

## Grep

```bash
rg "COMMERCIAL_GOAL-REF" ~/.sina/agent-workspaces/trustfield/commercial-goal/
rg "commercial_goal_specialist" ~/.sina/agent-workspaces/trustfield/commercial-goal/
```
