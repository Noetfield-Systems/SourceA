# Pre-LLM pipeline and WTM A1–D16 evidence

**Saved:** 2026-06-06T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit @ 2026-06-16T05:49:57Z  
**Path:** `scripts/pre_llm/` + WTM module validators  

---

## Pre-LLM role

Compiles governed context **before** any LLM call: retrieval, packing, policy attachment, hub-visible synthesis inputs. This is the core “compiler” identity of SourceA — not the chat UI.

---

## Capability scores (Section 3 style)

| Capability | Score | Evidence |
|------------|-------|----------|
| Context retrieval | 65% | pre_llm modules + validators present |
| Policy attachment | 70% | LOCKED index + brain rules |
| Packing / token budget | 55% | partial WTM D-steps |
| Embeddings | 40% | D5 PARTIAL hash_local |
| Dispatch integration | 35% | C7 shadow dry_run |
| Live eval loop | 15% | 402 block |
| Hub visibility | 60% | synthesis hub; queue tab missing |

**Blended pre-LLM maturity:** ~52% module presence, ~35% live path.

---

## WTM A1–D16 summary table

| Step | Name (abbrev) | Status | Notes |
|------|---------------|--------|-------|
| A1 | Spine bootstrap | DONE | SourceA layout |
| A2 | Validator fabric | DONE | 67 validate scripts |
| A3 | PRIORITY chain | DONE | Machine truth |
| A4 | REGISTRY pack | DONE | 1000 validated |
| A5 | Brain rules index | DONE | LOCKED v1 |
| A6 | Hub server | DONE | :13020 |
| A7 | Control panel | DONE | Beta− UX |
| B1 | Plan pick | DONE | plan-no-asf-run.sh |
| B2 | Worker closeout | DONE | evidence rows |
| B3 | do_not_redo | DONE | through sa-0201 |
| C1 | SinaPromptOS bridge | DONE | templates |
| C2 | prompt_router | DONE | shipped |
| C3 | Template library | DONE | prompt_library.py |
| C4 | Dispatch policy | DONE | errata doc |
| C5 | Agent registry | DONE | 8 private agents |
| C6 | execution_kernel_v0 | DONE | state file |
| C7 | Live dispatch | SHADOW | dispatch_ready=false |
| D1 | Pre-LLM ingest | DONE | modules |
| D2 | Context pack | DONE | |
| D3 | Synthesis hub | DONE | honest gates M2 |
| D4 | Eval scaffold | DONE | 7/7 |
| D5 | Embeddings | PARTIAL | hash_local |
| D6 | Memory ~/.sina | DONE | 414+ files |
| D7 | Brain pack sync | DONE | 6 files |
| D8 | Founder no-terminal | DONE | T0+T1 |
| D9 | Hooks M4 | PARTIAL | warn only |
| D10 | Fleet in FCB | DONE | sa-0107 |
| D11 | Autonomy APIs | DONE | post-restart |
| D12 | Kernel v1 wrapper | BUG | --json |
| D13 | sa-queue UI | NOT DONE | P1 |
| D14 | Eval-1b live | BLOCKED | 402 |
| D15 | Level 3 zero-human | NOT DONE | |
| D16 | Commercial gates | PARTIAL | honest off |

**~30 steps DONE** at module+validator level; live dispatch and L3 not shipped.

---

## D5 embeddings detail

- **Implementation:** hash_local path — not production embedding service  
- **Impact:** Retrieval quality capped vs cloud embeddings  
- **Priority:** P2 unless Eval-1b live unblocked first

---

## C7 dispatch shadow mode

```yaml
dispatch_ready: false
dry_run: true
eval_1b_gate_ok: false
```

Honest by design until OpenRouter credits and live eval PASS.

---

## Integration diagram

```
REGISTRY pick → worker sa-XXXX
       ↓
pre_llm compile → context pack
       ↓
prompt_router (L1) or template (SinaPromptOS)
       ↓
LLM call (when gates allow)
       ↓
closeout → PRIORITY evidence + REGISTRY update
```

---

## Related files

- `scripts/pre_llm/`  
- `scripts/prompt_router.py`  
- `scripts/strategic_synthesis_hub.py`  
- `os/plan-library/SOURCEA-PRIORITY.md`  
