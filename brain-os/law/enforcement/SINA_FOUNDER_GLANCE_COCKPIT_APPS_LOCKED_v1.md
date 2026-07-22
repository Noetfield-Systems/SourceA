# Founder Glance Cockpit Apps — LOCKED v1

**Version:** 1.0.0 · **Saved:** 2026-06-19T20:39:27Z · **Authority:** Founder — Mac control panel law  
**Registry:** `data/founder-glance-cockpit-apps-v1.json` · **Module:** `scripts/founder_glance_cockpit_v1.py`

---

## One law — all Mac cockpit apps

| Rule | Every standalone app |
|------|----------------------|
| **Zero tabs** | No segment nav · no step chrome above fold |
| **One primary CTA** | Single automation action per app |
| **Four stat tiles** | Glance metrics · tap to fix when bad |
| **More disclosure** | Manual · tools · settings — collapsed |
| **ui_contract on API** | `/health` + report payload |
| **No hub required** | Standalone ports only · `:13023–13026` |

Mac = cockpit · cloud = factory · founder taps only.

---

## Cockpit fleet (SSOT ports)

| App | Port | Primary CTA |
|-----|------|-------------|
| Chat Unify | `:13023` | Merge all & scan |
| Mac Health | `:13024` | Relieve pressure |
| Apple Health | `:13025` | Open Health app |
| N8N Integration | `:13026` | Capture intelligence |

Worker Hub `:13020` = queue · form · factory-now — separate surface (not founder-glance).

---

## Wiring chain

1. Version + contract on disk  
2. Standalone server `/health` → `ui_contract`  
3. `sina_command_lib` · `sina_link_graph` → standalone URLs  
4. `sync-standalone-apps-to-bundles-v1.sh`  
5. `validate-founder-glance-cockpit-apps-v1.sh` PASS  
6. Receipt `~/.sina/founder-glance-cockpit-wire-v1.json`

---

## Forbidden (all apps)

- Hub mini-app URLs when standalone exists  
- Equal-weight button rows above fold  
- Fake decorative tiles · emoji toolbars as primary chrome  
- Agent form submit · bulk apply
