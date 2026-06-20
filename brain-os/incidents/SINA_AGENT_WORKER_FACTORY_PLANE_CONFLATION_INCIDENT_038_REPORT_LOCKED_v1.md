# INCIDENT-038 — Mac control vs cloud factory (report pointer)

**Saved:** 2026-06-20T18:05:00Z · **Version:** 1.1 · **Status:** REMEDIATED (ASF v2 law)  
**Severity:** High · **Class:** execution-plane vocabulary

## One line

Agent first skipped Mac control law for secondary plans, then **over-corrected to “Worker on Mac runs every plan”** — ASF rejected both: **Mac control only · no factory on Mac · secondary 5000 = cloud/API only · Worker does NOT run every plan.**

## Canonical body

`brain-os/incidents/SINA_AGENT_WORKER_FACTORY_PLANE_CONFLATION_INCIDENT_038_LOCKED_v1.md`

## Machine SSOT

`data/mac-worker-vs-factory-vocabulary-v1.json`

## ASF final law (one sentence)

**Mac observes and controls. Cloud/API runs all factory work. Secondary 5000 never touch Mac. “Worker on Mac runs every plan” is FORBIDDEN.**

## Forbidden phrase (instant fail)

`Worker on Mac runs every plan`

---

*Root pointer · INCIDENT-038 v1.1*
