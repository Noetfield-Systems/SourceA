# L0 Repo Graph Report — sina-governance-ssot

Generated (last indexed): `2026-07-09T06:47:58Z`
Total files: 28061 · Total size: 432.0MB · Edges detected: 86974

**Read this file first.** Do not spawn broad repo-reading agents ("understand the repo", "map subsystem X", "audit Y") until you have read this report and, if you need more detail, queried the index with `python3 scripts/query_repo_graph_v1.py <subsystem-or-keyword>`. This report + a query response should answer routing questions ("which files touch X", "how big is subsystem Y") without opening every file in the subsystem.

## Subsystem map (sorted by size, descending)

| subsystem | files | size | largest files |
|---|---:|---:|---|
| brand/ | 565 | 99.8MB | `brand/icons/icns/sina-command.icns`, `brand/icons/icns/sina-status.icns`, `brand/icons/icns/sina-decide.icns`, `brand/icons/icns/sina-apple-health.icns`, `brand/macos-apps/Apple Health.app/Contents/Resources/AppIcon.icns`, `brand/icons/icns/sina-dispatch.icns` |
| witnessbc-site/ | 1107 | 67.4MB | `witnessbc-site/assets/w1-demo.mp4`, `witnessbc-site/assets/witnessbc-commercial.mp4`, `witnessbc-site/os/plan-library/witnessbc--1000/REGISTRY.json`, `witnessbc-site/assets/styles.css`, `witnessbc-site/proof.html`, `witnessbc-site/toolkits.html` |
| commercial-video-factory/ | 935 | 45.5MB | `commercial-video-factory/sourcea-commercial-66s-hf-v1/renders/SourceA-Commercial-66s-v1.mp4`, `commercial-video-factory/public/broll/w1-proof.mp4`, `commercial-video-factory/sourcea-commercial-hf-v1/renders/sourcea-commercial-v1.mp4`, `commercial-video-factory/sourcea-commercial-66s-hf-v1/renders/SourceA-Commercial-Fast-23s-v1.mp4`, `commercial-video-factory/sourcea-commercial-hf-v1/renders/sourcea-sting-v1.mp4`, `commercial-video-factory/sourcea-commercial-66s-hf-v1/assets/sourcea-hero-scroll.png` |
| brain-os/ | 19604 | 45.0MB | `brain-os/plan-registry/agentgo-case-study-6000/cs-a-factory/REGISTRY.json`, `brain-os/plan-registry/agentgo-case-study-6000/cs-b-dual/REGISTRY.json`, `brain-os/plan-registry/agentgo-case-study-6000/cs-c-wil/REGISTRY.json`, `brain-os/ssot/superseded/Source-A-SSOT-v1.2.pdf`, `brain-os/plan-registry/sourcea--1000/REGISTRY.json`, `brain-os/ssot/superseded/Source-A-SSOT-v1.1.pdf` |
| data/ | 649 | 43.5MB | `data/all-remaining-plan-backlog-v1.json`, `data/secondary-cloud-forge-run-batch-72-locked-v1.json`, `data/secondary-cloud-forge-run-batch-71-locked-v1.json`, `data/newmatch-factory-999-plan-v1.json`, `data/secondary-cloud-forge-run-batch-75-locked-v1.json`, `data/chatbot-knowledge/brain_knowledge_v1.sqlite` |
| archive/ | 48 | 27.4MB | `archive/sourcea-cleanup-snapshot-20260628/files.tar.gz`, `archive/attachments/commercial/witnessbc-site-proof-v1.html`, `archive/sourcea-cleanup-snapshot-20260628/manifest.json`, `archive/attachments/commercial/witnessbc-site-v1.html`, `archive/attachments/commercial/witnessbc-site-pricing-v1.html`, `archive/attachments/commercial/witnessbc-site-faq-v1.html` |
| infra/ | 58 | 26.1MB | `infra/cleanup/secret-scan-report.txt`, `infra/cleanup/cleanup-manifest.md`, `infra/cleanup/batch-5a-grep-audit.json`, `infra/cleanup/batch-5f-manifest-rows.md`, `infra/cleanup/batch-6-preflight-audit.json`, `infra/cleanup/batch-5e-manifest-rows.md` |
| agent-control-panel/ | 21 | 25.6MB | `agent-control-panel/command-data.json`, `agent-control-panel/command-data-canonical.json`, `agent-control-panel/command-data-runtime.json`, `agent-control-panel/command-data-shell.json`, `agent-control-panel/worker-hub/index.html`, `agent-control-panel/worker-hub/boot.json` |
| sites/ | 222 | 23.2MB | `sites/SourceA-landing/green-unified/assets/commercial-short-demo.mp4`, `sites/SourceA-landing/green-unified/assets/w1-demo-ingest.mp4`, `sites/SourceA-landing/green-unified/assets/w1-demo.mp4`, `sites/SourceA-landing/green-unified/downloads/chat-unify-mac-v1.dmg`, `sites/SourceA-landing/green-unified/sourcea.css`, `sites/SourceA-landing/green-unified/unify/terminal/terminal.js` |
| scripts/ | 2587 | 18.9MB | `scripts/.tools/actionlint`, `scripts/sina_command_lib.py`, `scripts/system_roadmap.py`, `scripts/chat-unify-standalone/terminal/terminal.js`, `scripts/sina-command-server.py`, `scripts/commercial_short_film_v1.py` |
| docs/ | 255 | 3.0MB | `docs/Source-A-Cloud-Kernel-v1.3.pdf`, `docs/FORGE_TERMINAL_BEST_UI_v1.4.0_REFERENCE_SCREENSHOT.png`, `docs/_archive/docx/FORGE_TERMINAL_BEST_UI_LOCKED_v1.4.0.docx`, `docs/SOURCEA_1000_STEP_MASTER_UPGRADE_PLAN15JUNE_LOCKED_v1.md`, `docs/PORTFOLIO_100_COMPARABLES_MARKET_REALITY_v1.md`, `docs/archive/superseded-law-v1/brain-os/law/SOURCEA_BLUEPRINT_COMPARISON_POSTMORTEM_v1.md` |
| receipts/ | 1311 | 2.1MB | `receipts/packs/forge-bay/run-receipt-v1.zip`, `receipts/forge_v0.1_output.json`, `receipts/forge_v0.2/forge_v0.2_run.json`, `receipts/packs/forge-bay/pack-receipt-v1.json`, `receipts/partners/wil_ai_design_partner/design-partner-receipt-v1.zip`, `receipts/partners/trustfield/design-partner-receipt-v1.zip` |
| apps/ | 118 | 953.7KB | `apps/forge-terminal-connect-v1/terminal/terminal.js`, `apps/forge-terminal-v1/terminal.js`, `apps/forge-terminal-connect-v1/app.js`, `apps/forge-terminal-connect-v1/terminal/terminal.css`, `apps/forge-terminal-v1/terminal.css`, `apps/forge-terminal-connect-v1/index.html` |
| imports/ | 4 | 950.3KB | `imports/iphone-cloud/iphone-cloud-manifest-20260604.jsonl`, `imports/iphone-cloud/iphone-cloud-inventory-20260604.csv`, `imports/iphone-cloud/777-consolidate-report.json`, `imports/iphone-cloud/iphone-cloud-move-report.txt` |
| cloud/ | 66 | 833.0KB | `cloud/workers/sourcea-brain-chat-v1/src/knowledge-bundle.json`, `cloud/sync-inbox/fbe_bay_events.jsonl`, `cloud/seed/federated-run-v1.json`, `cloud/workers/sourcea-brain-chat-v1/src/index.js`, `cloud/workers/sourcea-brain-chat-v1/src/retrieval.js`, `cloud/workers/sourcea-brain-chat-v1/src/guardrails.js` |
| investor/ | 22 | 268.7KB | `investor/CONNECTOR_BRIEF.pdf`, `investor/TRUSTFIELD_VC_TRUST_LEGAL_ANTI_MORTEM_v1.md`, `investor/AGENTIC_INFRA_FUNDRAISE_PORTFOLIO_STRATEGY_v1.md`, `investor/WHITEPAPER.md`, `investor/PITCH_DECK_SPEAKER_SCRIPT_FA.md`, `investor/PITCH_DECK_SPEAKER_SCRIPT_EN.md` |
| reports/ | 24 | 240.0KB | `reports/sourcea-website-ui-e2e-audit-v1.json`, `reports/locked-definitions-v1.json`, `reports/sourcea-contract-domains-acquisition-buyer-analysis-july-2026-v1.md`, `reports/chat_eval_last_run.json`, `reports/sanitizer-enforcement-v1-tests.md`, `reports/decision-core-v1-tests.md` |
| architecture_audit/ | 14 | 194.4KB | `architecture_audit/DEPENDENCY_GRAPH.svg`, `architecture_audit/DEPENDENCY_GRAPH.png`, `architecture_audit/API_MAP.md`, `architecture_audit/REBUILD_TRIGGER_MAP.md`, `architecture_audit/STATE_MAP.md`, `architecture_audit/ARCHITECTURE_ENTRYPOINTS.md` |
| packages/ | 56 | 183.8KB | `packages/mcp-sourcea-verify/package-lock.json`, `packages/sourcea-boot/.publish-export/src/sourcea_boot/checks.py`, `packages/sourcea-boot/src/sourcea_boot/checks.py`, `packages/sourcea-sdk/src/sourcea_sdk/workflow_health.py`, `packages/mcp-sourcea-verify/src/tools.ts`, `packages/sourcea-sdk/src/sourcea_sdk/receipt.py` |
| runtime/ | 6 | 153.9KB | `runtime/architect_reports/2026-06-02.yaml`, `runtime/architect_reports/2026-06-03.yaml`, `runtime/architect_reports/2026-06-04.yaml`, `runtime/architect_reports/2026-06-06.yaml`, `runtime/architect_reports/2026-06-05.yaml`, `runtime/architect_reports/2026-06-12.yaml` |
| os/ | 11 | 93.6KB | `os/commercial/CANADA_PRIORITY_A_SEND_READY_EMAILS_LOCKED_v1.md`, `os/commercial/CANADA_PRIORITY_A_SEND_READY_EMAILS_v1.md`, `os/commercial/CANADA_RWA_STRATEGY_DEEP_RESEARCH_UPGRADE_LOCKED_v2.md`, `os/commercial/SOURCEA_STACK_MAP_AND_BETTER_LOOP_LOCKED_v1.md`, `os/commercial/CANADA_RWA_NAMED_ACCOUNT_TARGET_LIST_LOCKED_v1.md`, `os/commercial/SOURCEA_ECOSYSTEM_FAST_BUSINESS_MODEL_LOCKED_v2.md` |
| product/ | 16 | 80.9KB | `product/PHASE1_MARKET_RESEARCH_2026.md`, `product/MERGEPACK_BUSINESS_DEFENSE_MEMO.md`, `product/PHASE2_3_EVALUATION_AND_WINNER.md`, `product/SINA_AUDIENCE_HUB_FREE_TIER_SPEC.md`, `product/EVIDENCE_FLYWHEEL_LOCKED_v1.md`, `product/PHASE1_OPPORTUNITIES_AND_30_RAW_IDEAS.md` |
| plans/ | 101 | 76.1KB | `plans/CLOUD-SEC-006.json`, `plans/CLOUD-SEC-043.json`, `plans/CLOUD-SEC-056.json`, `plans/CLOUD-SEC-001.json`, `plans/CLOUD-SEC-044.json`, `plans/CLOUD-SEC-003.json` |
| sina-bowl/ | 6 | 74.8KB | `sina-bowl/state.json`, `sina-bowl/MASTER_ORDERS.json`, `sina-bowl/DAILY_BOWL.md`, `sina-bowl/brief.fa.txt`, `sina-bowl/brief.txt`, `sina-bowl/DRIFT.json` |
| labs/ | 15 | 64.9KB | `labs/virelux-pilot/.sourcea/tasks.db`, `labs/forge-v0.1/forge_v01_engine.ts`, `labs/forge-v0.1/mock_cloud_plans.ts`, `labs/forge-v0.1/runner.ts`, `labs/virlux/README.md`, `labs/forge-v0.1/real_cloud_stream.ts` |
| founder/ | 24 | 57.3KB | `founder/repo-agent-notices/AGENT_READ_LINKS_INDEX.md`, `founder/NOETFIELD_CLOUD_FINAL_ACKNOWLEDGE_PROMPT_v1.md`, `founder/repo-agent-notices/manifest.json`, `founder/README.md`, `founder/ASF_FOUNDER_FAQ.md`, `founder/repo-agent-notices/SEMI_NOTICE_noetfield_cloud_v1.md` |
| knowledge-library/ | 25 | 53.1KB | `knowledge-library/fields/pre-llm-world-model/01-extracts/MANIFEST.md`, `knowledge-library/fields/commercial-governance/02-gathered/GATHER_v1_BLUEPRINT_MARKET_100_PLANS_2026-06-13.md`, `knowledge-library/fields/pre-llm-world-model/04-unified/ESSAY_v1_NO_MODEL_WITHOUT_PACKET.md`, `knowledge-library/KNOWLEDGE_LIBRARY_INDEX.md`, `knowledge-library/fields/pre-llm-world-model/03-merged/MERGE_v1_PRE_LLM_GATE_SYNTHESIS.md`, `knowledge-library/fields/commercial-governance/02-gathered/GATHER_v2_SOURCEA__LANDSCAPE_2026-06-15.md` |
| tests/ | 8 | 44.3KB | `tests/brain_core_v1/fixtures/gate_receipts_v1.json`, `tests/brain_core_v1/test_gate.py`, `tests/brain_core_v1/test_sanitizer.py`, `tests/brain_core_v1/test_live_status_probe.py`, `tests/brain_core_v1/test_d4_enforcement.py`, `tests/brain_core_v1/test_decision_core.py` |
| agent-skills/ | 24 | 43.7KB | `agent-skills/sourcea_worker/SKILL.md`, `agent-skills/REGISTRY_LOCKED_v1.json`, `agent-skills/shared/conscious-recovery/SKILL.md`, `agent-skills/shared/s10-eternal-self-heal/SKILL.md`, `agent-skills/sinaai_maintainer/SKILL.md`, `agent-skills/shared/narrative-translator/SKILL.md` |
| n8n/ | 25 | 34.8KB | `n8n/workflows/sinaai-stack-health-ping.json`, `n8n/workflows/wf-cloud-auto-runtime-v1.json`, `n8n/workflows/wf-openrouter-governance-hook-v1.json`, `n8n/workflows/wf-governance-fast-15m-v1.json`, `n8n/workflows/wf-agent-scoreboard-sync-v1.json`, `n8n/workflows/wf-backup-receipt-archiver-v1.json` |
| cinematic-film-factory/ | 10 | 33.0KB | `cinematic-film-factory/compiler.py`, `cinematic-film-factory/capture.py`, `cinematic-film-factory/assemble.py`, `cinematic-film-factory/film_memory.py`, `cinematic-film-factory/captions.py`, `cinematic-film-factory/build.sh` |
| .github/ | 14 | 28.8KB | `.github/workflows/external-verify.yml`, `.github/workflows/deploy-sourcea-buyer-surfaces-v1.yml`, `.github/workflows/validate.yml`, `.github/workflows/determinism-gate.yml`, `.github/workflows/repo-policy-gate.yml`, `.github/workflows/autonomous-drain-cron-v1.yml` |
| shared/ | 19 | 20.6KB | `shared/types/execution-contract-v1.ts`, `shared/database/migrations/006_mac_spine_bridge_v1.sql`, `shared/database/migrations/008_identity_profiles_venture_rls_v1.sql`, `shared/auth-core/src/middleware.ts`, `shared/database/migrations/002_truth_log_v1.sql`, `shared/database/migrations/001_truth_layer_cycle_receipts_v1.sql` |
| runreceipt/ | 5 | 20.4KB | `runreceipt/out/run.jsonl`, `runreceipt/out/evidence.snapshot.json`, `runreceipt/out/receipt-pack.zip`, `runreceipt/out/receipt.html`, `runreceipt/out/summary.json` |
| agent-pro-v1/ | 5 | 18.7KB | `agent-pro-v1/server.py`, `agent-pro-v1/public/app.js`, `agent-pro-v1/public/style.css`, `agent-pro-v1/README.md`, `agent-pro-v1/public/index.html` |
| founder-light-v1/ | 6 | 18.2KB | `founder-light-v1/scripts/founder_light_server_v1.py`, `founder-light-v1/public/app.js`, `founder-light-v1/public/style.css`, `founder-light-v1/public/index.html`, `founder-light-v1/README.md`, `founder-light-v1/scripts/run-founder-light-v1.sh` |
| cursor-plugin/ | 10 | 12.8KB | `cursor-plugin/sourcea-forge-governance/MARKETPLACE_LISTING.md`, `cursor-plugin/sourcea-forge-governance/README.md`, `cursor-plugin/sourcea-forge-governance/skills/verify-after-mcp/SKILL.md`, `cursor-plugin/sourcea-forge-governance/skills/governance-receipt-recovery/SKILL.md`, `cursor-plugin/sourcea-forge-governance/plugin-v1.json`, `cursor-plugin/sourcea-forge-governance/rules/receipt-native-governance.mdc` |
| prompts/ | 4 | 11.6KB | `prompts/ENFORCEMENT_6MO_MASTER_CONTROL_PROMPT_v1.md`, `prompts/COMPLEX_SITUATION_FORK_SESSION_PROMPT_LOCKED_v1.md`, `prompts/FIVE_STEP_SESSION_PROMPT_LOCKED_v1.md`, `prompts/SA_SITE_TRUTH_GATE_CLOUD_MISSION_LOCKED_v1.md` |
| demo/ | 11 | 10.5KB | `demo/governance/AEG_PIPELINE_v1.md`, `demo/governance/critic_fixtures_v1.json`, `demo/governance/K1_LOADER_HOOK_ARCHITECTURE_v1.md`, `demo/asset-b/creative-allow.json`, `demo/asset-b/outreach-allow.json`, `demo/asset-b/outreach-block.json` |
| launch/ | 5 | 5.3KB | `launch/com.sourcea.n8n.plist`, `launch/com.sourcea.routing-panel.plist`, `launch/com.sourcea.mac-law.plist`, `launch/com.sourcea.cloud-workers.plist`, `launch/com.sourcea.hub.plist` |
| launchers/ | 7 | 3.2KB | `launchers/EMERGENCY_STOP.app/Contents/MacOS/emergency-stop`, `launchers/SourceA Dashboard.command`, `launchers/SourceA Dashboard.app/Contents/Info.plist`, `launchers/EMERGENCY_STOP.app/Contents/Info.plist`, `launchers/Portfolio Mail.command`, `launchers/SourceA Dashboard.app/Contents/MacOS/launcher` |
| config/ | 3 | 2.5KB | `config/stranger-agent-safety-v1.default.json`, `config/stranger-agent-external-tokens-v1.default.json`, `config/aeg-config-v1.example.json` |
| templates/ | 7 | 1.9KB | `templates/sourcea-workspace-v2/agents.yaml`, `templates/sourcea-workspace-v2/project.yaml`, `templates/sourcea-workspace-v2/policies.yaml`, `templates/sourcea-workspace-v2/agents/builder.yaml`, `templates/sourcea-workspace-v2/agents/planner.yaml`, `templates/sourcea-workspace-v2/models.yaml` |
| internal/ | 1 | 864B | `internal/agent-reference/GOVERNANCE_DRIFT_DETECTION_ESSAY_2026.md` |
| entry/ | 2 | 749B | `entry/README.md`, `entry/MOVED.md` |
| internal-reference/ | 1 | 506B | `internal-reference/GOVERNANCE_DRIFT_DETECTION_INSIGHT_ESSAY_v1.md` |
| (root files) | 24 | 128.1KB | `PROGRAM_PROGRESS.json`, `PORT_REGISTRY.json`, `monitor.html`, `FEEDBACK_AGGREGATE.json`, `EXECUTION_TRUTH.json`, `PORT_CATALOG.json` |

## Dependency / reference edges

86974 static repo-relative path references were detected across .py/.sh/.md/.json/.yaml/.yml/.jsonc files (best-effort regex scan, not a real import graph — this is a governance/docs-heavy repo, not a single-language codebase). Full edge list is in `graph_index_v1.json`; query by file or subsystem with the query script rather than reading it directly.

## Ignored directories

`.cache`, `.git`, `.noos_cache`, `.pytest_cache`, `.venv`, `.wrangler`, `__pycache__`, `build`, `dist`, `graph-out`, `node_modules`, `venv`

## Query command

```
python3 scripts/query_repo_graph_v1.py <subsystem-name|keyword|path-fragment>
```

## Rebuild command

```
python3 scripts/build_repo_graph_v1.py
```

Rebuild whenever the file layout changes materially (new subsystem, large doc/data additions) — this report drifts from truth otherwise. See `docs/L0_REPO_GRAPH_MEMORY_v1.md` for the token budget rule and the broad-read prevention rule.
