---
updated: 2026-06-27T06:08:27Z
lane: core
source_path: sites/SourceA-landing/green-unified/data/aeg-live.json
public: true
kind: json
---

# Aeg Live

- **schema**: sourcea-aeg-live-v1
- **at**: 2026-06-27T03:41:31Z
- **evidence_id**: aeg-20260620T044750Z-ac101c6b
- **verdict**: PASS
## blockers
- **terminal_transcript**: $ python3 [REDACTED]/scripts/critic_boot_v1.py --json --no-aeg

CRITIC_BOOT BLOCK ok=False
RECEIPT=~/.sina/critic-boot-v1.json

  [PASS] ssot_brief: SSOT v3.1 sig refreshed from disk
  [PASS] voyage_provider: voyage
  [PASS] truth_match: inbox matches queue head
  [FAIL] gate_fresh: last session gate receipt ok=false

blockers:
  - last session gate receipt ok=false
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
- **site_proof_url**: https://source-a.vercel.app/sourcea/proof/live.html
- **forensic_archive_url**: https://locally-projected-shade-projection.trycloudflare.com/aeg-20260620T044750Z-ac101c6b/
- **hosted_at**: 2026-06-20T04:47:50Z
- **disclaimer**: Live inject from factory disk · same schema as weekly export bundle
