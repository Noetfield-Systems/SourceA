# DEPRECATED — nerve probes moved to SourceA loop-specialist

**Do not deploy this worker.**

Nerve probes (`nf_intake_e2e`, greeting, drift, uptime) piggyback on:

- `cloud/workers/loop-specialist-tick-v1` · `runNerveProbeCycle`
- SSOT: `data/nerve-probe-cloud-cron-v1.json`
- Deploy: `bash scripts/deploy_nerve_probe_24_7_v1.sh`
