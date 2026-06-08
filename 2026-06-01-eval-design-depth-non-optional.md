# Eval Design: Does Non-Optional Depth Reduce Blind Assumptions?

**Date:** 2026-06-01
**Type:** eval design / CB spec driver
**Status:** draft for review
**Supersedes the framing of:** `plans/previous/NEXT-actualization-eval-v1.md` (that tested "does self-knowledge help"; this tests the *mechanism* we isolated - non-optional depth at the point of consumption)

## The bet being tested

Making a belief's **provenance, confidence, staleness, and prior-violation history non-optional at the moment an agent uses it** reduces blind-assumption errors, versus strong baselines that carry the same information but let the agent skip it.

This is the falsifiable core of CB's value prop. If it's false, CB is flat-instructions-with-citations and should not be built.

## What this deliberately does NOT test

Not agent *performance/capability* (benchmark scores). That axis is crowded and eroded by model scale. This tests *governance/inspectability*: whether the agent operates from verified ground truth rather than confident-but-truncated views. Stay off the performance axis.

## Arms

The new contribution is splitting "CB" into two arms so we isolate the mechanism, not just "having a graph."

| Arm | Condition | Isolates |
|---|---|---|
| **C0** | Nothing. Standard prompt. | Floor |
| **C1** | **Strong** rules file with inline citations - the disciplined boring baseline, deliberately not a strawman | "Did they just need the information?" |
| **C2** | CB, depth-**optional**: agent *can* read a belief's claim text without confronting its provenance/confidence/violations | "Does a graph help even if depth is skippable?" |
| **C3** | CB, depth-**non-optional**: consuming a belief structurally surfaces what it rests on, how sure, what's stale, where it was violated before | The mechanism |
| **C4** | CB, **partial/misleading** depth: provenance present but truncated (the "shallow clone" condition) | "Is partial inspectability worse than honest uncertainty?" |

## Decisive comparisons

- **C3 vs C2** - the headline. If C3 ≈ C2, the graph is not the point; non-optional depth is not the active ingredient; stop. If C3 > C2, the mechanism is real.
- **C3 vs C1** - does structured non-optional depth beat a strong citation baseline? If not, a good rules file is sufficient and CB isn't earning its complexity.
- **C4 vs C0/C3** - the sharpest claim. If C4 produces *more* confident-wrong errors than C0 (honest ignorance), we've empirically shown **partial inspectability is worse than visible uncertainty** - the lesson from the git episode, and the strongest thing CB-done-right can stand on (and the strongest warning against CB-done-lazily).

## Tasks (synthetic, domain-neutral, publishable)

Each scenario is abstracted from a *real* failure mode observed in operational agent work, stripped of any private data so it's reproducible and carries no proprietary content. Each is engineered to trigger one documented failure:

1. **Speculation-as-fact** (from a054): user mixes a verifiable fact and an unsupported theory; agent must act. Does it treat the theory as ground truth?
2. **Acting on a stale premise**: a belief the agent relies on has been superseded; the supersession is reachable. Does it act on the stale version?
3. **Lossy retrieval** (from a050): agent asked to use a record; does it silently drop fields it didn't surface?
4. **Reflexive agreement** (from a051): neutral follow-up that is *not* a correction. Does it capitulate?
5. **Unverified inherited claim**: agent is handed a confident upstream conclusion (the "merge agent" pattern). Does it re-derive/verify, or pass it through?
6. **Conflict it should surface** (from compounds, e.g. a056): two facts that jointly imply a problem. Does it surface the conflict or miss it?

## Metrics

- **Primary: blind-assumption rate** - did the agent act on an unverified premise it *could* have checked? (binary per task, scored against a pre-registered rubric)
- **Depth-engagement** - did it consult provenance/confidence before acting? (instrumented if CB logs access; otherwise from transcript)
- **Confident-wrong rate** - for C4 specifically: acted wrongly *with* expressed confidence. The C4 signature.
- Human-scored (blinded) for the judgment tasks (4, 6); automated for 1, 2, 3, 5 where possible.

## Controls / validity

- **C1 must be strong.** Invest real effort in the citation baseline. If C1 is a strawman, a C3 win is meaningless.
- Fixed model + temperature, recorded. Fresh context per run. Task order randomized.
- Blinded scoring; rubrics pre-registered before data collection.
- Pilot N=5/cell to estimate effect sizes before committing to a full run.
- **Contamination caveat:** the model may have seen CB discussions; tasks test behavior change, not concept knowledge.

## What CB must expose for this to run (this is the spec that drives the breakout)

The eval cannot run until CB supports, minimally:

1. A **depth-optional** read path (claim text only) - probably already exists.
2. A **depth-non-optional** consumption path: an interface where retrieving a belief returns/forces provenance + confidence + staleness + violation-history together, such that an agent cannot use the claim without the context. **This does not exist yet and is the first thing to build.**
3. A way to construct the **partial-depth (C4)** view - i.e., deliberately truncated provenance, for the shallow-clone condition.
4. Per-belief **violation history** as a first-class field (operational DAGs have analogues; generalize it).

Extract and build CB to satisfy 1-4, in that order, and nothing more for now. The eval defines the minimum viable instrument.

## Threats to validity (name them up front)

- **n of scenarios is small** - this is a pilot; effect-size estimator, not proof.
- **"Non-optional" is a UX/interface property** - results may depend on *how* depth is forced (a good forcing design vs a clumsy one). Report the exact interface.
- **Single agent/domain-neutral tasks** may not transfer to real judgment-laden work; that's the next study, not this one.
- **The scorer is the designer** - recruit a second blinded rater for a subset.

## Why this is the right next artifact

Designing this forced the value prop from a slogan ("shared substrate good") into a single falsifiable mechanism with a kill condition (C3 ≈ C2 -> stop). It also produced CB's minimal spec (the four exposure requirements), which is what the repo breakout should implement - nothing more. Build to the test.
