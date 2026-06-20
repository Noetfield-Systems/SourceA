# Hub launchd supervisor (LOCKED v1)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Locked:** 2026-06-08 · **Authority:** ASF  
**Label:** `com.sourcea.hub`  
**Plist:** `~/Library/LaunchAgents/com.sourcea.hub.plist`  
**Source:** `launch/com.sourcea.hub.plist`  
**Install:** `bash scripts/install-hub-launchd-v1.sh`  
**Validator:** `bash scripts/validate-hub-launchd-v1.sh`

---

## Rule

Sina Command hub (`sina-command-server.py` :13020) **must** run under launchd with **KeepAlive** (restart on exit) and **RunAtLoad** (start at login).

Brain self-heal step 1 uses `launchctl kickstart -k gui/$UID/com.sourcea.hub` when health fails — not ad-hoc `nohup`.

---

*End HUB_LAUNCHD_SUPERVISOR_LOCKED_v1*
