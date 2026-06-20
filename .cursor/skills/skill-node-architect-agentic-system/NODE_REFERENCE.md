# SourceA — Node Reference (schema)

**Graph schema:** `sourcea-pipeline-node-graph-v1` · **Current version:** 1.2.0

---

## Node fields (mandatory)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | string | yes | snake_case · unique |
| `label` | string | yes | Founder-readable |
| `cmd` | string[] | yes | python3/bash vector |
| `receipt` | string | no | `~/.sina/*-receipt-v1.json` |
| `required` | bool | no | Fail tier if false and exit != 0 |
| `plane` | enum | no | INTERNAL · RUNTIME_GLUE · HUB_API · PORTFOLIO |
| `skip_if` | string | no | hub_down · panic_active |
| `edges_in` | object[] | v1.2+ | from · kind |
| `edges_out` | object[] | v1.2+ | to · kind · parallel? |
| `timeout_sec` | int | no | default 120 |

## Edge kinds

| Kind | Use |
|------|-----|
| `trigger` | Founder/session starts flow |
| `gate` | Must PASS before continue |
| `wire` | Live sync · receipt cascade |
| `fan-out` | Parallel siblings |
| `data` | SSOT artifact flows |
| `orchestrate` | Runner invokes tier |
| `surface` | Hub · Mac Health · UI |
| `glue` | n8n external only |
| `alarm` | Panic · skip nodes |

## Tier fields

| Field | Meaning |
|-------|---------|
| `id` | T0_safety · T1_truth_parallel · … |
| `parallel` | true = ThreadPool siblings |
| `budget_sec` | Tier time budget |
| `nodes` | Node array |

## Receipt schemas

| Receipt | Schema |
|---------|--------|
| Graph run | `pipeline-node-graph-receipt-v1` |
| Cart task | `cart-task-receipt-v1` |
| Session gate | `agent-session-gate-receipt-v1.1` |

## Validate

```bash
bash scripts/validate-pipeline-node-graph-v1.sh
```

---

**END NODE_REFERENCE**
