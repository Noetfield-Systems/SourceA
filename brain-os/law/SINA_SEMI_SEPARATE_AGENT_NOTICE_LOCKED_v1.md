# Semi-separate Cursor lanes — agent notice (locked)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Last updated:** 2026-06-04 · **Status:** LOCKED  
**Audience:** Chats that are **not** the five portfolio delivery lanes — but still on the same Mac / same founder OS.

---

## What “semi-separate” means

| In mainstream (five repos) | Semi-separate |
|----------------------------|---------------|
| TrustField · Mono · VIRLUX · Noetfield **local** · 777 | **Wire** · **Cursor OS Pro** · **Noetfield cloud** · MergePack · Prompt OS |
| `THREAD-PORTFOLIO` / `THREAD-SUPERBRAIN` | `THREAD-WIRE` · `THREAD-CURSOR-OS-PRO` · `THREAD-MERGEPACK` · `THREAD-PROMPTOS` |
| Full repo notice + portfolio Track | **SEMI_NOTICE_*.md** — slimmer, boundary-first |

**You still must know:** system update, Essentials map, no auto-paste into Cursor, no founder Terminal, one THREAD per reply, VERIFY at end.

**You do not:** pull five-repo `os/plan.json` tasks into a wire or App Store chat, or edit SourceA unless HQ maintainer.

---

## Lanes and notice files

| Lane | Cursor workspace | Notice file |
|------|------------------|-------------|
| **AI Dev Bridge (wire)** | `AI Dev Bridge OS` | `founder/repo-agent-notices/SEMI_NOTICE_wire_v1.md` |
| **Cursor OS Pro (App Store)** | `Cursor OS Pro` | `founder/repo-agent-notices/SEMI_NOTICE_cursor_os_pro_v1.md` |
| **MergePack** | `mergepack` | `founder/repo-agent-notices/SEMI_NOTICE_mergepack_v1.md` |
| **Prompt OS** | `SinaPromptOS` | `founder/repo-agent-notices/SEMI_NOTICE_promptos_v1.md` |
| **Noetfield cloud (older ship repo)** | `Noetfield` | `founder/repo-agent-notices/SEMI_NOTICE_noetfield_cloud_v1.md` |

**Noetfield split:** `Noetfield-All-Documents` = **local** docs (mainstream `REPO_NOTICE_noetfield`). `~/Desktop/Noetfield` = **cloud** ship (this table).

**Wire is not forgotten.** It is first-class under `ROLE-WIRE` in hierarchy — separate from purple App Store SKU and from portfolio IMPLEMENT chats.

---

## Must read (all semi-separate chats)

1. [SINA_COMMAND_SYSTEM_UPDATE_NOTICE_LOCKED_v1.md](SINA_COMMAND_SYSTEM_UPDATE_NOTICE_LOCKED_v1.md) — hub upgrade (Essentials, Personal DB, Live agents)
2. **This file** — boundaries
3. **Your lane’s** `SEMI_NOTICE_<lane>_v1.md` — paste at chat start

Hub: http://127.0.0.1:13020/?tab=essentials · Wire progress action: **Open wire progress doc**

---

## Cross-lane boundaries (do not mix)

```text
Cursor OS Pro     →  App Store / reference parity  (mobile/, distribution/)
AI Dev Bridge     →  orchestrator wire G1–G3       (agent/, desk, RUN SYSTEM)
Five portfolio    →  trustfield · mono · virlux · noetfield **local** · seven77
Noetfield cloud   →  Desktop/Noetfield GitHub ship (:13080, TLE, console)
MergePack         →  revenue / evidence factory    (≠ M8 wire automation)
Prompt OS         →  dispatch + paste files        (≠ implement product code here)
```

**Wrong chat = wrong thread.** Say which chat the founder should open — do not “help” by editing the other repo.

---

## Rebuild

```bash
cd ~/Desktop/SourceA && python3 scripts/build_repo_agent_notices.py
```

Full link index: `founder/repo-agent-notices/AGENT_READ_LINKS_INDEX.md`
