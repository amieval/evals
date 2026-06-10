#!/usr/bin/env python
"""inspect2manifest: convert Inspect .eval logs to a CB run-manifest.

The adapter side of the contract fixed by composable-beliefs
docs/run-manifest.md (manifest_version 1): Inspect adapts *to* the
manifest; CB never reads Inspect's native log format. One manifest
covers one eval; each .eval log becomes one run.

The adapter is mechanical. The single judgment input - which cases are
load-bearing - is passed explicitly via --load-bearing; everything else
is read from the logs. Logs from the mockllm provider force the
"fixture" tag (honest provenance per method:a5): a mock-derived
collection must never be mistaken for a finding.

Usage:

    inspect2manifest.py LOG.eval [LOG.eval ...] \
        --eval-id cb-ledger-smoke-v1 \
        --out run-manifest.json \
        [--model-version mockllm/model@unversioned] \
        [--load-bearing case3,case5] \
        [--tag extra-tag]

Outcome mapping: Inspect score value "C" -> "pass", "I" -> "fail",
anything else passes through stringified (e.g. partial credit values).
"""

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

from inspect_ai.log import read_eval_log

MANIFEST_VERSION = 1


def outcome(value) -> str:
    return {"C": "pass", "I": "fail"}.get(value, str(value))


def score_detail(score) -> str:
    parts = []
    if score.answer:
        parts.append(f"answer: {score.answer}")
    if score.explanation and score.explanation != score.answer:
        parts.append(f"explanation: {score.explanation}")
    return "; ".join(parts) or "no detail recorded by scorer"


def run_entry(log, log_path: Path, base_dir: Path, load_bearing: set[str]) -> dict:
    samples = log.samples or []
    scorer_names = sorted({name for s in samples for name in (s.scores or {})})

    scorers = []
    for name in scorer_names:
        scored = [(s, s.scores[name]) for s in samples if name in (s.scores or {})]
        counts = Counter(outcome(score.value) for _, score in scored)

        cases = [
            {
                "case_id": str(sample.id),
                "outcome": outcome(score.value),
                "detail": score_detail(score),
            }
            for sample, score in scored
            if str(sample.id) in load_bearing
        ]

        scorers.append(
            {
                "ruler": name,
                "aggregate": {"outcome_counts": dict(sorted(counts.items()))},
                "load_bearing_cases": cases,
            }
        )

    return {
        "run_id": log.eval.run_id,
        "log": f"document:{log_path.resolve().relative_to(base_dir).as_posix()}",
        "cases": len(samples),
        "scorers": scorers,
    }


def build_manifest(args) -> dict:
    logs = []
    for raw_path in args.logs:
        path = Path(raw_path)
        log = read_eval_log(str(path))
        if log.status != "success":
            sys.exit(f"inspect2manifest: refusing log with status {log.status!r}: {path}")
        logs.append((log, path))

    logs.sort(key=lambda pair: pair[0].stats.started_at)

    tasks = {log.eval.task for log, _ in logs}
    models = {log.eval.model for log, _ in logs}
    if len(tasks) > 1 or len(models) > 1:
        sys.exit(f"inspect2manifest: logs mix tasks/models: {sorted(tasks)}, {sorted(models)}")

    run_ids = [log.eval.run_id for log, _ in logs]
    if len(set(run_ids)) != len(run_ids):
        sys.exit("inspect2manifest: duplicate run_id across logs")

    first_log = logs[0][0]
    model = first_log.eval.model
    date = first_log.stats.started_at[:10]
    model_version = args.model_version or f"{model}@{date}"

    digest_input = f"{first_log.eval.task}|{first_log.eval.task_version}|{model}"
    config_digest = "sha256:" + hashlib.sha256(digest_input.encode()).hexdigest()[:16]

    tags = list(dict.fromkeys(args.tag or []))
    if model.startswith("mockllm/") and "fixture" not in tags:
        tags.append("fixture")

    base_dir = Path(args.out).resolve().parent
    load_bearing = {c for c in (args.load_bearing or "").split(",") if c}

    return {
        "manifest_version": MANIFEST_VERSION,
        "eval_id": args.eval_id,
        "date": date,
        "model": model,
        "model_version": model_version,
        "harness": {
            "name": "inspect",
            "version": first_log.eval.packages.get("inspect_ai", "unknown"),
            "task": first_log.eval.task,
            "config_digest": config_digest,
        },
        "tags": tags,
        "runs": [run_entry(log, path, base_dir, load_bearing) for log, path in logs],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", help="Inspect .eval log files (one per run)")
    parser.add_argument("--eval-id", required=True, help="the eval's identity (first eval: URI segment)")
    parser.add_argument("--out", required=True, help="manifest output path; log paths are recorded relative to it")
    parser.add_argument("--model-version", help="staleness pivot (default: <model>@<run date>)")
    parser.add_argument("--load-bearing", help="comma-separated case ids to mint per-case observations for")
    parser.add_argument("--tag", action="append", help="extra tag applied to every emitted belief (repeatable)")
    args = parser.parse_args()

    manifest = build_manifest(args)
    Path(args.out).write_text(json.dumps(manifest, indent=2) + "\n")
    runs = manifest["runs"]
    print(
        f"wrote {args.out}: {len(runs)} run(s), "
        f"{sum(len(r['scorers']) for r in runs)} (run, ruler) aggregate(s), "
        f"{sum(len(s['load_bearing_cases']) for r in runs for s in r['scorers'])} load-bearing case(s)"
    )


if __name__ == "__main__":
    main()
