# SourceA production at sourcea.app

[SourceA](https://sourcea.app/) is published by the existing Cloudflare Pages project `sourcea-com`. The `sourcea-app-proxy-v1` Worker routes requests for `sourcea.app` to Pages and the existing API upstreams. The Pages project name is an internal identifier. Verify every release on the public domain.

| Public route | Purpose |
| --- | --- |
| `/` | SourceA Studio homepage, built from `founder-home.html` |
| `/apps` | App Studio |
| `/sourcea/forge/terminal` | Forge Terminal |
| `/start` | Build brief intake |
| `/kernel/` | SourceA kernel |
| `www.sourcea.app` | Redirect to `sourcea.app` |

## Production release

The private [Founder OS release workflow](https://github.com/Noetfield-Systems/sina_founder_os/actions/workflows/sourcea-cloudflare-release.yml) deploys a pinned SourceA revision. Update its SOURCE_SHA to the reviewed SourceA main commit for each new release. The operator builds the site and Pages Functions separately from the credentialed deployment job, reads back the production deployment ID, verifies the public routes and registers the result in [the receipt directory](https://github.com/Noetfield-Systems/sina_founder_os/tree/main/integrations/cloudflare/receipts/sourcea).

The account-owned credential lives in the Founder OS Actions secret CLOUDFLARE_API_TOKEN. The account ID is set in the operator workflow. Use this path for production without copying the central credential into SourceA or Railway. The legacy SourceA-local workflow requires separate credentials if explicitly selected.

[Verified production receipt](https://github.com/Noetfield-Systems/sina_founder_os/blob/main/integrations/cloudflare/receipts/sourcea/46122118918-1.json)
