# The Composition Problem

**Why your agent misses things you told it**

---

You tell your agent that the production database supports 200 concurrent connections. In a separate conversation, you mention that each API instance holds 10 persistent connections. Later, you note that the DevOps lead is on leave in April. And in yet another thread, that the launch is April 15.

Each fact registers. None are forgotten. But the agent never surfaces the conflict: you can run at most 20 API instances with the current DB, launch traffic needs 200 instances, scaling requires DB admin access that only the DevOps lead has, and she's on leave during launch.

This isn't a retrieval failure. The agent has all the facts. It's a composition failure - the insight requires combining facts from different domains (infrastructure, personnel, timeline) into a conclusion that none of the individual facts contain. And composition, in a context window, is stochastic. It depends on which facts happen to be adjacent when the model attends to them.

This is the founding problem of Composable Beliefs.

## The eval

We seed three conditions with identical information - eight primitive facts about a product launch scenario. Two facts that individually seem innocuous compose into a launch-blocking conflict:

- **s001:** Database supports 200 concurrent connections
- **s002:** Each API instance holds 10 persistent connections
- **s003:** DevOps lead on leave April 1-30
- **s004:** Only DevOps lead has DB admin credentials
- **s005:** Launch is April 15
- **s006:** Launch traffic expected at 25x normal
- **s007:** Currently running 8 API instances
- **s008:** Scaling requires manual DB reconfiguration

The conflict: 200 connections / 10 per instance = 20 max instances. 25x traffic on 8 instances needs ~200 instances. Scaling past 20 requires DB admin credentials. Only Jordan has them. Jordan is on leave during launch.

### Condition C0: Raw facts

The agent receives the eight primitives as bullet points. No structure, no confidence, no relationships. Just the facts.

### Condition C1: Flat instructions

Same information, but with confidence labels ("high confidence", "moderate confidence") and prose descriptions of relationships. The information content is equivalent to C2, but without structural composition.

### Condition C2: Composable Beliefs DAG

The full DAG, including:
- Eight primitives with sources, evidence, and confidence scores
- Four compounds explicitly composing the primitives into the conflict chain
- One implication identifying the launch-blocking conclusion with three mitigation options

The critical question: does C2's structural composition help the agent surface the conflict more reliably than C0 or C1?

## What to measure

The scoring rubric has six criteria:

1. **Conflict detection** (weight 3) - Did the agent find the DB scaling + DevOps leave + launch date conflict?
2. **Reasoning chain** (weight 2) - Did it show the full chain (connections -> instances -> admin access -> leave)?
3. **Specificity** (weight 2) - Did it use the actual numbers (200, 10, 20, 25x)?
4. **Actionable recommendations** (weight 1) - Did it suggest mitigations?
5. **Confidence awareness** (weight 1) - Did it note that traffic projections (0.7) are less certain than infrastructure limits (0.95)?
6. **False positives** (weight -1) - Did it raise non-issues?

## Why this matters

The composition problem is not about having enough context. Modern models can hold millions of tokens. The problem is that composition is an active reasoning step, and whether the model takes it depends on how the information is arranged. A fact at position 10,000 and a related fact at position 150,000 may never be composed, even if both are within the context window.

The DAG makes composition structural. The compound assertion `s011` explicitly links `s001` and `s002` and states the conclusion: "at most 20 API instances." That composition was done once, by whatever process (human or agent) created the assertion, and every future reader inherits it.

This is the core value proposition: **composition should be structural, not stochastic.**

## Expected results

**C0** should show variable performance. Some runs will surface the conflict; others won't. The composition depends on the model's attention patterns during that specific run.

**C1** should improve slightly over C0. The prose descriptions of relationships give the model hints, but the model still has to perform the composition itself.

**C2** should show consistently high conflict detection. The composition is pre-computed in the DAG. The agent doesn't need to discover the relationship - it's explicit in the compound assertions.

If C2 significantly outperforms C1, the structure matters - not just the information, but how it's organized.

---
