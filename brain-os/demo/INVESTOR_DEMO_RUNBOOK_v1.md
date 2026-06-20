# INVESTOR_DEMO_RUNBOOK_v1 — Copilot BLOCK / ALLOW / TAMPER

**Sprint:** `DEMO-ENF-COPILOT-2026-06-11`  
**Law:** `brain-os/law/enforcement/ENFORCEMENT_6MO_INVESTOR_WIN_LOCKED_v1.md`  
**Speaker notes:** `investor/ENFORCEMENT_DEMO_5MIN.md`  
**Founder:** one-tap via Hub Action when Maintainer wires · until then executor runs script

---

## Pre-flight (2 min)

```bash
cd ~/Desktop/SourceA
bash scripts/validate-demo-enforcement-v1.sh
bash scripts/validate-universe-invariants-v1.sh
```

Both must print `OK:`.

---

## Live run (founder-visible)

```bash
bash scripts/demo-enforcement-5min-v1.sh
```

Pauses are built in for narration. Record screen + terminal.

---

## Manual beats (if script unavailable)

### 1. BLOCK

```bash
python3 scripts/sourcea_execute_v1.py --demo-enforcement --case block
echo "exit=$?"
```

Must be non-zero.

### 2. ALLOW

```bash
python3 scripts/sourcea_execute_v1.py --demo-enforcement --case allow
echo "exit=$?"
```

Must be zero. Receipt at `~/.sina/demo-enforcement/receipts/latest-demo-receipt.json`.

### 3. TAMPER

```bash
bash scripts/validate-demo-enforcement-v1.sh --tamper-test
```

Must detect tamper and restore receipt.

### 4. Full green

```bash
bash scripts/validate-demo-enforcement-v1.sh
```

---

## Dry-run (no spine write)

```bash
python3 scripts/commit_intent_v1.py --demo-enforcement --case allow --dry-run --json
```

---

## Post-demo checklist

| # | Item | PASS |
|---|------|------|
| 1 | BLOCK exited non-zero | ☐ |
| 2 | ALLOW receipt has `spine_event_id` + checksum | ☐ |
| 3 | Tamper test FAILED checksum | ☐ |
| 4 | Recording saved (2 takes max) | ☐ |
| 5 | W3 follow-up scheduled | ☐ |

---

## Known bypass (honest)

Demo path is sacred; **full repo** still allows Worker ACT without gate — see `brain-os/demo/DEMO_BYPASS_AUDIT_v1.md`. Do not claim whole-OS uncheatable until commit gate v1 ships post-1.10.
