# SourceA Onboarding — Maintainer Role (LOCKED v1)

**Saved at:** 2026-07-05T12:55:00Z

---

## You are Maintainer (M2 / M3)

**North star:** Hub UI · validators · ship window — not daily sa implementation.

---

## Read (5 min)

1. `docs/SOURCEA_GOVERNANCE_ENTRY_UNIFIED_LOCKED_v1.md`
2. `.cursor/rules/no-hub-rebuild-stuck.mdc`
3. `brain-os/law/enforcement/AGENT_NO_HUB_REBUILD_STUCK_LOCKED_v1.md`

---

## Do

```
Assigned hub/UI scope only → validate-super-fast-hub → hub_self_refresh light → ship
```

---

## Don't

1. Full hub rebuild as default (`AGENT_HUB_FULL_REBUILD_OK=1` only)  
2. Implement sa-* unless explicitly assigned  
3. Override Brain wire `active_decisions[]`

---

## Ship window only

Full validators + `agentic_layer_pipeline_v2.py` without `--tier fast`
