# Cursor Find Bugs automation — SourceA adaptation (LOCKED)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 — LOCKED  
**Source:** [Cursor Marketplace — Find critical bugs](https://cursor.com/marketplace/automations/find-bugs)  
**Runner:** `scripts/find_critical_bugs.py` · maintainer agent · optional daily schedule  
**Hub:** Backlog tab · Order Guardian when critical

---

## 0. One sentence

**Inspect recent SourceA/hub changes for high-severity correctness bugs only — minimal fix, full E2E validation, no style-chase PRs.**

---

## 1. What we adopt from Cursor automation

| Cursor rule | SourceA adaptation |
|-------------|-------------------|
| Daily trigger 11:00 UTC | Maintainer runs after hub edits · or `find_critical_bugs.py` |
| High-severity only | Data loss, hub down, API 500, `UnboundLocalError`, audit FAIL, WTM/UI empty |
| Concrete trigger scenario | Must describe user path (e.g. POST /refresh breaks) |
| Minimal fix + test | Fix + re-run `audit_backend_e2e.py` + affected API curl |
| No PR if uncertain | Report in hub Backlog / Order Guardian — ASF decides |
| Most days: no critical bugs | Expected OK summary |

---

## 2. Investigation targets (our stack)

1. **`sina-command-server.py`** — POST routes · `build_payload` scope · panel refresh  
2. **`app.js` + `hub_essentials_index.py`** — NAV tab drift · empty WTM Future column  
3. **`system_roadmap.py`** — `future_phase` when `RUNTIME_STACK_COMPLETE`  
4. **Audits** — 8 vs 9 agent count drift  
5. **`command-data.json`** — stale embed · missing `order_guardian` / `founder_agent_guide`  
6. **Server log** — `~/.sina/command-server.log` Tracebacks  

**Ignore:** typo in law doc, pill color, theoretical race without trigger.

---

## 3. Validation chain (after any fix)

```bash
cd ~/Desktop/SourceA/scripts
python3 find_critical_bugs.py
python3 build-sina-command-panel.py
./serve-sina-command.sh   # or Refresh in hub
```

---

## 4. Agents Window prompt (copy-paste)

```
Find critical bugs in SourceA hub — follow CURSOR_FIND_BUGS_AUTOMATION_LOCKED_v1.md.
Run find_critical_bugs.py. If FAIL: minimal fix only, re-run full chain, report bug/impact/root cause/fix.
If PASS: post "no critical bugs found" one line.
```

**LOCKED** — Maintainer runs after every hub sprint; Cursor cloud automation optional when ASF enables marketplace trigger.
