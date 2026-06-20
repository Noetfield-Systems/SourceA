# Repo inventory — ecosystem map

**Saved:** 2026-06-06T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit @ 2026-06-16T05:49:57Z  

---

## Primary repos

| Repo | Path | Role | Ops lane? |
|------|------|------|-----------|
| **SourceA** | `~/Desktop/SourceA` | Law, validators, hub, REGISTRY, workers | **YES** |
| **SinaPromptOS** | `~/Desktop/SinaPromptOS` | Prompt templates, dispatch-day | Bridge |
| **SinaaiDataBase** | `~/Desktop/SinaaiDataBase` | Archive chat, audits | **NO** (archive) |

---

## State directories

| Path | Role | File count (approx) |
|------|------|---------------------|
| `~/.sina/` | Closeouts, runtime, logs | 414+ |
| `~/.sina/brain/` | Brain mirror pack | 6 files |
| `~/.cursor/hooks.json` | M4 reply lint | 1 config |

---

## SourceA scale

| Asset type | Count |
|------------|-------|
| `.py` | ~358 |
| `.md` | ~1260 |
| `*_LOCKED*.md` | ~138 |
| `validate-*.sh` | ~67 |
| `scripts/` (total) | ~218 |

---

## Key entrypoints

| Entry | Path |
|-------|------|
| Machine truth | `os/plan-library/SOURCEA-PRIORITY.md` |
| Worker pick | `scripts/plan-no-asf-run.sh` |
| REGISTRY | `os/plan-library/sourcea-1000/REGISTRY.json` |
| Hub server | `scripts/sina-command-server.py` |
| Hub UI | `agent-control-panel/` |
| Brain rules | `os/chat-handoffs/BRAIN_RULES_AUTHORITY_INDEX_LOCKED_v1.md` |
| No Terminal law | `SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md` |
| Prompt router | `scripts/prompt_router.py` |
| Pre-LLM | `scripts/pre_llm/` |
| Runtime | `scripts/runtime/` |
| Agent registry | `scripts/agent_workspace_registry.py` |
| Template library | `SinaPromptOS/core/prompt_library.py` |

---

## Services and ports

| Service | Port | Status at audit |
|---------|------|-----------------|
| Sina Command Hub | 13020 | UP |
| Runtime spine | 8000 | DOWN (optional) |

---

## Missing / not found

| Item | Scan result |
|------|-------------|
| NOETFIELD_GOVERNANCE_PLANE | Path not found Desktop 2026-06-06 |
| Hub sa-queue tab | Not implemented |
| CANADA_AI in important_docs_index | Doc exists plan-library; index gap |

---

## Lane conflicts (resolved)

| Conflict | Resolution |
|----------|------------|
| SinaaiDataBase vs SourceA ops | Archive vs worker — documented |
| ASF_DAILY_CARD vs No Terminal | T0+T1 aligned |
| Three automation loops | Documented in extraction YAML |
| Dynamic router vs REGISTRY | Two-layer model — keep both |

---

## Audit export location

This inventory is part of `docs/system-audits/` — index at `README_INDEX.md`.
