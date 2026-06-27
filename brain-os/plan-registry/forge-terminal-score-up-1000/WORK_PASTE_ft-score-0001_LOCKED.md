# WORK PASTE — ft-score-0001 (facilitator · paste into Forge Terminal RAW AI)

**Saved at:** 2026-06-25T11:15:00Z  
**Plan:** `ft-score-0001`  
**Worker:** Pre-LLM Mac RAW AI · Cursor observes only  
**Surfaces:** `http://127.0.0.1:13029/terminal/` + `https://sourcea.app/sourcea/forge/terminal`

---

## Boot first (founder · if :13029 offline)

```bash
cd ~/Desktop/SourceA && bash scripts/wire-forge-terminal-os-v1.sh
# verify:
curl -sS http://127.0.0.1:13029/health
open http://127.0.0.1:13029/terminal/
```

---

## Paste below into Forge Terminal chat (one turn)

```
RAW AI WORK — ft-score-0001: Visual parity tokens (bounded)

MISSION: docs/FORGE_MISSION_6000_PLANS_LOCKED_v1.md
CONTRACT: data/forge-visual-parity-contract-v1.json
CURSOR: observer only — you are the worker body.

SCOPE (edit ONLY these):
- apps/forge-terminal-v1/forge-parity-tokens-v1.css (CREATE)
- apps/forge-terminal-v1/terminal.css (import tokens + map --accent etc.)
- apps/forge-terminal-v1/index.html (add Google fonts from contract)
- SourceA-landing/green-unified/sourcea-forge-terminal-demo.css (--ft-* align to same canonical vars)
- data/forge-visual-parity-contract-v1.json (add "css_file": "apps/forge-terminal-v1/forge-parity-tokens-v1.css" if helpful)

DO NOT touch: brain-os, scripts validators marathon, cloud workers, unrelated pages.

TASK:
1. Create forge-parity-tokens-v1.css with :root vars from contract color_tokens + fonts:
   --forge-bg #0c0e12, --forge-surface #141820, --forge-accent #5eead4, --forge-text #e8eaed, --forge-muted #9aa0a6
   --forge-font-body "Inter", --forge-font-display "Plus Jakarta Sans", --forge-font-mono "JetBrains Mono"
2. terminal.css :root — replace drifted --accent #4ade80 and SF Pro fonts with @import or link to parity tokens; keep layout vars (--sidebar-w etc.)
3. index.html — add contract fonts google_url in <head>
4. sourcea-forge-terminal-demo.css — map --ft-accent/--ft-bg to same values as parity file (single source of truth comment at top)
5. Document mapping in 5-line comment at top of forge-parity-tokens-v1.css

ACCEPTANCE:
- Local :13029/terminal/ uses Inter body + teal accent #5eead4 (not green #4ade80 / #3ecf8e)
- Online demo CSS uses matching --ft-* values
- No behavior changes to terminal.js

VERIFY (light):
- open http://127.0.0.1:13029/terminal/ — visual check topbar accent dot
- grep -E "5eead4|4ade80|3ecf8e" apps/forge-terminal-v1/ SourceA-landing/green-unified/sourcea-forge-terminal-demo.css

CLOSEOUT:
- Write ~/.sina/forge-plan-receipt-v1.json with plan_id ft-score-0001, files_changed[], ok:true
- Reply: list files + before/after accent hex
```

---

## Facilitator verify (Cursor · after RAW AI closeout)

```bash
test -f ~/.sina/forge-plan-receipt-v1.json && python3 -m json.tool ~/.sina/forge-plan-receipt-v1.json
grep -n "5eead4" apps/forge-terminal-v1/forge-parity-tokens-v1.css
```

Mark done in `forge-terminal-score-up-1000/REGISTRY.json` → `ft-score-0001` status done, built_by pre-llm-mac.

Online deploy (separate turn): build landing → wrangler pages deploy when founder approves.
