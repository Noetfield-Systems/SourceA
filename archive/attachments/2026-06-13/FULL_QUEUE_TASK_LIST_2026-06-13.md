# Full queue task list — 2026-06-13

**Saved:** 2026-06-13T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**SourceA PHASE_STRICT drain — s1 OpenRouter → s7 tail → s9**
**Turns:** 156 · **SAs:** 52

| 1 | sa-0101 | CHECK | YES | Run bash validate-eval-packet-v1b-live.sh; sustain 5/5 pilots ≥80% |
| 2 | sa-0101 | ACT | YES | Run bash validate-eval-packet-v1b-live.sh; sustain 5/5 pilots ≥80% |
| 3 | sa-0101 | VERIFY | YES | Run bash validate-eval-packet-v1b-live.sh; sustain 5/5 pilots ≥80% |
| 4 | sa-0102 | CHECK | YES | Wire validate-eval-packet-v1b-live into strict build default chain |
| 5 | sa-0102 | ACT | YES | Wire validate-eval-packet-v1b-live into strict build default chain |
| 6 | sa-0102 | VERIFY | YES | Wire validate-eval-packet-v1b-live into strict build default chain |
| 7 | sa-0104 | CHECK | YES | Verify dispatch_policy eval_1b_gate_ok true in /api/dispatch-policy-v1 |
| 8 | sa-0104 | ACT | YES | Verify dispatch_policy eval_1b_gate_ok true in /api/dispatch-policy-v1 |
| 9 | sa-0104 | VERIFY | YES | Verify dispatch_policy eval_1b_gate_ok true in /api/dispatch-policy-v1 |
| 10 | sa-0106 | CHECK | YES | Run eval live with SINA_AUDIT_STRICT=1; capture report to ~/.sina |
| 11 | sa-0106 | ACT | YES | Run eval live with SINA_AUDIT_STRICT=1; capture report to ~/.sina |
| 12 | sa-0106 | VERIFY | YES | Run eval live with SINA_AUDIT_STRICT=1; capture report to ~/.sina |
| 13 | sa-0110 | CHECK | YES | Run python3 eval_packet_v1b/runner.py live smoke — write_report true |
| 14 | sa-0110 | ACT | YES | Run python3 eval_packet_v1b/runner.py live smoke — write_report true |
| 15 | sa-0110 | VERIFY | YES | Run python3 eval_packet_v1b/runner.py live smoke — write_report true |
| 16 | sa-0115 | CHECK | YES | Run bash validate-eval-packet-v1b.sh scaffold arm after live pass |
| 17 | sa-0115 | ACT | YES | Run bash validate-eval-packet-v1b.sh scaffold arm after live pass |
| 18 | sa-0115 | VERIFY | YES | Run bash validate-eval-packet-v1b.sh scaffold arm after live pass |
| 19 | sa-0951 | CHECK | no | Document compare GPT-4o Claude Opus Gemini workflow gaps T3 research only |
| 20 | sa-0951 | ACT | no | Document compare GPT-4o Claude Opus Gemini workflow gaps T3 research only |
| 21 | sa-0951 | VERIFY | no | Document compare GPT-4o Claude Opus Gemini workflow gaps T3 research only |
| 22 | sa-0952 | CHECK | no | Write spike: Cursor agent vs Devin vs SWE-agent on SourceA verify gates |
| 23 | sa-0952 | ACT | no | Write spike: Cursor agent vs Devin vs SWE-agent on SourceA verify gates |
| 24 | sa-0952 | VERIFY | no | Write spike: Cursor agent vs Devin vs SWE-agent on SourceA verify gates |
| 25 | sa-0953 | CHECK | no | Compare RAGAS eval CI to Eval-1b live packet approach — internal note |
| 26 | sa-0953 | ACT | no | Compare RAGAS eval CI to Eval-1b live packet approach — internal note |
| 27 | sa-0953 | VERIFY | no | Compare RAGAS eval CI to Eval-1b live packet approach — internal note |
| 28 | sa-0955 | CHECK | no | Research L0-full Cursor MCP editor telemetry — defer per phase 6 |
| 29 | sa-0955 | ACT | no | Research L0-full Cursor MCP editor telemetry — defer per phase 6 |
| 30 | sa-0955 | VERIFY | no | Research L0-full Cursor MCP editor telemetry — defer per phase 6 |
| 31 | sa-0956 | CHECK | no | Document pos-dispatch policy promotion criteria — founder council vote |
| 32 | sa-0956 | ACT | no | Document pos-dispatch policy promotion criteria — founder council vote |
| 33 | sa-0956 | VERIFY | no | Document pos-dispatch policy promotion criteria — founder council vote |
| 34 | sa-0957 | CHECK | no | Compare best world model agent OS patterns to Sina D-layer stack |
| 35 | sa-0957 | ACT | no | Compare best world model agent OS patterns to Sina D-layer stack |
| 36 | sa-0957 | VERIFY | no | Compare best world model agent OS patterns to Sina D-layer stack |
| 37 | sa-0958 | CHECK | no | Analyze critic law effectiveness — external chat wrong rate table |
| 38 | sa-0958 | ACT | no | Analyze critic law effectiveness — external chat wrong rate table |
| 39 | sa-0958 | VERIFY | no | Analyze critic law effectiveness — external chat wrong rate table |
| 40 | sa-0959 | CHECK | no | Research fleet 8-agent scoreboard at scale — auto-check taxonomy |
| 41 | sa-0959 | ACT | no | Research fleet 8-agent scoreboard at scale — auto-check taxonomy |
| 42 | sa-0959 | VERIFY | no | Research fleet 8-agent scoreboard at scale — auto-check taxonomy |
| 43 | sa-0960 | CHECK | no | Document no-ASF verify authority pattern for other repos mono noetfield |
| 44 | sa-0960 | ACT | no | Document no-ASF verify authority pattern for other repos mono noetfield |
| 45 | sa-0960 | VERIFY | no | Document no-ASF verify authority pattern for other repos mono noetfield |
| 46 | sa-0961 | CHECK | no | Compare Mono 1000 pack workflow to SourceA 1000 — sync pick scripts |
| 47 | sa-0961 | ACT | no | Compare Mono 1000 pack workflow to SourceA 1000 — sync pick scripts |
| 48 | sa-0961 | VERIFY | no | Compare Mono 1000 pack workflow to SourceA 1000 — sync pick scripts |
| 49 | sa-0962 | CHECK | no | Research hub refresh parallelize progress+bowl — perf note only |
| 50 | sa-0962 | ACT | no | Research hub refresh parallelize progress+bowl — perf note only |
| 51 | sa-0962 | VERIFY | no | Research hub refresh parallelize progress+bowl — perf note only |
| 52 | sa-0963 | CHECK | no | Spike: eval live pilot expansion beyond 5 tasks — tasks.json design |
| 53 | sa-0963 | ACT | no | Spike: eval live pilot expansion beyond 5 tasks — tasks.json design |
| 54 | sa-0963 | VERIFY | no | Spike: eval live pilot expansion beyond 5 tasks — tasks.json design |
| 55 | sa-0965 | CHECK | no | Research event bus topic taxonomy for spine learning loop |
| 56 | sa-0965 | ACT | no | Research event bus topic taxonomy for spine learning loop |
| 57 | sa-0965 | VERIFY | no | Research event bus topic taxonomy for spine learning loop |
| 58 | sa-0966 | CHECK | no | Compare ENFORCE IDE bypass gap to industry gate patterns |
| 59 | sa-0966 | ACT | no | Compare ENFORCE IDE bypass gap to industry gate patterns |
| 60 | sa-0966 | VERIFY | no | Compare ENFORCE IDE bypass gap to industry gate patterns |
| 61 | sa-0967 | CHECK | no | Document two-speed clocks strategic slice vs lane P0 case study |
| 62 | sa-0967 | ACT | no | Document two-speed clocks strategic slice vs lane P0 case study |
| 63 | sa-0967 | VERIFY | no | Document two-speed clocks strategic slice vs lane P0 case study |
| 64 | sa-0968 | CHECK | no | Research governance fleet validator extensions for lazy-load FR rows |
| 65 | sa-0968 | ACT | no | Research governance fleet validator extensions for lazy-load FR rows |
| 66 | sa-0968 | VERIFY | no | Research governance fleet validator extensions for lazy-load FR rows |
| 67 | sa-0969 | CHECK | no | Spike: semantic diff L14 integration with packet assembly |
| 68 | sa-0969 | ACT | no | Spike: semantic diff L14 integration with packet assembly |
| 69 | sa-0969 | VERIFY | no | Spike: semantic diff L14 integration with packet assembly |
| 70 | sa-0970 | CHECK | no | Document world model v5 vs v4 migration lessons locked |
| 71 | sa-0970 | ACT | no | Document world model v5 vs v4 migration lessons locked |
| 72 | sa-0970 | VERIFY | no | Document world model v5 vs v4 migration lessons locked |
| 73 | sa-0971 | CHECK | no | Research agent essay discourse as fleet compliance moat |
| 74 | sa-0971 | ACT | no | Research agent essay discourse as fleet compliance moat |
| 75 | sa-0971 | VERIFY | no | Research agent essay discourse as fleet compliance moat |
| 76 | sa-0972 | CHECK | no | Compare founder hub-only law to terminal-first agent products |
| 77 | sa-0972 | ACT | no | Compare founder hub-only law to terminal-first agent products |
| 78 | sa-0972 | VERIFY | no | Compare founder hub-only law to terminal-first agent products |
| 79 | sa-0973 | CHECK | no | Document validate-spine-bridge-founder proof types matrix |
| 80 | sa-0973 | ACT | no | Document validate-spine-bridge-founder proof types matrix |
| 81 | sa-0973 | VERIFY | no | Document validate-spine-bridge-founder proof types matrix |
| 82 | sa-0974 | CHECK | no | Research PROGRAM_PROGRESS machine sync vs manual ASF edit incidents |
| 83 | sa-0974 | ACT | no | Research PROGRAM_PROGRESS machine sync vs manual ASF edit incidents |
| 84 | sa-0974 | VERIFY | no | Research PROGRAM_PROGRESS machine sync vs manual ASF edit incidents |
| 85 | sa-0975 | CHECK | no | Append phase s9 research index to SOURCEA-1000-LOCK.md bibliography |
| 86 | sa-0975 | ACT | no | Append phase s9 research index to SOURCEA-1000-LOCK.md bibliography |
| 87 | sa-0975 | VERIFY | no | Append phase s9 research index to SOURCEA-1000-LOCK.md bibliography |
| 88 | sa-0976 | CHECK | no | Document compare GPT-4o Claude Opus Gemini workflow gaps T3 research only |
| 89 | sa-0976 | ACT | no | Document compare GPT-4o Claude Opus Gemini workflow gaps T3 research only |
| 90 | sa-0976 | VERIFY | no | Document compare GPT-4o Claude Opus Gemini workflow gaps T3 research only |
| 91 | sa-0977 | CHECK | no | Write spike: Cursor agent vs Devin vs SWE-agent on SourceA verify gates |
| 92 | sa-0977 | ACT | no | Write spike: Cursor agent vs Devin vs SWE-agent on SourceA verify gates |
| 93 | sa-0977 | VERIFY | no | Write spike: Cursor agent vs Devin vs SWE-agent on SourceA verify gates |
| 94 | sa-0978 | CHECK | no | Compare RAGAS eval CI to Eval-1b live packet approach — internal note |
| 95 | sa-0978 | ACT | no | Compare RAGAS eval CI to Eval-1b live packet approach — internal note |
| 96 | sa-0978 | VERIFY | no | Compare RAGAS eval CI to Eval-1b live packet approach — internal note |
| 97 | sa-0980 | CHECK | no | Research L0-full Cursor MCP editor telemetry — defer per phase 6 |
| 98 | sa-0980 | ACT | no | Research L0-full Cursor MCP editor telemetry — defer per phase 6 |
| 99 | sa-0980 | VERIFY | no | Research L0-full Cursor MCP editor telemetry — defer per phase 6 |
| 100 | sa-0981 | CHECK | no | Document pos-dispatch policy promotion criteria — founder council vote |
| 101 | sa-0981 | ACT | no | Document pos-dispatch policy promotion criteria — founder council vote |
| 102 | sa-0981 | VERIFY | no | Document pos-dispatch policy promotion criteria — founder council vote |
| 103 | sa-0982 | CHECK | no | Compare best world model agent OS patterns to Sina D-layer stack |
| 104 | sa-0982 | ACT | no | Compare best world model agent OS patterns to Sina D-layer stack |
| 105 | sa-0982 | VERIFY | no | Compare best world model agent OS patterns to Sina D-layer stack |
| 106 | sa-0983 | CHECK | no | Analyze critic law effectiveness — external chat wrong rate table |
| 107 | sa-0983 | ACT | no | Analyze critic law effectiveness — external chat wrong rate table |
| 108 | sa-0983 | VERIFY | no | Analyze critic law effectiveness — external chat wrong rate table |
| 109 | sa-0984 | CHECK | no | Research fleet 8-agent scoreboard at scale — auto-check taxonomy |
| 110 | sa-0984 | ACT | no | Research fleet 8-agent scoreboard at scale — auto-check taxonomy |
| 111 | sa-0984 | VERIFY | no | Research fleet 8-agent scoreboard at scale — auto-check taxonomy |
| 112 | sa-0985 | CHECK | no | Document no-ASF verify authority pattern for other repos mono noetfield |
| 113 | sa-0985 | ACT | no | Document no-ASF verify authority pattern for other repos mono noetfield |
| 114 | sa-0985 | VERIFY | no | Document no-ASF verify authority pattern for other repos mono noetfield |
| 115 | sa-0986 | CHECK | no | Compare Mono 1000 pack workflow to SourceA 1000 — sync pick scripts |
| 116 | sa-0986 | ACT | no | Compare Mono 1000 pack workflow to SourceA 1000 — sync pick scripts |
| 117 | sa-0986 | VERIFY | no | Compare Mono 1000 pack workflow to SourceA 1000 — sync pick scripts |
| 118 | sa-0987 | CHECK | no | Research hub refresh parallelize progress+bowl — perf note only |
| 119 | sa-0987 | ACT | no | Research hub refresh parallelize progress+bowl — perf note only |
| 120 | sa-0987 | VERIFY | no | Research hub refresh parallelize progress+bowl — perf note only |
| 121 | sa-0988 | CHECK | no | Spike: eval live pilot expansion beyond 5 tasks — tasks.json design |
| 122 | sa-0988 | ACT | no | Spike: eval live pilot expansion beyond 5 tasks — tasks.json design |
| 123 | sa-0988 | VERIFY | no | Spike: eval live pilot expansion beyond 5 tasks — tasks.json design |
| 124 | sa-0990 | CHECK | no | Research event bus topic taxonomy for spine learning loop |
| 125 | sa-0990 | ACT | no | Research event bus topic taxonomy for spine learning loop |
| 126 | sa-0990 | VERIFY | no | Research event bus topic taxonomy for spine learning loop |
| 127 | sa-0991 | CHECK | no | Compare ENFORCE IDE bypass gap to industry gate patterns |
| 128 | sa-0991 | ACT | no | Compare ENFORCE IDE bypass gap to industry gate patterns |
| 129 | sa-0991 | VERIFY | no | Compare ENFORCE IDE bypass gap to industry gate patterns |
| 130 | sa-0992 | CHECK | no | Document two-speed clocks strategic slice vs lane P0 case study |
| 131 | sa-0992 | ACT | no | Document two-speed clocks strategic slice vs lane P0 case study |
| 132 | sa-0992 | VERIFY | no | Document two-speed clocks strategic slice vs lane P0 case study |
| 133 | sa-0993 | CHECK | no | Research governance fleet validator extensions for lazy-load FR rows |
| 134 | sa-0993 | ACT | no | Research governance fleet validator extensions for lazy-load FR rows |
| 135 | sa-0993 | VERIFY | no | Research governance fleet validator extensions for lazy-load FR rows |
| 136 | sa-0994 | CHECK | no | Spike: semantic diff L14 integration with packet assembly |
| 137 | sa-0994 | ACT | no | Spike: semantic diff L14 integration with packet assembly |
| 138 | sa-0994 | VERIFY | no | Spike: semantic diff L14 integration with packet assembly |
| 139 | sa-0995 | CHECK | no | Document world model v5 vs v4 migration lessons locked |
| 140 | sa-0995 | ACT | no | Document world model v5 vs v4 migration lessons locked |
| 141 | sa-0995 | VERIFY | no | Document world model v5 vs v4 migration lessons locked |
| 142 | sa-0996 | CHECK | no | Research agent essay discourse as fleet compliance moat |
| 143 | sa-0996 | ACT | no | Research agent essay discourse as fleet compliance moat |
| 144 | sa-0996 | VERIFY | no | Research agent essay discourse as fleet compliance moat |
| 145 | sa-0997 | CHECK | no | Compare founder hub-only law to terminal-first agent products |
| 146 | sa-0997 | ACT | no | Compare founder hub-only law to terminal-first agent products |
| 147 | sa-0997 | VERIFY | no | Compare founder hub-only law to terminal-first agent products |
| 148 | sa-0998 | CHECK | no | Document validate-spine-bridge-founder proof types matrix |
| 149 | sa-0998 | ACT | no | Document validate-spine-bridge-founder proof types matrix |
| 150 | sa-0998 | VERIFY | no | Document validate-spine-bridge-founder proof types matrix |
| 151 | sa-0999 | CHECK | no | Research PROGRAM_PROGRESS machine sync vs manual ASF edit incidents |
| 152 | sa-0999 | ACT | no | Research PROGRAM_PROGRESS machine sync vs manual ASF edit incidents |
| 153 | sa-0999 | VERIFY | no | Research PROGRAM_PROGRESS machine sync vs manual ASF edit incidents |
| 154 | sa-1000 | CHECK | no | Append phase s9 research index to SOURCEA-1000-LOCK.md bibliography |
| 155 | sa-1000 | ACT | no | Append phase s9 research index to SOURCEA-1000-LOCK.md bibliography |
| 156 | sa-1000 | VERIFY | no | Append phase s9 research index to SOURCEA-1000-LOCK.md bibliography |
