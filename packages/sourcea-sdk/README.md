# sourcea-sdk

Governance receipt spine for agent actions **after** `sourcea-boot` PASS.

## Install (monorepo dev)

```bash
pip install -e packages/sourcea-sdk
```

PyPI publish is **not live** — do not claim `pip install sourcea-sdk` on public surfaces until published.

## Quick start

```bash
sourcea-boot --json   # PASS required first

sourcea-sdk sign --intent '{"intent_id":"demo","agent_id":"dev","object_id":"demo-1"}'
sourcea-sdk replay --last
sourcea-sdk spine-tail --n 5
```

Portable mode writes under `.sourcea/` in the current working directory.
