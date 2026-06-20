# INCIDENT-020 — Agent topic conflation (S10 mixed with founder bash · bad summary)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 LOCKED  
**Class:** Agent reasoning · incident taxonomy · summary hygiene  
**Reporter:** ASF correction  
**Agent:** Cursor Worker · **sequence_id:** SA-2026-06-10-INCIDENT-020  
**Opened:** 2026-06-10  
**Triggered by:** ASF — "incident 019 was separate with s10"  
**Related:** INCIDENT-019 · INCIDENT-021  
**Status:** REMEDIATED (split + pointer docs)

---

## 1. What happened

After ASF reported Terminal failure (`~ % python3 scripts/...` → ENOENT), the agent:

1. **Merged two unrelated topics** into one incident titled `S10 wrong bash`
2. **Wrote remediation prose** that was half S10 SSOT delivery, half founder communication law
3. **Updated S10 law §5** to point at INCIDENT-019 for bash — coupling systemic meta-phase to a chat-format bug
4. **Shipped a "full summary"** that treated S10 implementation status and bash cwd miss as a single story

ASF correction: **right bash is agent communication with founder**. **S10 is a total agentic systemic subject** (eternal audit engine, 100 prompts, machine loop). They must not share one incident or one summary arc.

---

## 2. Category error (bad reasoning)

| Topic | What it is | Correct home |
|-------|------------|--------------|
| **Founder bash** | How agents format shell for ASF (cwd, wrappers, no Terminal default) | `AGENT_FOUNDER_BASH_COMMUNICATION_LOCKED_v1.md` · INCIDENT-019 |
| **S10 eternal** | Meta-phase s10 — 100-prompt machine self-heal loop, packs, receipts, launchd | `SOURCEA_S10_ETERNAL_SELF_HEAL_AUDIT_LOCKED_v1.md` · `~/.sina/s10-eternal-manifest-v1.json` |

**Agent mistake:** Used S10 as the **incident title and class** because S10 was the **example command** in the failing paste.

---

## 3. Violations

| # | Policy | Violation |
|---|--------|-----------|
| V1 | One topic → one canonical LOCKED doc | Bash law stuffed into S10 law + S10-titled incident |
| V2 | Incident taxonomy | INCIDENT-019 named after subsystem not failure class |
| V3 | Summary honesty | Combined "S10 built OK" + "chat bash wrong" into one remediation narrative |
| V4 | ASF mental model | Forces founder to think S10 is broken when only chat paths were wrong |

---

## 4. Root cause

1. **Convenience collapse** — one reply, one incident, one summary for two concerns.  
2. **Recency bias** — last built thing (S10) became incident umbrella.  
3. **Missing taxonomy step** — agent did not ask: "Is this communication or subsystem?"  
4. **Miss loop shortcut** — patched in chat + S10 files before splitting topics logged.

---

## 5. Agent rule (after INCIDENT-020)

Before filing or summarizing:

```
1. Name the failure CLASS (communication · UX · queue · governance · …)
2. Name the SUBSYSTEM only if the bug is IN that subsystem's SSOT
3. Never title incident after example command's package
4. Separate summaries: "what we built" vs "how we talked to founder"
```

**Check question:** Would this incident still exist if the example had been `scripts/hub_self_refresh_v1.py`?  
If yes → communication incident. If no → subsystem incident.

---

## 6. Never forget

- **Example ≠ subject** — S10 command in paste does not make it an S10 incident.  
- **Communication bugs get communication laws** — not subsystem rewrites.  
- **Full summaries must be topic-pure** — ASF corrected this; disk must match.

**LOCKED** — canonical body · `brain-os/incidents/`
