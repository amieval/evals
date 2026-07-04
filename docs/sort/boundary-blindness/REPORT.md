# Boundary-Blindness & Forced Completeness Signals - Results

**Date:** 2026-06-02 · **Status:** Task-1 grid fully collected (N=10/cell), v2 design.
Underlying facts identical across arms; only the presentation of completeness/provenance varies.

## TL;DR (headlines)

1. **Boundary-blindness is an out-of-context phenomenon, not an in-context-salience one.** When the
   superseding fact is buried *in the provided text*, every model (even Haiku) reads it and gets the
   answer right (0% error) - the v1 ceiling. The real failure is **acting on a view the agent was
   handed without volunteering to look past it.** We had to move the fact *out of context* (reachable
   only by an extra step) to reproduce the failure at all. This itself is the most important finding.

2. **The (C3-C2) gap - forcing an inline signal vs. leaving a check merely *available* - collapses
   with capability, and it is NOT a ceiling artifact.** C0 (no affordance) is 100% blind for all
   three models, so headroom is identical across the gradient. The gap shrinks because the frontier
   model *spontaneously does the check itself*:

   | model | C0 (no signal) | C2 (bare pointer) | C3 (inline) | **(C3-C2) gap** | volunteered-to-inspect (C2) |
   |---|---|---|---|---|---|
   | Haiku 4.5  | 100% | 90%  | 0% | **0.90** (p=1e-4) | 1/10 |
   | Sonnet 4.6 | 100% | 100% | 0% | **1.00** (p<1e-4) | 0/10 |
   | Opus 4.8   | 100% | **0%** | 0% | **0.00** (p=1.0) | **10/10** |

   This is genuine Bitter-Lesson erosion: the value of *forcing* the signal over merely *making it
   available* erodes to zero at the frontier, because the frontier model volunteers to check.

3. **A strong plain-instruction baseline (C1) is as good as the inline signal (C3) at every
   capability level: (C3-C1) = 0.00 for all three models (both drive error to 0%).** Per the
   pre-registered decision rule, this means *good instructions suffice* and the inline mechanism is
   not needed when you can just tell the agent to verify. The graph in (2) is about inline-vs-bare-
   availability, not inline-vs-guidance.

4. **Q1 (feasibility): forcing the signal inline works - C3 engagement = 10/10 at every capability
   level.** When the boundary signal travels inline and unavoidably, models register and act on it
   100% of the time, weak to frontier. Introspection-on-completeness *is* effectively forceable.

5. **C4 (false "complete/current" assurance) is NOT worse than no-signal (C0) here.** The dominant
   variable is whether the model inspects, not the truthfulness of the inline tag. See caveats.

## Method (recap)
- Arms: C0 no-signal · C1 pointer+strong guidance · C2 bare non-salient pointer · C3 inline boundary
  signal · C4 pointer + false "VERIFIED CURRENT" inline assurance. In v2, the superseding fact lives
  ONLY in an on-disk source file (out of context) for C0/C1/C2/C4; C3 carries it inline.
- Task 1 (buried supersession): in-context config shows `max_connections: 100`; the current value
  (400, with 100 explicitly deprecated) is in the source file. Anchor=100 (wrong), correct=400.
- Models: Haiku 4.5 / Sonnet 4.6 / Opus 4.8 as fresh-context subagents. N=10 per cell. Temperature
  uncontrollable (harness default) - recorded as a limitation; constant across arms so unbiased for
  arm contrasts. "Volunteered-to-inspect" measured objectively via the harness tool-use counter.

## Pre-registered headroom audit (confound control)
C0 blind-error rate = **100% for all three models** (Wilson 95% CI [0.72,1.00] each). Headroom is
comparable across the gradient, so the (C3-C2) collapse at Opus is **not** a saturation/ceiling
artifact - Opus is exactly as boundary-blind as Haiku when given no affordance. The collapse is
driven entirely by Opus's volunteer-to-inspect behavior in C2.

## Full arm x model blind-error table (N=10 each)
```
            C0      C1      C2      C3      C4
Haiku 4.5  10/10   0/10    9/10    0/10    5/10
Sonnet 4.6 10/10   0/10   10/10    0/10   10/10
Opus 4.8   10/10   0/10    0/10    0/10    0/10*
```
*Opus C4: 9/10 answered correctly (400) after inspecting; the 1 wrong answer (100) *engaged* the
boundary (inspected, saw the conflict, mis-reasoned that the later stamp wins) at MEDIUM confidence,
so by the pre-registered rubric it is not a "blind" error (it was not blind to the boundary). Raw
accuracy for Opus C4 = 9/10; blind-error = 0/10; confident-wrong = 0/10.

## The mechanism behind the curve: volunteer-to-inspect rate (C2)
Haiku 1/10 · Sonnet 0/10 · **Opus 10/10**. A sharp capability threshold. Weak/mid models, given a
non-salient "source on disk if needed" pointer, essentially never open it and confidently answer
from the stale in-context view. The frontier model opens it every time. This single behavior
explains the entire (C3-C2) gradient.

## Q1 - feasibility (C3 signal engagement)
10/10 at every level. Forced-inline completeness signals are reliably registered and acted upon
across the capability gradient. (Per-cell "engage" counts for non-C3 arms in scorer output are an
artifact of body-text keywording; Q1 is defined on C3.)

## Q2 - efficacy and effect sizes (Fisher exact, odds ratios)
- C3 vs C0: error 100%->0% for all models. p<1e-4, OR~0 (huge). The signal works.
- C3 vs C2: Haiku 0.90 (p=1e-4, OR=0.01); Sonnet 1.00 (p<1e-4); **Opus 0.00 (p=1.0, OR=1.0)**.
- C3 vs C1: 0.00 for all (p=1.0). Inline does not beat strong guidance.

## C4 - is false completeness worse than no signal?
Not in this regime. C4-vs-C0 error reduction: Haiku +0.50 (the false "reviewed/verified" tag
*raised* Haiku inspection to 5/10 vs C2's 1/10), Sonnet 0.00, Opus +1.00. C4 vs C2 (cleaner false-
assurance test): Haiku 50% vs 90% (lower), Sonnet 100% vs 100% (unchanged), Opus 0/10 blind vs 0/10
(the false tag cost Opus one *non-blind* mis-resolution at medium confidence, not a confident-wrong).
Conclusion: the truthfulness of the inline tag mattered far less than whether the model inspected;
"false sense of completeness is worse than none" is **not supported** at N=10 on this task.

## Limitations (stated plainly)
- **Single task family fully powered.** Only Task 1 (buried supersession) was collected at N=10x5x3.
  Five other boundary-blindness task families are built (`gen_materials.py`) but not run (compute
  budget). Generalization across task types is therefore unverified - the headline rests on one
  family. This is the biggest caveat.
- **Narrow, same-generation gradient.** Haiku 4.5 / Sonnet 4.6 / Opus 4.8. The capability range is
  compressed; "erosion with capability" is demonstrated across one generation, not a wide ladder.
  The Sonnet>Haiku non-monotonicity in volunteering (0 vs 1) is within noise.
- **Temperature uncontrolled** (harness default). Constant across arms; adds variance, no arm bias.
- **Scoring largely deterministic** (answer parse + tool-use counter) and effects are near-saturated
  (0% vs 100%), so blinded human adjudication was not the bottleneck; the one judgment nuance (Opus
  C4) is documented above.
- **Subjects are tool-using agents** that read their whole context; this is exactly why the in-context
  v1 design hit a ceiling and why the out-of-context v2 design was necessary. Findings apply to the
  agentic setting (model + tools + retrievable sources), which is the setting of interest.

## Bottom line for the strategic question
Under a properly-powered boundary-blindness regime (C0 = 100% for all models), **forcing a
completeness signal inline (C3) is highly effective (Q1 + Q2 both strongly positive), but its
advantage is entirely over leaving the check *merely available* (C2), and that advantage erodes to
zero at the frontier because the frontier model volunteers to check on its own.** Against a strong
plain-instruction baseline (C1), the inline mechanism adds nothing at any capability level. So: if
you can give the agent good standing instructions to verify completeness, do that - it is as good as
inline signals and far cheaper than re-engineering every record to carry inline provenance. The
inline mechanism's niche is weak/mid agents operating *without* such guidance and *without* the
disposition to volunteer a check.
