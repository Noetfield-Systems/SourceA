# Agent Skills & Research Pipeline (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-06-AGENT-SKILLS-RESEARCH  
**Parent:** `AGENT_ECOSYSTEM_UNIFICATION_POLICY_LOCKED_v1.md`  
**Governance:** `META_REASONING_POLICY_STACK_LOCKED_v1.md` §9 (classify → evaluate before promote)  
**Hub tab:** Agent hub (`?tab=agent-loop`) · API `GET/POST /api/agent-research`

---

## 0. One sentence

**Every agent has distinct Cursor skills; all research enters Agent Hub first, passes brainstorm + evaluation, then promotes to skill · council · order — never straight to build from raw chat.**

---

## 1. Two systems (do not merge)

| System | Location | Purpose |
|--------|----------|---------|
| **Cursor Agent Skills** | `SourceA/agent-skills/<agent-id>/SKILL.md` → `~/.cursor/skills/sina-<agent-id>/` | How each agent executes in IDE |
| **Research pipeline** | `~/.sina/agent-research/items.jsonl` + hub UI | Intake → brainstorm → evaluate → promote |

**Law:** Research from hub-edit workspace, portfolio agents, ChatGPT, or external docs is **INPUT** (L1). Promotion requires **evaluation scores** (L9) before skill or order change (L11).

---

## 2. Registered agent skills (9 agents + 2 shared)

| Agent id | Skill name | Primary job |
|----------|------------|-------------|
| **`sourcea_worker`** | **`sina-sourcea-worker`** | **Goal 1 INBOX drain — CHECK/ACT/VERIFY, broker, receipts** |
| **`sourcea_brain`** | **`sina-sourcea-brain`** | **Judge, hygiene, ASF routing, acceptance** |
| `trustfield` | `sina-trustfield` | Infra, law alignment, compliance lane |
| `virlux` | `sina-virlux` | DNS, Vercel, live site proof |
| `ai_dev_bridge_os` | `sina-ai-dev-bridge-os` | Wire G1/G2/G3 evidence |
| `noetfield_local` | `sina-noetfield-local` | Local SSOT docs — never cloud repo |
| `noetfield_cloud` | `sina-noetfield-cloud` | GitHub ship, CI, deploy |
| `seven77` | `sina-seven77` | Foundation web ops, cohort gates |
| `semej` | `sina-semej` | Browser multi-AI chain — SourceA read-only |
| **shared** | `sina-research-intake` | Submit research to Agent Hub pipeline |
| **shared** | `sina-registry-drain` | Honest receipt drain — hygiene gates |
| **shared** | `sina-agentic-commercial` | Agentic outreach + demo booking — founder never email/call |
| **shared** | `sina-conscious-recovery` | **Lost-link recovery** — transcript + disk · FOUND report · truth tree down-only |
| **shared** | `truth-projection` | Disk truth vs hub · agent truth bundle · dual-pick |
| **shared** | `anti-staleness-machine` | AS bundle after hub projection edits |
| **user** | `agent-self-audit-loop` | Session start/close ledger (`~/.cursor/skills/`) |

**SSOT:** `agent-skills/REGISTRY_LOCKED_v1.json` · sync: `scripts/sync-cursor-agent-skills.sh`  
**Mandatory:** `MANDATORY_READ_BY_ROLE_LOCKED_v1.md` v1.3 · `@sina-conscious-recovery` on Brain/Worker/governance turns

---

## 3. Research pipeline stages

```text
INTAKE      → submit title + body + source + target agent(s)
BRAINSTORM  → ≥1 perspective note (agents or governance lane)
EVALUATE    → auto scores: governance · actionability · evidence · agent_fit
PROMOTED    → skill_draft | council_topic | agent_report | deferred
ARCHIVED    → closed without promote
```

### 3.1 Intake rules

- **Source types:** `hub_research` · `agent_research` · `external_critic` · `council_insight` · `user_paste`
- External paste → classify `EXTERNAL_CRITIC` (L1) — pipeline holds, does not auto-build
- Minimum body: 40 chars

### 3.2 Brainstorm rules

- At least **one** brainstorm note before evaluate
- Notes tagged with `agent_id` + `stance` (`support` · `challenge` · `extend` · `neutral`)
- Council Room may link as related topic — not duplicate mind-share spam

### 3.3 Evaluate rubric (0–100 each)

| Dimension | What it measures |
|-----------|------------------|
| `governance_alignment` | SSOT, L0–L12, validation gates mentioned |
| `actionability` | Concrete next steps, file paths, owners |
| `evidence_quality` | Audits, validators, links, reproducible checks |
| `agent_fit` | Matches tagged agent lane + forbidden_roots |
| `composite` | Weighted average — **≥65** to recommend promote |

### 3.4 Promote targets

| Target | When | Where it lands |
|--------|------|----------------|
| `skill_draft` | Repeatable agent workflow | `agent-skills/<id>/drafts/` |
| `council_topic` | Needs multi-agent vote | Council Room `topics.jsonl` |
| `agent_report` | Hub bug or missing Action | Backlog agent-review |
| `deferred` | Good idea, wrong WTM step | Order Guardian defer note |

**Law:** Promote does **not** change `CURRENT_*_STEP` — only ASF explicit order or machine SSOT does (L3).

---

## 4. Agent mandatory behavior

1. **Before deep research** in repo chat → submit summary to Agent Hub research intake (or use `sina-research-intake` skill).
2. **Use your agent skill** — hub code edits use SinaaiDataBase workspace only (`SINA_COMMAND_EDIT_LOCK`).
3. **After brainstorm closes** → read evaluation scores in hub before implementing.
4. **Never** skip pipeline for structural changes (new steps, law edits, hub tabs).

---

## 5. Hub surfaces (LOCKED — in app)

| Surface | Path |
|---------|------|
| **Agent hub** | Research pipeline panel + skills grid |
| **Payload** | `command-data.json` → `agent_skills` · `agent_research_pipeline` |
| **API** | `GET/POST /api/agent-research` |
| **Essentials** | Agents pillar → this law |
| **Council Room** | Promoted `council_topic` items appear in topics |

---

## 6. Install Cursor skills (SinaaiDataBase workspace or founder one-tap later)

```bash
cd ~/Desktop/SourceA/scripts
./sync-cursor-agent-skills.sh
```

Copies `agent-skills/*/SKILL.md` → `~/.cursor/skills/sina-*/SKILL.md`.

---

**LOCKED** — Per-agent skills + research-before-build pipeline.
