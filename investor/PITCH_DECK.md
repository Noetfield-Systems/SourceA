# Pitch deck — slide-by-slide

**Copy each `## Slide N` block into Keynote / Google Slides. One idea per slide.**

---

## Slide 1 — Title

**Sina portfolio OS**  
*One founder. Several businesses. Remote operations. Customer-visible results.*

ASF · June 2026

---

## Slide 2 — The human problem

- One founder, **multiple real companies** — not a student project.
- Work used to stop when the founder left the desk.
- Investors don’t fund “I can SSH”; they fund **shipped products and revenue per company**.

---

## Slide 3 — What we built (capability — 30 seconds)

**Portfolio operating system**

- Mac = production floor (code, Cursor, deploy scripts).
- Phone = **remote start + status** (home Wi‑Fi or away on Tailscale).
- One spine ranks **which company is on deck today** and writes **today’s work orders**.

*This slide is not the product we sell — it’s how we run the portfolio.*

---

## Slide 4 — What we sell (results)

| Company | Customer pays for |
|---------|-------------------|
| TrustField | Trust / field operations platform |
| VIRLUX | Commerce / luxury stack live |
| Sinaai Mono | Runtime + control plane for AI ops |
| 777 Foundation | Mission, site, partnerships |
| Noetfield | Enterprise knowledge / audit (future build) |

**Separate program:** Cursor OS Pro → App Store remote IDE (own deck).

---

## Slide 5 — Demo frame (what you will show)

1. iPhone on **cellular** (optional: Wi‑Fi off).
2. Open remote desk → start **production** run (not a 5-second test).
3. Mac executes real pipeline → log on phone.
4. **Pivot:** “Revenue is VIRLUX live, TrustField pilot, etc.” — show URL or TestFlight when ready.

---

## Slide 6 — Architecture (executive)

```text
         ┌─────────────┐
Phone ──►│ Remote desk │──► Mac agent ──► SinaPromptOS (brain)
         └─────────────┘         │
                                   ├──► TrustField repo → deploy
                                   ├──► VIRLUX repo → deploy
                                   ├──► Mono / 777 / Noetfield
                                   └──► Reports + plans (Source A)
```

**Governance:** Source A (law, priority, ports) — single truth for humans and agents.

---

## Slide 7 — Traction (honest, June 2026)

**Done**

- Remote production trigger from phone (LAN + Tailscale).
- Multi-repo dispatch + ingest loop operational.
- Locked product lanes (portfolio vs App Store app).
- Ranked ecosystem priority (architect cycle).

**In progress**

- Auto-handoff of work orders into Cursor chats (paused for safety; manual or one-repo dispatch today).
- Per-company **customer-visible** milestones (staging, pilots, TestFlight).

**Not claimed**

- Aggregate ARR slide (fill when contracts exist).

---

## Slide 8 — Why now

- Founder-led multi-SMB portfolios are common; **integrated ops** are rare.
- AI dev tools exploded; **orchestration + governance** is the gap.
- Remote work is permanent — **phone → Mac production** is a real operating advantage.

---

## Slide 9 — Moat

1. **Governance stack** (Source A, locked plans, port law) — not five random repos.
2. **Prompt OS brain** — dispatch, ingest, architect refresh, execution logs.
3. **Remote ops proven** — same pipeline away from home.
4. **Separation** — commercial App Store SKU not confused with internal orchestra.

---

## Slide 10 — Business model

| Layer | Monetization |
|-------|----------------|
| TrustField | B2B SaaS / services |
| VIRLUX | Commerce / B2B |
| Mono | Platform / partner integrations |
| 777 | Grants, partnerships, programs |
| Noetfield | Enterprise license (post-build) |
| Cursor OS Pro | Consumer subscription (separate cap table story if applicable) |

HoldCo value = **speed + oversight + lower founder bottleneck**.

---

## Slide 11 — 90-day roadmap (portfolio)

See `ROADMAP.md` — one **customer-visible** deliverable per company per quarter.

**Lead metric:** # of live URLs / pilots / paying accounts — not # of automation runs.

---

## Slide 12 — Use of funds (template)

| Bucket | % | Outcome |
|--------|---|---------|
| Ship VIRLUX + TrustField to revenue | 40% | Pilots → contracts |
| Mono spine + ops | 20% | Reliable `:8000` + approvals |
| Noetfield build activation | 15% | MVP spec → code |
| 777 field + brand | 10% | Site + gate-0 execution |
| Ops safety + auto-handoff | 15% | Remove paste bottleneck |

*Adjust numbers per round.*

---

## Slide 13 — Team

**ASF** — founder, portfolio CEO, product authority.  
**System** — AI-assisted execution with human approval (ASF is final override).  
**Advisors needed** — regtech/commerce GTM, App Store growth (Pro), enterprise sales (Noetfield).

---

## Slide 14 — Risks

| Risk | Mitigation |
|------|------------|
| Founder bottleneck | Remote ops + ranked dispatch |
| AI reliability | VERIFY gates, human ingest, no blind auto-merge |
| Scope creep | Locked lanes; force majeure — wire doesn’t block company ships |
| Security | Local-first Mac; Tailscale; no secrets in repo |

---

## Slide 15 — Ask

- **Introductions** to first paying pilot (VIRLUX / TrustField).
- **Advisor** with multi-company operator experience.
- **Capital** (if applicable) tied to **named milestone** in `ROADMAP.md`.

---

## Slide 16 — Close

**We are not a university automation lab.**  
**We are a multi-business operator with a remote production floor.**  
**The meeting after this should be: live demo of what a customer pays for.**

**Appendix (only if asked):** technical proof logs — not in main deck.
