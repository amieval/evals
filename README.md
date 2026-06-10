# Composable Beliefs — Eval Suite

Controlled evaluations testing whether structuring knowledge as a **belief /
assertion DAG** (primitives + compounds with explicit dependencies) produces
measurably better LLM behavior than the same information as prose or flat rules.

## Core concepts

- **Primitive** — an atomic, source-grounded claim; the smallest unit reasoned about.
- **Compound** — a composition of primitives (and other compounds) with an
  explicit dependency graph; the composition is *declared*, not left for the
  model to infer.
- **Assertion DAG** — the reasoning structure, externalized. The bet under test:
  an explicit, inspectable dependency structure changes model behavior in ways
  flat prose does not.

## The evals

| Eval | Tests | Status |
|---|---|---|
| **`boundary-blindness/`** | Whether forcing a completeness/provenance signal at the point of use reduces agents acting confidently on incomplete views. Five conditions C0–C4, three models (Haiku/Sonnet/Opus), N=10. | **Run** — `REPORT.md` (Task 1, buried supersession); other task families built, not yet run. Has `PREREGISTRATION.md`, `scorer.py`, `runs/`, `STATUS.md`. |
| **`purity-test/`** | Prose context vs assertion-DAG context on a bash test-generation task. N=3 per context. | **Run** — DAG 9/9 compound adherence vs prose 2/9 (see `results/`, `run.sh` / `score.sh`). |
| **`conceptual-prototype/`** | Logical-validity proof of concept (apples / fruit / reproduction). | Prototype — `verdict.md`, `diagram.txt`. |
| **`its-just-shell-reasoning-test/`** | Qualitative: does DAG-structured context yield more insightful reasoning than the prose equivalent? | Designed — `prose.md` vs `dag/`, manual comparison. |
| **`knowledge-domains/`** | Template for decomposing a domain into a DAG (stable-marriage instantiated under `domains/`). | Template — no runs. |

## Where the infra lives

This repo is the **append-only archive of executed evals**: each directory above is
a run record (task snapshot, logs, results, report). Shared execution infra - the
Inspect adapter (`inspect2manifest.py`), LLM-judge scorers, study scaffolds in
development (dag-vs-prose-v2), and the toolchain - lives in the sibling **`bench`**
repo; the belief-graph framework it feeds is `composable-beliefs`, and the graphs
themselves are `belief-collections`. When a bench study runs for real, its record
lands here as a snapshot. (`cb-ledger/` briefly lived here before moving to bench.)

## Design driver & content

- **`2026-06-01-eval-design-depth-non-optional.md`** — the current spec that
  drives the suite: it isolates *non-optional depth* (C0–C4) and is the design
  `boundary-blindness/` realizes.
- **`blog/`** — eval-driven post drafts. They are design sketches, not results;
  `blog/README.md` maps which map to real runs.

## Analysis docs

`METHODOLOGY.md` (full method + purity-test findings), `IMPLICATIONS.md`,
`CONFLATION.md` (hallucination-as-conflation), `LIKELIHOOD_ANALYSIS.md`,
`NEXT_EXPERIMENT.md`, `SESSION_SUMMARY.md`, `ASSERTION_DAGS_THESIS_SECTION.md`,
`CONNECTION_TO_ITSJUSTSHELL.md`.

## Quick start (purity-test)

```bash
cd purity-test/
./run.sh 3     # 3 runs per context (prose vs DAG)
./score.sh     # score outputs against primitives + compounds
cat results/summary.txt
```

Requires the `claude` CLI (Claude Code) installed and authenticated.

## Status

Early-stage but with real runs: **purity-test** (N=3, one task, one model — strong
but narrow signal) and **boundary-blindness** (N=10 on one task family, full
`REPORT.md`). The remaining evals are designed or templated. Proof of concept,
not a validated result.
