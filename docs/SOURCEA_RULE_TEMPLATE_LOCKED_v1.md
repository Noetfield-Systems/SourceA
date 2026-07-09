# SourceA Rule Template (LOCKED v1)

**Saved at:** 2026-07-05T12:50:00Z  
**Enforcer:** `scripts/lint-cursor-rules-format-v1.sh`

---

## Required frontmatter

```yaml
---
description: One-line purpose
globs:
  - "**/*"   # optional
alwaysApply: false   # true only if in 9-rule cap
---
```

---

## Required sections

```markdown
# Title

**Law:** `path/to/LOCKED_v1.md`

## Law (one sentence)

> ...

## Required / Forbidden

| Required | Forbidden |
|----------|-----------|
| ... | ... |
```

---

## Always-apply cap

Max **8** requestable + **9** always-apply (see `045-cursor-cost-intelligence-routing-v1.mdc`). New always-apply requires ASF approval + retire one.

---

## Pointer-only rule

Do not restate full law prose — cite LOCKED path + one-line summary.
