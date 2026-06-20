# SourceA — Three-Zone Hub Spine (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Date:** 2026-06-14 · **Authority:** ASF — daily spine vs heavy vs museum quarantine  
**Supersedes:** ambiguous unqualified "Hub" · command-data as agent SSOT · museum investigation loops  
**Related:** `SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md` · `FOUNDER_MUSEUM_READ_ONLY_RESTORE_LOCKED_v1.md` · INCIDENT-032 · INCIDENT-033

---

## Law (one sentence)

**Agents use ZONE A only for runtime truth; ZONE B is Maintainer-scheduled; ZONE C is founder browse-only — agents FORBIDDEN.**

---

## ZONE A — DAILY SPINE (agents MUST use)

| SSOT | Path / surface |
|------|----------------|
| Factory line | `~/.sina/factory-now-v1.json` |
| Truth bundle | `python3 scripts/agent_truth_bundle_v1.py --json` |
| Form slice | `python3 scripts/live_founder_decision_form_v1.py --json` |
| H1 API | `GET http://127.0.0.1:13020/api/worker-hub/v1` (~4 KB) |
| Execution | **RUN INBOX** `sa-*` in Worker chat |

**Agents MUST:** session-start truth bundle → factory-now line → queue/inbox → speak from ZONE A only.

**Agents MUST NOT:** cite `command-data.json` hero · Prompt feed · unqualified "Sina Command" · museum URL for audits.

---

## ZONE B — HEAVY / SCHEDULED (Maintainer, not daily)

| Surface | Role |
|---------|------|
| `http://127.0.0.1:13020/machines/` | Machine Hub (H2) |
| H2 pending registry | `~/.sina/h2-pending-registry-v1.json` (and sync scripts) |
| Judge full batch | Weekly — not daily poll |

**Founder:** optional glance · one-tap Actions when shipped.  
**Agents:** no daily steering to H2 rebuild · no "investigate hub" homework for ASF.

---

## ZONE C — MUSEUM / QUARANTINE (founder browse-only · agents FORBIDDEN)

| Surface | Role |
|---------|------|
| `http://127.0.0.1:13020/legacy/` | Founder Museum — full frozen monolith |
| `agent-control-panel/command-data.json` | Museum projection (~10.7 MB) — **not agent SSOT** |
| `/oldhubsinacommand/` | **SHIP** — same museum alias (maintainer) |

**Founder:** browse · read-only · reference · rare Actions in legacy UI.  
**Agents FORBIDDEN:** audit from command-data · E2E from museum · "investigate hub" · claim erased · steer Prompt feed · use museum for progress/queue/mode truth.

**Byte proof museum exists:** `wc -c command-data.json` + `curl /legacy/` 200 — label `[MUSEUM/READ-ONLY]` if mentioned once.

---

## Zone test (before any agent reply)

```text
Need runtime truth?     → ZONE A only
Need heavy machine?     → ZONE B · Maintainer schedule
Need old monolith UI?   → ZONE C · founder browse · agent hands off URL once · no investigation
```

---

## Verification

```bash
python3 scripts/agent_truth_bundle_v1.py --json | python3 -c "import sys,json; print(json.load(sys.stdin).get('factory_now_line'))"
curl -sf http://127.0.0.1:13020/api/worker-hub/v1 | python3 -c "import sys,json; d=json.load(sys.stdin); print('ok',d.get('ok'),'bytes',len(sys.stdin.buffer))"
wc -c ~/Desktop/SourceA/agent-control-panel/command-data.json
curl -sf -o /dev/null -w "%{http_code}\n" http://127.0.0.1:13020/legacy/
```

---

**END THREE-ZONE SPINE**
