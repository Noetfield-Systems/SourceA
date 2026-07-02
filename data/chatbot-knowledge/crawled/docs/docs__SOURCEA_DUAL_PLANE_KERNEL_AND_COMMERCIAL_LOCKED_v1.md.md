---
lane: developer
updated: 2026-07-02T10:32:00Z
source_path: docs/SOURCEA_DUAL_PLANE_KERNEL_AND_COMMERCIAL_LOCKED_v1.md
public: true
---

# SourceA dual plane — Kernel vs Commercial (LOCKED v1)

**Saved:** 2026-06-23T07:00:00Z · **Machine:** `data/sourcea-dual-plane-v1.json`

## One law

> **SourceA is always the foundation kernel for the portfolio. Commercial is a separate plane for paying customers. Other repos depend on kernel backups — never ship commercial experiments into governance SSOT.**

---

## Plane 1 — Foundation kernel (MAIN)

| What | Where |
|------|--------|
| Governance + brain entry | `brain-os/law/entry/` |
| Cloud factory + drains | `cloud/` · Railway FBE |
| Apps + packages | `apps/` · `packages/` |
| Data SSOT | `data/` |
| Living center | `data/sourcea-living-center-v1.json` |
| Historical database | `~/Desktop/SinaaiDataBase/archive/` (not in daily SourceA) |

**Backup before commercial work:**

```bash
bash scripts/sourcea_foundation_kernel_backup_v1.sh
git tag foundation-kernel-2026-06-23   # after commit
```

Other repos (TrustField, Noetfield, mono) **pin to this tag** when they need a stable kernel.

---

## Plane 2 — Commercial (paying customers)

Less infra vibe · more **agentic real systems** · users build their agent factory over time.

### Business A — Service (NOW)

- **Headline:** "We build your startup's MVP in 48 hours."
- **Revenue:** $2k–$10k · first dollar **this week**
- **Stack:** intake form (5 questions) + founder skills + Cursor — **no platform yet**
- **Wedge:** Apple App Store specialty — "AI-built App Store apps"

### Business B — Platform (LATER)

- **Headline:** "Come build on our platform"
- **Revenue:** subscription + usage
- **Needs:** Forge, auth, sandbox, billing — **2–3 months**
- **Funded by:** first 3 service clients ($6k–$10k)

**Lock order:** Business A page + form on `sourcea.com` / `sourcea.app` **before** any sandbox or free tier.

---

## Form spec (Business A v1)

1. What are you building? (app / website / MVP / video / text)
2. Competitor or example? (URL or name)
3. Deadline? (this week / 2 weeks / flexible)
4. Budget? ($500–1k / $1k–3k / $3k–10k / let's talk)
5. Email

End: *We'll respond in 2 hours with a plan.*

---

## Forbidden

- Customer intake rows in `brain-os/law/` LOCKED files
- Mixing WitnessBC lane credentials with commercial deploy
- Deleting kernel backup tags when iterating commercial copy
