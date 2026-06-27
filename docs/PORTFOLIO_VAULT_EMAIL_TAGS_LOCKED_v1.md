# Portfolio vault email tags — LOCKED v1

**Version:** 1.1.0 · **Saved:** 2026-06-21T05:06:59Z · **Authority:** ASF SAVE TO  
**Path:** `docs/PORTFOLIO_VAULT_EMAIL_TAGS_LOCKED_v1.md`  
**Machine SSOT:** `data/portfolio-vault-email-tags-v1.json`  
**Parent:** `docs/PORTFOLIO_ACCOUNT_STRUCTURE_LOCKED_v1.md` · `data/portfolio-account-structure-v1.json`

---

## One law

> **Three licensed mailboxes per domain · one app password tag per mailbox · one brand lane.**  
> Tag every mailbox in `~/.sina/secrets.env`. Never mix WitnessBC tokens into TrustField send scripts.

Values stay in the vault only — never in git.

---

## Tag pattern

```text
{BRAND}-{LOCALPART}-GOOGLE_WORKSPACE_APP_PASSWORD=<16 chars, no spaces>
```

- **BRAND** = `TF` · `NF` · `SA` · `VL` · `WBC`  
- **LOCALPART** = mailbox user name (`HELLO` · `CONTACT` · `OPERATIONS` · `OPERATION` · `PROOF` · `SUPPORT`)  
- **One tag per mailbox** — if three users on a domain, three tags (three app passwords in Google Admin).

---

## Three mailboxes per domain (15 tags total)

### trustfield.ca — TrustField (`TF`)

| Vault tag | Address | Role | Agent / script |
|-----------|---------|------|----------------|
| `TF-HELLO-GOOGLE_WORKSPACE_APP_PASSWORD` | `hello@trustfield.ca` | **Greet / outbound** | `agentic_msb_wave_send.sh` · MSB wave · `--lane TF` |
| `TF-CONTACT-GOOGLE_WORKSPACE_APP_PASSWORD` | `contact@trustfield.ca` | **Intake / inbound** | Receive tests · form reply · `founder_email_deliver.sh` |
| `TF-OPERATIONS-GOOGLE_WORKSPACE_APP_PASSWORD` | `operations@trustfield.ca` | **Ops / regulated** | Ops routing · alternate intake |

### noetfield.com — Noetfield (`NF`)

| Vault tag | Address | Role | Agent / script |
|-----------|---------|------|----------------|
| `NF-HELLO-GOOGLE_WORKSPACE_APP_PASSWORD` | `hello@noetfield.com` | **Greet / commercial** | Canada priority copy · brand line |
| `NF-OPERATIONS-GOOGLE_WORKSPACE_APP_PASSWORD` | `operations@noetfield.com` | **Intake / inbound** | Form delivery · Resend `INTAKE_EMAIL_TO` |
| `NF-OPERATION-GOOGLE_WORKSPACE_APP_PASSWORD` | `operation@noetfield.com` | **Outbound / compliance** | `commercial_mail_draft_v1.py --lane NF` · NW1 · W3 |

### sourcea.app — SourceA (`SA`)

| Vault tag | Address | Role | Agent / script |
|-----------|---------|------|----------------|
| `SA-HELLO-GOOGLE_WORKSPACE_APP_PASSWORD` | `hello@sourcea.app` | **Greet / outbound** | `send_ab1_single_v1.py` · `--lane AB1` |
| `SA-CONTACT-GOOGLE_WORKSPACE_APP_PASSWORD` | `contact@sourcea.app` | **Intake / inbound** | MVP intake · general contact |
| `SA-PROOF-GOOGLE_WORKSPACE_APP_PASSWORD` | `proof@sourcea.app` | **Proof / demo** | Proof-demo booking · procurement |
| `SA-FORGE-GOOGLE_WORKSPACE_APP_PASSWORD` | `forge@sourcea.app` | **Prompt Forge** | Mission prompts · `/sourcea/forge/` product lane |

**Note:** SourceA uses **four** licensed mailboxes on `sourcea.app` (product lane adds Forge). Signature URL: **https://sourcea.app** only.

### virlux.com — VIRLUX (`VL`)

| Vault tag | Address | Role | Agent / script |
|-----------|---------|------|----------------|
| `VL-HELLO-GOOGLE_WORKSPACE_APP_PASSWORD` | `hello@virlux.com` | **Greet / product** | Product contact |
| `VL-CONTACT-GOOGLE_WORKSPACE_APP_PASSWORD` | `contact@virlux.com` | **Intake / inbound** | General inbound |
| `VL-SUPPORT-GOOGLE_WORKSPACE_APP_PASSWORD` | `support@virlux.com` | **Support** | Customer support lane |

### witnessbc.com — WitnessBC (`WBC`) — isolated lane

| Vault tag | Address | Role | Agent / script |
|-----------|---------|------|----------------|
| `WBC-HELLO-GOOGLE_WORKSPACE_APP_PASSWORD` | `hello@witnessbc.com` | **Greet / support** | Toolkit support · site mailto |
| `WBC-PROOF-GOOGLE_WORKSPACE_APP_PASSWORD` | `proof@witnessbc.com` | **Proof / demo** | 15-min proof CTA · `cta.json` |
| `WBC-CONTACT-GOOGLE_WORKSPACE_APP_PASSWORD` | `contact@witnessbc.com` | **Intake / inbound** | General contact |

**WitnessBC tags never load into TrustField `GOOGLE_WORKSPACE_APP_PASSWORD`.**

---

## Canonical runtime key (TrustField MSB default only)

| Key | Meaning |
|-----|---------|
| `GOOGLE_WORKSPACE_APP_PASSWORD` | **Active default** for TrustField SMTP — maps to **`hello@trustfield.ca` only** |

**Resolution order** (`load_founder_secrets.sh`):

1. `GOOGLE_WORKSPACE_APP_PASSWORD` if set  
2. Else `TF-HELLO-GOOGLE_WORKSPACE_APP_PASSWORD`  
3. Sets `SMTP_USER=hello@trustfield.ca` · `SMTP_HOST=smtp.gmail.com` · `EMAIL_ENABLED=true`

All other tags export as `{BRAND}_{LOCALPART}_GOOGLE_WORKSPACE_APP_PASSWORD` (underscore env names) for lane-specific scripts — **not** the MSB default.

---

## Export env map (loader)

| Vault tag | Export env |
|-----------|------------|
| `TF-HELLO-*` | `TF_HELLO_GOOGLE_WORKSPACE_APP_PASSWORD` |
| `TF-CONTACT-*` | `TF_CONTACT_GOOGLE_WORKSPACE_APP_PASSWORD` |
| `TF-OPERATIONS-*` | `TF_OPERATIONS_GOOGLE_WORKSPACE_APP_PASSWORD` |
| `NF-HELLO-*` | `NF_HELLO_GOOGLE_WORKSPACE_APP_PASSWORD` |
| `NF-OPERATIONS-*` | `NF_OPERATIONS_GOOGLE_WORKSPACE_APP_PASSWORD` |
| `NF-OPERATION-*` | `NF_OPERATION_GOOGLE_WORKSPACE_APP_PASSWORD` |
| `SA-HELLO-*` | `SA_HELLO_GOOGLE_WORKSPACE_APP_PASSWORD` |
| `SA-CONTACT-*` | `SA_CONTACT_GOOGLE_WORKSPACE_APP_PASSWORD` |
| `SA-PROOF-*` | `SA_PROOF_GOOGLE_WORKSPACE_APP_PASSWORD` |
| `SA-FORGE-*` | `SA_FORGE_GOOGLE_WORKSPACE_APP_PASSWORD` |
| `VL-HELLO-*` | `VL_HELLO_GOOGLE_WORKSPACE_APP_PASSWORD` |
| `VL-CONTACT-*` | `VL_CONTACT_GOOGLE_WORKSPACE_APP_PASSWORD` |
| `VL-SUPPORT-*` | `VL_SUPPORT_GOOGLE_WORKSPACE_APP_PASSWORD` |
| `WBC-HELLO-*` | `WBC_HELLO_GOOGLE_WORKSPACE_APP_PASSWORD` |
| `WBC-PROOF-*` | `WBC_PROOF_GOOGLE_WORKSPACE_APP_PASSWORD` |
| `WBC-CONTACT-*` | `WBC_CONTACT_GOOGLE_WORKSPACE_APP_PASSWORD` |

---

## App password rules

1. **16 characters** — Google App Password only (not normal Google password).  
2. **No spaces** — paste without display gaps.  
3. **One password per mailbox user** — three users on a domain = three app passwords in Google Admin.  
4. **2FA ON** on each user before app passwords appear.

---

## Example vault block (partial)

```bash
# TrustField — 3 mailboxes
GOOGLE_WORKSPACE_APP_PASSWORD=xxxxxxxxxxxxxxxx          # canonical = hello@
TF-HELLO-GOOGLE_WORKSPACE_APP_PASSWORD=xxxxxxxxxxxxxxxx
TF-CONTACT-GOOGLE_WORKSPACE_APP_PASSWORD=xxxxxxxxxxxxxxxx
TF-OPERATIONS-GOOGLE_WORKSPACE_APP_PASSWORD=xxxxxxxxxxxxxxxx

# Noetfield — 3 mailboxes
NF-HELLO-GOOGLE_WORKSPACE_APP_PASSWORD=xxxxxxxxxxxxxxxx
NF-OPERATIONS-GOOGLE_WORKSPACE_APP_PASSWORD=xxxxxxxxxxxxxxxx
NF-OPERATION-GOOGLE_WORKSPACE_APP_PASSWORD=xxxxxxxxxxxxxxxx

# SourceA · VIRLUX · WitnessBC — add all three per domain when ready
```

---

## Verify (TrustField hello@)

```bash
cd ~/Desktop/TrustField\ Technologies
./scripts/trustfield_google_workspace_outbound_probe.sh   # expect OK: sent
./scripts/trustfield_inbox_check_v1.sh --domain trustfield.ca
./scripts/agentic_msb_wave_send.sh 15                       # live MSB uses hello@ only
```

All 15 portfolio inboxes: `./scripts/trustfield_inbox_check_v1.sh` (TrustField repo)

**Portfolio Mail Hub (UI):** `http://127.0.0.1:13020/mail-hub/` · API `GET/POST /api/portfolio-mail/v1`

---

## Related

| Artifact | Role |
|----------|------|
| `data/portfolio-vault-email-tags-v1.json` | Machine SSOT · all 15 tags |
| `TrustField Technologies/docs/GOOGLE_WORKSPACE_APP_PASSWORD_SETUP.md` | App password creation |
| `scripts/commercial_mail_draft_v1.py` | Lane → FROM map |
| `data/commercial-mail-from-gate-v1.json` | Mail.app FROM gate |
