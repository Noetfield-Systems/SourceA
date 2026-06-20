# INCIDENT-019 — Agent-founder bash communication (repo-relative cwd miss)

**Saved:** 2026-06-16T05:49:57Z · **Retrofit:** doc-datetime-law batch retrofit
**Version:** 1.1 LOCKED  
**Class:** Agent communication · founder command hygiene  
**Topic:** How agents write bash for ASF — **not** any subsystem (S10, drain, hub)  
**Reporter:** ASF (Terminal paste failure)  
**Agent:** Cursor Worker · **sequence_id:** SA-2026-06-10-INCIDENT-019  
**Opened:** 2026-06-10  
**Canonical law:** `AGENT_FOUNDER_BASH_COMMUNICATION_LOCKED_v1.md`  
**Related:** INCIDENT-020 (topic conflation)  
**Status:** REMEDIATED (law + wrapper pattern logged)

---

## 1. What happened

Agent gave **repo-relative** shell paths in chat:

```bash
python3 scripts/s10_eternal_audit_loop_v1.py --daily --json
bash scripts/validate-s10-eternal-loop-v1.sh
```

ASF ran from **home directory** (`~`):

```text
sinakazemnezhad@Sinas-MacBook-Pro ~ %
```

Shell resolved to `/Users/sinakazemnezhad/scripts/...` — **ENOENT**.  
Scripts live under `/Users/sinakazemnezhad/Desktop/SourceA/scripts/...`.

**This incident is about communication format**, not whether S10 works. S10 disk artifacts were present; chat commands were unsafe.

---

## 2. Violations

| # | Law | Violation |
|---|-----|-----------|
| V1 | `SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md` | Pushed Terminal to ASF without one-tap alternative |
| V2 | `AGENT_MISS_DISK_FIRST_CORRECTION_LOOP_LOCKED_v1.md` | Relative paths without `cd` / absolute / wrapper |
| V3 | `AGENT_FOUNDER_BASH_COMMUNICATION_LOCKED_v1.md` | (created after miss) — no cwd guard |
| V4 | Topic separation | First draft wrongly titled "S10 wrong bash" — **fixed in INCIDENT-020** |
| V5 | `AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md` | First filed at repo root only — **fixed in INCIDENT-021** |

---

## 3. Root cause

1. Agent assumed cwd = SourceA repo root.  
2. No line-1 `cd` guard in copy-paste block.  
3. Agent bundled **communication fix** into **S10 narrative** — category error.

---

## 4. Remediation

| Fix | Path |
|-----|------|
| Canonical communication law | `AGENT_FOUNDER_BASH_COMMUNICATION_LOCKED_v1.md` |
| Cwd-safe wrapper pattern | `~/.sina/bin/<name>` with fixed `ROOT` |
| Example wrappers | `s10-eternal-daily` · `s10-eternal-validate` · `s10-eternal-full` |
| Canonical incident body | This file · `brain-os/incidents/` |

Wrappers are **ergonomics** for this incident class — not S10 law.

---

## 5. Founder-right bash (generic template)

```bash
cd /Users/sinakazemnezhad/Desktop/SourceA && python3 scripts/<script>.py <args>
cd /Users/sinakazemnezhad/Desktop/SourceA && bash scripts/<script>.sh
~/.sina/bin/<wrapper-name>
cat /Users/sinakazemnezhad/.sina/<artifact>.json
```

---

## 6. Verify

```bash
cd ~
cd /Users/sinakazemnezhad/Desktop/SourceA && python3 scripts/cursor_entry_gate.py --role worker
```

Expected: gate output · exit 0. Proves **cwd rule**, not subsystem health.

---

## 7. Never forget

- **Wrong bash = agent communication bug** — separate from subsystem SSOT.  
- **One topic → one incident → one law file.**  
- S10 eternal loop ≠ this incident (see `SOURCEA_S10_ETERNAL_SELF_HEAL_AUDIT_LOCKED_v1.md`).

**LOCKED** — canonical body · `brain-os/incidents/`
