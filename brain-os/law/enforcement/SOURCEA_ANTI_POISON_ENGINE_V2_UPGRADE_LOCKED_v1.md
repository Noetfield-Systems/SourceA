# SourceA — Anti-Poison Engine v2 upgrade (LOCKED)

**Saved:** 2026-06-26 · **UTC:** 2026-06-26T06:50:00Z  
**Authority:** ASF order — anti-poison deep analysis + `ASF: ANTI-POISON-v2 — projection sanitize`  
**Parent:** `SINA_POISON_TRACKING_METHOD_LOCKED_v1.md` · `SOURCEA_POISON_AND_REALTIME_BLOCKER_TERMINOLOGY_LOCKED_v1.md`  
**Pair:** `data/agent-law-poison-registry-v1.json` v2.0.0 · `data/agent-memory-mirror-poison-law-v1.json` v2.2.0  
**Incidents:** INCIDENT-034 · INCIDENT-039 · INCIDENT-040 · INCIDENT-041 · INCIDENT-042 · INCIDENT-043

---

## 1. One sentence

> **Anti-Poison Engine v2 = registry-driven T0 Safety node — detect law poison (P1–P18) and projection poison (PP01–PP08) separately, sanitize hub JSON on ship window, never validator-marathon on Mac founder session.**

---

## 2. Two words (do not merge)

| Term | What | Machine |
|------|------|---------|
| **Poison** | Law/mirror text that **orders** harmful agent conduct (validator marathons, check cart before reply) | `anti_poison_engine_v2.py --tier fast` |
| **Realtime blocker** | Stale hub projection vs live surfaces (wrong URL, empty `factory_now_line`, trashed `:13020`) | `projection_poison_sanitize_v1.py` · `disk_live_wire_sync_v1.py` |

Law: `SOURCEA_POISON_AND_REALTIME_BLOCKER_TERMINOLOGY_LOCKED_v1.md`

---

## 3. Machine stack (v2)

| Layer | Path | Job |
|-------|------|-----|
| Registry SSOT | `data/agent-law-poison-registry-v1.json` | Patterns P01–P18 · PP01–PP08 · replacements · realtime SSOT URLs |
| Shared lib | `scripts/anti_poison_lib_v1.py` | Scan · classify · sanitize · positive-inject check |
| Engine | `scripts/anti_poison_engine_v2.py` | Orchestrate tiers · write receipt |
| Projection sanitize | `scripts/projection_poison_sanitize_v1.py` | Rewrite `command-data*.json` + `boot.json` |
| Law scrub (legacy) | `scripts/agent_mirror_poison_scrub_v1.py` | Now delegates law scan to lib |
| Pre-write hook | `scripts/pre_write_guard_v1.py` post-write | Scan new rule/law writes for poison |
| Validator (fast) | `scripts/validate-anti-poison-engine-v2-v1.sh` | Mac-safe ≤90s |

**Receipt:** `~/.sina/anti-poison-engine-v2-receipt-v1.json`  
**Projection receipt:** `~/.sina/projection-poison-sanitize-receipt-v1.json`

---

## 4. Engine tiers

| Tier | Command | PASS means | Mac founder session |
|------|---------|------------|---------------------|
| **fast** | `--tier fast` | Law poison 0 hits · scrub ok | **Allowed** — session gate compatible |
| **projection** | `--tier projection` | Hub projection 0 hits | **Read-only scan** — sanitize needs ship window |
| **full** | `--tier full` | Law + projection + vocab + positive inject | Diagnostic only — not pre-reply marathon |

```bash
cd ~/Desktop/SourceA
python3 scripts/anti_poison_engine_v2.py --tier fast --json
python3 scripts/anti_poison_engine_v2.py --tier projection --json
```

---

## 5. P-CLASS taxonomy (v2 extension)

| Class | Name | Writer | Fix |
|-------|------|--------|-----|
| P1–P10 | PT-METHOD original | rules · mirror · API · runtime · projection · prohibition · queue · propagation · chat-echo · split-SSOT | `SINA_POISON_TRACKING_METHOD_LOCKED_v1.md` |
| **P11-DRAIN** | Single-plan / one-row proceed | cloud drain scripts · hub copy | `full_pack` + `max_advance: 100` only (INCIDENT-042/043) |
| **P12-URL** | Retired domain/email | landing · command-data · mail routes | `hello@sourcea.app` · `https://sourcea.app` |
| **P13-SURFACE-TRASH** | Trashed daily surface | `boot.json` · hub hero | Cloud Workers `:13027` · Chat Unify form `:13023/form/` |

**Projection patterns:** PP01–PP08 in registry — scan `agent-control-panel/` only.

---

## 6. Realtime SSOT (projection replacements)

| Stale | Current |
|-------|---------|
| `http://127.0.0.1:13020/form/` | `http://127.0.0.1:13023/form/` |
| `INCIDENT-037 block ON` | `founder picks only` |
| `hello@sourcea.com` | `hello@sourcea.app` |
| `one CLOUD-SEC per cron tick` | `100 rows per Cloud Forge Run turn (INCIDENT-043)` |

**Cockpit:** `http://127.0.0.1:13027/` — `data/cloud-workers-control-plane-v1.json`  
**Form SSOT:** `scripts/form_official_canvas_route_v1.py`

---

## 7. ASF batch — projection sanitize (executed 2026-06-26)

**Order:** `ASF: ANTI-POISON-v2 — projection sanitize`

```bash
python3 scripts/projection_poison_sanitize_v1.py --force --json
```

**Result (disk):** `hits_before: 0` · `hits_after: 0` · `ok: true`  
**Touched:** `command-data.json` · `command-data-shell.json` · `command-data-runtime.json` · `command-data-canonical.json` · `worker-hub/boot.json`  
**Receipt:** `~/.sina/projection-poison-sanitize-receipt-v1.json`

**Note:** Hub rebuild (`align_command_data_ui_v1.py` / `hub_projection_sync_v1.py`) can re-introduce stale hero text — run projection sanitize **after** hub refresh in ship window until builder SSOT is wired.

---

## 8. Session discipline (all agents)

### Mac founder session (INCIDENT-039)

1. Read `~/.sina/agent_session_gate_receipt_v1.json` once per chat  
2. Optional: `anti_poison_engine_v2 --tier fast` (≤1s)  
3. Reply <30s · **no** `validate-* && validate-*` · **no** scrub `--all` mid-turn  

### Ship window / cloud CI only

```bash
python3 scripts/agent_mirror_poison_scrub_v1.py --all
python3 scripts/projection_poison_sanitize_v1.py --json
bash scripts/validate-anti-poison-engine-v2-v1.sh
bash scripts/validate-agent-law-poison-free-v1.sh
```

---

## 9. Pre-write poison hook

On `pre_write_guard_v1.py post-write` for rule/governance paths:

- Scans written file via `anti_poison_lib_v1.scan_file`
- **Blocks** only when `~/.sina/asf-ship-window-v1.flag` present and not Mac-only founder session
- Receipt field: `anti_poison_post_write`

---

## 10. Positive inject schema (ship window)

Mirror must inject (not prohibition tables):

- `read_receipt_paths`
- `factory_now_line_from_surfaces_or_receipt`
- `mac_law_control_only`
- `reply_under_30s_then_stop`
- `cloud_executes_factory_body`

Check: `anti_poison_lib_v1.check_positive_inject()` · full tier only.

---

## 11. Next upgrades (honest backlog)

| Priority | Item | Done when |
|----------|------|-----------|
| B1 | Wire `projection_poison_sanitize` after `hub_projection_sync_v1.py` | Hub refresh cannot resurrect PP01 |
| B2 | Graph node row in `sourcea_pipeline_node_graph_v1.json` T0 | Receipt in graph runner |
| B3 | Session gate merges engine fast receipt | Single poison line on gate receipt |
| C1 | Semantic poison classifier (cloud batch) | Rephrased validator orders caught |
| C2 | P9 chat-echo detector | Transcript close-line vs disk |
| C3 | Cloud Workers `:13027` poison glance tile | Founder one-line status |

---

## 12. Forbidden

- Merge poison with realtime blocker in one “fix everything” validator chain on Mac  
- Close poison track on chat apology without disk receipt  
- Rebuild hub projection without post-sanitize when ASF moved surfaces  
- Say “drain/loop” to founder for cloud motor (use Cloud Forge Run / Auto Runtime — INCIDENT-043)

---

**END LOCKED v1**
