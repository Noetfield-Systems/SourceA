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

## Production credential

In the Cloudflare account that contains `sourcea-com`, open **Manage Account → Account API Tokens** and create a custom token named `sourcea-app-pages-production`. Set **Account → Cloudflare Pages → Edit** and restrict account resources to the account that contains the project. Copy the Account ID from the Cloudflare dashboard for that same account.

Save both values under **Settings → Environments → production → Environment secrets** in `Noetfield-Systems/SourceA`:

| GitHub Actions secret | Value |
| --- | --- |
| `CLOUDFLARE_API_TOKEN` | The token value shown by Cloudflare when created |
| `CLOUDFLARE_ACCOUNT_ID` | The Cloudflare account ID for the Pages project |

The workflow reads the exact names from the GitHub Actions secrets context. A secret in another repository, an unshared organization secret, or a Railway variable is not available to this workflow. If there is already a working token, use it in the same production secret. Keep any recovery copy in the owner's password manager under `SourceA / Cloudflare Pages / production`. Record only the token label, scope, destination and rotation date in documentation. Never place values in repo files, chat or logs.

From an authenticated GitHub CLI, these commands prompt for the values without putting them in command arguments:

```bash
gh secret set CLOUDFLARE_API_TOKEN --repo Noetfield-Systems/SourceA --env production
gh secret set CLOUDFLARE_ACCOUNT_ID --repo Noetfield-Systems/SourceA --env production
gh secret list --repo Noetfield-Systems/SourceA --env production
```

## Publish and verify

Run [deploy-sourcea-buyer-surfaces-v1](https://github.com/Noetfield-Systems/SourceA/actions/workflows/deploy-sourcea-buyer-surfaces-v1.yml) on `main` or retry the latest production attempt after saving the secrets. The workflow stages the current build and uploads it to `sourcea-com`. Keep the existing DNS and Worker routes in place for routine Pages releases.

Verify the new homepage content at `https://sourcea.app/`, the actual App Studio content at `/apps`, Forge Terminal, and the intake page. A status of HTTP 200 can be the old homepage returned as a fallback, so compare the content and stylesheet type as well. If the workflow fails at the token step, inspect repository, organization and production-environment secret names and access before replacing credentials.

Official references: [Cloudflare Pages CI setup](https://developers.cloudflare.com/pages/how-to/use-direct-upload-with-continuous-integration/) and [GitHub Actions secrets](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets).
