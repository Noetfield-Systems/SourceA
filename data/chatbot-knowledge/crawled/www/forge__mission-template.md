---
updated: 2026-06-30T12:43:40Z
lane: developer
source_path: sites/SourceA-landing/green-unified/forge/mission-template.html
public: true
www_url: https://sourcea.app/sourcea/forge/mission-template
---

# Mission Template

## Page title
Mission prompt template | Prompt Forge · SourceA

## Summary
Every Forge run outputs a scoped mission your agents can execute — GOAL, DONE, VERIFY. Execution-first, with a receipt on every run.

## Mission shape agents actually run

## Output shape (every run)

## Forge this job

## Other Forge pages

SourceA is an AI execution platform powered by Forge — real builds, automations, and agent workflows, with a verifiable receipt on every run. Every job leaves a bounded mission: clear goal, done criteria, and how to verify — not open-ended chat.

GOAL: Wire sourcea.app DNS to Cloudflare Pages with clean URLs — no .html in the address bar. CONTEXT (true now — do not re-derive): - ALREADY DONE / DEPLOYED (do NOT redo): green-unified dist logged · _redirects written - Systems involved: Cloudflare Pages · sourcea.app DNS · publish script WHAT I WANT: Live site shows extensionless URLs; old .html paths 301 to clean paths. DONE = curl -I https://sourcea.app/sourcea/proof returns 200 at clean URL; .html URL 301s. VERIFY: curl -sI https://sourcea.app/sourcea/proof | head · curl -sI https://sourcea.app/sourcea/proof.html | grep -i location CONSTRAINTS: - NO rebuild from scratch if dist already correct - One job only — DNS + publish, not unrelated product work IF BLOCKED or ambiguous: STOP and tell me what's missing or which decision is mine. This is the same shape enforced by scripts/prompt_forge_pipeline_v1.py — not a marketing abstraction.

How Prompt Forge works · SSOT policy layer · Chat Unify integration · Cursor bridge · Try Prompt Forge

SourceA is an AI execution platform powered by Forge — real builds, automations, and agent workflows, with a verifiable receipt on every run.

© 2026 Noetfield Systems Inc. · SourceA is a product of Noetfield Systems Inc. · noetfield.com · Prompt Forge · sourcea.app · Technical overview · GitHub
