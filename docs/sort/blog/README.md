# Composable Beliefs Blog

Eval-driven content exploring how a structured belief DAG grounds LLM reasoning
and produces demonstrably better outcomes.

## Status — read first

These six posts are **early design sketches, not writeups of completed evals.**
Each isolates one failure mode in an illustrative C0/C1/C2 scenario, but **none
was run as written**, several carry "Expected results" rather than data, and
posts 05–06 explore schema features (`confidence`, `patch`) that were later
removed. The program they prefigure was consolidated into the
[`eval-design-depth-non-optional`](../2026-06-01-eval-design-depth-non-optional.md)
spec (C0–C4, *non-optional depth*) and partially realized in
[`boundary-blindness/`](../boundary-blindness/) — the only eval in this repo with
a real `REPORT.md`. Treat these posts as **content seeds to be rewritten against
real data**, not as published results.

## Posts

| # | Title | Failure mode | Real-eval status |
|---|---|---|---|
| 01 | The Composition Problem | non-adjacent conflict to surface | designed — boundary-blindness joint-conflict task (not run) |
| 02 | Your Agent's Beliefs Are Stale | acting on a buried supersession | **RUN** — boundary-blindness Task 1 (N=10) |
| 03 | The Amnesiac Agent | cross-session reasoning carryover | not in the current eval program |
| 04 | The Self-Aware Agent | speculation-as-fact / reflexive agreement | designed — eval-design tasks 1 & 4 (not run) |
| 05 | How Certain Is Your Agent? | confidence calibration | feature removed (`confidence` field) |
| 06 | Patches: Reproducible Arguments | reproducible argument routing | feature removed (`patch` kind) |

Each post carries a matching status banner at its head.

## Design decisions (carried over from the sketches)

**Synthetic data over real DAG data.** Each scenario is purpose-built in a
neutral domain (software project planning) rather than real operational data:
isolation (one phenomenon per eval), privacy (no private data), reproducibility
(readers can run it), domain neutrality (relatable to a technical audience).

**The critical control is C1.** Flat instructions carrying the *same*
information isolate structure from content — without it, any C2 gain could be
"they just had the information." The consolidated design ([`eval-design-depth-non-optional`](../2026-06-01-eval-design-depth-non-optional.md))
extends this to five conditions (C0–C4) to also isolate *non-optional depth* and
a misleading-partial-depth arm.

**Scoring rubrics, not binary pass/fail.** Weighted criteria capture different
quality aspects; negative weights penalize specific failure modes (false
confidence, theory-as-fact, contradictions).
