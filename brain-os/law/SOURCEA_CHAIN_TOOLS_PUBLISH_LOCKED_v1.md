# SourceA Chain Tools — Publish Pattern (Graphify class) — LOCKED v1

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.0 · **Locked:** 2026-06-15  
**Authority:** SW1 · Buyer 1 eval motion · open-core GTM  
**Law:** `SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md` §10 · §11 SW1  
**Sender:** `SOURCEA_COMMERCIAL_SENDER_LOCKED_v1.md` → **hello@sourcea.app**

---

## What chain tools have in common (Graphify pattern)

- Sit **between** the developer and the AI — not as the AI
- **One command in**, one useful artifact out (`BOOT_REPORT.json`, receipt, gate decision)
- Solve a problem at **every** execution, not once
- **Zero configuration** — works against any project (optional `.sourcea-boot.json`)
- **Open source core**, paid API or hosted tier later

**Category:** Infrastructure that makes agents more reliable — not a new agent.

---

## Three publishable chain tools (now)

| Tool | What it does | Publish as | Status |
|------|-------------|------------|--------|
| **`sourcea-boot`** | 4 checks · PASS/BLOCK before any agent works | `pip install sourcea-boot` | **v0.1.0 logged** · `packages/sourcea-boot/` |
| **Governance receipt + spine** | Signs and logs every agent action · replay-able | `pip install sourcea-sdk` | P1 — extract from spine after boot ships |
| **`POST /v1/decision`** (Noetfield OS) | Policy gate before execution | Public API + npm SDK | P1 — Noetfield lane |

---

## Build pattern (repeat per tool)

1. Identify one pain every AI developer hits (e.g. "is it safe to run agents right now?")
2. Build the smallest thing that solves it (one script · one endpoint · one command)
3. Output something **persistent** (file · receipt · JSON)
4. Publish to **PyPI or npm** with a **3-line README**
5. GitHub stars follow if the pain is real

---

## sourcea-boot (P0 — ship first)

```bash
pip install sourcea-boot
sourcea-boot
# → BOOT_REPORT.json · exit 0 = PASS · exit 1 = BLOCK
```

| Check | Factory mode | Portable mode |
|-------|--------------|---------------|
| `policy_version` | SSOT brief vs disk | `POLICY.md` sig vs `.sourcea/policy-state.json` |
| `provider` | Voyage / embedding provider | `.env` / `OPENAI_API_KEY` |
| `receipt_fresh` | `~/.sina` gate receipt <8h | `.sourcea/boot-receipt.json` |
| `queue_truth` | run-inbox truth_match | optional queue/inbox files in config |

**Package:** `packages/sourcea-boot/`  
**Validator:** `scripts/validate-sourcea-boot-v1.sh`  
**Factory bridge:** `scripts/critic_boot_v1.py` delegates when package on path

---

## SW1 unlock

Buyer 1 installs `sourcea-boot` in **<1 minute**. README runnable in **<5 min** = SW1 prerequisite (portfolio SSOT §10).

**Outbound:** chain-tool pitch uses **hello@sourcea.app** — never personal email.

---

## Void

| VOID | REPLACE WITH |
|------|--------------|
| "We built an agent" as hero | Chain tool — **infrastructure between dev and AI** |
| Governance slides without CLI | `sourcea-boot` PASS/BLOCK in terminal |
| PyPI later after perfect kernel | **v0.1.0 publish** — boot gate first |

---

**End LOCKED v1**
