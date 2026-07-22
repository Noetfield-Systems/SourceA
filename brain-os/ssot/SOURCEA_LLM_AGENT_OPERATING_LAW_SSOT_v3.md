# SOURCE-A — LLM Agent Operating Law (SSOT v3)

**Status:** ACTIVE · **Registry id:** `llm_agent_operating_law_v3` · `data/sourcea-governance-ssot-registry-v1.json`  
**Do not operate from superseded copies** — see `brain-os/ssot/superseded/`

**My single source of truth for handing work to Cursor, reading what comes back, and deciding what to dispatch — enforced by my Chat Unify machines, not just by memory.**
I am the founder and observer. The agent is the worker. The architecture is the engine. **Receipts on my disk are the only truth.**

---

## What's new in v3 (learned from running my own machines on a real reply)

- **The Dispatch Gate is now law.** No agent reply becomes an order until it passes the ORD Truth gate. My machines already do this — v3 writes it into the law.
- **"Disk-bound or it's draft."** A claim I can't tie to a file on *my* Mac is a draft, not a fact — no matter how confident or correct it sounds. (My ORD loop scored a confident, well-written reply **27/100 → BLOCK** purely because nothing was bound to my disk. The gate was right.)
- **BLOCK ≠ false.** A block means *"not proven here yet,"* not *"wrong."* The fix is to bind it to disk and re-score — never to argue with the gate, never to assume it's false.
- **Red-flag watchlist** added (from ORD): *Unverified*, *Fake layering*. I now reject these on sight — including from advisors and from the LLM that writes my prompts.
- **One bounded action out.** Every loop ends in exactly one next action. "Many stack words, unclear single action" is a failure, not a feature.
- **The closed cycle** (Prompt Forge → Cursor → ORD gate → Founder loop → bounded order) is named, so the machines stop being islands.

---

## 0. The one rule above all

> **Direction, not force.** I give the goal and the guardrails. The agent diagnoses and fixes *itself*. I describe the outcome; it finds the path. I do not prescribe commands I'm unsure of.

---

## A. Laws of the Mission — how I scope work going OUT

1. **Mission, not micro-steps.** One bounded project with a clear finish line per session. Cursor ships on missions, wanders on tiny steps.
2. **One job per mission.** Never bundle unrelated jobs. Different files / risk / blast radius = different missions.
3. **State what's already done — never restart from zero.** Every prompt pins `ALREADY DONE / DEPLOYED (do NOT redo)`. If I don't pin current state, the agent redoes finished work.
4. **Name the systems, leave the method.** Name the hosts/platforms (Vercel, Cloudflare, Railway, Supabase, GitHub, n8n) so the agent knows the terrain — but let it choose *how*.
5. **Founder decisions stay with me.** Naming, paths, which project/provider, what a page shows, what to sell. The agent asks; it never guesses.
6. **One bounded action out.** Every mission, and every loop reading a reply, resolves to exactly ONE next action. If it can't, it's not ready to dispatch.

---

## B. Laws of Truth & Dispatch — how I judge what comes BACK

7. **Disk-bound or it's draft.** A claim is trusted only if it cites a path on *my* Mac that actually exists and says what the claim says. No disk binding → it's a draft, treat the whole reply as draft.
8. **Truth from receipts, never self-report.** "Done / PASS / wired / green" from an agent is a claim, not proof. Proof is a receipt, a test log, a `curl`, a live URL — on my disk.
9. **Run the Dispatch Gate before any order.** Every agent reply goes through ORD (Parser → Classifier → Consistency → Source → Simplifier → Red flags → Report → Truth gate) before it becomes a Cursor order. **Dispatch only on PASS.** The exact scoring formula and BLOCK threshold live in the ORD machine — that file is the authority, not this sentence.
10. **BLOCK means "bind it," not "trash it."** On BLOCK: save the artifact to disk, run it, generate the receipt, re-score. Promote draft → dispatch by *proof*, never by re-asserting confidence.
11. **End-to-end on the real surface.** Final truth = the actual thing working where it lives (open the URL, run the endpoint), not an internal pass.
12. **Cloud/authoritative state is truth; local observes.** When two copies disagree, the local copy is discarded and truth is re-read. Applies to agents too: authority is in receipts/registries, not an agent's memory.
13. **Privacy-first.** Extracts and receipts stay local under `~/.sina/` (`~/.sina/chat-unify/`). Truth lives on my machine.

---

## C. Laws of Restraint — when NOT to act, when NOT to add

14. **Green and serving the need beats ideal.** If it's live and does the job, I don't optimize it mid-flight. I log the imperfection and move on.
15. **Log the debt as a receipt-for-myself.** Working-but-imperfect (e.g. extra Worker proxy) gets one durable line so future-me/agent isn't confused. Visible debt, not hidden.
16. **Constraints in every prompt.** Name what NOT to touch and what's deferred (no motor rewrite, no Neon, touch only named files).
17. **Hard stop over placeholder.** Can't find what it needs → STOP and report. Never fake a result or ship an empty placeholder.
18. **Asking for access/inputs is correct, not failure.** Needs my Cloudflare/Vercel/GitHub access or a decision → it asks. An agent asking is the system working.
19. **Don't kill a running agent.** Let a mission finish; judge the result, then decide.
20. **Verify before destructive moves.** Look first before any delete / checkout / stash-pop / DNS change.
21. **Firewall the machine from drift.** `.cursorignore` at repo root; agents can't scan upward/sideways and loop.
22. **Context discipline.** Heavy session → dump state to a disk handoff file, restart with a light bootstrap + lazy-loading. Never carry a bloated context.

---

## D. The planner LLM (the one that writes my prompts — including external advisors)

The LLM that drafts a Cursor prompt — or any outside advisor — is under the **same** law it enforces, and under the **same Dispatch Gate**.

- **It translates my need — it does not add to it.** "Fix the DNS" stays about DNS. Added scope is a violation, same as an agent guessing my intent.
- **Its confident prose is still draft until disk-bound.** A helpful, correct-*sounding* reply that cites nothing on my disk gets treated as draft and run through ORD like anything else. (This is exactly how a 27/100 BLOCK happened — and it was right.)
- **No fake layering.** Many stack/governance words wrapping an unclear action = a red flag. Strip it to one plain action.
- **Frustration / repetition is the alarm.** If I'm correcting the same thing twice, an LLM added scope or restarted from zero. Stop, restate my one line, strip the rest.

---

## E. The Chat Unify machine cycle (the law, running as code)

My machines are the law enforced. The full loop is a closed cycle, and nothing dispatches without passing the gate:

```
  founder language
        │
        ▼
  [Prompt Forge]  ── outbound: founder language → SSOT-shaped Cursor mission
        │
        ▼
     Cursor (agent does the work, returns a reply)
        │
        ▼
  [ORD loop + Truth gate]  ── inbound: reply → disk-checked → PASS / BLOCK
        │  PASS only
        ▼
  [Founder loop]  ── reply → ONE bounded action
        │
        ▼
  bounded order back to Cursor   (or: BLOCK → bind to disk → re-score)
```

- **Prompt Forge** = the outbound machine (this law, applied to what I send).
- **ORD loop** = the inbound truth machine (this law, applied to what I get back).
- **Founder loop** = the decision machine (reply → one bounded action).
- They are one system, not three tools. The gate sits between "reply" and "order."

---

## F. Red-flag watchlist (reject on sight — from ORD)

- ❌ **Unverified** — claims with no disk binding → draft, do not dispatch.
- ❌ **Fake layering** — many stack words, unclear single action → strip to one action.
- ❌ **Bundled jobs** — two+ unrelated jobs in one ask → split, keep the primary.
- ❌ **Rebuild risk** — "exists" + "build/deploy" in the same breath → pin ALREADY DONE.
- ❌ **Self-report green** — PASS/wired/done without a receipt → unproven.
- ❌ **Scope inflation** — the prompt-writer adding what I didn't ask for.

---

## G. Two modes
| Mode | When | What I write |
| :-- | :-- | :-- |
| **Direction** | unsure of the fix / agent knows the code better now | the goal + constraints; let it diagnose |
| **Spec** | I know exactly what & how | bounded steps, still binary DONE, still receipts |

Default **Direction** when unsure. Force only when certain.

---

## H. The Mission Prompt Template (v3)
```
GOAL: <one plain sentence>

CONTEXT (true now — do not re-derive):
  - ALREADY DONE / DEPLOYED (do NOT redo): <...>
  - Systems involved: <name hosts/platforms>
  - Accounts/access if relevant: <...>

WHAT I WANT: <the outcome, not the steps>

DONE = <one binary, disk-checkable, end-to-end condition>

VERIFY: <exact proof bound to MY disk — receipt path / test log / curl / live URL>

CONSTRAINTS:
  - NO rebuild/redeploy if it already exists — wire/fix, don't recreate.
  - One job only. Don't bundle. Touch only <named area>. Don't break what works.
  - Verdicts from receipts only — no self-report, no fake layering.

END IN ONE BOUNDED ACTION. IF BLOCKED/ambiguous: STOP, say what's missing or which
decision is mine. Don't guess. Don't placeholder. (This reply will be run through ORD —
make claims disk-checkable.)
```

---

## I. The Direction Prompt (safest default)
```
The goal is simple: <what I want to work>.
Current state as I understand it: <true facts, incl. what's already live>.
Look at it yourself, understand what's wrong, fix it your way — do not rebuild or
redeploy anything that already works. Then show me how you verified it, with proof I
can check on my own disk.
```

---

## J. My Dispatch Checklist (run before sending ANY order)
1. One job? (else split)
2. ALREADY DONE pinned? (else rebuild risk)
3. DONE condition disk-checkable? (else it's draft)
4. Ends in one bounded action? (else fake layering)
5. Would it pass ORD? Any red flags? (else fix first)
6. Founder decisions left to me, not guessed? (else add "ask, don't guess")

If any fails → fix before dispatch. The checklist *is* the gate, by hand.

---

## K. My role + the dispatch creed

I am the **observer and manager**, not the actor. I set goal, guardrails, finish line. The gates and receipts supervise. The agent turns the tools. If I'm typing commands or babysitting steps, I dropped a layer — step back up to direction.

When choosing which mission to run next, I prefer the one closest to a **demoable receipt or a paying outcome** — proof and revenue over polish.

> **Fundable systems are proven by receipts, not diagrams.**
> **Good agent work is proven the same way — by receipts, not by what the agent says.**
> **And nothing I'm told — by an agent, an advisor, or the LLM writing my prompts — becomes an order until it's bound to my disk and clears the gate.**

---

*SSOT v3 · Source-A · keep at brain-os/ssot/ · supersedes v1 & v2 · supersede only with a versioned v4.*
