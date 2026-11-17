# WITNESS · Web3 Genesis

**Live venture thesis:** independent Web3-native AI Governance Builders Community. This fully replaces the former institutional governance-services website, corporate outreach, and Stripe toolkit sales as the Witness public product.

## Product
- `/` — Web3-native community portal, real Genesis CTA and founding quests
- `/genesis` — external authenticated Community Economy pilot (wallet optional)
- `/quests` — three reviewed founding quests: 80, 150, 100 XP
- `/guild` — builders guild lanes
- `/arena` — interactive **illustrative local** AI policy decisions; never labelled a real chain receipt
- `/reputation` — actual CE account-private member history and reviewed XP
- `/governance` — proposals and progressive governance
- `/economy` — optional onchain reputation, useful economic primitives, no token sale
- `/builders` — independent BuildRelay builder matching
- `/manifesto` — immutable community-first doctrine

**Community truth:** Founder activation pending. The CE pilot is a blueprint until an authorized real founder publishes. No fake members, votes, earned XP, token or treasury funding.

## Source
`web3/pages/*.html` are the public product pages; `web3/assets` holds custom UI, interactions and identity. `config/VENTURE_IDENTITY.json` is the machine-readable anti-drift law. `scripts/build-web3.mjs` stages **only** those files into `dist/deploy`. Prior institutional page sources remain in Git history/working tree solely as legacy archive and are **excluded** from public output.

## Build
```bash
cd witnessbc-site
node scripts/build-web3.mjs
node scripts/verify-web3.mjs
python3 -m http.server 8091 --directory dist/deploy
```

Vercel `vercel.json` uses `node scripts/build-web3.mjs`, clean URLs, and redirects retired corporate pages to appropriate community pages. No generated mirror or retired deployment token is required for direct canonical SourceA deployments.

## Operating boundary
- Witness is independent of Noetfield, 777 Foundation, ARQANT, Cairn and BuildRelay. Shared infrastructure does not grant representation rights.
- No outward mail, external corporate identity, official institutional outreach or checkout links are allowed by default. Never use `operations@noetfield.com` or another Noetfield corporate sender to represent Witness.
- Web3 community growth via public Genesis, Web3 social sharing, member referrals, GitHub/DAO/developer circles and genuine contribution.
- A CE authenticated member (not this static site) owns submissions. Human approval creates nontransferable XP once; meaningful referral activation follows contributed work.
- Funding, bounties and token/treasury are future or optional until actual authenticated, source-linked and settled proof is obtained.
- All Witness agents must read both `config/VENTURE_IDENTITY.json` and `COMMUNITY-ECONOMY/docs/AGENT-MANDATE-WITNESS.md`. The Web3 thesis overrides historic "preserve corporate pricing and Stripe" text.

## Validation
New `scripts/verify-web3.mjs` and CI enforce the Web3 page allowlist, the lack of Stripe/Noetfield corporate public leakage, three real blueprint quest values, working Genesis navigation, multi-viewport browser readback and source/deployment integrity. Live Vercel status alone is not proof of public content.
