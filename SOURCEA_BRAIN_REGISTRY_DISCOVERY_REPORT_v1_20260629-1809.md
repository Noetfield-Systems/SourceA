# SOURCEA_BRAIN_REGISTRY_DISCOVERY_REPORT_v1_20260629-1809

## Existing Assets Found

- asset_id: source_state_origin_main_sync
  asset_type: crawl_truth_state
  current_location: git object tree `origin/main`; sync command `git pull origin main`
  status: `origin/main` reported already up to date; local checkout branch was `fix/cloud-drain-queue-head-rewind`, so reconnaissance read Git main tree objects and avoided local dirty state as code truth.
  owning_layer: BOOT
  mutation_class: LOCKED
  last_modified: 2026-06-29
  dependents: all inventory rows in this report; R1/R2 crawl-truth requirement; needs explicit registry field for source revision/hash in Task 1.

- asset_id: strategy_ssot_v6_split
  asset_type: vocabulary_ssot
  current_location: `/Users/sinakazemnezhad/Downloads/strategy-ssot-v6-split (1).md`
  status: Loaded as Level 0 plus D1-D5 vocabulary layer. Defines SSOT, layer, receipt, verified, gate, and eval framing for this report. Not present in `origin/main` under exact requested filename.
  owning_layer: CONSTITUTION
  mutation_class: LOCKED
  last_modified: unknown_external_download
  dependents: brain registry vocabulary normalization; D4 author-separation receipt rules; needs repo registry pointer or founder review because source path is outside Git main.

- asset_id: d4_portable_runtime_rules_r1_r2_r6_r7
  asset_type: vocabulary_runtime_rule_source
  current_location: prompt text plus partial matches in repo; exact standalone source not found by narrow search
  status: R1/R2 crawl rule applied from prompt (`git pull origin main`, Git main only). R6/R7 standalone D4-portable source was not found. Treat as layer_unknown until founder points to canonical file.
  owning_layer: layer_unknown
  mutation_class: GATED
  last_modified: unknown
  dependents: registry language conformance; needs registry entry only after founder confirms canonical source.

- asset_id: brain_os_law_plane
  asset_type: ssot_library
  current_location: `brain-os/law/`, `brain-os/laws/`, `brain-os/system/`, `brain-os/runtime/`
  status: Existing locked law and system source library, including runtime stack, dispatch policy, receipt index, authority maps, and governance rules. Needs normalized registry rows per asset or grouped namespace.
  owning_layer: CONSTITUTION
  mutation_class: LOCKED
  last_modified: 2026-06-19 to 2026-06-20
  dependents: Cursor rules, Brain rules, dispatch policy, eval gates, receipt hierarchy, RAG source selection.

- asset_id: cursor_rule_plane
  asset_type: agent_rule_library
  current_location: `.cursor/rules/`, `brain-os/cursor/rules/`
  status: Existing rule surface for Brain/Worker behavior, Mac control plane, anti-staleness, founder intent, and cost routing. No single brain registry row set with owning_layer/mutation_class/dependency fields.
  owning_layer: AGENT
  mutation_class: GATED
  last_modified: 2026-06-19 to 2026-06-22
  dependents: session gate, agent behavior, prompt routing, Mac safety receipts, worker inbox routing.

- asset_id: brain_memory_library
  asset_type: memory_store
  current_location: `brain-os/memory/`
  status: Existing locked memory and knowledge indexes (`BRAIN_MASTER_MEMORY`, `BRAIN_KNOWLEDGE_INDEX`, `BRAIN_RESEARCH_LIBRARY`, founder intent registry). Needs freshness and dependency fields for RAG use.
  owning_layer: SSOT_RAG
  mutation_class: LOCKED
  last_modified: 2026-06-19
  dependents: Brain answers, public chatbot corpus, knowledge bundle generation, founder intent routing.

- asset_id: brain_chat_knowledge_bundle
  asset_type: rag_bundle
  current_location: `data/brain-chat-knowledge-bundle-v1.json`; `cloud/workers/sourcea-brain-chat-v1/src/knowledge-bundle.json`
  status: Existing generated Brain public knowledge bundle with chunk metadata and retrieval mode. Needs registry linkage to source files, evals, and freshness receipts.
  owning_layer: SSOT_RAG
  mutation_class: GATED
  last_modified: 2026-06-27 in worker bundle; local data path observed in repo search
  dependents: public Brain chatbot, RAG retrieval, knowledge parity audits.

- asset_id: sourcea_runtime_stack
  asset_type: brain_module_stack
  current_location: `brain-os/law/SINA_RUNTIME_STACK_LOCKED_v1.md`; `scripts/runtime/`
  status: Existing runtime plan and modules for tool graph, verification, execution router, repair loop, context fabric, planner, orchestrator, dispatch policy. Several modules are code-present but not all are promotion-gated as brain modules.
  owning_layer: ROUTER
  mutation_class: GATED
  last_modified: 2026-06-19 to 2026-06-20
  dependents: execution router, dispatch policy, receipts, future live/sandbox brain split.

- asset_id: prompt_forge_pipeline
  asset_type: prompt_pipeline
  current_location: `scripts/prompt_forge_pipeline_v1.py`; `scripts/chat_unify_prompt_forge_v1.py`; `docs/FORGE_TERMINAL_WORKER_CRITIC_HANDOFF_LOCKED_v1.md`
  status: Existing prompt-forge components with receipt output under `~/.sina/prompt-forge-receipts/`. No discovered brain registry lane row for prompt-forge promotion thresholds.
  owning_layer: AGENT
  mutation_class: GATED
  last_modified: 2026-06-19 to 2026-06-22
  dependents: Forge Terminal, Chat Unify, founder-language-to-bounded-mission flow, future prompt-forge promotion lane.

## Existing Evals Found

- asset_id: phase2_evaluations
  asset_type: eval_registry
  current_location: `data/root-machine/PHASE2_EVALUATIONS.json`; root symlink `PHASE2_EVALUATIONS.json`
  status: Existing rules-mode project evaluation map. PASS/BLOCK equivalent is `evaluation.verdict` (`DONE` or `NOT_DONE`) with confidence/risk/reasons. Receipts are execution logs; absence of execution log produces NOT_DONE.
  owning_layer: REGRESSION
  mutation_class: GATED
  last_modified: 2026-06-22
  dependents: Phase 2 project truth, execution log requirements, registry status.

- asset_id: eval_1_structural_packet
  asset_type: eval
  current_location: `scripts/eval_packet_v1/runner.py`; validators referenced by `brain-os/law/COUNCIL_BRIEF_STRATEGIC_SLICE_EVAL_L0_ENFORCE_LOCKED_v1.md`
  status: Existing structural eval. Command: `validate-eval-packet-v1.sh`. PASS criteria: at least 80 percent packet wins on readiness_score/gate_eligible; no live LLM. Receipt: `~/.sina/eval_packet_v1_report.json`.
  owning_layer: REGRESSION
  mutation_class: GATED
  last_modified: 2026-06-20
  dependents: strategic slice, dispatch policy context, hub Eval-1 panel.

- asset_id: eval_1b_behavioral_packet
  asset_type: eval
  current_location: `scripts/eval_packet_v1b/runner.py`; validators referenced by `brain-os/law/COUNCIL_BRIEF_STRATEGIC_SLICE_EVAL_L0_ENFORCE_LOCKED_v1.md`
  status: Existing behavioral eval lane. Commands: `validate-eval-packet-v1b.sh`, `validate-eval-packet-v1b-grounding.sh`, `validate-eval-packet-v1b-live.sh`. PASS criteria: scaffold composite >=70 percent and live pilots >=80 percent; OpenRouter 402 is honest skip/block. Receipt: `~/.sina/eval_packet_v1b_report.json`.
  owning_layer: PROMOTION
  mutation_class: GATED
  last_modified: 2026-06-20
  dependents: dispatch policy `eval_1b_gate_ok`, model/router promotion readiness, founder gate.

- asset_id: agent_runtime_validator_index
  asset_type: eval_index
  current_location: `data/agent-runtime-validator-index-v1.json`
  status: Existing validator tier index. Defines mac_light, ship, cloud_ci, deploy_only, max runtimes, network requirements, and validators. PASS/BLOCK is delegated to listed scripts; registry lacks asset-level owning_layer/mutation_class fields.
  owning_layer: REGRESSION
  mutation_class: GATED
  last_modified: 2026-06-22
  dependents: agent runtime checks, cloud CI, Mac light safety, factory runtime promotion.

- asset_id: agent_runtime_index_validator
  asset_type: eval
  current_location: `scripts/validate-agent-runtime-index-v1.sh`
  status: Command exists. PASS criteria: every validator named in `data/agent-runtime-validator-index-v1.json` exists on disk. BLOCK criteria: missing validator script.
  owning_layer: REGRESSION
  mutation_class: GATED
  last_modified: 2026-06-22
  dependents: validator index integrity; no separate receipt path found beyond stdout/exit code.

- asset_id: agent_runtime_promotion_validator
  asset_type: promotion_eval
  current_location: `scripts/validate-agent-runtime-promotion-v1.sh`; `scripts/agent_runtime_promotion_report_v1.py`
  status: Golden promotion gate. Command: `python3 scripts/agent_runtime_promotion_report_v1.py --no-write --json`. PASS criteria: report JSON `ok:true` and no SSOT auto-promote. BLOCK criteria: non-ok report or unsafe promotion mutation.
  owning_layer: PROMOTION
  mutation_class: GATED
  last_modified: 2026-06-22
  dependents: factory golden/runtime promotion gates; live-vs-sandbox separation; founder manual bump.

- asset_id: prompt_router_validator
  asset_type: router_eval
  current_location: `scripts/validate-prompt-router-v1.sh`; `scripts/prompt_router.py`
  status: Existing dry-run router eval. PASS criteria: JSON envelope parses, governance event is emitted, dry-run route for keyword/lane succeeds. BLOCK criteria: invalid JSON, missing event, dry-run failure.
  owning_layer: ROUTER
  mutation_class: GATED
  last_modified: 2026-06-19 to 2026-06-20
  dependents: prompt routing, worker lane mapping, future router promotion lane.

- asset_id: vector_retrieval_validator
  asset_type: rag_eval
  current_location: `scripts/validate-vector-retrieval-v1.sh`; `scripts/validate-vector-retrieval-hybrid-score-v1.sh`; `scripts/pre_llm/vector_retrieval/`
  status: Existing retrieval eval. PASS criteria inferred from validator: retrieval modules import and query path works. BLOCK criteria: retrieval engine/store/query failure. Receipt path not found in sampled files.
  owning_layer: SSOT_RAG
  mutation_class: GATED
  last_modified: 2026-06-19
  dependents: RAG source selection, pre-LLM packet quality, Brain knowledge retrieval.

- asset_id: ragas_eval1b_crossref_validator
  asset_type: rag_eval
  current_location: `scripts/validate-ragas-eval1b-crossref-v1.sh`
  status: Existing cross-reference validator. PASS criteria: referenced receipt `receipts/sa-0953-receipt.json` and expected cross-ref assets exist. BLOCK criteria: missing receipt or missing cross-ref. Receipt is the checked SA receipt, not a new independent verifier receipt.
  owning_layer: REGRESSION
  mutation_class: GATED
  last_modified: 2026-06-19
  dependents: Eval-1b grounding, RAGAS-related evidence, receipt cross-linking.

- asset_id: gate_receipts_validator
  asset_type: receipt_eval
  current_location: `scripts/validate-gate-receipts-v1.sh`; `scripts/validate-gate-receipts-routes-v1.sh`; `scripts/validate-gate-receipts-route-alignment-v1.sh`
  status: Existing gate receipt validators. PASS criteria: gate receipt files/routes align and parse. BLOCK criteria: missing receipt surface, route mismatch, malformed receipt. Receipts checked under `~/.sina/gate_shadow_v1.jsonl`, `~/.sina/gate_enforce_v1.jsonl`, and hub route `/api/gate-receipts-v1`.
  owning_layer: RECEIPT
  mutation_class: GATED
  last_modified: 2026-06-19 to 2026-06-20
  dependents: dispatch policy, model gate mode, receipt promotion gate.

- asset_id: truth_bundle_registry_validator
  asset_type: ssot_rag_eval
  current_location: `scripts/validate-truth-bundle-registry-v1.sh`; `scripts/agent_truth_bundle_v1.py`
  status: Existing truth bundle validator. PASS criteria: registry exists, `agent_truth_bundle_v1.py --json` succeeds, and required truth bundle fields parse. BLOCK criteria: missing registry or bundle generation failure.
  owning_layer: SSOT_RAG
  mutation_class: GATED
  last_modified: 2026-06-19
  dependents: session truth bundle, anti-staleness, Brain RAG freshness.

## Existing RAG/SSOT Sources Found

- asset_id: sourcea_ssot_index
  asset_type: ssot_index
  current_location: `docs/SOURCEA_SSOT_INDEX_LOCKED_v1.md`; `docs/CURSOR_CONTEXT_INDEX_LOCKED_v1.md`; `docs/CURSOR_CORPORATE_BOOTSTRAP_PACK_LOCKED_v1.md`
  status: Existing context/SSOT entry points. Needs direct registry rows linking each indexed SSOT to owning_layer, mutation_class, freshness, and eval coverage.
  owning_layer: SSOT_RAG
  mutation_class: LOCKED
  last_modified: 2026-06-19 to 2026-06-20
  dependents: context cache, RAG source selection, entry gate.

- asset_id: incident_registry_and_reports
  asset_type: incident_source_library
  current_location: `brain-os/incidents/`; `brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md`; `brain-os/incidents/ECOSYSTEM_INCIDENTS_INDEX_LOCKED_v1.md`
  status: Existing locked incident corpus and indexes. Needs normalized dependency links from incidents to affected validators, rules, and receipts.
  owning_layer: RECEIPT
  mutation_class: LOCKED
  last_modified: 2026-06-19 to 2026-06-20
  dependents: anti-staleness, validator pressure rules, Brain safety vocabulary, regression gaps.

- asset_id: plan_registries
  asset_type: registry_library
  current_location: `brain-os/plan-registry/*/REGISTRY.json`; `brain-os/plan-registry/*LOCK*.md`
  status: Existing task/plan registries across SourceA, enforcement, broker, automation, worker-dual, , site-score. These are not yet a Brain asset registry with owning_layer/mutation_class/freshness fields.
  owning_layer: SSOT_RAG
  mutation_class: GATED
  last_modified: 2026-06-19 to 2026-06-22
  dependents: worker inbox, prompt queues, future registry_inventory import.

- asset_id: sourcea_public_brain_rules
  asset_type: public_rag_rule_source
  current_location: `data/brain-public-rules-v1.json`; `cloud/workers/sourcea-brain-chat-v1/src/knowledge-bundle.json`
  status: Existing pinned public Brain rules inside generated bundle. Needs freshness receipt and registry dependency to locked private source(s).
  owning_layer: SSOT_RAG
  mutation_class: GATED
  last_modified: 2026-06-27 in generated bundle
  dependents: public Brain chatbot answers, public/private parity checks.

- asset_id: cursor_skills_library
  asset_type: skill_source_library
  current_location: `.cursor/skills/`; `agent-skills/`; external Cursor/Cloudflare skills under user directories
  status: Existing skill corpus used by agents. SourceA-local skills need registry rows for scope, owning_layer, mutation_class, source of truth, and eval coverage.
  owning_layer: AGENT
  mutation_class: GATED
  last_modified: 2026-06-19 to 2026-06-22
  dependents: agent behavior, hub app work, brain/public chatbot audits, commercial film factory.

- asset_id: prompts_and_queues
  asset_type: prompt_source_library
  current_location: `prompts/`; `brain-os/plan-registry/**/prompts/`; `scripts/prompt_queue.py`
  status: Existing prompt assets and queue machinery. Needs registry links to evals, router awareness, and receipt outputs.
  owning_layer: AGENT
  mutation_class: OPEN
  last_modified: 2026-06-19 to 2026-06-22
  dependents: worker execution, prompt router, prompt-forge, queue drain.

## Existing Databases/Receipts Found

- asset_id: receipts_index_locked
  asset_type: receipt_index
  current_location: `brain-os/runtime/RECEIPTS_INDEX_LOCKED_v1.md`
  status: Existing receipt catalog. Lists Brain receipts, broker inbox, goal lane broker, healthy orchestrator state, worker prompt inbox, and Brain pack mirror. Needs machine-readable registry equivalent.
  owning_layer: RECEIPT
  mutation_class: LOCKED
  last_modified: 2026-06-19
  dependents: receipt lookup, D4 verification, Task 1 registry import.

- asset_id: run_receipt_schema
  asset_type: receipt_schema
  current_location: `data/schemas/run-receipt-output-v1.json`; `scripts/runreceipt/`
  status: Existing run receipt schema with required fields `ok`, `tier_achieved`, `receipt_pack_uri`. Needs dependency links to validators that produce/consume it.
  owning_layer: RECEIPT
  mutation_class: LOCKED
  last_modified: 2026-06-19
  dependents: runreceipt packer, factory proof, verification gates.

- asset_id: mcp_receipts_bucket_spec
  asset_type: receipt_storage_spec
  current_location: `data/mcp-receipts-bucket-spec-v1.json`
  status: Existing receipt bucket spec. Forbids writing `~/.sina` via MCP. Needs registry connection to Supabase/R2 bucket implementation and receipt validators.
  owning_layer: RECEIPT
  mutation_class: LOCKED
  last_modified: 2026-06-19
  dependents: MCP receipt storage, public/private proof export, D4 author-separation.

- asset_id: truth_layer_cycle_receipts_db
  asset_type: database
  current_location: `infra/supabase/portfolio-spine/migrations/001_truth_layer_cycle_receipts_v1.sql`
  status: Existing Supabase migration for truth-layer cycle receipts. Needs Brain registry row and dependency links to public/probe receipt flows.
  owning_layer: RECEIPT
  mutation_class: GATED
  last_modified: 2026-06-22
  dependents: Supabase portfolio spine, truth-layer receipts, verification storage.

- asset_id: validator_machine_receipt
  asset_type: receipt_machine
  current_location: `data/validator-machine-registry-v1.json`; runtime receipt `~/.sina/validator-machine-last-receipt-v1.json`
  status: Existing validator machine registry with log dir and hub API. PASS/BLOCK is machine-defined per app/tier; agents are instructed to read receipts instead of rerunning validators.
  owning_layer: REGRESSION
  mutation_class: GATED
  last_modified: 2026-06-22
  dependents: Mac light validation, cloud CI validation, receipt-first proof.

- asset_id: cloud_drain_receipts
  asset_type: receipt_store
  current_location: `data/cloud-drain-auto-runtime-v1.json`; cloud `/app/receipts/cloud/autonomous-drain-cycles/`; Mac mirror `~/.sina/autonomous-drain-cycle-receipts/`
  status: Existing cloud drain receipt paths and tick receipt `~/.sina/cloud-drain-auto-tick-receipt-v1.json`. Needs registry link to promotion gate and source SSOT.
  owning_layer: RECEIPT
  mutation_class: GATED
  last_modified: 2026-06-22
  dependents: Cloudflare cron, Railway auto-tick, autorun proof.

## Existing Pipelines/Routes Found

- asset_id: cloud_drain_auto_runtime
  asset_type: pipeline
  current_location: `data/cloud-drain-auto-runtime-v1.json`
  status: Existing cloud autorun config. Route: Cloudflare cron to Railway server-side PROVE/SHIP; `POST /api/cloud-drain/auto-tick/v1`; observer URLs present. Receipts configured for cloud and Mac mirror.
  owning_layer: AGENT
  mutation_class: GATED
  last_modified: 2026-06-22
  dependents: autorun automation, loop specialist, cloud receipts, founder opt-in.

- asset_id: dispatch_policy
  asset_type: router_gate
  current_location: `brain-os/law/DISPATCH_POLICY_LOCKED_v1.md`; `scripts/runtime/dispatch_policy/`
  status: Existing dispatch policy. PASS gate: Eval-1b live A/B >=80 percent, gate mode enforce, bridge gate ok, critical_count 0, then orchestrator dispatch_ready true. Receipts: `~/.sina/gate_shadow_v1.jsonl`, `~/.sina/gate_enforce_v1.jsonl`, `/api/gate-receipts-v1`.
  owning_layer: ROUTER
  mutation_class: LOCKED
  last_modified: 2026-06-19
  dependents: model dispatch, orchestrator dispatch_ready, founder confirm.

- asset_id: execution_router
  asset_type: router_module
  current_location: `scripts/runtime/execution_router/`; `brain-os/law/SINA_RUNTIME_STACK_LOCKED_v1.md`
  status: Existing controlled dispatcher module. It selects next executable instruction from verified tool graph and policy inputs; it does not execute or mutate spine/queue/worker.
  owning_layer: ROUTER
  mutation_class: GATED
  last_modified: 2026-06-19
  dependents: tool graph verification, dispatch policy, runtime orchestrator.

- asset_id: tool_graph_verification
  asset_type: verifier_module
  current_location: `scripts/runtime/tool_graph_verification/`; validator `validate-tool-graph-verify-v1.sh` referenced in runtime stack
  status: Existing verification module for cycle check, dependency validation, scoring, API. Needs direct registry row and receipt path.
  owning_layer: CRITIC
  mutation_class: GATED
  last_modified: 2026-06-19
  dependents: execution router, runtime stack, promotion gates.

- asset_id: agent_runtime_factory_registry
  asset_type: factory_registry
  current_location: `data/agent-runtime-factory-registry-v1.json`
  status: Existing factory registry for comprehension-loop, video-ad, and noetfield-copilot runtimes. Each row includes SSOT, golden, eval script, validator, env SSOT, and receipt.
  owning_layer: AGENT
  mutation_class: GATED
  last_modified: 2026-06-22
  dependents: runtime promotion gate, factory evals, cloud CI, live/sandbox config diffs.

- asset_id: forge_mvp_router_rules
  asset_type: model_router_config
  current_location: `data/forge-mvp-router-rules-v0.1.json`
  status: Existing Forge router rules. Defines CLOUD_ONLY mode, Mac build forbidden, OpenRouter primary router, model/task routing, cost caps, and FBE wiring.
  owning_layer: ROUTER
  mutation_class: GATED
  last_modified: 2026-06-20
  dependents: Forge MVP, OpenRouter use, cost routing, cloud-only execution.

- asset_id: openrouter_activation_queue
  asset_type: model_provider_queue
  current_location: `brain-os/law/SOURCEA_OPENROUTER_ACTIVATION_QUEUE_LOCKED_v1.md`
  status: Existing OpenRouter activation law/queue. Activation is separate from hub dispatch_ready. Needs registry link to provider configs and eval-threshold gates.
  owning_layer: ROUTER
  mutation_class: LOCKED
  last_modified: 2026-06-20
  dependents: Eval-1b live arm, model dispatch, cloud drain, Forge router.

- asset_id: vector_retrieval_pipeline
  asset_type: rag_pipeline
  current_location: `scripts/pre_llm/vector_retrieval/`
  status: Existing retrieval modules (`index_builder`, `embedding_provider`, `query_engine`, `retrieval_engine`, `store`). Needs direct source registry and freshness receipt.
  owning_layer: SSOT_RAG
  mutation_class: GATED
  last_modified: 2026-06-19
  dependents: pre-LLM packet compiler, Brain RAG, Eval-1/Eval-1b grounding.

- asset_id: sourcea_brain_chat_worker
  asset_type: public_brain_runtime
  current_location: `cloud/workers/sourcea-brain-chat-v1/`
  status: Existing Cloudflare Worker Brain chat runtime with generated knowledge bundle. Needs registry links to private SSOT sources, eval gates, model/provider config, and receipt/promotion gate.
  owning_layer: AGENT
  mutation_class: GATED
  last_modified: 2026-06-27 observed in generated bundle
  dependents: public Brain chatbot, public RAG parity, live/sandbox Brain separation.

## Missing Registry Fields

- asset_id: missing_registry_inventory_schema
  asset_type: registry_gap
  current_location: not found as `registry_inventory.json` in repo or Downloads
  status: Task 1 field shape is known from prompt, but canonical `registry_inventory.json` implementation artifact was not present. Required fields are asset_id, asset_type, current_location, status, owning_layer, mutation_class, last_modified, dependents.
  owning_layer: BOOT
  mutation_class: GATED
  last_modified: unknown
  dependents: Task 1 import; all rows above.

- asset_id: missing_owning_layer_tags
  asset_type: registry_gap
  current_location: existing assets across `brain-os/`, `data/`, `scripts/`, `.cursor/rules/`, `cloud/`
  status: Most assets imply layer by path/function but do not carry machine-readable owning_layer tags from BOOT/CONSTITUTION/SSOT_RAG/ROUTER/AGENT/CRITIC/RECEIPT/TAMPER/REGRESSION/PROMOTION.
  owning_layer: BOOT
  mutation_class: GATED
  last_modified: unknown
  dependents: registry filtering, promotion gates, eval coverage.

- asset_id: missing_mutation_class_tags
  asset_type: registry_gap
  current_location: existing assets across repo
  status: LOCKED/GATED/OPEN is usually inferred from filename/path but not consistently encoded. Assets with unclear class need founder review before registry import.
  owning_layer: BOOT
  mutation_class: GATED
  last_modified: unknown
  dependents: safe mutation policy, sandbox candidate rules, promotion lane controls.

- asset_id: missing_freshness_receipt_fields
  asset_type: registry_gap
  current_location: RAG bundles, rules, skills, prompts, validators
  status: Freshness exists in some receipts and generated timestamps, but there is no uniform registry field naming the required receipt, verifier, author separation, or stale threshold per asset.
  owning_layer: RECEIPT
  mutation_class: GATED
  last_modified: unknown
  dependents: D4 verification, Brain RAG freshness, public/private parity.

- asset_id: missing_dependency_links
  asset_type: registry_gap
  current_location: evals, RAG sources, routers, receipts, promotion gates
  status: Dependencies are documented in scattered law/docs and code imports. No single graph connects SSOT source -> RAG chunk -> router/model/critic -> eval -> receipt -> promotion gate.
  owning_layer: BOOT
  mutation_class: GATED
  last_modified: unknown
  dependents: Task 2 connection layer; promotion readiness.

## Missing Connections

- asset_id: isolated_brain_chat_bundle
  asset_type: connection_gap
  current_location: `data/brain-chat-knowledge-bundle-v1.json`; `cloud/workers/sourcea-brain-chat-v1/src/knowledge-bundle.json`
  status: Bundle exists, but registry link to source SSOT rows, freshness receipt, eval coverage, router awareness, and promotion gate is incomplete.
  owning_layer: SSOT_RAG
  mutation_class: GATED
  last_modified: 2026-06-27 observed in generated worker bundle
  dependents: public Brain answer quality; Task 2 RAG/SSOT connection layer.

- asset_id: isolated_validator_scripts
  asset_type: connection_gap
  current_location: `scripts/validate-*.sh`, `scripts/validate_*.py`
  status: Large validator fleet exists, but many scripts have no registry row connecting protected layer, PASS/BLOCK criteria, receipt produced, and assets protected.
  owning_layer: REGRESSION
  mutation_class: GATED
  last_modified: 2026-06-19 to 2026-06-22
  dependents: eval registry, validator-machine registry, promotion gates.

- asset_id: isolated_prompt_forge
  asset_type: connection_gap
  current_location: `scripts/prompt_forge_pipeline_v1.py`; `scripts/chat_unify_prompt_forge_v1.py`
  status: Prompt-forge receipts exist, but no discovered promotion lane connection to router eval, RAG freshness, critic, and receipt promotion gate.
  owning_layer: AGENT
  mutation_class: GATED
  last_modified: 2026-06-19 to 2026-06-22
  dependents: future prompt-forge v0.1 lane, founder-language pipeline, Forge Terminal.

- asset_id: isolated_model_provider_configs
  asset_type: connection_gap
  current_location: `data/forge-mvp-router-rules-v0.1.json`; `brain-os/law/SOURCEA_OPENROUTER_ACTIVATION_QUEUE_LOCKED_v1.md`; model dispatch docs
  status: Model/provider configs exist, but there is no single registry connection from provider choice to eval thresholds, critic coverage, receipt path, and promotion decision.
  owning_layer: ROUTER
  mutation_class: GATED
  last_modified: 2026-06-20
  dependents: router promotion lane, Eval-1b live arm, OpenRouter activation.

- asset_id: isolated_receipt_storage
  asset_type: connection_gap
  current_location: `brain-os/runtime/RECEIPTS_INDEX_LOCKED_v1.md`; `data/mcp-receipts-bucket-spec-v1.json`; Supabase receipt migration
  status: Receipt storage/indexes exist, but not all evals and routers declare exact produced receipt and verifier author-separation requirement.
  owning_layer: RECEIPT
  mutation_class: GATED
  last_modified: 2026-06-19 to 2026-06-22
  dependents: D4 verification, promotion gate decisions, public proof.

## Required Promotion Gates (note only -- do not build)

- asset_id: live_brain_vs_sandbox_brain_gate
  asset_type: required_promotion_gate
  current_location: not centralized; related assets in `data/agent-runtime-factory-registry-v1.json`, `scripts/agent_runtime_promotion_report_v1.py`, Brain chat worker bundle
  status: Existing factory promotion machinery supports golden/runtime comparison and no-write promotion reports, but live Brain vs sandbox Brain separation is not centralized as a registry gate.
  owning_layer: PROMOTION
  mutation_class: GATED
  last_modified: unknown
  dependents: public Brain chatbot, sandbox candidate configs, founder manual promotion.

- asset_id: prompt_forge_promotion_lane_v0_1
  asset_type: required_promotion_gate
  current_location: prompt-forge scripts and receipts exist; lane registry not found
  status: Needs note-only lane connection: prompt candidate -> router/RAG/critic eval -> receipt -> founder promotion. Do not build in this pass.
  owning_layer: PROMOTION
  mutation_class: GATED
  last_modified: unknown
  dependents: prompt-forge pipeline, Forge Terminal, Chat Unify.

- asset_id: router_promotion_lane_v0_2
  asset_type: required_promotion_gate
  current_location: `scripts/prompt_router.py`; `scripts/runtime/execution_router/`; `brain-os/law/DISPATCH_POLICY_LOCKED_v1.md`
  status: Existing router modules and evals need promotion lane connection from dry-run PASS to sandbox route to gated live route.
  owning_layer: PROMOTION
  mutation_class: GATED
  last_modified: unknown
  dependents: model dispatch, execution router, dispatch_ready.

- asset_id: eval_threshold_promotion_lane_v0_3
  asset_type: required_promotion_gate
  current_location: Eval-1/Eval-1b docs; `scripts/agent_runtime_promotion_report_v1.py`; runtime golden configs
  status: Thresholds exist for Eval-1/Eval-1b and runtime golden configs, but not as a unified Brain registry promotion lane. Do not build in this pass.
  owning_layer: PROMOTION
  mutation_class: GATED
  last_modified: unknown
  dependents: Eval-1b live, agent runtime promotion, model/router/critic gates.

## Critical Gaps

- asset_id: gap_no_single_brain_registry
  asset_type: critical_gap
  current_location: absent centralized registry; partial sources in `brain-os/`, `data/`, `scripts/`
  status: SourceA has many registries, indexes, validators, receipts, and RAG bundles, but no single Brain Registry inventory with uniform fields and dependency graph.
  owning_layer: BOOT
  mutation_class: GATED
  last_modified: unknown
  dependents: Task 1 registry_inventory, Task 2 connections, Task 3 promotion gate mapping.

- asset_id: gap_exact_d4_portable_runtime_rules_source
  asset_type: critical_gap
  current_location: exact standalone file not found
  status: R1/R2 were available in prompt and applied; R6/R7 canonical D4-portable source needs founder-provided path or registry discovery before hard-coding.
  owning_layer: layer_unknown
  mutation_class: GATED
  last_modified: unknown
  dependents: vocabulary conformance, registry law, future promotion report wording.

- asset_id: gap_eval_receipt_author_separation
  asset_type: critical_gap
  current_location: validator scripts and receipt indexes
  status: Existing validators often use stdout/exit code or local receipt paths. Registry must distinguish builder SUBMITTED state from independent verifier PASS/FAIL/BLOCKED per D4.
  owning_layer: RECEIPT
  mutation_class: GATED
  last_modified: unknown
  dependents: valid verification, promotion gates, public proof.

- asset_id: gap_public_brain_freshness
  asset_type: critical_gap
  current_location: Brain chat knowledge bundles and SSOT sources
  status: Generated bundle timestamps exist, but no discovered registry row requires source hash, freshness receipt, stale threshold, and eval coverage before public Brain promotion.
  owning_layer: SSOT_RAG
  mutation_class: GATED
  last_modified: unknown
  dependents: public Brain accuracy, private/public parity, sandbox/live separation.

- asset_id: gap_mutation_trials_flag_guard
  asset_type: critical_gap
  current_location: `SOURCEA_PHASE2_MUTATION_TRIALS` references not found in targeted scan
  status: User explicitly forbids flipping flag; targeted scan did not find a canonical flag location. Needs registry row before any future mutation trial work.
  owning_layer: PROMOTION
  mutation_class: GATED
  last_modified: unknown
  dependents: sandbox candidate config-diff trials, live Brain protection.

## Recommended Minimal Next Action

- asset_id: next_action_task1_registry_inventory_seed
  asset_type: next_action
  current_location: proposed Task 1 artifact only; no file created in this pass
  status: Founder review this report, then seed `registry_inventory.json` from the rows above using the exact eight-field structure. First seed should cover only the critical spine: vocabulary source, law plane, Brain knowledge bundle, Eval-1/Eval-1b, validator index, prompt router, dispatch policy, receipt index, runtime factory registry, public Brain worker.
  owning_layer: BOOT
  mutation_class: GATED
  last_modified: 2026-06-29
  dependents: SOURCEA_BRAIN_REGISTRY_LEARNING_GATE_v0.1.4 Tasks 1-3; no implementation without founder review.
