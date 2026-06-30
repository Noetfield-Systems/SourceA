---
updated: 2026-06-30T11:15:38Z
lane: core
source_path: sites/SourceA-landing/green-unified/data/ui-upgrade-baseline-v1.json
public: true
kind: json
---

# Ui Upgrade Baseline V1

- **schema**: sourcea-ui-upgrade-baseline-v1
- **version**: 1.0.0
- **at**: 2026-06-18T00:10:24Z
- **authority**: SOURCEA_UI_UPGRADE_NO_DOWNGRADE_LOCKED_v1.md
- **e2e_receipt**: validate-sourcea-landing-e2e-v1.sh PASS · run-recipe --e2e
- **root**: SourceA-landing/green-unified
## files
### index.html
#### must_contain
- sa-buyer-toggle
- sa-chain-beats
- sa-mock-panel
- id="sa-agent-pill-text"
- sa-factory-pass-chip
- data-trust-valid-yes
- data-trust-receipts-lifetime
- Close clients with live proof
- /sourcea/proof/live
- sourcea-trust-bar.js
- sourcea-live-console.js
- id="case-studies"
- sourcea-products.js
#### min_count
- **sa-chain-beat**: 6
### proof.html
#### must_contain
- sa-chain-beats
- data-trust-valid-yes
- data-trust-receipts-lifetime
#### min_count
- **sa-chain-beat**: 6
### platform.html
#### must_contain
- sa-buyer-chip
- data-trust-valid-yes
- data-trust-receipts-lifetime
- id="sa-products-grid"
- data-mode="full"
- sourcea-products.js
### offer.html
#### must_contain
- sourcea-chatbot.js
- case-studies/pureflow
- case-studies/agentgo
- data-mode="case-studies"
### case-studies/index.html
#### must_contain
- id="case-studies-grid"
- data-mode="case-studies"
- sourcea-chatbot.js
- sourcea-products.js
### sourcea-chatbot.js
#### must_contain
- sa-brain-composer
- sa-brain-input
- sa-brain-offline
- openrouter
### security.html
#### must_contain
- data-trust-valid-yes
- data-trust-receipts-lifetime
- data-sa-trust-bar
### status.html
#### must_contain
- data-trust-valid-yes
- data-trust-receipts-lifetime
- data-sa-trust-bar
### sourcea-trust-bar.js
#### must_contain
- paintFactoryChip
- dataset.saLive
- valid yes
### sourcea-live-console.js
#### must_contain
- Factory pass
- valid yes
- dataset.saLive
### sourcea-motion.js
#### must_contain
- sa-factory-pass-chip
- dataset.saLive
### sourcea.css
#### must_contain
- sa-buyer-toggle
- sa-chain-beats
- sa-mock-panel
- sa-hero-stats-row
- sa-brain-composer
- sa-products-grid
