> **Status — design sketch (2026-06).** An *illustrative* C0/C1/C2 scenario, never run. Cross-session reasoning carryover is *not* a task in the current eval program ([`eval-design-depth-non-optional`](../../2026-06-01-eval-design-depth-non-optional.md) / [`boundary-blindness`](../../boundary-blindness/)), which narrowed to in-context boundary/inspectability failures. Predates the removal of the `confidence` field (now structural support).

# The Amnesiac Agent

**Why your agent forgets what it decided and why**

---

Session 1 spent 45 minutes evaluating deployment strategies. It ruled out rolling deployment because the payment API isn't backward-compatible. It considered blue-green but flagged the budget concern. It chose canary deployment but documented an open question: can the canary router split traffic at the endpoint level?

Session 2 starts cold. It has access to the same documents, the same codebase, the same configuration files. But the reasoning - why rolling was eliminated, why blue-green was expensive, what specific concern remained about canary - is gone. Not compressed. Not summarized. Gone. The instance that produced it no longer exists.

Session 2 may reach the same conclusion. Or it may not. It might recommend rolling deployment because it never encounters the payment API incompatibility in the right context. It might recommend blue-green because it never notices the budget constraint. It might recommend canary without the caveat about endpoint-level routing that session 1 carefully documented.

This is the session boundary problem. Every new session is a distribution shift where prior reasoning is lost.

## The eval

Session 1 establishes a decision with full reasoning:
- Rolling deployment: **ruled out** (payment API version incompatibility)
- Blue-green deployment: **expensive** ($24k transition vs. $15k budget cap)
- Canary deployment: **recommended** with an open question about endpoint-level routing

Session 2 receives new information: the canary router supports sticky sessions by user ID, but webhook callbacks from the payment processor cannot be made sticky (they come from the processor's servers, not the user's session).

The question: should we proceed with canary, or reconsider?

### Three conditions

**C0:** Session 2 gets only the new webhook information. No session 1 context.

**C1:** Session 2 gets a natural language summary: "In a previous session, we evaluated deployment strategies. Rolling was ruled out due to payment API incompatibility. Blue-green was flagged as expensive. Canary was recommended but we had a question about endpoint-level routing."

**C2:** Session 2 gets the full DAG - ten assertions including the eliminated options, the reasoning chain, the decision, and the documented uncertainty (s009-s010).

### What to measure

The scoring has a critical negative criterion: **contradiction** (weight -3). Did the agent contradict session 1's reasoning? Did it recommend rolling without acknowledging the incompatibility? Did it ignore the budget constraint? Did it forget the endpoint routing concern entirely?

Positive criteria focus on continuity:
- **Prior reasoning preserved** (weight 3) - Does the agent know what was decided and why?
- **Open question addressed** (weight 3) - Does it connect the new webhook information to the documented concern?
- **Nuanced analysis** (weight 2) - Sticky sessions solve the user-facing problem but not the webhook problem. Does the agent catch this?
- **Decision consistency** (weight 2) - Does the response build on session 1 rather than starting from scratch?

## The structural difference

A natural language summary (C1) captures what was decided. The DAG (C2) captures the reasoning structure.

Consider what happens when session 2 processes the new webhook information:

**With C1 summary:** The agent knows canary was recommended and there was a question about endpoint routing. The webhook information is relevant, but the agent must reconstruct why endpoint routing mattered and how it connects to the payment API concern.

**With C2 DAG:** The agent sees:
- `s009`: "Unknown whether canary routing can split at API endpoint level" (confidence 0.5)
- `s010`: "Must verify canary router supports endpoint-level routing before proceeding" (deps: s008 + s009)
- `s004`: "Payment API is not backward-compatible across versions" (confidence 0.95)

The webhook information directly addresses `s009`. The agent can trace the dependency: webhooks can't be made sticky -> endpoint-level routing is partially solved (user requests yes, webhooks no) -> the payment API incompatibility concern (s004) is partially unresolved -> the canary recommendation (s008) needs revision.

This tracing is structural. The agent follows explicit dependency links rather than reconstructing the reasoning from prose.

## Why this matters

Session boundaries are the fundamental constraint of agent-based work. Every other capability - retrieval, reasoning, tool use, planning - resets at the session boundary. The quality of work in session N+1 depends entirely on what carries over from session N.

Most carryover mechanisms preserve content: documents, summaries, conversation logs. The DAG preserves structure: what was concluded, what it depended on, what was uncertain, and what was explicitly ruled out. Structure is harder to lose during carryover because it's not subject to summarization loss or context-window-dependent attention.

The broader principle: **reasoning that survives session boundaries must be structural, not narrative.**

---
