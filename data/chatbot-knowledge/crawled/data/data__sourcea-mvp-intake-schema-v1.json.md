---
updated: 2026-07-06T10:57:13Z
lane: core
source_path: data/sourcea-mvp-intake-schema-v1.json
public: true
kind: json
---

# Sourcea Mvp Intake Schema V1

- **schema**: sourcea-mvp-intake-schema-v1
- **version**: 1.0.0
- **plane**: commercial
- **business**: 48h-mvp-service
## fields
### building
- **required**: True
- **type**: string
- **max_len**: 2000
- **label**: What are you building?
### building_type
- **required**: False
- **type**: enum
#### values
- app
- website
- mvp
- video
- other
### 
- **required**: False
- **type**: string
- **max_len**: 500
- **label**:  or example
### deadline
- **required**: True
- **type**: enum
#### values
- this_week
- two_weeks
- flexible
### budget
- **required**: True
- **type**: enum
#### values
- 500_1k
- 1k_3k
- 3k_10k
- lets_talk
### email
- **required**: True
- **type**: email
- **label**: Your email
- **contact_email**: hello@sourcea.app
- **notify_to**: hello@sourcea.app
- **public_domain**: source.app
- **notify_from**: SourceA Intake <onboarding@resend.dev>
- **end_screen**: We'll respond in 2 hours with a plan.
- **inbox_dir**: data/commercial-intake/inbox
