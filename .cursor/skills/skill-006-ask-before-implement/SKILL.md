---
name: skill-006-ask-before-implement
description: Founder law — always ask next move, clarification, and suggested options before any disk edit. All SourceA ecosystem agents.
disable-model-invocation: true
---

# SKILL-006 — Ask before implement (ecosystem)

**When:** Every session — before first disk mutation and at session end.

**Authority:** INCIDENT-010 · INCIDENT-011 · `001-founder-verbs-rewrite-save-asf-mandatory.mdc` · Noetfield R-007/R-008 (ported)

**On rule conflict:** Run [skill-007-ecosystem-conflict-resolution](../skill-007-ecosystem-conflict-resolution/SKILL.md) first.

---

## Before any disk edit

1. State what you understood from the founder message.
2. List **suggested** next moves (options A/B/C).
3. If founder gave pathless `SAVE` / `SAVE AND LOCK` / `LOCK` / `FILE` / filing `ASF:` intent, run:
   `python3 scripts/agent_filing_registry_gate_v1.py resolve --agent <id> --intent "<founder message>" --json`.
   If `ok:true`, use `route_id`, `path`, and `next_steps[]`; do not ask ASF for an exact path.
4. **ASK** founder only when no registry route exists, routes are ambiguous, or a non-filing task still lacks scope.
5. Wait for explicit order: `SAVE TO:`, registry-resolved filing intent, `EDIT ALLOWED:` + `ACTION:`, `ASF:`, or bounded `WORK:` / `sa-*`.
6. Only then: edit, commit, push (if authorized).

## Default mode

**Advise-only** — no writes until founder orders with intent + evidence in the **same message** (see `001-founder-verbs`).

## Ecosystem exceptions (still bounded)

| Trigger | Meaning |
|---------|---------|
| `SAVE TO:` / `SAVE AS:` + path | **One new file** at that path only → STOP |
| Pathless `SAVE` / `SAVE AND LOCK` / `LOCK` / `FILE` | Run filing registry; use resolved path and next steps; ask category/scope only if unresolved |
| `EDIT ALLOWED:` + path + `ACTION:` | Named path/action only |
| `ASF:` + explicit phrase | Only what the phrase authorizes |
| `WORK:` + `sa-*` or INBOX scope | Worker/Product bound build — normal speed in scope |
| `yes` / option letter after ASK | Only the option founder just approved |

## Session end (mandatory)

1. Summary: done / open / blocked.
2. Open P0/P1 incidents if relevant.
3. **ASK:** "What is your next move?"

## Fail response

```
I will not edit disk yet.
Suggested options: [A] [B] [C]
Which should I do, or clarify scope?
```

---

**END**
