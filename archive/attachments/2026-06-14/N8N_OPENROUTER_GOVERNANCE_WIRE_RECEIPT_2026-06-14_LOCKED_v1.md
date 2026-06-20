# n8n + OpenRouter governance wire receipt (LOCKED v1)

**Saved:** 2026-06-14T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Authority:** ASF order · Q-GOV-FAST-WIRE-v1 A  
**Machine receipt:** `~/.sina/governance-n8n-openrouter-wire-v1.json`  
**Validator:** `scripts/validate-governance-n8n-wire-v1.sh` — **PASS**

---

## Wired workflows (disk → import into n8n UI)

| ID | Schedule | CLI glue |
|----|----------|----------|
| **wf-governance-fast-15m** | every 15m | `governance_center_run_v1.py --tier fast` + `brain_governance_wire_v1.py` |
| **wf-judge-audit-batch** | daily 6am | `judge_center_run_v1.py --write-form` + governance full |
| **wf-thread-scout-weekly** | Mon 7am | `thread_room_run_v1.py` — **H2 second hop** |
| **wf-openrouter-governance-hook** | post-governance webhook | `governance_n8n_openrouter_wire_v1.py --openrouter-hook` |

**Stub paths:** `~/Desktop/SourceA/n8n/workflows/*.stub.json`

---

## OpenRouter lane

| Signal | Value |
|--------|-------|
| Wired | **yes** |
| Gate | **shadow** (honest) |
| Live eval | **blocked** until `~/.sina/openrouter-credits-ok.flag` |
| Queue law | `SOURCEA_OPENROUTER_ACTIVATION_QUEUE_LOCKED_v1.md` · head **sa-0101** |
| Rule | EXTERNAL_CRITIC class only · never law · never auto-send |

---

## Runtime proof (this session)

| Check | Result |
|-------|--------|
| n8n running | **true** (:5678) |
| Governance fast center | **PASS** |
| Brain governance wire | **PASS** |
| Validator bundle | **PASS** |

---

## One-tap re-wire

```bash
python3 ~/Desktop/SourceA/scripts/governance_n8n_openrouter_wire_v1.py --json
```

*End N8N_OPENROUTER_GOVERNANCE_WIRE_RECEIPT_2026-06-14_LOCKED_v1*
