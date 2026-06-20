# Machine three pipelines — Calibrate · Tune · machine prove (LOCKED v1)

**Version:** 1.1.0 · **Saved:** 2026-06-18T21:05:49Z-06-18T21:04:57Z · **Status:** LOCKED
**Authority:** ASF  
**Unified:** `REFINEMENT_UNIFIED_AGENT_MACHINE_LOCKED_v1.md`  
**Test ladder (Tune uses this):** `SOURCEA_MACHINE_TEST_AND_UPGRADE_LADDER_LOCKED_v1.md`  
**Registry:** `~/.sina/machine-three-pipelines-registry-v1.json`  
**Router:** `scripts/machine_three_pipelines_router_v1.py`  
**Vocabulary SSOT:** `data/machine-three-pipelines-vocabulary-v1.json` · `data/sourcea-forge-vocabulary-disambiguation-v1.json`

---

## 0. Name disambiguation (read first)

| Term | Meaning |
|------|---------|
| **machine prove** | Tier-3 pipeline — Calibrate · Tune · **Prove** upgrade gauntlet before ship |
| **Founder trigger word `forge`** | Still runs `machine_forge_pipeline_v1.py` — agents say **machine prove** in prose |
| **Forge** (capital F) | **Product only** — AI-native dev platform · `~/Desktop/forge` · THREAD-FORGE — **not** this pipeline |
| **ICP compile** | Email/output factory — FDG → loops → Sina read — **not** this pipeline |

**Law:** Filename retains `FORGE` for receipt stability. Human label for tier 3 = **machine prove**.

---

## One sentence

> **Calibrate maps the machine forest · Tune runs the cadence ladder · machine prove proves an upgrade before ship — longest, worst, passport required.**

---

## Tier model (parallel to agents)

| Tier | Trigger | Label | Length | Purpose |
|------|---------|-------|--------|---------|
| **1** | **calibrate** | Blueprint | Short | Machine catalog · test law · upgrade board · no ship |
| **2** | **tune** | Tune-up | Medium | daily/3day ladder · dual heal · baseline · shorter than machine prove |
| **3** | **forge** (founder word) | **machine prove** | Long · worst | before/after baseline · weekly+monthly ladder · 3 PROVEN lines · passport |

---

## P1 — Calibrate

**Stations:** test ladder law · machine law · unified refinement · agentic stack · two-hub · architecture · runbook · ecosystem catalog · refinement runners · reading pack.

```bash
python3 scripts/machine_three_pipelines_router_v1.py calibrate --json
```

Receipt: `~/.sina/machine-calibrate-receipt-v1.json`  
Pack: `~/.sina/machine-calibrate-reading-pack-v1.json`

---

## P2 — Tune

**Stations:** calibrate cert · test ladder (daily or 3day) · dual hub heal · baseline snapshot · critical check.

```bash
python3 scripts/machine_three_pipelines_router_v1.py tune --json
python3 scripts/machine_tune_pipeline_v1.py --ladder-tier 3day --json
```

Receipt: `~/.sina/machine-tune-receipt-v1.json`  
Escalate to **machine prove** if `critical_count > 0`.

---

## P3 — machine prove (founder trigger: `forge`)

**Phases:** baseline before · calibrate replay · ladder weekly · ladder monthly · critical zero · 3 PROVEN lines · baseline after.

```bash
python3 scripts/machine_forge_pipeline_v1.py --upgrade-id UP-02 --write-proven "PROVEN: …" --json
```

Receipt: `~/.sina/machine-forge-receipt-v1.json`  
Passport: `~/.sina/machine-forge-passport-v1.json`  
Attest: `~/.sina/machine-forge-proven-lines-v1.json`

**Not:** Forge product build · ICP compile · Controlled App Factory line.

---

## Upgrade board (H2)

Brain syncs via `machine_refinement_h2_sync_v1.py` → `maintainer_ship` bucket.

| ID | Goal | Win |
|----|------|-----|
| UP-01 | RAGAS CI vs Eval-1b | W2 |
| UP-02 | Demo film W1 | W1 |
| UP-03 | Kernel single write path | W2 |
| UP-04 | Machine test ladder | H1 |
| UP-05 | Machine refine pipelines | H1 |
| UP-06 | Agentic layer v3 | W2 |

---

## Portfolio sequence (after commercial ICP compile)

```text
SourceA → Noetfield → TrustField (ICP compile)
→ Forge product (~/Desktop/forge)
→ WitnessBC · 777 · advisor_pre_call
```

ICP compile closes before Forge product clock resumes (`data/icp-output-compiler-v1.json`).

---

*End MACHINE_THREE_PIPELINES_CALIBRATE_TUNE_FORGE_LOCKED_v1 · v1.1 vocabulary sync*
