# Signal Factory memory_line format v1

**Schema:** `signal-factory-memory-line-v1`  
**Parent:** `data/signal-factory-v1.json` · Iteration 2 lock

## Format

```text
signal-factory-v1 | entity={entity_scope} | class={classification} | decision={decision} | id={signal_id}
```

## Example

```text
signal-factory-v1 | entity=TrustField | class=client | decision=create_service_pattern | id=550e8400-e29b-41d4-a716-446655440000
```

## Brain ingestion rules

1. One line per triage run — append-only in Brain memory, never overwrite doctrine.
2. `classification` and `decision` must match receipt JSON on same `signal_id`.
3. No sender assertions in memory_line — claims live in receipt `sender_claims[]` only.
4. Entity scope must match receipt `entity_scope` — no cross-attribution.

## Receipt linkage

| Receipt field | memory_line source |
|---------------|-------------------|
| `signal_id` | `id=` suffix |
| `entity_scope` | `entity=` |
| `classification` | `class=` |
| `decision` | `decision=` |

## Compatibility

Iteration 2 enums: `vendor | partner | client | investor | risk | bug | idea | spam | unclear` and decisions `ignore | archive | reply | route | build_automation | create_service_pattern`.
