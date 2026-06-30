---
updated: 2026-06-30T12:43:40Z
lane: core
source_path: sites/SourceA-landing/green-unified/data/aeg-live.json
public: true
kind: json
---

# Aeg Live

- **schema**: sourcea-aeg-live-v1
- **at**: 2026-06-27T18:09:51Z
- **evidence_id**: aeg-20260627T180927Z-c604de95
- **verdict**: PASS
## blockers
- **terminal_transcript**: $ python3 [REDACTED]/scripts/critic_boot_v1.py --json --no-aeg

CRITIC_BOOT BLOCK ok=False
RECEIPT=~/.sina/critic-boot-v1.json

  [FAIL] ssot_brief: briefed SSOT version mismatch (disk v3.3, brief '** 3.2 — LOCKED')
  [PASS] voyage_provider: voyage
  [PASS] truth_match: inbox matches queue head
  [PASS] gate_fresh: session gate completing

blockers:
  - briefed SSOT version mismatch (disk v3.3, brief '** 3.2 — LOCKED')
## checks
## policy_version
- **id**: C1
- **name**: policy_version
- **ok**: True
- **reason**: no policy file (POLICY.md) — skipped
- **mode**: portable
- **skipped**: True
## provider
- **id**: C2
- **name**: provider
- **ok**: True
- **reason**: provider env present (ANTHROPIC_API_KEY)
- **mode**: portable
## receipt_fresh
- **id**: C3
- **name**: receipt_fresh
- **ok**: True
- **reason**: no prior receipt — first boot allowed
- **mode**: portable
- **skipped**: True
## queue_truth
- **id**: C4
- **name**: queue_truth
- **ok**: True
- **reason**: no queue files configured — skipped
- **mode**: portable
- **skipped**: True
- **boot_verdict**: PASS
- **site_proof_url**: https://69c94902.sourcea-com.pages.dev/sourcea/proof/live.html
- **forensic_archive_url**: https://locally-projected-shade-projection.trycloudflare.com/aeg-20260627T180927Z-c604de95/
- **hosted_at**: 2026-06-27T18:09:27Z
- **disclaimer**: Live inject from factory repository · same schema as weekly export bundle
