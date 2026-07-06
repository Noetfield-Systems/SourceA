---
updated: 2026-07-06T09:57:10Z
lane: buyer
source_path: sites/SourceA-landing/green-unified/data/boot-proof.json
public: true
kind: json
---

# Boot Proof

- **schema**: sourcea-boot-proof-v1
- **at**: 2026-07-02T08:45:00Z
- **verdict**: PASS
- **ok**: True
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
- **founder_line**: Factory boot PASS — four checks logged
