# NewMatch — Phase 0 graph scaffold

**Factory:** `newmatch_router_cloud` · **Plan:** NM-001 (W1 graph SSOT)  
**Law:** `data/newmatch-factory-v1.json` · `data/newmatch-graph-schema-v1.json`

Local JSON SSOT for people graph during Phase 0 ($0). Cloud router lives at `scripts/newmatch_situation_router_t0_v1.py`.

## Layout

| Path | Purpose |
|------|---------|
| `data/graph-v1.json` | Local people graph seed (person · edge · signal · situation · follow_up) |
| `schema/graph-v1.json` | Schema mirror for app-local validation |
| `package.json` | App metadata · no paid deps |

## Commands

```bash
python3 scripts/newmatch_situation_router_t0_v1.py --demo --json
python3 scripts/newmatch_free_tier_check_v1.py --json
bash scripts/validate-newmatch-scaffold-v1.sh
```
