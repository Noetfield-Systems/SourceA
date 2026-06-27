# Site Intelligence Hub Locked v1

Saved: 2026-06-27T01:17:41Z

## Locked Decision

SourceA will not treat chatbot feedback as full inspection.

The product direction is a unified **Site Intelligence Hub**: human/agent feedback plus silent machine inspection, merged into one private control panel above all portfolio sites.

## Why

The founder has multiple public sites, including:

- `noetfield.com`
- `sourcea.app`
- `trustfield.ca`

Managing each site one by one hides repeated issues, silent failures, UX confusion, leaks, routing conflicts, and proof gaps. Visitor feedback is useful, but it only captures what someone notices and chooses to report. Machine inspection catches failures that never speak.

## System Shape

Every site sends two classes of signal:

1. **Human / agent feedback**
   - Chatbot conversations
   - Feedback forms
   - Visitor questions
   - Agent or human testing notes
   - UX confusion and feature requests

2. **Machine inspection**
   - Health probes
   - API failures
   - Broken links
   - Failed receipt writes
   - Database/write errors
   - Page status and runtime exceptions

Both streams enter one private layer:

```text
portfolio sites
  -> feedback + chats + telemetry + probes
  -> sanitize
  -> classify
  -> dedupe
  -> risk score
  -> Site Intelligence Hub
  -> per-site and all-sites action queue
```

## Security Rule

Anonymous site input is never allowed to directly control private systems or agents.

Visitor and external-agent messages must pass through:

```text
intake -> quarantine -> classification -> admin review -> approved action
```

## Product Contract

- One global private panel shows all sites in one picture.
- Each site has a drill-down view, but the overview remains above all sites.
- Feedback is signal, not proof.
- Machine inspection is proof when backed by receipts, telemetry, and health checks.
- Critic Observer reviews unified signals and recommends whether the next move is `TASK`, `FIX`, `CRITIC`, or `MONITOR`.
- Builder/Worker agents only act after approved, bounded tasks.

## First Implementation Scope

Implement a local/private Site Intelligence Hub in Forge Terminal:

- `site_intelligence_ingest`: record feedback, chat, probe, error, or receipt event.
- `site_intelligence_summary`: return all-sites and per-site grouped issues.
- Private UI panel: all-sites overview, repeated issues, risk buckets, and next actions.

This is the spine for later production wiring into `sourcea.app`, `noetfield.com`, and `trustfield.ca`.
