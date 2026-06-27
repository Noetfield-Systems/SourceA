---
updated: 2026-06-27T08:46:57Z
lane: core
source_path: sites/SourceA-landing/green-unified/data/factory-live.json
public: true
kind: json
---

# Factory Live

- **schema**: sourcea-factory-live-v1
- **at**: 2026-06-24T03:23:04Z
- **account**: sourcea
- **console_url**: command.sourcea.com/team
## pipeline
- **schema**: commercial-pipeline-glance-v1
- **at**: 2026-06-24T03:23:04Z
### lanes
- AB1
- NW1
- WBC
### counts
- **researched**: 0
- **personalized_sent**: 0
- **replied**: 0
- **proof_viewed**: 3
- **eval_scheduled**: 1
- **pilot_deposit**: 0
- **close**: 0
- **lost**: 0
### targets
- **researched**: 500
- **personalized_sent**: 100
- **replied**: 30
- **proof_viewed**: 20
- **eval_scheduled**: 10
- **pilot_deposit**: 5
- **close**: 1
- **active_conversations**: 4
- **headline**: 0 sent · 4 active · 0 close — optimize pipeline state
- **founder_line**: Pipeline · 0 personalized · 1 eval · 0 pilot
### top_next
## cp-32ddb1794d
- **id**: cp-32ddb1794d
- **company**: AB1 prospect (draft)
- **lane**: AB1
- **status**: proof_viewed
- **next_action**: Book 15 min eval · eval booking agent
- **proof_url**: https://30351aca.sourcea-com.pages.dev/sourcea/proof/live.html
- **next_agent**: eval_booking_agent
## cp-a0c7c6c607
- **id**: cp-a0c7c6c607
- **company**: AEG proof prospect (draft)
- **lane**: AB1
- **status**: eval_scheduled
- **next_action**: Founder send eval invite · Mail draft in outbound pack
- **proof_url**: https://30351aca.sourcea-com.pages.dev/sourcea/proof/live.html
- **next_agent**: await_prospect_slot
- **proof_label**: Live forensic proof
## cp-0b9b8c4eff
- **id**: cp-0b9b8c4eff
- **company**: NW1 design partner (draft)
- **lane**: NW1
- **status**: proof_viewed
- **next_action**: Book 15 min eval · eval booking agent
- **proof_url**: https://needle-celtic-effectiveness-cheapest.trycloudflare.com/aeg-20260615T174938Z-65bffb9f/
- **next_agent**: eval_booking_agent
## cp-47ccf0bd93
- **id**: cp-47ccf0bd93
- **company**: WitnessBC Proof Lab (reference)
- **lane**: WBC
- **status**: proof_viewed
- **next_action**: Founder send eval invite · Mail draft in outbound pack
- **proof_url**: https://30351aca.sourcea-com.pages.dev/sourcea/scenario.html
- **next_agent**: eval_booking_agent
- **rows_total**: 4
## boot
- **verdict**: PASS
- **ok**: True
### checks
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
- **pass_count**: 4
- **block_count**: 0
## metrics
- **active**: 4
- **proof_viewed**: 3
- **eval_scheduled**: 1
- **sent**: 0
## aeg
- **schema**: sourcea-aeg-live-v1
- **at**: 2026-06-24T03:02:39Z
- **evidence_id**: aeg-20260620T044750Z-ac101c6b
- **verdict**: PASS
### blockers
- **terminal_transcript**: $ python3 [REDACTED]/scripts/critic_boot_v1.py --json --no-aeg

CRITIC_BOOT BLOCK ok=False
RECEIPT=~/.sina/critic-boot-v1.json

  [PASS] ssot_brief: SSOT v3.1 sig refreshed from disk
  [PASS] voyage_provider: voyage
  [PASS] truth_match: inbox matches queue head
  [FAIL] gate_fresh: last session gate receipt ok=false

blockers:
  - last session gate receipt ok=false
### checks
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
- **site_proof_url**: https://30351aca.sourcea-com.pages.dev/sourcea/proof/live.html
- **forensic_archive_url**: https://locally-projected-shade-projection.trycloudflare.com/aeg-20260620T044750Z-ac101c6b/
- **hosted_at**: 2026-06-20T04:47:50Z
- **disclaimer**: Live inject from factory repository · same schema as weekly export bundle
- **valid_yes_total**: 1000
- **aeg_live_url**: https://30351aca.sourcea-com.pages.dev/sourcea/proof/live.html
