# INCIDENT-049 report — intent copied literally into Brain identity

**Locked:** 2026-06-27T09:09:00Z  
**Canonical body:** `brain-os/incidents/SINA_AGENT_LITERAL_INTENT_COPY_BRAIN_CONFIDENCE_INCIDENT_049_LOCKED_v1.md`

## Summary

Founder said Brain should operate in a “highest confidence state.” The agent copied that phrase into Brain’s public system identity instead of translating it into architecture: retrieval, live tools, guardrails, uncertainty handling, evals, and clean public copy.

## Law

Founder language is often architecture intent, not copy. Agents must preserve intent, not paste phrases.

## Fix

Brain no longer self-identifies as “highest confidence.” The prompt now says Brain is the public guide for SourceA + Forge, and confidence is implemented as evidence-backed behavior.

## Mandatory rule

`.cursor/rules/047-agent-intent-over-literal-copy-v1.mdc`

