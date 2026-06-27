# Chat Unify founder smoke — Audit Trail / ORD (STAB-044)

**Saved at:** 2026-06-24T01:40:00Z

## Steps

1. Safari → http://127.0.0.1:13023/ → **Audit Trail** tab.
2. Paste agent output or disk claim to audit.
3. Run ORD loop — 7 steps through truth gate.
4. Sidebar shows linked Verify run when applicable (STAB-045).

## Pass

- Truth gate verdict visible (PASS or BLOCK — both honest)
- Receipt in `~/.sina/` or app export path

## Safari vs Cursor (STAB-037)

Cursor embedded browser often blocks localhost. Use **Safari** or native **Chat Unify.app** for smoke tests.
