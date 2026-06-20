# Sina Thread Room — Draft v1 (awaiting Form PICK)

**Saved:** 2026-06-12T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**trace_id:** `THREAD-ROOM-DRAFT-2026-06-12`  
**Parent blueprint:** `SINA_ROOMS_UNIFIED_BLUEPRINT_DRAFT_v1.md` §6  
**Form fork:** `Q-THREAD-ROOM-v1`  
**Status:** DRAFT — not law until PICK

---

## 0. One sentence

> **Scout chats → map THREAD-* arcs → curate organize plan onto Form §THREAD rows — nothing lost (T30), no RIGHT/STALE alarms (Judge Center job).**

---

## Inner pipeline

| Layer | Role | Output |
|-------|-----|--------|
| **L1 Scout** | Extract · candidate threads · mega anchors | `scout_packet.json` |
| **L2 Cartographer** | T30/T20/T10 · clocks · gaps · CONTINUITY outline | `thread_map.json` |
| **L3 Curator** | MERGE/SPLIT/DEFER plan · Form §THREAD draft | `curator_plan.json` |

## Founding law IDs

`THREAD_ACTIVATION` · `THREAD-CHAT-CONSOLIDATION` · `ASF_PROGRAM_THREADS` · `CANVAS_PER_CHAT` · `LOST_LINK_ETHICS` · `ECOSYSTEM_MASTER_CATALOG`

## Scripts (proposed v1.0)

```bash
python3 scripts/thread_room_scout_v1.py --chats a53f3fa1,3369d11c,74f5ccab --json
python3 scripts/thread_room_cartographer_v1.py --packet ~/.sina/thread-room/latest-scout.json
python3 scripts/thread_room_curator_v1.py --map ~/.sina/thread-room/latest-map.json --write-form
```

## Registry

`~/.sina/thread-room/threads.jsonl` · SSOT mirror `~/.sina/brain/thread_activation_registry_v1.yaml`

---

**END DRAFT**
