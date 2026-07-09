# SourceA Audit Ground Truth Pack

**Saved at:** 2026-07-05T12:55:00Z  
**Purpose:** Audit-defense — honest claim = reality. No motor/L4 fixes in this pass.

---

## 1. Receipt table

| Signal | Source | Timestamp | Result |
|--------|--------|-----------|--------|
| sourcea.app | `curl -o /dev/null -w %{http_code}` | 2026-07-05 | **200** |
| noetfield.com | `curl` | 2026-07-05 | **200** |
| Public Brain chat API | `POST /api/brain/chat/v1` | 2026-07-05 | **200** (OpenRouter chat — not brain-core gate) |
| Railway FBE health | `GET .../health` | 2026-07-05T12:53:07Z | **200** `ok:true` |
| Cloud drain queue | `GET .../queue/v1` | 2026-07-05T12:53:07Z | **ok** · `registry_exhausted` · head `CLOUD-SEC-7666` |
| Autorun pending (authoritative) | `scripts/autorun_pending_v1.py --write --json` | 2026-07-05T12:53:01Z | **ok:false** · P0 `external_verify_l4` · truth log stale |
| Autorun mirror sync | `~/.sina/autorun-pending-v1.json` | 2026-07-05T12:53:01Z | **Matches repo receipt** |
| Last cloud auto-tick | `~/.sina/cloud-drain-auto-tick-receipt-v1.json` | 2026-06-23T20:58:33Z | **ok:false** (stale) |
| Mac autorun launchd | `launchctl print .../com.sourcea.autorun-worker` | 2026-07-05 | **Not loaded** (DISABLED) |
| CF cron worker root | `curl workers.dev/` | 2026-07-05 | **404** (no health at root — capture from CF dashboard post-audit) |
| Revenue / ROI | `~/.sina/sourcea-revenue-engine-crm-v1.json` | 2026-06-24 | **Pre-revenue** · 0 `won` · template prospects |

**Receipt paths (autorun):**
- Repo: `receipts/cloud/autorun-pending/pending-latest-v1.json`
- Mirror: `~/.sina/autorun-pending-v1.json`

---

## 2. Live-claim hygiene changes

| File | Change |
|------|--------|
| `sites/SourceA-landing/sourcea-layout-dark.html` | Removed “operates a self-healing factory daily”; added **pre-revenue**; Self-heal → Monitor/target language; Live → Demo |
| `sites/SourceA-landing/sourcea-layout-light.html` | Removed daily factory / self-healing claims; LIVE → TARGET; added **pre-revenue** |
| `sites/SourceA-landing/green-unified/attach/agency-onepager.html` | Self-healing monitor → ops monitor (retainer target) |
| `sites/SourceA-landing/green-unified/kernel/legacy-full-home-v1.html` | Same retainer wording fix |

**Left as product UI (not live-autonomy claims):** Forge Terminal `Self-heal` button = L2 patch mode name.

---

## 3. Current offline / stale / blocked status

| Component | Status | Evidence |
|-----------|--------|----------|
| **Deterministic brain-core gate** | **OFFLINE** | Not deployed between model and public reply |
| **Public Brain chat** | **LIVE** | API 200 — separate from deterministic gate |
| **Autorun motor** | **BLOCKED + EXHAUSTED** | P0 L4 stale · queue `registry_exhausted` |
| **Mac autorun launchd** | **DISABLED** | Not loaded; documented in `docs/brain-runbook/brain-operational-runbook.md` |
| **Cloud auto-tick receipt** | **STALE** | Last ok:false 2026-06-23 |
| **ROI intelligence** | **PRE-REVENUE** | Policy logged · zero customer return signal |
| **Commercial productization** | **PARTIAL** | Sites live · packaged paid delivery not complete |

---

## 4. Walk-in script

```
LIVE:       Websites (200) · Railway health (200) · public Brain chat API (200)
OFFLINE:    Deterministic brain-core gate · Mac autorun launchd (DISABLED)
STALE:      Cloud auto-tick receipt (2026-06-23, ok:false)
BLOCKED:    Autorun P0 external_verify L4 (truth log stale since 2026-07-02)
EXHAUSTED:  Cloud drain registry_exhausted at CLOUD-SEC-7666
PRE-REVENUE: ROI/revenue CRM — templates only, no won deals, no customer ROI
HONEST:     Public pages no longer claim live self-healing factory or daily autonomous motor
```

**ROI one-liner for auditor:** Policy and routing SSOT exist logged; **pre-revenue — no customer ROI signal yet.**

---

## 5. Post-audit recovery list (do not do before audit)

1. **L4 external_verify** — dispatch `read_action_runs_v1.py --dispatch --wait` · sink truth_log PASS (not mirror_only)
2. **Motor** — new registry rows or next motor SSOT after `registry_exhausted`
3. **Cloud auto-tick** — prove fresh `ok:true` receipt post-deploy
4. **CF cron** — verify `*/10` cron receipt from Cloudflare dashboard
5. **Mac launchd** — only re-enable with ASF + correct `Noetfield-Systems/SourceA` path
6. **brain-core-v1** — deploy gate when ready; until then keep “public chat live / deterministic gate offline”
7. **Revenue** — first paid engagement + log `won` in CRM
8. **Deploy** — push sourcea-layout-dark/sourcea-layout-light HTML hygiene to production if not auto-deployed

---

## Commands to re-verify (auditor room)

```bash
bash scripts/validate-governance-consistency-v1.sh
python3 scripts/autorun_pending_v1.py --json
curl -sS https://sourcea-fbe-runner-production.up.railway.app/api/cloud-drain/queue/v1
launchctl print "gui/$(id -u)/com.sourcea.autorun-worker" 2>&1 | head -3
```
