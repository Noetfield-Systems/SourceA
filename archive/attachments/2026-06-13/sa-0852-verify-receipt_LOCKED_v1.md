# sa-0852 VERIFY receipt

**Saved:** 2026-06-13T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Turn:** VERIFY · **Status:** **done**  
**Date:** 2026-06-13T22:20Z

## Proof

| Signal | Value |
|--------|-------|
| Shell bytes (post-heal) | **301464** (~294 KB) |
| Cap | **512000** |
| Headroom | **210536 B** |
| Validator | `validate-command-data-shell-size-v1` **PASS** |

## Shipped (ACT + VERIFY heal)

| Piece | Action |
|-------|--------|
| `validate-command-data-shell-size-v1.sh` | measure + cap gate |
| `sina_command_lib.py` | defer `agent_reviews` · `hub_essentials` · `live_products` from shell (sa-0852) |
| `heal_command_data_shell_from_disk(force=True)` | shell rewritten on disk |

## Validators

| Validator | Result |
|-----------|--------|
| validate-command-data-shell-size-v1 | PASS |
| validate-command-data-lazy-shell-v1 | PASS |
| validate-app-js-lazy-bootstrap-v1 | PASS |
| worker_verify_fast_v1 | partial — health=critical unrelated |

## Closeout

- REGISTRY `sa-0852` → **done**
- `SOURCEA-PRIORITY.md` evidence row added

*End VERIFY*
