---
updated: 2026-07-06T09:57:10Z
lane: core
source_path: sites/SourceA-landing/green-unified/data/aeg-live.json
public: true
kind: json
---

# Aeg Live

- **schema**: sourcea-aeg-live-v1
- **at**: 2026-07-06T09:54:53Z
- **evidence_id**: aeg-20260702T194402Z-2c9c78f7
- **verdict**: PASS
## blockers
- **terminal_transcript**: $ sourcea-boot --json

SOURCEA_BOOT PASS ok=true
REPORT=receipts/sourcea-boot/BOOT_REPORT.json

  [SKIP] policy_version: no policy file (POLICY.md) (not configured)
  [PASS] provider: provider env present (ANTHROPIC_API_KEY)
  [SKIP] receipt_fresh: no prior receipt — first boot allowed
  [SKIP] queue_truth: no queue files configured (not configured)

blockers:
  (none)
## checks
## policy_version
- **id**: C1
- **name**: policy_version
- **ok**: True
- **reason**: portable mode: policy file not required on public eval
- **mode**: portable
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
- **reason**: first boot allowed (no prior receipt required)
- **mode**: portable
## queue_truth
- **id**: C4
- **name**: queue_truth
- **ok**: True
- **reason**: portable mode: queue files not required on public eval
- **mode**: portable
- **boot_verdict**: PASS
- **site_proof_url**: https://sourcea.app/sourcea/proof/live.html
- **forensic_archive_url**: https://locally-projected-shade-projection.trycloudflare.com/aeg-20260702T194402Z-2c9c78f7/
- **hosted_at**: 2026-07-02T19:44:02Z
- **disclaimer**: Live inject from factory repository · same schema as weekly export bundle
