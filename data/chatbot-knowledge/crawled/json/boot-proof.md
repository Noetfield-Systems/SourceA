---
updated: 2026-06-30T12:42:32Z
lane: buyer
source_path: sites/SourceA-landing/green-unified/data/boot-proof.json
public: true
kind: json
---

# Boot Proof

- **schema**: sourcea-boot-proof-v1
- **at**: 2026-06-27T18:07:35Z
- **verdict**: PASS
- **ok**: True
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
- **founder_line**: Factory boot PASS — four checks logged
