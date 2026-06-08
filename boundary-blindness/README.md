# Boundary-Blindness & Forced Completeness Signals - Eval

A controlled behavioral eval testing whether forcing a **completeness/provenance signal inline**
with each fact reduces an agent's rate of **acting confidently on an incomplete view**
(boundary-blindness), and whether that benefit erodes or persists across a model-capability gradient.

## Files
- `PREREGISTRATION.md` - design locked before data collection (arms, tasks, prompts, rubric,
  confound control, stats, decision rules).
- `gen_materials.py` - parametrized material generator. `python3 gen_materials.py <task> <arm> <tier>`
  prints a subject prompt; `sources` writes C2 inspect-files; `key` prints the scoring key.
- `scorer.py` - reads `runs/results.jsonl`, prints per-cell error rates + Wilson CIs, Fisher exact
  contrasts, odds ratios, (C3−C2)/(C3−C1) gaps per model, C0-headroom audit, Q1 + C4 metrics.
- `key.json` - scoring key (anchor vs correct values + boundary keywords) for all 6 tasks.
- `sources/` - C2 "inspectable source" files.
- `runs/results.jsonl` - collected run records (appended during collection).
- `STATUS.md` - execution log, including the 2026-06-02 capacity-overload blocker and recovery.

## Arms
C0 no-signal (boundary fact buried) · C1 +strong guidance · C2 boundary fact behind a costly
unsignposted inspect step · C3 inline boundary signal · C4 inline but MISLEADING (false-complete).

## Harness
Each run = one fresh-context subagent pinned to a model (Haiku 4.5 / Sonnet 4.6 / Opus 4.8).
Temperature is harness-default and uncontrolled (recorded as a limitation; constant across arms).

## Status
See `STATUS.md`. Apparatus complete; collection runs appended to `runs/results.jsonl`.
