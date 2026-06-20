# Automated Evidence Generation (AEG) v1

**Date:** 2026-06-15  
**Lane:** Engineering — proof-of-failure logs → buyer-clickable forensic bundle  
**Law:** Gemini AEG stack — BLOCK is a first-class log, not a chat note.

## Architecture (Gemini → disk)

| Layer | Tool | Output |
|-------|------|--------|
| **Capture — terminal** | `asciinema rec` (fallback: transcript) | `evidence.cast` or `terminal.txt` |
| **Capture — UI** | Playwright headless @ `:13023` | `ui.png` + `ui.webm` |
| **Compile** | `aeg_capture_v1.py` | `evidence_report.md` + `index.html` (asciinema player embed) |
| **Deliver** | `host_aeg_bundle_v1.py` | `https://…/proof/{evidence_id}/` or local `index.html` |

## Auto-trigger on BLOCK

`critic_boot_v1.py` runs AEG automatically when `AEG_ON_BLOCK=1` (default). Session gate uses `--in-gate` → UI capture skipped for speed.

```bash
# BLOCK → forensic bundle (automatic)
python3 scripts/critic_boot_v1.py --json

# Skip AEG
AEG_ON_BLOCK=0 python3 scripts/critic_boot_v1.py --json
# or
python3 scripts/critic_boot_v1.py --no-aeg --json
```

## Decorator (agent sessions)

```python
from evidence_capture_v1 import evidence_capture

@evidence_capture(terminal_command="python3 scripts/critic_boot_v1.py --json")
def run_agent_session():
    return run_boot(...)
```

## One-command full stack

```bash
bash scripts/run_aeg_full_stack_v1.sh
```

Runs: `setup_aeg_deps_v1.sh` → `run_aeg_critic_boot_demo_v1.sh` → `validate-aeg-capture-v1.sh` → `host_aeg_bundle_v1.py` → outbound draft.

## Scripts

| Script | Role |
|--------|------|
| `scripts/aeg_capture_v1.py` | Capture + compile + publish bundle |
| `scripts/evidence_capture_v1.py` | `@evidence_capture` decorator |
| `scripts/critic_boot_v1.py` | Layer 1 boot — auto AEG on BLOCK |
| `scripts/setup_aeg_deps_v1.sh` | `brew install asciinema` + `playwright install chromium` |
| `scripts/host_aeg_bundle_v1.py` | Cloudflare Pages or tunnel → proof URL |
| `scripts/send_aeg_proof_outbound_v1.py` | Mail draft with proof link |
| `scripts/run_aeg_critic_boot_demo_v1.sh` | BLOCK → heal side-by-side demo |
| `scripts/validate-aeg-capture-v1.sh` | Structure validator |

## Config

Copy `config/aeg-config-v1.example.json` → `~/.sina/aeg-config-v1.json`:

```json
{
  "base_url": "https://sourcea.com/proof",
  "ui_url": "http://127.0.0.1:13023/"
}
```

Env: `AEG_BASE_URL` · `AEG_UI_URL` · `AEG_ON_BLOCK`

## Receipts

| Path | Role |
|------|------|
| `~/.sina/critic-boot-v1.json` | Boot verdict (+ `aeg` block when captured) |
| `~/.sina/aeg-latest-receipt-v1.json` | Latest bundle + `proof_url` |
| `~/.sina/aeg-index-v1.jsonl` | Append-only index |
| `~/.sina/aeg/{evidence_id}/` | Full bundle |
| `archive/attachments/evidence/aeg/{evidence_id}/` | Archive mirror |

## Buyer workflow

1. System BLOCKs → AEG runs in ~5s  
2. `host_aeg_bundle_v1.py` returns one URL  
3. `send_aeg_proof_outbound_v1.py --to agency@…` opens Mail with link  
4. Buyer clicks → forensic page: terminal + UI + broken vs heal + JSON receipt
