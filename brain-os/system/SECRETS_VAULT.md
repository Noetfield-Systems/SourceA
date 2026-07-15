# Sina Secret Vault (one place)

**Master file:** `~/.sina/secrets.env` (chmod 600)

**MergePack deploy URLs (public, not keys):** `~/.sina/mergepack.env` (chmod 600) — `MERGEPACK_API_URL`, `NEXT_PUBLIC_API_URL`, Railway project/service IDs. Load with `source ~/.sina/mergepack.env`. Pointer: `~/Desktop/mergepack/DEPLOY_INFRA.md`.

## Collect once (ASF / Terminal)

```bash
cd ~/Desktop/SinaPromptOS
./scripts/vault-harvest.sh
```

Reads local `.env` files listed in `config/vault_harvest_sources.json` — merges into the vault (never overwrites with empty).

## Status (no values printed)

```bash
./scripts/vault-status.sh
```

## Push vault → repo env files

```bash
./scripts/vault-sync-all.sh
```

Targets: `config/vault_map.json` (TrustField `.env.founder`, SinaaiRuntime, VIRLUX, …)

## Voyage AI embeddings (P05 · COMM-PARTNER-BOOT) — **CONFIGURED**

**Status:** `VOYAGE_API_KEY` set in vault · `EMBEDDING_PROVIDER=voyage` · **629 chunks** re-indexed (`voyage-reindex-p05` · 2026-06-15) · `semantic:true` · **P05 done** · next: **P03 NVIDIA Inception**.

**Vault slots (do not re-paste if already set):**

```bash
VOYAGE_API_KEY=          # configured — https://dash.voyageai.com/
EMBEDDING_PROVIDER=voyage
VOYAGE_MODEL=voyage-4-lite
```

**Proof:** `cd ~/Desktop/SourceA && python3 -c "import sys; sys.path.insert(0,'scripts'); from pre_llm.vector_retrieval.embedding_provider import provider_payload; print(provider_payload())"`

**Hub:** Sina Command → **Safety** · **Actions → Open secret vault** (edit only if rotating key — never paste in chat).

## Still manual (not logged anywhere)

- **TrustField (free):** `CF_API_TOKEN`, `CF_ZONE_ID` only — **no** `RENDER_API_KEY` if card required. Then `vault-sync-all.sh` + `founder_free_auto.sh`. Rule: `FOUNDER_NO_CREDIT_CARD_INFRA_LOCKED_v1.md`

Never paste keys into Cursor chat. Never commit the vault.
