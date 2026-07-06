---
updated: 2026-07-06T10:57:13Z
lane: developer
source_path: sites/SourceA-landing/green-unified/data/n8n-template-sourcea-chat-unify-v1.json
public: true
kind: json
---

# N8N Template Sourcea Chat Unify V1

- **name**: SourceA Chat Unify → Proof Pack
## nodes
## Webhook
#### parameters
- **httpMethod**: POST
- **path**: sourcea-forge
- **responseMode**: responseNode
- **name**: Webhook
- **type**: n8n-nodes-base.webhook
- **typeVersion**: 1
#### position
- 240
- 300
## SourceA Relay
#### parameters
- **url**: https://hooks.sourcea.app/v1/relay
- **method**: POST
- **jsonParameters**: True
#### options
- **bodyParametersJson**: ={{ JSON.stringify({ event: $json.body.event || 'forge.mission', payload: $json.body, source: 'n8n' }) }}
- **name**: SourceA Relay
- **type**: n8n-nodes-base.httpRequest
- **typeVersion**: 4
#### position
- 480
- 300
## connections
### Webhook
#### main
- [{'node': 'SourceA Relay', 'type': 'main', 'index': 0}]
## meta
- **templateId**: sourcea-chat-unify-webhook-v1
- **description**: STAB-057 — n8n webhook → SourceA hosted relay → Chat Unify hook
