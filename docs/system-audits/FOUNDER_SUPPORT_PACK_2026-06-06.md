# Founder support pack — hub ops without Terminal

**Saved:** 2026-06-06T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit @ 2026-06-16T05:49:57Z  

---

## Golden rules

1. **No Terminal** for ASF — hub only  
2. **One worker task** per session — `sa-XXXX` from live pick  
3. **Brain chat** routes; **worker chat** codes closeout  
4. **SinaaiDataBase** = archive audits only  
5. **Refresh hub** after autonomy code changes  

---

## Hub quick path

| Step | Action |
|------|--------|
| 1 | Open hub `http://127.0.0.1:13020` |
| 2 | Refresh |
| 3 | Check synthesis gates: `dispatch_ready`, `eval_1b_gate_ok` |
| 4 | Use Actions / Private agents — not Terminal |
| 5 | Route worker: `worker sa-0202` (verify pick first) |

---

## Magic phrases (worker lane)

```
worker sa-0202
```

```
Verify live pick only — no redo sa-0108–sa-0201
```

```
Hub Refresh — check gates honest
```

---

## Live pick verification

**Without Terminal (founder asks brain/worker in SourceA chat):**

Brain reads `SOURCEA-PRIORITY.md` + reports pick from last validator run.

**Expected at save:** **sa-0202** (s2 hub-build-ci).

---

## When gates are false (normal)

| Gate | Meaning | Founder action |
|------|---------|----------------|
| `dispatch_ready=false` | No live autonomous dispatch | Continue structural worker tasks |
| `eval_1b_gate_ok=false` | Live eval blocked | OpenRouter top-up |
| `structural_only` | Scaffold mode | OK for verify work |

---

## Private agents

- Registry: `scripts/agent_workspace_registry.py`  
- Count: **8** private agents  
- Use via hub — not ad-hoc Terminal agents  

---

## Commercial parallel (do not block worker)

- TrustField demos P10  
- CanadaBuys  
- PacifiCan/BDC LIFT  
- OpenRouter top-up (**unblocks gates**)  
- G3 Tailscale  
- MergePack MP-SHIP Vercel  
- Canada AI funding alignment  

---

## Troubleshooting (hub-first)

| Symptom | Fix |
|---------|-----|
| Autonomy API 404 | Restart hub server |
| Pick seems stale | Brain re-read PRIORITY |
| Worker redo loop | Check do_not_redo list |
| Reply suggests Terminal | Ignore — use hub; M4 may warn |

---

## Brain pack mirror

```bash
# Worker lane only if explicitly approved — founder uses hub
~/.sina/brain/  # 6 files synced via sync-brain-pack.sh
```

---

## Audit docs location

All saved analyses: `SourceA/docs/system-audits/` — see `README_INDEX.md`.

---

## Single lever reminder

**OpenRouter credits → Eval-1b live PASS once** — highest ROI founder commercial action for platform gates.
