# SOURCE-A — LLM Agent Operating Law (SSOT v1)

**Status:** SUPERSEDED · **Registry id:** `llm_agent_operating_law_v1` · **Superseded by:** v3 (`llm_agent_operating_law_v3`)  
**Do not operate from this file** — lineage/history only.

**My single source of truth for how I hand work to Cursor and any LLM agent.**
Read this before writing any agent prompt. I am the founder and observer; the agent is the worker. The architecture is the engine — the agent only turns the tools.

---

## 0. The one rule above all

> **Direction, not force.**
> I give the goal and the guardrails. The agent diagnoses and fixes the issue *itself*.
> I do not prescribe exact commands — I might be wrong, and a wrong command misleads the agent worse than no command. I describe the outcome; the agent finds the path.

---

## 1. The Laws

1. **Mission, not micro-steps.** Cursor ships when given one bounded project with a clear finish line. It wanders and burns context on tiny steps. One mission = one session.

2. **One job per mission.** Never bundle unrelated jobs in one prompt (e.g. DNS + queue logic). Different files / different risk / different blast radius = different missions. Mixing them makes the agent drift and makes failure impossible to diagnose.

3. **Truth from receipts, never self-report.** "Done" is proven by a receipt, a test log, a `curl` output — never by the agent saying "green." Every mission ends with: *show me how you verified.*

4. **Binary done-condition.** Every mission states one provable done state. If it can't be proven, it isn't done. No "build theater."

5. **Constraints are part of every prompt.** Always name what NOT to touch and what is deferred (e.g. no motor rewrite, no Neon, touch only the named files). Guardrails protect my deferred decisions from being undone by accident.

6. **Founder decisions stay with me.** Product and intent choices — which domain, which project, what a page shows, which provider — are mine. The agent executes; it does not infer my intent. If intent is unclear, the agent STOPS and asks. It never guesses.

7. **Hard stop over placeholder.** If the agent can't find what it needs, it STOPS and reports. It never invents a placeholder, fakes a result, or ships something empty to satisfy the prompt.

8. **Don't kill a running agent.** Let a mid-flight mission finish — killing it halfway leaves half-done state. I judge the *result*, then decide. Reverting a finished result is clean; interrupting a running one is not.

9. **Verify before destructive moves.** Before any checkout / stash-pop / delete / DNS change — look first (list the stash, read what's in it, check the branch). Never run a blind destructive command, mine or the agent's.

10. **Firewall the machine from drift.** A `.cursorignore` at the repo root so agents can't scan upward or sideways and fall into loops. Keep the workspace bounded so the agent can only see its own territory.

11. **Context discipline.** When a session gets heavy, dump full state to a disk handoff file and start fresh with a light bootstrap prompt + lazy-loading (open files just-in-time, not all at once). Never carry a bloated context into a new chat.

12. **Cloud is truth, Mac observes.** When cloud state and local state disagree, local discards its copy and re-reads truth. This applies to my agents too: the authoritative state lives in receipts/registries, not in an agent's memory of it.

---

## 2. Two modes — pick before I write the prompt

| Mode | When | What I write |
| :-- | :-- | :-- |
| **Direction** | The agent knows the codebase better than I do in the moment, or I'm unsure of the fix | The *goal* + constraints. Let it diagnose. "Look at the current state, understand what's wrong, fix it your way, show me how you verified." |
| **Spec** | I know exactly what I want built and how | A bounded mission with explicit steps, but still a binary done-condition and receipts. |

Default to **Direction** when I'm not certain. Force only when I'm certain.

---

## 3. The Mission Prompt Template

```
MISSION: <one-sentence goal>

CONTEXT: <the minimal true facts about the current state — no file dumps>

WHAT I WANT: <the outcome, not the steps>

DONE = <one binary, provable condition>

VERIFY: <the exact proof to show me — curl output / test log / receipt path>

CONSTRAINTS:
- Do NOT touch <deferred things / other systems>.
- Touch only <named files/area>.
- This is <one job> only — do not bundle other work.

IF BLOCKED: STOP and report what's missing. Do not guess my intent.
Do not invent a placeholder. Verdicts from receipts only — no build theater.
```

---

## 4. The Direction Prompt (when I'm unsure — safest default)

```
The goal is simple: <plain statement of what I want to work>.

Here's the current state as I understand it: <one or two true facts>.

Please look at it yourself, understand what's actually wrong, and fix whatever is
needed. You decide the right approach — I'm not prescribing the steps.

When you're done, show me how you verified it actually works.
```

---

## 5. Anti-patterns (the things that have burned me)

- ❌ Bundling two unrelated jobs into one prompt → agent wanders, failures un-diagnosable.
- ❌ Prescribing exact commands I'm not 100% sure of → misleads the agent.
- ❌ Letting the agent infer a product/intent decision → it guesses wrong.
- ❌ Trusting "it's green" without a receipt → false confidence, hidden corruption.
- ❌ Killing an agent mid-run → half-done state, lost work.
- ❌ Running a destructive command (stash pop / checkout / DNS) without looking first.
- ❌ Carrying a bloated context into a new chat → 40% burned before work starts.

---

## 6. My role, restated

I am the **observer and manager**, not the actor. I set the goal, the guardrails, and the finish line. The gates and receipts supervise execution. The agent turns the tools. If I find myself typing commands or babysitting steps, I've dropped into the wrong layer — I step back up to direction.

> **Fundable systems are proven by receipts, not diagrams.**
> **Good agent work is proven the same way — by receipts, not by what the agent says.**

---

*SSOT v1 · Source-A · keep at brain-os/ssot/ · supersede only with a versioned v2.*
