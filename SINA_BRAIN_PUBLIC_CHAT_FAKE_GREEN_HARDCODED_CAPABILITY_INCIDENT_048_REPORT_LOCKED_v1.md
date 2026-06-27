# INCIDENT-048 report — Brain fake-green hardcoded capability patch

**Locked:** 2026-06-27T08:58:00Z  
**Canonical body:** `brain-os/incidents/SINA_BRAIN_PUBLIC_CHAT_FAKE_GREEN_HARDCODED_CAPABILITY_INCIDENT_048_LOCKED_v1.md`

## Summary

Brain wrongly claimed it could not answer in Farsi or Spanish and could not translate. The first fix risked fake green by hardcoding the reported examples.

## Law

Brain code must implement the general capability behind examples. Do not add one branch per founder example and call it intelligence.

## Fix

Language requests now route through the normal retrieval + LLM path with a generic “answer in requested language” instruction. Farsi/Spanish are routing examples, not canned responses.

## Mandatory rule

`.cursor/rules/046-brain-code-general-capability-no-hardcode-v1.mdc`

