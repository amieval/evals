# cb-ledger: Inspect -> composable-beliefs adapter + the v2 study scaffold

The harness side of the CB run-manifest contract
(`composable-beliefs/docs/run-manifest.md`). CB is the ledger, not the lab bench:
Inspect runs live here, and only their *output record* - a neutral run-manifest -
crosses into the belief graph.

## Layout

- `inspect2manifest.py` - the adapter: N Inspect `.eval` logs (one per run) -> one
  version-1 run-manifest. Mechanical except for one judgment input
  (`--load-bearing`). Logs from `mockllm/*` models force the `fixture` tag - a
  mock-derived collection must never be mistaken for a finding.
- `task_smoke.py` + `logs/` + `run-manifest.json` - the tier-2 round-trip artifact:
  a trivial task run 3x under Inspect's `mockllm` provider (real logs, zero API
  cost), adapted, and imported into `collection/` (`fxm:` namespace).
- `collection/` + `collections.json` - the imported fixture collection; verify with
  `mix cb.verify.collection fxm --registry <this dir>/collections.json` from the
  composable-beliefs repo.
- `dag-vs-prose-v2/` - the four-condition isolation study (NEXT_EXPERIMENT.md) plus
  the flat-bullets control, scaffolded so the real run is one command plus judgment.
- `.venv-inspect/` (repo root) - `inspect-ai` virtualenv.

## The one-command path to a real finding

```bash
cd cb-ledger/dag-vs-prose-v2
./run.sh anthropic/<model-under-test> anthropic/<judge-model>   # N=10, R=3 runs/condition
```

then, per condition, with your judgment supplying the load-bearing cases:

```bash
../../.venv-inspect/bin/python ../inspect2manifest.py logs/b/*.eval \
    --eval-id dag-vs-prose-v2-b --out manifest-b.json --load-bearing gen03,gen07
```

then in composable-beliefs:

```bash
mix cb.import.eval manifest-b.json --collection <eval-collection>/beliefs.json --write
mix cb.verify.collection <ns> --registry <registry>
```

The importer emits observation primitives only. Cross-ruler agreement compounds,
verdicts, and guidance are yours to author through the preflight/adjudicate/import
write flow - that division of labor is the point.

## Judge validation (m-judge-validation)

The nine scorers are LLM judges (`llm-judge-*` per `method:a4`), so the methodology
contract demands a human-agreement record per (judge, eval):

```bash
../../.venv-inspect/bin/python sample_judge_validation.py sample logs/**/*.eval \
    --k 45 --out judge-validation-sheet.json
# fill in the "human" fields, blind to the judge column, then:
../../.venv-inspect/bin/python sample_judge_validation.py score judge-validation-sheet.json
```

Cite the scored sheet as the artifact of a `judge-validation`-tagged belief carrying
the ruler and eval subjects.

## Status

- Adapter: validated against genuine Inspect logs (mockllm-produced; tier 2). Real
  API-model logs have the same structure but remain unexercised.
- Condition prompts: `a`/`b` are verbatim from `purity-test/context_{a,b}`;
  `c`/`d`/`e` are mechanical renderings of the same assertion texts - review `c`
  (compounds-as-prose) before the real run, since its framing carries the
  specificity-vs-structure question.
- `dag-vs-prose-v2/logs-smoke/`, `manifest-smoke.json`, `sheet-smoke.json`:
  disposable plumbing-smoke artifacts, safe to delete.
- **The mission gate stays open**: one actual finding, end to end, with a human
  choosing the eval, the load-bearing cases, and the verdict.
