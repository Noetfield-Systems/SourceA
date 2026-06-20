# SourceA Next-Level Evidence Binder

**Saved:** 2026-06-16T04:33:35Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-15  
**Parent:** [`SOURCEA_HIGH_GRADE_UPGRADE_BENCHMARK_ADDENDUM_2026-06-15_v1.md`](SOURCEA_HIGH_GRADE_UPGRADE_BENCHMARK_ADDENDUM_2026-06-15_v1.md)  
**Surface:** `http://127.0.0.1:5180/sourcea/`

## Honest dual score (post next-level pass)

| Lens | Score | Notes |
|------|-------|-------|
| **Friendly UX** | **88** | Live terminal · sources page · procurement attach · K1 on hub |
| **Critic falsification** | **82** | Up from ~78; Trust still capped until named partner + live send |
| **Claimed A (90+)** | **Withheld** | AB1/NW1 `sent` requires founder Mail click — packs ready |

## Evidence index

| Plan | Proof logged | Path |
|------|---------------|------|
| 1 Live terminal | Boot inject receipt | `~/.sina/sourcea-boot-terminal-inject-v1.json` |
| 2 Sources | Cited evidence page | `/sourcea/sources.html` |
| 3 W1 film | Receipt + validator | `~/.sina/enforcement/w1-film-receipt-v1.json` · `scripts/validate-w1-film-receipt-v1.sh` |
| 4 SW1 | Eval thread + CI workflow | `~/.sina/sw1-eval-thread-receipt-v1.json` · `.github/workflows/validate-sourcea-boot-v1.yml` |
| 5 AB1 | Outbound pack + receipt | `~/.sina/outbound/ab1-send-001/` · `~/.sina/ab1-outbound-send-receipt-v1.json` |
| 6 NW1 | Outbound pack + receipt | `~/.sina/outbound/nw1-send-001/` · `~/.sina/nw1-outbound-send-receipt-v1.json` |
| 7 Named trust | Permission gate | `~/.sina/design-partner-permission-v1.json` · `scripts/apply_design_partner_trust_v1.py` |
| 8 Procurement | Printable attach | `/sourcea/attach/procurement-pack.html` |
| 9 Hub K1 | Worker hub slice | `GET /api/worker-hub/v1` → `kernel_k1` · Safety receipt |
| 10 Binder | This file | `archive/attachments/commercial/SOURCEA_NEXT_LEVEL_EVIDENCE_BINDER_2026-06-15_v1.md` |

## Dimension targets

| Dimension | Pre next-level | Post | Gate |
|-----------|----------------|------|------|
| Hero | 9 | **9** | Live boot CTA |
| Visual | 8 | **8** | Held |
| Trust | 7 | **7–8** | 8+ needs named partner permission |
| CTA | 9 | **9** | Procurement + boot paths |
| Proof | 9–10 | **10** | W1 strip + live terminal |
| IA | 9 | **9** | sources #14 · procurement attach |
| Critic overall | 78 | **82** | 85+ after ≥1 win code `sent` |

## Validation pipeline

```bash
python3 scripts/sync_sourcea_landing_pages_v1.py
python3 scripts/inject_sourcea_boot_terminal_v1.py
bash SourceA-landing/green-unified/scripts/run-recipe.sh --e2e
bash scripts/validate-sourcea-boot-v1.sh
bash scripts/validate-enforcement-kernel-v1.sh --quick
bash scripts/validate-w1-film-receipt-v1.sh
python3 scripts/worker_hub_v1.py --no-cache --json | python3 -c "import json,sys; d=json.load(sys.stdin); print('K1', (d.get('kernel_k1') or {}).get('verdict'))"
```

## Founder next taps

1. Hard refresh `http://127.0.0.1:5180/sourcea/` — terminal must match `sourcea-boot --json`
2. Worker Hub → Safety — confirm **K1 PASS/BLOCK** line
3. Mail → AB1 pack at `~/.sina/outbound/ab1-send-001/` → then `python3 scripts/mark_outbound_sent_v1.py --lane ab1`
4. When partner permits → edit `~/.sina/design-partner-permission-v1.json` → `apply_design_partner_trust_v1.py`
5. Record W1 film → drop `assets/w1-demo.mp4` → update receipt `status: filmed`

## Frozen

No SOC2 claims · no self-score 90+ without win receipt · no fake `sent` without founder Mail click.
