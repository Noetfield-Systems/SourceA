# Governance Self-Heal — G7 unified daemon (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**sequence_id:** SA-2026-06-11-GOV-G7  
**Authority:** ASF · unifies **S10 eternal loop** + **conscious-recovery** + **G3/G4** runtime heal  
**Parent:** `GOVERNANCE_RUNTIME_GOLDEN_RULE_LOCKED_v1.md` · `SOURCEA_S10_ETERNAL_SELF_HEAL_AUDIT_LOCKED_v1.md`  
**Machine:** `scripts/governance_self_heal_daemon_v1.py`

---

## One sentence

> **G7 is the governance-runtime self-heal contract** — scan drift · stale projections · graph orphans · queue backlog → remediate via G3 drain · G4 replay hook · monitor sync · S10 delegate.

---

## Unified stack (do not duplicate)

| Layer | Role | Machine |
|-------|------|---------|
| **G7 daemon** | Governance scan + light heal each cycle | `governance_self_heal_daemon_v1.py` |
| **S10** | Deep 100-prompt eternal audit (daily pack) | `s10_eternal_audit_loop_v1.py` |
| **Conscious recovery** | Lost-link · FOUND · transcript search | `@sina-conscious-recovery` skill |
| **G3** | Stale projection → selective materialize | `governance_projection_g3_v1.py --drain` |
| **G4** | Crash → context replay | `governance_replay_worker_v1.py` |

**G7 does not replace S10** — it delegates deep audit to S10 and runs **fast governance heals** every scan.

---

## Scan categories

1. **Graph** — reference graph missing / stale / low node count  
2. **Projection** — canonical hub age · expired gate · pending G3 queue  
3. **Monitor** — `monitor-live-v1.json` stale  
4. **Spine** — ledger exists · recent recovery row  
5. **S10** — daily receipt age (WARN only — kick `s10_eternal_audit_loop_v1.py --daily` on heal)  
6. **Queue truth** — inbox vs disk truth mismatch (WARN)

---

## Schedule (machine)

| Trigger | Cadence | Action |
|---------|---------|--------|
| **Monitor sync** | ≥30 min when WARN/FAIL | `maybe_run_heal_from_monitor()` in `monitor_live_sync_v1.py` |
| **launchd** | Every 3600s | `com.sourcea.g7-governance-self-heal` → `--heal` |
| **S10** | Daily UTC | Deep audit (delegate — not replaced) |

**Install hourly launchd:**

```bash
bash scripts/install-g7-self-heal-launchd.sh
```

**Logs:** `~/.sina/g7-governance-self-heal.log` · monitor field `g7_self_heal` on `monitor-live-v1.json`

---

## Commands

```bash
# Scan only
python3 scripts/governance_self_heal_daemon_v1.py --scan --json

# Scan + light heal
python3 scripts/governance_self_heal_daemon_v1.py --heal --json

# Validator
bash scripts/validate-governance-self-heal-g7-v1.sh
```

**Receipt:** `~/.sina/governance-self-heal-receipt-v1.json`  
**Monitor state:** `~/.sina/governance-self-heal-monitor-v1.json`

---

*End G7 law*
