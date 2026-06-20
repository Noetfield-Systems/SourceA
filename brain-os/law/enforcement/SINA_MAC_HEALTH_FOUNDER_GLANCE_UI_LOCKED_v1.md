# Mac Health — Founder Glance UI — LOCKED v1

**Version:** 1.1.0 · **Saved:** 2026-06-20T19:30:00Z · **Authority:** Founder — Mac cockpit SSOT  
**surface_id:** `mac_health` · **UI mode:** `founder_glance` · **App version:** `4.0.0`  
**URL:** http://127.0.0.1:13024/ · **Root:** `scripts/mac-health-standalone/`  
**Machine contract:** `data/mac-health-founder-glance-ui-contract-v1.json`  
**Version SSOT:** `scripts/mac_health_version_v1.py`  
**Ledger:** `brain-os/law/enforcement/ui-upgrade-ledgers/MAC_HEALTH_UI_UPGRADE_LEDGER_LOCKED_v1.md`

---

## One law — Mac = cockpit glance only

| Rule | Meaning |
|------|---------|
| **Zero tabs** | No segment nav · no fake chrome · one card |
| **One primary CTA** | `Relieve pressure` — auto heal without founder steps |
| **Four stat tiles** | Memory · CPU · Disk · Background — tap fixes when bad |
| **More = advanced only** | Manual relief · disk/logs · auto guard · tools — collapsed |
| **No founder terminal** | Agents run shell · founder taps only |
| **No fragmentation** | Single version SSOT · bundle sync · validators · API `ui_contract` |

Cloud executes · Mac watches · founder never carries machine sickness in silence.

---

## Frozen UX contract (v4.0.0)

**Always visible**

1. Title **Mac Health** + LIVE badge  
2. Score ring + one-line story  
3. Primary button **Relieve pressure** (`#btn-heal`)  
4. **Cloud glance strip** (`#cloud-glance-strip`) — read-only Railway + last dispatch · links to Worker Hub  
5. Four live stat tiles (`#pressure-grid`)  
6. **Needs attention** section — only when findings exist  
7. `<details>` **More** — everything else

**v4 additive law:** Cloud strip is **read-only** — Mac never runs cloud job bodies from Mac Health.

---

## Frozen UX contract (v3.3.0 baseline — preserved)

**Removed permanently (no downgrade)**

- Tab bar (`mhg-seg-nav`, Overview/RAM/Cool Down/Auto guard tabs)  
- Founder poem · seven guardians · domains · SASCIP tile  
- Duplicate toolbar buttons · help-card prose blocks  
- Equal-weight button rows above the fold

**Emergency banners** — show only when triggered (Cursor hot · stuck browser · log bomb).

---

## Automation stack (founder zero-task)

| Layer | What runs | Founder |
|-------|-----------|---------|
| Heart `:13024` | Live pulse 8s · auto_apply · prevention | Open app · glance |
| Primary CTA | `action: heal` pipeline | One tap if needed |
| Stat tile tap | Targeted fix per pressure card | One tap if bad |
| LaunchAgent | `install-mac-health-launchagent-v1.sh` | Never manual serve |
| H1 bridge | `mac_health_live_v1.py` → Worker Hub card | Read-only glance |

Agents **never** answer form PICKs · **never** bulk-apply · **never** submit founder decisions.

---

## Wiring (ecosystem)

| Surface | Wire |
|---------|------|
| Version | `mac_health_version_v1.py` → server · UI cache buster · validators |
| API | `GET /health` · `POST /api/mac-health` → `ui_contract` block |
| UI registry | `data/ui-upgrade-surface-registry-v1.json` → `mac_health` |
| Ledger | `data/ui-upgrade-ledgers/mac_health-v1.json` → UP-MH-001 |
| Hub link | `sina_command_lib.py` · `sina_link_graph.py` → `:13024` |
| Bundle | `sync-standalone-apps-to-bundles-v1.sh` after UI ship |
| Validators | `validate-mac-health-founder-glance-v1.sh` (SSOT gate) |

---

## Before any UI edit

1. `python3 scripts/ui_upgrade_first_check_v1.py --surface mac_health --ack --json`  
2. Read this doc + machine contract  
3. Append ledger row · bump `MAC_HEALTH_VERSION` · sync bundles  
4. `bash scripts/validate-mac-health-founder-glance-v1.sh` PASS

---

## Upgrade history

| id | When | Summary |
|----|------|---------|
| UP-MH-000 | 2026-06-19 | Ledger bootstrap |
| UP-MH-001 | 2026-06-19 | **Founder Glance v3.3.0** — SSOT locked · ecosystem wired |
| UP-MH-002 | 2026-06-20 | **Control Plane Glance v4.0.0** — cloud read strip · Hub bridge · E2E |
