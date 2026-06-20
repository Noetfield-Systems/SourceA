# Cursor OS Pro — two chats policy (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-06  
**Repo:** `~/Desktop/Cursor OS Pro` · **Semi-separate** from SourceA core  
**Feeds:** `UNIFIED_RESEARCH_ROOT_LOCKED_v1.md` via `research_root_sync.py`

---

## 0. Two chats — never merge

| Chat | Mission | Handoff | Writes |
|------|---------|---------|--------|
| **A — Product / App Store builder** | Ship IDE For Cursor mobile · bridge · voice modal · TestFlight | `MANDATORY_CURSOR_OS_PRO_CHAT_LOCKED_v1.md` · workspace `AI Dev Bridge OS/mobile` or `Cursor OS Pro` | Code in `mobile/` only |
| **B — Research lane** | Voice AI **dev company** comparison (200 global + Canada 100) — **not** consumer App Store IAP apps | This policy + `Cursor OS Pro/docs/research/README.md` | YAML/JSON in `docs/research/` + `scripts/` |

**Law:** Research chat **does not** ship product code. Product chat **does not** own competitor matrices.

---

## 1. Research lane canonical hub (lane SSOT)

**Start here:** `~/Desktop/Cursor OS Pro/docs/research/README.md`

| Layer | Path | Role |
|-------|------|------|
| Human source YAML | `docs/research/market-brain-june-2026.yaml` | B2B voice snapshot |
| Canada peers | `docs/research/canada-voice-100.yaml` | 100 Canada companies |
| Machine 200 matrix | `scripts/investor-data-200.json` | List 1+2, tiers, refreshed 2026-06-04 |
| Canada JSON export | `scripts/canada-voice-100.json` | Canvas pipeline |
| Voice roadmap law | `docs/VOICE_AGENT_ROADMAP_LOCKED_v1.md` | Product stack — cites JSON |
| Canvases (UI) | `~/.cursor/projects/.../canvases/*.canvas.tsx` | Ephemeral — regenerate from JSON |

**Not peer comparison list:** App Store consumer IAP rankings in mixed market snapshots — use 200 JSON + Canada YAML instead.

---

## 2. Link to ecosystem unified research root

After **every** research session in Chat B:

```bash
python3 ~/Desktop/SourceA/scripts/research_root_sync.py register \
  --path ~/Desktop/Cursor\ OS\ Pro/docs/research/canada-voice-100.yaml \
  --producer cursor_os_pro --lane cursor_os_pro --bucket voice_agent \
  --cores research,commercial

python3 ~/Desktop/SourceA/scripts/research_root_sync.py register \
  --path ~/Desktop/Cursor\ OS\ Pro/scripts/investor-data-200.json \
  --producer cursor_os_pro --bucket competitor --cores research

python3 ~/Desktop/SourceA/scripts/research_root_sync.py sync
```

**Ecosystem reads:** `~/.sina/research-root/filtered/` — not full 200 JSON in Execution Core.

---

## 3. Who consumes lane research

| Consumer | Reads | Does not read |
|----------|-------|---------------|
| Research Acquisitor (SourceA) | Lane YAML + JSON summary in briefs | Rebuild 200 matrix |
| Commercial Goal Specialist | Filtered commercial signals | Raw JSON |
| Product Chat A | `VOICE_AGENT_ROADMAP` + tier picks from JSON | Canada 100 narrative in chat |
| Execution Core | `execution_core.digest.yaml` | Canvases |

---

## 4. Regenerate pipeline (research chat only)

```bash
cd ~/Desktop/Cursor\ OS\ Pro
node scripts/generate-investor-200.js
node scripts/generate-canada-voice-100-json.js
node scripts/refresh-investor-canvas.js
npm run check
research_root_sync.py sync   # from SourceA scripts path
```

---

## 5. Short prompt — Research Chat B

```text
CURSOR OS PRO — RESEARCH LANE ONLY. No mobile/ code changes.

Read: docs/research/README.md
Peer data: scripts/investor-data-200.json + docs/research/canada-voice-100.yaml
Ignore: App Store consumer IAP peer lists.

After work: research_root_sync.py register + sync (UNIFIED_RESEARCH_ROOT law).
No sa-XXXX. No SourceA spine edits.
```

---

## 6. Short prompt — Product Chat A

```text
CURSOR OS PRO — PRODUCT LANE. Ship mobile IDE + voice modal per VOICE_AGENT_ROADMAP.

Read: docs/SINGLE-SOURCE-OF-TRUTH.md · docs/VOICE_AGENT_ROADMAP_LOCKED_v1.md
Competitor tiers: scripts/investor-data-200.json (read-only reference)

Do not expand 200 matrix here — use Research Chat B.
```

---

*End two-chat policy v1*
