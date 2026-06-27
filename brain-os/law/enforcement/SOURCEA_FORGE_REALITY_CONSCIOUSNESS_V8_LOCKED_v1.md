# SourceA Forge Reality-Coupled Consciousness v8 (LOCKED)

**Saved:** 2026-06-25T23:00:00Z  
**Version:** 8.0 — LOCKED  
**Parent:** `SOURCEA_FORGE_PLANETARY_CONSCIOUSNESS_V7_LOCKED_v1.md`

---

## One law

> **Planetary consciousness MUST couple to live disk reality — Mac control plane, founder session gate, cloud autorun receipts, and Forge motor — not simulation alone.**

---

## Core shift (v7 → v8)

| v7 | v8 |
|----|-----|
| Simulated world signals | **Live receipt ingestion** |
| Internal awareness only | **Reality health score (0–1)** |
| Self-stabilize simulation | **Recommend cloud/Mac actions from stale receipts** |
| 45/55 blend | coupledAwareness = 45% sim + 55% reality |

---

## Reality receipt bundle

| Signal | Path |
|--------|------|
| Mac control plane | `~/.sina/mac-control-plane-v1.flag` |
| Brain session | `~/.sina/brain_session_receipt_v1.json` |
| Session gate | `~/.sina/agent_session_gate_receipt_v1.json` |
| Cloud auto runtime | `~/.sina/cloud-auto-runtime-tick-receipt-v1.json` |
| Hub cloud proceed | `~/.sina/hub-cloud-forge-run-proceed-receipt-v1.json` |
| Cycle receipts | `~/.sina/autonomous-forge-run-cycle-receipts/` |
| Civilization tick | `~/.sina/forge-civilization-tick-latest-v1.json` |
| Forge runtime | `~/.sina/forge-prompt-os-runtime-latest-v3.json` |

---

## Reality health statuses

| Status | Meaning |
|--------|---------|
| healthy | Receipts present + fresh |
| stale_cloud | Cloud tick > 48h old |
| degraded | Health < 0.4 |
| mac_unarmed | Control plane flag absent |

---

## Module

| Resource | Address |
|----------|---------|
| Runtime | `scripts/forge_reality_consciousness_v8.py` |
| State | `~/.sina/forge-reality-consciousness-v8.json` |
| Receipt | `~/.sina/forge-reality-consciousness-tick-latest-v8.json` |

---

## API

```json
{ "action": "reality_consciousness_tick", "dry_run": true, "run_v7": true }
{ "action": "reality_consciousness_status" }
```

---

## Mac rule

Read-only receipt ingestion on Mac — safe founder session. Stabilization actions are recommendations unless `dry_run=false` on cloud body.

---

## Proof

```bash
python3 scripts/forge_terminal_living_ui_e2e_verify_v1.py
```
