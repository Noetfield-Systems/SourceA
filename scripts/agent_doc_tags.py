#!/usr/bin/env python3
"""Per-agent doc tag standards — exclusive (particular) traceability for every registered agent."""
from __future__ import annotations

from pathlib import Path

from agent_workspace_registry import AGENT_WORKSPACES

AGENT_TAG_PREFIX: dict[str, str] = {
    "trustfield": "TRUSTFIELD",
    "virlux": "VIRLUX",
    "ai_dev_bridge_os": "AIDEVBRIDGE",
    "noetfield_local": "NOETFIELD_LOCAL",
    "noetfield_cloud": "NOETFIELD_CLOUD",
    "seven77": "SEVEN77",
    "semej": "SEMEJ",
    "sinaai_maintainer": "MAINTAINER",
}


def tag_prefix(agent_id: str) -> str:
    return AGENT_TAG_PREFIX.get(agent_id, agent_id.upper().replace("-", "_")[:24])


def doc_tag_standard_md(agent_id: str, label: str, repo_chat: str, workspace: Path) -> str:
    prefix = tag_prefix(agent_id)
    return f"""# Doc tag standard — {label}

```
[{prefix}_AGENT_REF · {agent_id} · {prefix}-REF-TAG-STD-000]
```

| Field | Value |
|-------|-------|
| **ref_tag** | `{prefix}-REF-{{TOPIC}}-{{NNN}}` |
| **trace_id** | `{prefix}-REF-YYYY-MM-DD-{{TOPIC}}-{{NNN}}` |
| **agent_id** | `{agent_id}` |
| **repo_chat** | `{repo_chat}` |
| **workspace** | `{workspace}` |
| **canonical** | `false` |

## Law

Every private reference doc from this agent chat **must** use `{prefix}_AGENT_REF` on line 1 so other agents do not mix or treat it as root LOCKED law.

## Required header

```markdown
[{prefix}_AGENT_REF · {agent_id} · {prefix}-REF-{{TOPIC}}-{{NNN}}]
```

Adoption into SourceA root LOCKED law only via Governance Unification Engine + ASF.
"""


def ensure_agent_doc_tag_standard(agent_id: str, private_root: Path) -> None:
    spec = next((w for w in AGENT_WORKSPACES if w["id"] == agent_id), None)
    if not spec:
        return
    label = spec.get("label") or agent_id
    repo = spec.get("cursor_workspace_hint") or label
    path = private_root / "DOC_TAG_STANDARD.md"
    path.write_text(doc_tag_standard_md(agent_id, label, repo, private_root), encoding="utf-8")


def ensure_all_doc_tag_standards(workspaces_root: Path) -> dict:
    done = []
    for spec in AGENT_WORKSPACES:
        root = workspaces_root / spec["id"]
        root.mkdir(parents=True, exist_ok=True)
        ensure_agent_doc_tag_standard(spec["id"], root)
        done.append(spec["id"])
    return {"ok": True, "agents": done}
