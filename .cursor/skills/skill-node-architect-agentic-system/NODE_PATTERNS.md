# SourceA — Node Patterns

Copy-paste patterns for adding nodes. **Always** update graph + directory map + mesh catalog in same session.

---

## Pattern A — Live wire node (T1 Truth)

**When:** Session-tier sync that writes receipt + updates live surfaces.

1. Create `scripts/my_live_wire_v1.py` with `--json` and receipt writer  
2. Add graph node in `T1_truth_parallel` with `parallel: true`  
3. Add `edges_in` wire from `disk_live_wire` · `edges_out` gate to downstream  
4. Register in directory map under `scripts/`  
5. Add mesh catalog `active_nodes` row  
6. Add `validate-my-live-wire-v1.sh` or W10 bundle row  

```json
{
  "id": "my_live_wire",
  "label": "My live wire",
  "cmd": ["python3", "scripts/my_live_wire_v1.py", "--json"],
  "receipt": "~/.sina/my-live-wire-receipt-v1.json",
  "required": true,
  "plane": "INTERNAL",
  "edges_in": [{"from": "disk_live_wire", "kind": "wire", "parallel": true}],
  "edges_out": [{"to": "agentic_layer_fast", "kind": "gate"}]
}
```

**Verify:** G1 graph validate · G2 tier run · CART TASK node-mesh

---

## Pattern B — Validator node (T3 Proof)

**When:** Standalone or W10 `validate-*` script.

- `required: false` unless ship-blocking  
- `skip_if: hub_down` when hub-dependent  
- `edges_in` orchestrate from runner or upstream proof node  

---

## Pattern C — Hub surface node (HUB_API)

**When:** H1/H2 projection or heal.

- Plane `HUB_API`  
- `skip_if: hub_down` for heal validators  
- `edges_out` surface to `hub_projection_v1`  

---

## Pattern D — n8n glue node (RUNTIME_GLUE)

**When:** External cron/webhook only.

- Plane `RUNTIME_GLUE`  
- Manifest row in `scripts/fixtures/n8n/workflow_manifest.json`  
- **Never** law/brain/INBOX SSOT  

```json
{
  "id": "n8n_my_glue",
  "plane": "RUNTIME_GLUE",
  "edges_in": [{"from": "external_cron", "kind": "glue"}],
  "edges_out": [{"to": "n8n_glue_runner_v1", "kind": "glue"}]
}
```

---

## Pattern E — Portfolio node (L3)

**When:** TrustField · Noetfield · YA5 read-only probe.

- Plane `PORTFOLIO`  
- Build N10 · no cross-repo writes from SourceA Worker  
- Receipt in portfolio repo or ~/.sina portfolio slice  

---

## Anti-patterns (refuse)

- Orphan script without graph row  
- Second orchestrator outside runner + session gate  
- Pipeline doc without node cluster ids  
- Chat done without validator + cart receipt  

---

**END NODE_PATTERNS**
