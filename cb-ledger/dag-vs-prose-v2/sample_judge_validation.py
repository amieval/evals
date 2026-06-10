#!/usr/bin/env python
"""Judge-validation sampling hook (CB m-judge-validation / method:a4).

Two modes:

1. Sample: draw K (generation, assertion) judge decisions from .eval
   logs into a human-scoring sheet. The human fills in "human" with
   yes/no for each row, blind to the judge column order.

       sample_judge_validation.py sample logs/**/*.eval --k 45 --seed 7 \
           --out judge-validation-sheet.json

2. Score: once the sheet is filled, compute raw agreement and Cohen's
   kappa - the artifact a judge-validation belief cites.

       sample_judge_validation.py score judge-validation-sheet.json

The default K of 45 matches NEXT_EXPERIMENT.md's scorer-consistency
budget (5 outputs x 9 assertions).
"""

import argparse
import json
import random
import sys
from pathlib import Path

from inspect_ai.log import read_eval_log

from assertions import ASSERTIONS


def collect_decisions(log_paths):
    decisions = []
    for path in log_paths:
        log = read_eval_log(str(path))
        for sample in log.samples or []:
            for scorer_name, score in (sample.scores or {}).items():
                assertion_id = scorer_name.removeprefix("llm-judge-")
                if assertion_id not in ASSERTIONS:
                    continue
                decisions.append(
                    {
                        "log": str(path),
                        "run_id": log.eval.run_id,
                        "case_id": str(sample.id),
                        "ruler": scorer_name,
                        "assertion_id": assertion_id,
                        "assertion": ASSERTIONS[assertion_id],
                        "code": sample.output.completion,
                        "judge": "yes" if score.value == "C" else "no",
                        "human": None,
                    }
                )
    return decisions


def cmd_sample(args):
    decisions = collect_decisions(args.logs)
    if not decisions:
        sys.exit("no judge decisions found in the given logs")

    rng = random.Random(args.seed)
    k = min(args.k, len(decisions))
    sheet = {
        "instructions": (
            "For each row read the assertion and the code, then set \"human\" to "
            "\"yes\" or \"no\": does the code satisfy or reflect the assertion in its "
            "design? Judge independently - do not look at the \"judge\" field until done. "
            "Then run: sample_judge_validation.py score <this file>"
        ),
        "seed": args.seed,
        "rows": rng.sample(decisions, k),
    }
    Path(args.out).write_text(json.dumps(sheet, indent=2) + "\n")
    print(f"wrote {args.out}: {k} of {len(decisions)} judge decisions sampled")


def cohen_kappa(pairs):
    n = len(pairs)
    agree = sum(1 for j, h in pairs if j == h)
    p_observed = agree / n
    p_judge_yes = sum(1 for j, _ in pairs if j == "yes") / n
    p_human_yes = sum(1 for _, h in pairs if h == "yes") / n
    p_chance = p_judge_yes * p_human_yes + (1 - p_judge_yes) * (1 - p_human_yes)
    if p_chance == 1.0:
        return 1.0
    return (p_observed - p_chance) / (1 - p_chance)


def cmd_score(args):
    sheet = json.loads(Path(args.sheet).read_text())
    rows = sheet["rows"]
    unscored = [r for r in rows if r.get("human") not in ("yes", "no")]
    if unscored:
        sys.exit(f"{len(unscored)} of {len(rows)} rows still lack a human yes/no")

    pairs = [(r["judge"], r["human"]) for r in rows]
    agree = sum(1 for j, h in pairs if j == h)
    kappa = cohen_kappa(pairs)

    by_assertion = {}
    for r in rows:
        slot = by_assertion.setdefault(r["assertion_id"], [0, 0])
        slot[1] += 1
        if r["judge"] == r["human"]:
            slot[0] += 1

    print(f"rows: {len(rows)}")
    print(f"raw agreement: {agree}/{len(rows)} ({agree / len(rows):.2%})")
    print(f"cohen kappa: {kappa:.3f}")
    for aid in sorted(by_assertion):
        a, t = by_assertion[aid]
        print(f"  {aid}: {a}/{t}")
    print(
        "\nCite this output (with the sheet file) as the artifact of the "
        "judge-validation belief: an active belief tagged judge-validation with the "
        "ruler and eval subjects (method:a4)."
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)

    s = sub.add_parser("sample", help="draw judge decisions into a human-scoring sheet")
    s.add_argument("logs", nargs="+", help=".eval log files")
    s.add_argument("--k", type=int, default=45)
    s.add_argument("--seed", type=int, default=7)
    s.add_argument("--out", required=True)
    s.set_defaults(func=cmd_sample)

    c = sub.add_parser("score", help="compute agreement + kappa from a filled sheet")
    c.add_argument("sheet")
    c.set_defaults(func=cmd_score)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
