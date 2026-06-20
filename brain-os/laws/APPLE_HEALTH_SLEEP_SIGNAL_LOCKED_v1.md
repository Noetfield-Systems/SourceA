# Apple Health Sleep Signal (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-08  
**Authority:** ASF  
**Mechanism:** `scripts/apple_health_mini.py` · `scripts/apple_health_sleep_bridge_v1.py`  
**Hub:** `POST /api/apple-health` · mini-app `/mini-apps/apple-health/`

---

## One sentence

**Apple Health tells us when you're asleep — not a 300s timer. Health event → arm sleep. Wake event → stop overnight.**

---

## Signal SSOT

`~/.sina/apple-health/sleep-signal-v1.json`

| `state` | Meaning |
|---------|---------|
| `asleep` | Founder sleeping — recommend `arm sleep` |
| `awake` | Founder up — recommend wake / Worker lane |

**Source:** iPhone Shortcut · Apple Watch · Mac Health app · manual Hub tap.

---

## Shortcut actions (POST hub)

| action | Effect |
|--------|--------|
| `sleep_start` | Record asleep · optional auto `arm-sleep-mode-v1.sh` |
| `sleep_end` | Record awake · stop overnight · `founder_busy` |
| `health_sample` | Update metrics (steps, sleep hours) |
| `enable_auto_arm` | `sleep_start` arms Claude team automatically |
| `disable_auto_arm` | Manual `arm sleep` only (default for pre-sleep monitor) |

---

## Governance map

```
Apple Health asleep  →  (optional auto) arm sleep  →  Claude team owns map
Apple Health awake   →  wake bridge  →  ASF / Worker owns map
```

**Pre-sleep monitor:** auto-arm **OFF** — you verify first.  
**After trust:** Hub → enable auto arm OR Shortcut `sleep_start` only when in bed.

---

## Monitor

- Dashboard `monitor.html` + `dashboard_server_v1.py` show `apple_health` block
- `python3 scripts/apple_health_sleep_bridge_v1.py --json` — recommend stay | arm_sleep | wake

---

*LOCKED — Rational player: Health is the sensor. Code reacts to life, not the clock.*
