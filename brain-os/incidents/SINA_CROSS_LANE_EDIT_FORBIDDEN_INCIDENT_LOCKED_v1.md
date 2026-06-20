# Cross-lane edit forbidden — HIGHEST governance red flag (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-09  
**sequence_id:** SA-2026-06-09-INCIDENT-CIR-COSPRO  
**Severity:** **P0 — infrastructure governance** (highest red flag)  
**Trigger incident:** `CIR-COSPRO-RESEARCH-SAVE-2026-06-07` — Research Lane B edited product SSOT after founder said **“save your research report”** only.

---

## One sentence (memorize)

> **SAVE = put one physical file in docs for future reference — untouched, stable, nothing else. WORK = your assigned job only. Anything else needs ASK first or EDIT ALLOWED.**

---

## Three verbs only (no friction for Worker)

| Verb | Who | Meaning | Friction |
|------|-----|---------|----------|
| **SAVE** | Research · advise · report chats | Write **one named file** to vault/docs. **Do not** edit, wire, register, or “improve” anything else. File stays stable as reference. | Low — path must be named |
| **WORK** | SourceA Worker · Product build | Execute bound INBOX / assigned `sa-*` / `npm run check` scope. **No extra ASK** inside scope. | **None** — normal speed |
| **EDIT ALLOWED** | Any chat | Cross-lane or SSOT change. Founder names path + action in same message. | Only when crossing desks |

**SAVE does not mean:** update AGENTS · SSOT · roadmap · README governance · registry · sync · other agents’ files · “helpful wiring”.

**SAVE does mean:** `docs/research/my_report.yaml` → write file → **STOP**.

---

## When to ASK (advise / research / unclear scope only)

| Situation | Worker | Research / advise |
|-----------|--------|-------------------|
| Bound INBOX / assigned `sa-*` | **Execute** — no ask | N/A |
| Founder says **save** with path | N/A | Write that file only |
| Founder says **save** without path | N/A | **ASK:** which file path? |
| Cross-lane or SSOT path | Refuse unless `EDIT ALLOWED` | Refuse unless `EDIT ALLOWED` |
| `execution_authority: false` | N/A | Never SSOT / Brain / product law |

---

## EDIT ALLOWED (cross-desk only)

```text
EDIT ALLOWED: <full path>
ACTION: <what to change>
```

---

## Lane ownership (who owns what)

| Owner | Canonical paths (others must not edit) |
|-------|----------------------------------------|
| **SourceA Brain** | `brain-os/**`, `ACTIVE_NOW.md`, `ARCHITECT_REPORT.yaml`, assignment/routing law |
| **SourceA Worker** | `prompts/**`, `receipts/**`, implementation under assigned `sa-*` scope only |
| **Cursor OS Pro Product chat** | `AGENTS.md`, `docs/SINGLE-SOURCE-OF-TRUTH.md`, `docs/VOICE_AGENT_ROADMAP_LOCKED_v1.md`, `packages/**`, `apps/**` |
| **Cursor OS Pro Research B** | `docs/research/**`, `scripts/investor-data-200.json`, research generators only |
| **Research Acquisitor** | `RESEARCH/by_date/**` mirrors via enforcer — not product SSOT |

**Shared read:** any lane may **read** another lane’s docs. **Write = owner only** unless `EDIT ALLOWED` above.

---

## Mechanical enforcement

```bash
python3 scripts/cross_lane_edit_guard_v1.py check \
  --agent <agent_id> --path "<target>" [--explicit-order "<founder text>"]
bash scripts/validate-cross-lane-edit-v1.sh
```

**Cursor rules (always-on):** `.cursor/rules/000-cross-lane-edit-forbidden.mdc` in SourceA and Cursor OS Pro.

**Entry gate:** `cursor_entry_gate.py` hashes this file for Brain + Worker roles.

---

## Agent refusal block (paste when blocked)

```yaml
status: CROSS_LANE_EDIT_REFUSED
incident_law: SINA_CROSS_LANE_EDIT_FORBIDDEN_INCIDENT_LOCKED_v1.md
reason: path owned by another lane/agent — founder must issue EDIT ALLOWED + ACTION
execution_authority: false
```

---

## Recurrence

Any repeat → **STOP all autoloop** · founder incident review · agent chat probation until guard PASS logged.

*End LOCKED incident law*
