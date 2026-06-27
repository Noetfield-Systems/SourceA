# FORGE-MISSION-6000 — machine index

**Saved at:** 2026-06-25T11:00:00Z  
**Law:** `docs/FORGE_MISSION_6000_PLANS_LOCKED_v1.md`  
**Observer law:** `brain-os/law/enforcement/SOURCEA_CURSOR_OBSERVER_FORGE_MISSION_LOCKED_v1.md`  
**Master:** `FORGE_MISSION_6000_MASTER_v1.json`

| Pack | Plans | Prefix |
|------|------:|--------|
| Shared spine 1 | 1000 | `sa-score-` |
| Shared spine 2 | 1000 | `sa-score2-` |
| Forge Terminal | 1000 | `ft-score-` |
| Chat Unify | 1000 | `cu-score-` |
| **Total** | **6000** | |

**Worker:** Pre-LLM Mac RAW AI · **Cursor:** observer only

```bash
python3 scripts/pick_forge_mission_plan_v1.py --surface forge --phase NOW
bash scripts/validate-forge-mission-6000-v1.sh
```
