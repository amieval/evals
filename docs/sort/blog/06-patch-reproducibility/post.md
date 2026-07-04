> **Status — design sketch (2026-06).** An *illustrative* C0/C1/C2 scenario, never run. It explores the since-removed `patch` assertion kind (and author-vs-earned confidence), so the mechanism no longer exists as written. Preserved as design history; see the current schema in the repo README / CLAUDE.md.

# Patches: Reproducible Arguments

**When the routing IS the argument**

---

In a modular synthesizer, a patch is a specific routing of signals through modules. The same modules, wired differently, produce different sounds. The patch doesn't describe the sound - it produces it. The routing is the composition.

The DAG has a fourth assertion kind that works the same way: **patches**. Unlike compounds (which synthesize dependencies into a single belief), patches present evidence as a routing through nodes for independent evaluation. The routing is the argument. Confidence starts null because it's derived from evaluator agreement, not author assessment.

This is a distinct epistemological operation. Compounds say "I combined A + B and concluded C." Patches say "here is the path A -> B -> C -> D -> E - trace the routing and see what you conclude."

## Why patches matter

Most arguments are rhetorical. A prose argument selects evidence, arranges it narratively, and guides the reader toward a conclusion. The structure of the argument - which evidence is emphasized, what order it's presented in, how transitions are framed - shapes the conclusion as much as the evidence itself.

Patches strip the rhetoric. They present a structured path through evidence nodes with explicit dependencies. Two people reading the same patch may reach different conclusions - and that disagreement is informative. If ten independent evaluations of the same patch agree, the argument is strong. If they diverge, the argument is weak or ambiguous, regardless of how compelling the prose version sounds.

This is reproducibility applied to reasoning, not just data.

## The eval

The scenario presents an engineering team in decline - velocity dropping, code reviews bottlenecked, senior engineers departing, requirements increasing. The underlying pattern is a capacity death spiral: attrition causes bottlenecks, bottlenecks increase pressure, pressure drives more attrition.

Three representations of the same argument:

**C0 - Prose narrative:**
A well-written paragraph describing the situation. The narrative structure guides the reader through the evidence toward the death spiral conclusion. It reads naturally and persuasively.

**C1 - Bullet list:**
The same evidence as ten bullet points. No narrative structure, but also no explicit relationships between the data points.

**C2 - DAG patch:**
Nine nodes in three layers with a patch (s009) that routes through all of them:

```
Layer 1: Observations
  s001: Velocity down 30%
  s002: Review time 4hrs -> 2 days
  s003: 3 senior engineers departed

Layer 2: Structure
  s004: Departed engineers did 60% of reviews
  s005: Requirements up 40%
  s006: EM in 30+ hrs/week meetings

Layer 3: Composition
  s007: Review bottleneck is structural (deps: s002, s003, s004)
  s008: Velocity decline masked by pressure (deps: s001, s005, s006)

Patch:
  s009: Capacity death spiral (routes through all nodes)
  confidence: null (derived from eval agreement)
```

### The meta-metric

Unlike other evals in this series, the patch eval measures **agreement rate across multiple runs**, not just quality per run. Each condition is evaluated N times independently (recommended N=10). The scoring asks:

- Did the evaluator identify the self-reinforcing cycle?
- Did it distinguish structural from procedural causes?
- Did it make a specific prediction?
- Did it cite specific evidence?

Then, across all N runs of each condition: **how consistent are the conclusions?**

If the patch (C2) produces higher agreement than prose (C0) or bullets (C1), the structured routing makes reasoning more reproducible.

## What patches add to the uniqueness argument

Most knowledge systems have one composition operation: combine inputs, produce output. The DAG has three:

| Operation | Kind | What it does |
|---|---|---|
| Synthesize | compound | Combines deps into a single belief |
| Act | implication | Identifies action from composed beliefs, materializes into todos |
| Present | patch | Routes through nodes for independent evaluation |

Patches are the most unusual. They acknowledge that some arguments shouldn't be pre-concluded - they should be presented as evidence structures for independent evaluation. The DAG author builds the routing but does not dictate the conclusion. Confidence comes from evaluator consensus, not author conviction.

This has implications for agent-human collaboration:
- An agent can build a patch by identifying relevant nodes and their relationships
- A human can evaluate the patch independently, without being influenced by the agent's conclusion
- Multiple evaluations produce a confidence score grounded in agreement, not assertion
- Disagreement is a signal that the argument needs refinement, not that someone is wrong

## The modular synth parallel

The modular synth metaphor is not decorative. In both systems:

- **Modules are reusable.** The same assertion can appear in multiple patches.
- **Routing creates meaning.** The same modules, routed differently, produce different arguments.
- **The output is emergent.** Neither the modules nor the routing alone determine the conclusion - it emerges from the combination.
- **Patches are shareable.** You can give someone a patch (routing diagram) and they can run it themselves on the same modules.

The key difference from musical patches: belief patches produce conclusions that can be evaluated for truth, not just aesthetic quality. The agreement metric is the evaluation function.

---
