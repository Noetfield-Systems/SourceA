---
name: sina-research-intake
description: Submits research and analysis to the Sina Agent Hub pipeline (intake → brainstorm → evaluate → promote). Use when the user or agent finishes research,  analysis, external paste review, or any finding that should be evaluated before implementation.
disable-model-invocation: true
---

# Sina Research Intake

## When to use

- Finished research, analysis, or comparison
- User pasted ChatGPT / external doc that might affect build order
- Cross-agent insight that should not go straight to code

## Pipeline (mandatory for structural impact)

```text
INTAKE → BRAINSTORM → EVALUATE → PROMOTE (skill | council | report)
```

## Submit via hub (preferred — no founder Terminal)

1. Open `http://127.0.0.1:13020/?tab=agent-loop`
2. **Research pipeline** → fill title, body, source agent, target agents
3. Or `POST /api/agent-research` with `action: submit`

## Submit via API

```json
{
  "action": "submit",
  "title": "Short title (8+ chars)",
  "body": "Findings, evidence, paths, proposed next steps (40+ chars)",
  "source_agent": "sinaai_maintainer",
  "source_type": "maintainer_research",
  "target_agents": ["noetfield_local"]
}
```

## After submit

1. Add ≥1 brainstorm note (`action: brainstorm`)
2. Run evaluate (`action: evaluate`)
3. Promote only if composite ≥65 (`action: promote`)

## Governance

- Classify external paste: `INPUT CLASS: EXTERNAL_CRITIC` (L1)
- Do not change WTM step from research alone (L3)
- Law: `AGENT_SKILLS_AND_RESEARCH_PIPELINE_LOCKED_v1.md`
