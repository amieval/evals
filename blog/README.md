# Composable Beliefs Blog

Eval-driven content exploring how a structured belief DAG grounds LLM reasoning and produces demonstrably better outcomes.

## Posts

| # | Title | Status |
|---|---|---|
| 01 | The Composition Problem | draft |
| 02 | Your Agent's Beliefs Are Stale | draft |
| 03 | The Amnesiac Agent | draft |
| 04 | The Self-Aware Agent | draft |
| 05 | How Certain Is Your Agent? | draft |
| 06 | Patches: Reproducible Arguments | draft |

## Evals

Each post documents a three-condition evaluation (C0 baseline, C1 flat instructions, C2 composable beliefs DAG). The eval materials for the boundary-blindness eval ship in `evals/boundary-blindness/` and include `PREREGISTRATION.md`, `REPORT.md`, and `scorer.py`.

## Architecture

- `evals/` - eval materials: preregistrations, reports, and scoring scripts
- `blog/NN-*/post.md` - blog writeups

## Design Decisions

**Synthetic data over real DAG data.** Each eval uses a purpose-built scenario in a neutral domain (software project planning) rather than real operational data. Reasons: isolation (one phenomenon per eval), privacy (no private data), reproducibility (readers can run the evals), domain neutrality (relatable to technical audience).

**Three conditions, not two.** C1 (flat instructions with the same information) is the critical control. Without it, any improvement in C2 could be attributed to simply having the information. C1 isolates structure from content.

**Scoring rubrics, not binary pass/fail.** Each eval has weighted criteria that capture different aspects of quality. Negative weights penalize specific failure modes (false confidence, theory-as-fact, contradictions).
