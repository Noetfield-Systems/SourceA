# SourceA — Node Build Plan (skill copy)

**LOCKED SSOT:** `docs/SOURCEA_NODE_MESH_SYNESTM_BUILD_PLAN_LOCKED_v1.md`  
**Catalog:** `data/sourcea_node_mesh_catalog_v1.json`

---

## Agent progress tracker

```text
Synestm mesh progress:
- [x] N01 graph + runner + validator
- [x] N02 charter + skills + references
- [x] N05 edges_in/out v1.2
- [x] Directory map + mesh catalog + cart task
- [ ] N03 session gate → runner delegate
- [ ] N04 remove duplicate gate steps
- [ ] N06 event bus spine.bridge emit
- [ ] N07 Hub node canvas
- [ ] N08 Hub run-tier tap
- [ ] N11–N12 crawl/mirror subgraphs
```

## Wave 1 commands (N03 target)

```bash
# After N03 ships:
python3 scripts/agent_session_gate_run_v1.py --role worker --json
# gate receipt must show graph tier delegation — not duplicate crawl-mirror
```

## Every new node session

1. Read NODE_PATTERNS.md — pick pattern A–E  
2. Edit graph + directory map + catalog  
3. `bash scripts/validate-pipeline-node-graph-v1.sh`  
4. `CART TASK node-mesh`  

---

**END NODE_BUILD_PLAN · sync with LOCKED doc on milestone**
