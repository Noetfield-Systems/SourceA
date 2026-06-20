---
name: founder-linkedin-language
description: >-
  Load founder voice from LinkedIn SOT, dictionary, forbidden list, and Hub notes
  before writing M1 form rows, hub copy, or outbound posts. Use when drafting form
  questions, terminology, LinkedIn content, commercial copy, or when ASF mentions
  founder language, LinkedIn profile, plain English on form, or pre-execution governance.
---

# Founder LinkedIn language

## When to load

- Drafting or editing **M1 Canvas form rows** (`integrity-open-row-spec.ts`)
- Writing **hub** founder-facing copy
- **LinkedIn** posts, headline, or outbound one-liners
- Interpreting **founder notes** (`~/.sina/founder-notes.json`)

## Read order (disk — not chat memory)

1. `archive/attachments/founder-language/linkedin-voice.yaml`
2. `archive/attachments/founder-language/dictionary.yaml`
3. `archive/attachments/founder-language/forbidden.yaml`
4. `archive/attachments/founder-language/phrase-corpus.yaml`
5. `~/.sina/founder-notes.json` (if present)
6. LinkedIn profile SOT: `Noetfield-All-Documents/.../linkedin-profile-hyper-commercial-v4.md`

Quick check: `python3 scripts/founder_voice_sources_v1.py`

## Locked public voice

**Headline:** AI Governance & RWA Infrastructure Architect | Pre-Execution Risk & Compliance

**Category line:** We make AI execution impossible to bypass governance.

**Products (exact names):** Trust Brief · Evidence-Grade Audit Engine · Policy Replay · Pre-Execution Regulatory Pack

**Perimeter (always):** No custody · no payment initiation · advisory only — licensed partners execute settlement.

## Form row rules (FR-FORM)

| Write on card | Never on card |
|---------------|---------------|
| Plain English case story | `§OPEN_QUESTIONS`, `EXTERNAL_CRITIC` |
| Effect if pick X | "Maintainer explains in chat" |
| Disk today in founder words | Hub jargon, 616 hero, Trust OS build pitch |

Confirm locally · **Submit** on Canvas when done — not auto-apply on tick.

## After terminology changes

```bash
python3 scripts/sync_founder_linkedin_voice_v1.py
```

Regenerates M1 Canvas `FORM_TERMINOLOGY_REQUIRED` + form receipt.

## Say checklist

- [ ] Loaded linkedin-voice.yaml
- [ ] Checked forbidden.yaml — no FT-* phrases
- [ ] Form row readable without opening another chat
- [ ] CAPS treated as intent (FOUNDER_MSG_NORM)
- [ ] Ran sync if terminology block changed
