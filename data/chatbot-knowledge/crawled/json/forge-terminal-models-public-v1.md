---
updated: 2026-06-27T08:46:57Z
lane: developer
source_path: sites/SourceA-landing/green-unified/data/forge-terminal-models-public-v1.json
public: true
kind: json
---

# Forge Terminal Models Public V1

- **schema**: forge-terminal-models-public-v1
- **version**: 1.0.0
- **generated_at**: 2026-06-25T15:26:12Z
## models
## gemini-1.5-flash
- **id**: gemini-1.5-flash
- **label**: Gemini 1.5 Flash
- **subtitle**: Fast verify loop · $
- **group**: Google
- **provider**: gemini_direct
- **api_model**: gemini-2.5-flash
- **tier_hint**: T1_fast
#### use_roles
- check
- bulk
- **cost_band**: $
- **available**: True
## gemini-1.5-pro
- **id**: gemini-1.5-pro
- **label**: Gemini 1.5 Pro
- **subtitle**: 2M context · architecture · $$$
- **group**: Google
- **provider**: gemini_direct
- **api_model**: gemini-2.5-pro
- **tier_hint**: T3_heavy
#### use_roles
- build
- reason
- critical
- **cost_band**: $$$
- **available**: True
## deepseek-v4
- **id**: deepseek-v4
- **label**: DeepSeek V4
- **subtitle**: OpenRouter · Logic & JSON · $
- **group**: OpenRouter
- **provider**: openrouter
- **api_model**: deepseek/deepseek-chat-v3-0324
- **tier_hint**: T1_fast
#### use_roles
- bulk
- check
- **cost_band**: $
- **available**: True
## deepseek-r1-or
- **id**: deepseek-r1-or
- **label**: DeepSeek R1
- **subtitle**: OpenRouter · Reasoning · $$
- **group**: OpenRouter
- **provider**: openrouter
- **api_model**: deepseek/deepseek-r1-0528
- **tier_hint**: T3_heavy
#### use_roles
- reason
- **cost_band**: $$
- **available**: True
## claude-haiku-4-direct
- **id**: claude-haiku-4-direct
- **label**: Claude Haiku 4.5
- **subtitle**: Anthropic direct · Check & bulk · $
- **group**: Anthropic
- **provider**: anthropic_direct
- **api_model**: claude-haiku-4-5-20251001
- **tier_hint**: T1_fast
#### use_roles
- bulk
- check
- **cost_band**: $
- **available**: True
## claude-sonnet-4-direct
- **id**: claude-sonnet-4-direct
- **label**: Claude Sonnet 4.6
- **subtitle**: Anthropic direct · Build & act · $$$
- **group**: Anthropic
- **provider**: anthropic_direct
- **api_model**: claude-sonnet-4-6
- **tier_hint**: T2_medium
#### use_roles
- build
- act
- critical
- **cost_band**: $$$
- **available**: True
## claude-3.5-sonnet
- **id**: claude-3.5-sonnet
- **label**: Claude 3.5 Sonnet
- **subtitle**: OpenRouter · Agentic coding · $$$
- **group**: OpenRouter
- **provider**: openrouter
- **api_model**: anthropic/claude-3.5-sonnet
- **tier_hint**: T2_medium
#### use_roles
- build
- act
- **cost_band**: $$$
- **available**: True
## claude-opus-4-or
- **id**: claude-opus-4-or
- **label**: Claude Opus 4
- **subtitle**: OpenRouter · Critical · $$$$
- **group**: OpenRouter
- **provider**: openrouter
- **api_model**: anthropic/claude-opus-4
- **tier_hint**: T4_marathon
#### use_roles
- critical
- reason
- **cost_band**: $$$$
- **available**: True
## gpt-4o-mini-or
- **id**: gpt-4o-mini-or
- **label**: GPT-4o mini
- **subtitle**: OpenRouter · Cheap control · $
- **group**: OpenRouter
- **provider**: openrouter
- **api_model**: openai/gpt-4o-mini
- **tier_hint**: T1_fast
#### use_roles
- check
- bulk
- **cost_band**: $
- **available**: True
## gpt-4o
- **id**: gpt-4o
- **label**: GPT-4o
- **subtitle**: OpenAI · Build & act · $$$
- **group**: OpenAI
- **provider**: openai
- **api_model**: gpt-4o
- **tier_hint**: T2_medium
#### use_roles
- build
- act
- **cost_band**: $$$
- **available**: True
## openai-o1
- **id**: openai-o1
- **label**: OpenAI o1
- **subtitle**: Deep reasoning · Critical · $$$$
- **group**: OpenAI
- **provider**: openai
- **api_model**: o1
- **tier_hint**: T4_marathon
#### use_roles
- reason
- critical
- **cost_band**: $$$$
- **available**: True
## model_groups
## Google
- **name**: Google
#### models
## gemini-1.5-flash
- **id**: gemini-1.5-flash
- **label**: Gemini 1.5 Flash
- **subtitle**: Fast verify loop · $
- **group**: Google
- **provider**: gemini_direct
- **api_model**: gemini-2.5-flash
- **tier_hint**: T1_fast
#### use_roles
- **cost_band**: $
- **available**: True
## gemini-1.5-pro
- **id**: gemini-1.5-pro
- **label**: Gemini 1.5 Pro
- **subtitle**: 2M context · architecture · $$$
- **group**: Google
- **provider**: gemini_direct
- **api_model**: gemini-2.5-pro
- **tier_hint**: T3_heavy
#### use_roles
- **cost_band**: $$$
- **available**: True
## Anthropic
- **name**: Anthropic
#### models
## claude-haiku-4-direct
- **id**: claude-haiku-4-direct
- **label**: Claude Haiku 4.5
- **subtitle**: Anthropic direct · Check & bulk · $
- **group**: Anthropic
- **provider**: anthropic_direct
- **api_model**: claude-haiku-4-5-20251001
- **tier_hint**: T1_fast
#### use_roles
- **cost_band**: $
- **available**: True
## claude-sonnet-4-direct
- **id**: claude-sonnet-4-direct
- **label**: Claude Sonnet 4.6
- **subtitle**: Anthropic direct · Build & act · $$$
- **group**: Anthropic
- **provider**: anthropic_direct
- **api_model**: claude-sonnet-4-6
- **tier_hint**: T2_medium
#### use_roles
- **cost_band**: $$$
- **available**: True
## OpenRouter
- **name**: OpenRouter
#### models
## deepseek-v4
- **id**: deepseek-v4
- **label**: DeepSeek V4
- **subtitle**: OpenRouter · Logic & JSON · $
- **group**: OpenRouter
- **provider**: openrouter
- **api_model**: deepseek/deepseek-chat-v3-0324
- **tier_hint**: T1_fast
#### use_roles
- **cost_band**: $
- **available**: True
## deepseek-r1-or
- **id**: deepseek-r1-or
- **label**: DeepSeek R1
- **subtitle**: OpenRouter · Reasoning · $$
- **group**: OpenRouter
- **provider**: openrouter
- **api_model**: deepseek/deepseek-r1-0528
- **tier_hint**: T3_heavy
#### use_roles
- **cost_band**: $$
- **available**: True
## claude-3.5-sonnet
- **id**: claude-3.5-sonnet
- **label**: Claude 3.5 Sonnet
- **subtitle**: OpenRouter · Agentic coding · $$$
- **group**: OpenRouter
- **provider**: openrouter
- **api_model**: anthropic/claude-3.5-sonnet
- **tier_hint**: T2_medium
#### use_roles
- **cost_band**: $$$
- **available**: True
## claude-opus-4-or
- **id**: claude-opus-4-or
- **label**: Claude Opus 4
- **subtitle**: OpenRouter · Critical · $$$$
- **group**: OpenRouter
- **provider**: openrouter
- **api_model**: anthropic/claude-opus-4
- **tier_hint**: T4_marathon
#### use_roles
- **cost_band**: $$$$
- **available**: True
## gpt-4o-mini-or
- **id**: gpt-4o-mini-or
- **label**: GPT-4o mini
- **subtitle**: OpenRouter · Cheap control · $
- **group**: OpenRouter
- **provider**: openrouter
- **api_model**: openai/gpt-4o-mini
- **tier_hint**: T1_fast
#### use_roles
- **cost_band**: $
- **available**: True
## OpenAI
- **name**: OpenAI
#### models
## gpt-4o
- **id**: gpt-4o
- **label**: GPT-4o
- **subtitle**: OpenAI · Build & act · $$$
- **group**: OpenAI
- **provider**: openai
- **api_model**: gpt-4o
- **tier_hint**: T2_medium
#### use_roles
- **cost_band**: $$$
- **available**: True
## openai-o1
- **id**: openai-o1
- **label**: OpenAI o1
- **subtitle**: Deep reasoning · Critical · $$$$
- **group**: OpenAI
- **provider**: openai
- **api_model**: o1
- **tier_hint**: T4_marathon
#### use_roles
- **cost_band**: $$$$
- **available**: True
## model_roles
## bulk
- **id**: bulk
- **label**: Massive work
- **hint**: Highest volume · lowest $/token — drafts, rows, exploration
- **default_model**: gpt-4o
- **available**: True
## build
- **id**: build
- **label**: Build
- **hint**: Code gen · patches · refactors · ship-quality output
- **default_model**: claude-sonnet-4-direct
- **available**: True
## act
- **id**: act
- **label**: Act
- **hint**: Execute plans · tool-heavy · multi-step agent turns
- **default_model**: claude-sonnet-4-direct
- **available**: True
## check
- **id**: check
- **label**: Check
- **hint**: Verify · lint · read-only audit · Haiku-class ROI
- **default_model**: claude-haiku-4-direct
- **available**: True
## reason
- **id**: reason
- **label**: Reason
- **hint**: Deep logic · architecture · debug root-cause
- **default_model**: deepseek-r1-or
- **available**: True
## critical
- **id**: critical
- **label**: Critical
- **hint**: Governance · security · no-fail decisions — spend only when blocked
- **default_model**: claude-opus-4-or
- **available**: True
- **default_model**: gpt-4o
- **default_role**: bulk
## keys_ready
- **gemini**: True
- **openrouter**: True
- **openai**: True
- **anthropic**: True
