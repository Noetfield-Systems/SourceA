# Sina Command — system update notice (all Cursor agents)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.1 · **Last updated:** 2026-06-07 · **Status:** LOCKED  
**Audience:** Every Cursor agent chat — HQ, five product repos, private agents  
**Hub:** http://127.0.0.1:13020/

---

## General notice — read first

Sina Command was upgraded in one pass. **Do not work from memory of old hub layout.** Use the live app and the per-repo notice for **this** chat only.

| What changed | Where in hub |
|--------------|----------------|
| **Essentials map** | Tab **Essentials** — one non-repetitive index of every important tab, app, doc, action |
| **Personal Database (Layer A)** | Tab **Personal DB** — P0 SSOT at `SinaaiMonoRepo/SinaaiDataBase/data/` L0–L4 |
| **Mac Health Guard** | Connected Apps → mini app — local scan only, no Apple private API |
| **Live agents** | Tab **Live agents** — stable chat; no auto-paste into Cursor coding chat |
| **Incident Room + index** | Weekly share + **Doc library** → All incidents (unified) |
| **Track / source labels** | Track cards show bowl vs manual vs workstream |
| **App quit** | Quitting **Sina Command.app** stops hub (`POST /shutdown`) — not emergency stop |

**Founder rule:** No Terminal for founder — **Actions** one-tap only. Hub/SourceA implementation → **SourceA Worker chat** only (`WORKER_ASSIGNMENT_AND_CHAT_ROUTING_LOCKED_v1.md`). **SinaaiDataBase** = archive/broker — no build assignments.

---

## Introduction — how the system works now

```text
Layer A (Personal DB)     ← wins on founder truth (mono data/L0–L4)
        ↑ read
Sina Command hub :13020     ← Essentials, Track, agents, ingestion
        ↑ aggregates
Source A + bowl + Prompt OS ← law, dispatch, five-repo paste files
        ↑
Five product repo chats     ← ONE thread + ONE lane task per chat
```

1. **Essentials** — when lost, open `?tab=essentials` (full map). Home stays short (8 quick tiles).
2. **Personal DB** — build Layer A: drop files in `imports/raw` → Personal DB → **Scan imports** → promote to L2/L3. Law: `SINA_PERSONAL_DATABASE_LAYER_A_LOCKED_v1.md`.
3. **Private agents** — sidebar **Agent hub** — one page per agent (TrustField, 777, …); 10-pack loop in app only.
4. **Live agents** — online API/coach only; **never** re-enable auto-paste into Cursor without ASF + new incident report.
5. **Mandatory reads** — same order as Essentials **Read chain** (Home card + Essentials tab).

---

## Every agent must (this week)

| # | Action |
|---|--------|
| 1 | Read **this notice** + the **repo-specific notice** pasted at top of your lane brief (Repos → Copy lane brief). |
| 2 | Open Sina Command → **Essentials** once — confirm your tab exists on the map. |
| 3 | State **one THREAD** in line 1 of every reply (`ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md`). |
| 4 | End session with **VERIFY** + YAML ingest contract if you shipped repo work (`SINAAI_AGENT_YAML_INGEST_LOCKED_v1.md`). |
| 5 | **Private agents:** post in **Incident Room** once this ISO week (UI only). |
| 6 | **Do not** edit `~/Desktop/SourceA` hub/spine unless you are **SourceA Worker** under Brain handoff (`MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md`). SinaaiDataBase archive chat does **not** implement. |

---

## Per-repo notices (paste into each chat separately)

Copy from Sina Command **Repos** tab → **Copy lane brief** (includes repo notice), or open:

| Repo | Cursor workspace | Notice file |
|------|------------------|-------------|
| TrustField | TrustField Technologies | `founder/repo-agent-notices/REPO_NOTICE_trustfield_v1.md` |
| Mono | SinaaiMonoRepo | `founder/repo-agent-notices/REPO_NOTICE_mono_v1.md` |
| VIRLUX | VIRLUX | `founder/repo-agent-notices/REPO_NOTICE_virlux_v1.md` |
| Noetfield (local) | Noetfield-All-Documents | `founder/repo-agent-notices/REPO_NOTICE_noetfield_v1.md` |
| 777 | The 777 Foundation | `founder/repo-agent-notices/REPO_NOTICE_seven77_v1.md` |
| HQ archive (no jobs) | SinaaiDataBase | `founder/repo-agent-notices/REPO_NOTICE_hq_v1.md` — broker/search only; builds → SourceA Worker |

### Semi-separate lanes (wire, App Store, utility — still read hub law)

| Lane | Workspace | Notice file |
|------|-----------|-------------|
| **AI Dev Bridge (wire)** | AI Dev Bridge OS | `founder/repo-agent-notices/SEMI_NOTICE_wire_v1.md` |
| **Cursor OS Pro** | Cursor OS Pro | `founder/repo-agent-notices/SEMI_NOTICE_cursor_os_pro_v1.md` |
| **MergePack** | mergepack | `founder/repo-agent-notices/SEMI_NOTICE_mergepack_v1.md` |
| **Prompt OS** | SinaPromptOS | `founder/repo-agent-notices/SEMI_NOTICE_promptos_v1.md` |
| **Noetfield cloud (GitHub ship)** | Noetfield | `founder/repo-agent-notices/SEMI_NOTICE_noetfield_cloud_v1.md` |

**Noetfield local** (`Noetfield-All-Documents`) stays in mainstream table above — do not open cloud repo from that chat.

Master for semi lanes: `SINA_SEMI_SEPARATE_AGENT_NOTICE_LOCKED_v1.md`

Prompt OS paste files (after rebuild): `~/Desktop/SinaPromptOS/outputs/ready_to_paste/ready_to_paste_<lane>.txt`

---

## Rebuild notices + paste files

```bash
cd ~/Desktop/SourceA && python3 scripts/build_repo_agent_notices.py
```

Then: **Actions** → Morning dispatch (optional) → each repo chat gets updated lane brief.

---

## Controlled OS

June 2026: SourceA Brain = sole execution router. Read `ECOSYSTEM_BRAIN_ROLLOUT_LOCKED_v1.md` + lane handoff. MSB is Tier 5 parallel only. Default automation priority: **FORGE + WTM + REGISTRY** (`GOAL_HIERARCHY_LOCKED_v1.md`). Old Cursor threads are not SSOT — disk + hub + handoffs carry work forward.

---

## Law cross-links

- `SINA_HUB_ESSENTIALS_LOCKED_v1.md` — map SSOT  
- `SINA_PERSONAL_DATABASE_LAYER_A_LOCKED_v1.md` — Layer A  
- `SINA_MAC_HEALTH_GUARD_LOCKED_v1.md` — Mac mini app  
- `ECOSYSTEM_INCIDENTS_INDEX_LOCKED_v1.md` — all incident surfaces  
- `AGENT_GOVERNANCE_INDEX_LOCKED_v1.md` — nine private agents + forbidden paths
