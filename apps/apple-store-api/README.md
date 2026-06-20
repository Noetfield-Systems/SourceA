# Apple Store API — billing · push · Swift client bridge

**Saved:** 2026-06-19T06:34:29Z · **Status:** PHASE_2 reserved

## Layout

```text
apple-store-api/
├── core/           # Auth · profiles
├── billing/        # StoreKit 2 webhooks
└── push-gateway/   # APNS when render completes
```

## Law

- No ElevenLabs/Fal imports in this package.  
- `apple_original_transaction_id` on `profiles` table (see migrations README).  
- SwiftUI client lives outside this repo or in sibling iOS workspace.
