# Agent Control Panel — local fleet monitor (LOCKED spec)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
| | |
|--|--|
| **Version** | `AGENT-CP-1.0-LOCKED` |
| **Locked** | 2026-06-04 |
| **Codename** | **ASF Agent Desk** |
| **Audience** | ASF, Architect advisor, senior implementer leads |

---

## Problem

10–100 Cursor chats across repos → no single view of:

- Which agent is active where
- Whether thread law was followed
- What shipped vs promised
- Blockers across wire / portfolio / utilities

---

## Solution (local-first)

**Mac-local control panel** — no cloud required v0.

```text
~/.cursor/projects/*/agent-transcripts/*.jsonl
        ↓ scan (every 5–15 min or on-demand)
SourceA/data/agent_fleet/AGENT_FLEET_REGISTRY.json
        ↓
SourceA/agent-control-panel/index.html  (or Next.js v1)
        ↓
ASF / Architect / lead agents read dashboard
```

---

## v0 (ship now — in repo)

| Piece | Path |
|-------|------|
| Scanner | `SourceA/scripts/scan-cursor-agent-fleet.py` |
| Registry | `SourceA/data/agent_fleet/AGENT_FLEET_REGISTRY.json` |
| Dashboard | `SourceA/agent-control-panel/index.html` (static, data inlined on scan) |
| Refresh hook | Call scanner from `update-program-progress.sh` |

### Registry schema

```json
{
  "scanned_at": "ISO8601",
  "workspaces": [
    {
      "slug": "Users-sinakazemnezhad-Desktop-mergepack",
      "display_name": "mergepack",
      "sessions": [
        {
          "transcript_id": "uuid",
          "updated_at": "ISO8601",
          "user_messages": 12,
          "size_kb": 340,
          "preview": "first user query…",
          "subagent_count": 2
        }
      ]
    }
  ],
  "summary": {
    "workspace_count": 14,
    "session_count": 48,
    "active_24h": 6
  }
}
```

---

## v1 (2–4 weeks)

| Module | Function |
|--------|----------|
| **Thread compliance** | Parse opening line vs `ASF_PROGRAM_THREADS_REGISTRY` |
| **Outcome score** | Heuristic: files touched, tests, deploy keywords |
| **VERIFY ingest** | Pull YAML blocks → `AGENT_OUTPUT_CONTRACT` table |
| **KPI bridge** | MergePack `/v1/kpi`, wire proof, `PROGRAM_PROGRESS.json` |
| **Alerts** | Stale thread >7d, mixed-thread warning, blocker B-00x |

Stack: **Next.js** in `SourceA/agent-control-panel/` or **SinaPromptOS desk** tab — ASF pick.

---

## v2 (company-scale agents)

Integrate:

- **SinaaiRuntime** agent roster (mono)
- **Noetfield** governance events (when live)
- **SinaPromptOS** orchestrator queue (`run-orchestrator-v1`)
- **DevBridge** RUN SYSTEM status

Target: **fleet graph** — who dispatched whom, serial vs parallel lanes.

```text
ASF → Orchestrator → Repo Implementer (Cursor)
                  → Architect (read-only)
                  → Wire agent (DevBridge)
```

---

## Roles on dashboard

| Badge | Source |
|-------|--------|
| IMPLEMENTER | Default Cursor repo chat |
| ARCHITECT | `run-architect.sh` output freshness |
| ORCHESTRATOR | SinaPromptOS dispatch log |
| WIRE | `AI Dev Bridge OS/config/locked_plan.json` |
| BLOCKED | Architect `system_blockers` |

---

## Privacy & security

- **Local only** — transcripts stay on Mac; registry is derived metadata
- **No** upload to Vercel/Railway
- Redact paths in previews (optional flag)
- Subagent transcripts: count only in v0 (no body in dashboard)

---

## Parallel founder workflow

| Mode | Control panel view |
|------|-------------------|
| **Serial** | One “active” session per P0 thread |
| **Parallel** | Matrix: thread × repo × last outcome |
| **Review** | Architect + fleet scan before morning dispatch |

---

## Success metrics

| Metric | Target |
|--------|--------|
| Scan freshness | <15 min when ASF working |
| Registry coverage | 100% of `~/.cursor/projects` workspaces |
| Thread violation visibility | Flag within 1 session |
| Time to answer “what did agents ship yesterday?” | <2 min |

---

## Related

| Doc | Role |
|-----|------|
| `AGENT_OPERATING_ROLES_LOCKED_v1.md` | Role definitions |
| `AGENT_SELF_AUDIT_ASF_REPORT_2026-06-04.md` | Example audit |
| `AGENT_OUTPUT_CONTRACT_v1.yaml` | Machine VERIFY |
| `ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md` | Thread law |

---

**LOCKED.**
