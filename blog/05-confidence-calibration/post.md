> **Historical note.** This post explores an earlier design. The `confidence` field was later removed from the schema - see the current schema rules in the repo README / CLAUDE.md. The reasoning is preserved here as design history.

# How Certain Is Your Agent?

**Structured confidence vs. the illusion of certainty**

---

Ask an LLM how sure it is about something. It will usually say "I'm fairly confident" or "I believe this is likely correct." These phrases are semantically empty - they don't distinguish between "confirmed by three independent sources" and "I read one blog post about this once."

LLMs are notoriously poorly calibrated. They express similar confidence levels across very different evidence quality. A fact grounded in an authoritative source and a rumor from an informal contact receive the same rhetorical treatment.

The DAG's confidence scores are a structural intervention. When every assertion carries a number from 0.0 to 1.0 with defined semantics, the agent can reason about which conclusions are well-grounded and which rest on weak signals.

## The eval

The scenario presents a market entry decision with deliberately mixed evidence quality:

**High confidence (0.9-1.0):**
- $2M available capital (confirmed by finance, board-approved)
- Regulatory approval secured (certificate in hand)
- Three competitors identified with known market shares

**Medium confidence (0.5-0.6):**
- Customer acquisition cost estimated at $150 (could range $100-$250)
- Average revenue per customer estimated at $40/month (from competitor pricing)

**Low confidence (0.3):**
- Competitor Alpha rumored to be exiting (single informal source at a conference)
- Possible regulatory change in Q4 could increase costs 40% (proposed, 50% probability)

The compounds inherit this uncertainty:
- Payback period: 4 months (confidence 0.45 - both inputs are uncertain)
- Market window: favorable if Alpha exits (confidence 0.3 - rests on a rumor)
- Regulatory risk: could eliminate payback advantage (confidence 0.3 - two layers of uncertainty)

The overall implication: "Market entry is viable but the business case rests on uncertain assumptions" (confidence 0.6).

### Three conditions

**C0:** All facts as bullet points. No confidence indicators.

**C1:** Facts with text labels ("high confidence", "low confidence") and prose noting which conclusions are speculative.

**C2:** Full DAG with numerical confidence scores, evidence entries, and compounds whose confidence reflects their dependency quality.

### What to measure

- **Confidence differentiation** (weight 3) - Did the agent distinguish between solid facts and speculation?
- **Uncertainty propagation** (weight 3) - Did it note that conclusions from uncertain inputs inherit that uncertainty?
- **Calibrated recommendation** (weight 2) - Is the recommendation appropriately hedged?
- **False precision** (weight -2) - Did it present uncertain estimates as precise numbers?
- **Uniform confidence** (weight -2) - Did it treat all information equally?

## What confidence is and isn't

The DAG's confidence score is not a probability. It's a qualitative assessment of source reliability and specificity on a defined scale:

| Score | Meaning |
|---|---|
| 1.0 | Confirmed by authoritative source, specific and unambiguous |
| 0.9 | Strong source but could change |
| 0.7 | Reasonable belief with some ambiguity |
| 0.5 | Plausible but unconfirmed |
| 0.3 | Weak signal, speculative |
| 0.0 | Placeholder, known to be incomplete |

This scale is small enough to internalize (six levels) and specific enough to be useful. It doesn't pretend to be more precise than the underlying evidence supports.

Critically, **confidence does not propagate mechanically**. A compound's confidence is independently assessed based on dependency confidence, reasoning strength, and sensitivity to uncertainty. A conclusion can have high confidence even when one dependency has low confidence - if the conclusion's validity doesn't depend on the uncertain input. And a conclusion can have low confidence even when all dependencies are strong - if the reasoning step is a stretch.

This is different from probabilistic graphical models where belief propagation is automatic. In the DAG, every confidence score is a human or agent judgment about that specific claim, not a mathematical derivation from upstream scores.

## Why this matters

Poor calibration has real costs. An agent that says "I'm fairly confident" about a major decision based on a conference rumor is providing false assurance. An agent that says "this estimate has significant uncertainty - the actual range could be wide" is providing useful information.

The eval tests whether structural confidence information produces better-calibrated output. If C2 agents consistently distinguish between what's known and what's speculative while C0 and C1 agents treat everything uniformly, the structure is doing real work.

The broader principle: **uncertainty should be a first-class data type, not a rhetorical afterthought.**

---
